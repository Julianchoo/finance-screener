import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import io
from datetime import datetime as dt
import sys
import os

# Add the parent directory to sys.path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.financial_analysis import advanced_screen_stocks, get_field_options, validate_screening_filters
from config import (
    ESSENTIAL_SCREENING_FIELDS, ADVANCED_SCREENING_FIELDS, ALL_SCREENING_FIELDS,
    SCREENING_CATEGORIES, PREDEFINED_SCREENS, CHART_COLORS
)

st.set_page_config(page_title="Advanced Stock Screening", page_icon="🔎", layout="wide")

def create_filter_ui(field_name, field_config, key_prefix=""):
    """Create UI elements for a screening field filter"""
    display_name = field_config['display_name']
    data_type = field_config['data_type']
    comparison_ops = field_config['comparison_ops']
    
    st.write(f"**{display_name}**")
    
    # Operator selection
    op_labels = {
        'gt': 'Greater than (>)',
        'gte': 'Greater than or equal (≥)',
        'lt': 'Less than (<)',
        'lte': 'Less than or equal (≤)',
        'eq': 'Equal to (=)',
        'btwn': 'Between',
        'is-in': 'Is one of'
    }
    
    selected_ops = [op for op in comparison_ops if op in op_labels]
    op_options = [op_labels[op] for op in selected_ops]
    
    operator_key = f"{key_prefix}_{field_name}_op"
    selected_op_label = st.selectbox("Condition:", op_options, key=operator_key)
    selected_op = selected_ops[op_options.index(selected_op_label)]
    
    # Value inputs based on data type and operator
    values = []
    
    if data_type == 'categorical':
        options = get_field_options(field_name)
        if selected_op == 'is-in':
            value_key = f"{key_prefix}_{field_name}_values"
            values = st.multiselect("Select values:", options, key=value_key)
        else:  # eq
            value_key = f"{key_prefix}_{field_name}_value"
            value = st.selectbox("Select value:", options, key=value_key)
            if value:
                values = [value]
    
    else:  # numeric
        if selected_op == 'btwn':
            col1, col2 = st.columns(2)
            with col1:
                min_key = f"{key_prefix}_{field_name}_min"
                if field_config['format'] == 'billions':
                    min_val = st.number_input("Minimum (Billions $):", key=min_key, value=0.0)
                    min_val = min_val * 1000000000  # Convert to actual value
                elif field_config['format'] == 'percentage':
                    min_val = st.number_input("Minimum (%):", key=min_key, value=0.0)
                else:
                    min_val = st.number_input("Minimum:", key=min_key, value=0.0)
            with col2:
                max_key = f"{key_prefix}_{field_name}_max"
                if field_config['format'] == 'billions':
                    max_val = st.number_input("Maximum (Billions $):", key=max_key, value=100.0)
                    max_val = max_val * 1000000000  # Convert to actual value
                elif field_config['format'] == 'percentage':
                    max_val = st.number_input("Maximum (%):", key=max_key, value=100.0)
                else:
                    max_val = st.number_input("Maximum:", key=max_key, value=100.0)
            values = [min_val, max_val]
        else:
            value_key = f"{key_prefix}_{field_name}_value"
            if field_config['format'] == 'percentage':
                value = st.number_input("Value (%):", key=value_key, value=5.0, step=0.1)
            elif field_config['format'] == 'billions':
                value = st.number_input("Value (Billions $):", key=value_key, value=1.0, step=0.1)
                # Convert billions to actual value for yfinance
                value = value * 1000000000
            elif field_config['format'] == 'currency':
                value = st.number_input("Value ($):", key=value_key, value=10.0, step=0.1)
            else:
                value = st.number_input("Value:", key=value_key, value=1.0, step=0.1)
            values = [value]
    
    # Return in EquityQuery format: (operator, [field, value(s)])
    return (selected_op, [field_name] + values) if values else None

def create_screening_charts(df):
    """Create comprehensive screening visualizations"""
    if df.empty:
        return None, None, None
    
    # Market Cap vs PE Ratio scatter
    scatter_fig = None
    if all(col in df.columns for col in ['Market Cap (Billion $)', 'PE Ratio', 'Symbol']):
        plot_df = df.dropna(subset=['Market Cap (Billion $)', 'PE Ratio'])
        if not plot_df.empty:
            scatter_fig = px.scatter(
                plot_df,
                x='Market Cap (Billion $)',
                y='PE Ratio',
                size='Market Cap (Billion $)',
                color='Sector' if 'Sector' in plot_df.columns else None,
                hover_name='Symbol',
                hover_data=['Company'] if 'Company' in plot_df.columns else None,
                title="Market Cap vs PE Ratio",
                template="plotly_white",
                log_x=True
            )
            scatter_fig.update_layout(height=500)
    
    # Sector distribution pie chart
    pie_fig = None
    if 'Sector' in df.columns:
        sector_counts = df['Sector'].value_counts().head(10)
        if not sector_counts.empty:
            pie_fig = px.pie(
                values=sector_counts.values,
                names=sector_counts.index,
                title="Sector Distribution",
                template="plotly_white"
            )
            pie_fig.update_layout(height=400)
    
    # Top performers bar chart
    bar_fig = None
    if 'Market Cap (Billion $)' in df.columns and 'Company' in df.columns:
        top_companies = df.nlargest(15, 'Market Cap (Billion $)')
        bar_fig = go.Figure(data=[
            go.Bar(
                x=top_companies['Market Cap (Billion $)'],
                y=top_companies['Company'].str[:40],  # Truncate long names
                orientation='h',
                marker_color=CHART_COLORS[0]
            )
        ])
        bar_fig.update_layout(
            title="Top 15 Companies by Market Cap",
            xaxis_title="Market Cap (Billion $)",
            yaxis_title="Company",
            template="plotly_white",
            height=600
        )
    
    return scatter_fig, pie_fig, bar_fig

def display_results_table(df, max_rows=100):
    """Display results with formatting and pagination"""
    if df.empty:
        st.warning("No results found matching your criteria.")
        return
    
    # Show summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Results", len(df))
    
    with col2:
        if 'Market Cap (Billion $)' in df.columns:
            avg_mcap = df['Market Cap (Billion $)'].mean()
            st.metric("Avg Market Cap", f"${avg_mcap:.1f}B")
    
    with col3:
        if 'PE Ratio' in df.columns:
            avg_pe = df['PE Ratio'].mean()
            st.metric("Avg PE Ratio", f"{avg_pe:.1f}")
    
    with col4:
        if 'Dividend Yield (%)' in df.columns:
            avg_div = df['Dividend Yield (%)'].mean()
            st.metric("Avg Div Yield", f"{avg_div:.1f}%")
    
    st.markdown("---")
    
    # Display options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Get numeric columns for sorting - simplified approach
        sort_options = []
        for col in df.columns:
            try:
                if pd.api.types.is_numeric_dtype(df[col]):
                    sort_options.append(col)
            except:
                continue
        
        if not sort_options:
            # Fallback to common numeric column names
            common_numeric = ['intradaymarketcap', 'peratio.lasttwelvemonths', 'forward_dividend_yield', 'percentchange', 'volume']
            sort_options = [col for col in common_numeric if col in df.columns]
        
        if sort_options:
            sort_by = st.selectbox("Sort by:", sort_options, index=0)
        else:
            sort_by = None
    
    with col2:
        sort_order = st.selectbox("Order:", ["Descending", "Ascending"], index=0)
        ascending = sort_order == "Ascending"
    
    with col3:
        show_rows = st.selectbox("Show rows:", [25, 50, 100, 250], index=1)
    
    # Sort and limit dataframe
    if sort_options and sort_by:
        df_display = df.sort_values(sort_by, ascending=ascending).head(show_rows)
    else:
        df_display = df.head(show_rows)
    
    # Format numeric columns for display
    display_df = df_display.copy()
    
    # Handle duplicate column names
    if len(display_df.columns) != len(set(display_df.columns)):
        st.warning("⚠️ Duplicate column names detected. Removing duplicates...")
        # Get unique column names by keeping first occurrence
        display_df = display_df.loc[:, ~display_df.columns.duplicated(keep='first')]
    
    # Format currency columns
    for col in display_df.columns:
        try:
            if 'Price' in col and pd.api.types.is_numeric_dtype(display_df[col]):
                display_df[col] = display_df[col].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "N/A")
            elif 'Billion' in col and pd.api.types.is_numeric_dtype(display_df[col]):
                display_df[col] = display_df[col].apply(lambda x: f"${x:.2f}B" if pd.notna(x) else "N/A")
            elif ('Yield' in col or '%' in col) and pd.api.types.is_numeric_dtype(display_df[col]):
                display_df[col] = display_df[col].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "N/A")
            elif col in ['PE Ratio', 'EPS', 'Debt to Equity'] and pd.api.types.is_numeric_dtype(display_df[col]):
                display_df[col] = display_df[col].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "N/A")
        except:
            continue
    
    # Display the table
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        height=600
    )

def main():
    st.title("🔎 Advanced Stock Screening")
    st.markdown("*Screen all available stocks with comprehensive filtering capabilities*")
    st.markdown("---")
    
    # Sidebar for screening controls
    st.sidebar.header("🔍 Screening Controls")
    
    # Mode selection
    screening_mode = st.sidebar.radio(
        "Screening Mode:",
        ["Quick Screens", "Custom Filters", "Advanced Builder"],
        help="Choose your screening approach"
    )
    
    st.sidebar.markdown("---")
    
    # Initialize screening parameters
    filters = []
    predefined_screen = None
    
    if screening_mode == "Quick Screens":
        st.sidebar.subheader("📋 Predefined Screens")
        
        screen_options = list(PREDEFINED_SCREENS.keys())
        selected_screen = st.sidebar.selectbox(
            "Choose a predefined screen:",
            [""] + screen_options
        )
        
        if selected_screen:
            predefined_screen = selected_screen
            screen_config = PREDEFINED_SCREENS[selected_screen]
            st.sidebar.info(f"**{selected_screen}**\n\n{screen_config['description']}")
    
    elif screening_mode == "Custom Filters":
        st.sidebar.subheader("🎯 Essential Filters")
        
        # Group essential fields by category
        essential_by_category = {}
        for field_name, field_config in ESSENTIAL_SCREENING_FIELDS.items():
            category = field_config['category']
            if category not in essential_by_category:
                essential_by_category[category] = {}
            essential_by_category[category][field_name] = field_config
        
        # Create expandable sections for each category
        for category, fields in essential_by_category.items():
            with st.sidebar.expander(f"{category} ({len(fields)} fields)"):
                for field_name, field_config in fields.items():
                    enable_key = f"enable_{field_name}"
                    enable_filter = st.checkbox(
                        field_config['display_name'],
                        key=enable_key,
                        help=f"Filter by {field_config['display_name'].lower()}"
                    )
                    
                    if enable_filter:
                        filter_tuple = create_filter_ui(field_name, field_config, "custom")
                        if filter_tuple:
                            filters.append(filter_tuple)
    
    elif screening_mode == "Advanced Builder":
        st.sidebar.subheader("⚡ Advanced Filters")
        
        # All fields available
        all_by_category = {}
        for field_name, field_config in ALL_SCREENING_FIELDS.items():
            category = field_config['category']
            if category not in all_by_category:
                all_by_category[category] = {}
            all_by_category[category][field_name] = field_config
        
        # Create tabs for different categories
        categories = list(all_by_category.keys())
        selected_category = st.sidebar.selectbox("Select Category:", categories)
        
        if selected_category:
            st.sidebar.write(f"**{selected_category}**")
            st.sidebar.write(SCREENING_CATEGORIES.get(selected_category, ""))
            
            fields = all_by_category[selected_category]
            for field_name, field_config in fields.items():
                enable_key = f"enable_adv_{field_name}"
                enable_filter = st.sidebar.checkbox(
                    field_config['display_name'],
                    key=enable_key
                )
                
                if enable_filter:
                    with st.sidebar.expander(f"Configure {field_config['display_name']}", expanded=True):
                        filter_tuple = create_filter_ui(field_name, field_config, "advanced")
                        if filter_tuple:
                            filters.append(filter_tuple)
    
    # Result settings
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Results Settings")
    
    result_count = st.sidebar.slider(
        "Max Results:",
        min_value=25,
        max_value=250,
        value=100,
        step=25,
        help="Maximum number of stocks to return"
    )
    
    sort_options = ['intradaymarketcap', 'avgdailyvol3m', 'intradayprice', 'peratio.lasttwelvemonths', 'forward_dividend_yield']
    sort_field = st.sidebar.selectbox(
        "Sort by:",
        sort_options,
        index=0,
        format_func=lambda x: {
            'intradaymarketcap': 'Market Cap',
            'avgdailyvol3m': 'Volume', 
            'intradayprice': 'Price',
            'peratio.lasttwelvemonths': 'PE Ratio',
            'forward_dividend_yield': 'Dividend Yield'
        }.get(x, x)
    )
    
    sort_ascending = st.sidebar.checkbox("Sort Ascending", value=False)
    
    # Debug mode
    debug_mode = st.sidebar.checkbox("🐛 Debug Mode", value=False, help="Show detailed debugging information")
    
    # Screen button
    screen_button = st.sidebar.button("🔍 Run Screen", type="primary", use_container_width=True)
    
    # Main content area
    
    # Information section
    with st.expander("ℹ️ How to Use Advanced Stock Screening", expanded=False):
        st.markdown("""
        **Advanced Stock Screening** uses yfinance's powerful EquityQuery system to screen all available stocks:
        
        **📋 Quick Screens**: Pre-configured strategies for common investment approaches
        - Large Cap Value, High Growth, Dividend Aristocrats, Quality Small Caps
        
        **🎯 Custom Filters**: Essential fields organized by category
        - Market Data, Valuation, Profitability, Growth, Dividend, Financial Health, Geographic
        
        **⚡ Advanced Builder**: Access to all available screening fields
        - Technical indicators, ESG scores, detailed financial metrics
        
        **Key Features:**
        - Screen all stocks globally, not just predefined lists
        - Complex multi-condition filtering
        - Real-time data from yfinance
        - Interactive visualizations and exports
        
        **Tips:**
        - Start with Quick Screens to learn the system
        - Combine multiple filters for precise targeting
        - Use visualizations to spot patterns and outliers
        """)
    
    # Show active filters
    if filters:
        st.subheader("🎯 Active Filters")
        filter_descriptions = []
        
        for filter_tuple in filters:
            operator = filter_tuple[0]
            
            # Handle EquityQuery format: ('gt', ['field', value]) vs old format: ('gt', 'field', value)
            if isinstance(filter_tuple[1], list):
                # EquityQuery format
                field = filter_tuple[1][0]
                values = filter_tuple[1][1:]
            else:
                # Old format
                field = filter_tuple[1]
                values = filter_tuple[2:]
            
            field_config = ALL_SCREENING_FIELDS.get(field, {})
            display_name = field_config.get('display_name', field)
            
            op_text = {
                'gt': '>',
                'gte': '≥', 
                'lt': '<',
                'lte': '≤',
                'eq': '=',
                'btwn': 'between',
                'is-in': 'in'
            }.get(operator, operator)
            
            if operator == 'btwn' and len(values) == 2:
                desc = f"{display_name} {op_text} {values[0]} and {values[1]}"
            elif operator == 'is-in':
                desc = f"{display_name} {op_text} {', '.join(map(str, values))}"
            else:
                desc = f"{display_name} {op_text} {values[0]}"
            
            filter_descriptions.append(desc)
        
        st.info(" • ".join(filter_descriptions))
    
    elif predefined_screen:
        st.subheader("📋 Selected Screen")
        screen_config = PREDEFINED_SCREENS[predefined_screen]
        st.info(f"**{predefined_screen}**: {screen_config['description']}")
    
    else:
        st.info("👆 Configure your screening criteria in the sidebar and click 'Run Screen' to begin.")
    
    # Execute screening
    if screen_button:
        if not filters and not predefined_screen:
            st.warning("Please configure at least one filter or select a predefined screen.")
        else:
            # Validate filters
            if filters:
                is_valid, error_msg = validate_screening_filters(filters)
                if not is_valid:
                    st.error(f"Filter validation error: {error_msg}")
                    return
            
            with st.spinner("🔍 Screening stocks... This may take a moment."):
                # Execute the screen
                if debug_mode:
                    results_df, debug_info = advanced_screen_stocks(
                        filters=filters,
                        predefined_screen=predefined_screen,
                        count=result_count,
                        sort_field=sort_field,
                        sort_asc=sort_ascending,
                        debug_mode=True
                    )
                    # Store debug info in session state
                    st.session_state['debug_info'] = debug_info
                else:
                    results_df = advanced_screen_stocks(
                        filters=filters,
                        predefined_screen=predefined_screen,
                        count=result_count,
                        sort_field=sort_field,
                        sort_asc=sort_ascending,
                        debug_mode=False
                    )
                
                # Store results in session state
                st.session_state['screening_results'] = results_df
                st.session_state['screening_timestamp'] = dt.now()
    
    # Display results
    if 'screening_results' in st.session_state:
        results_df = st.session_state['screening_results']
        timestamp = st.session_state.get('screening_timestamp', dt.now())
        
        # Show debug information if available
        if 'debug_info' in st.session_state and debug_mode:
            debug_info = st.session_state['debug_info']
            
            with st.expander("🐛 Debug Information", expanded=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Environment Info:**")
                    st.write(f"yfinance version: `{debug_info.get('yfinance_version', 'Unknown')}`")
                    st.write(f"Import status: `{debug_info.get('import_status', 'Unknown')}`")
                    st.write(f"Query built: `{debug_info.get('query_built', 'Unknown')}`")
                    st.write(f"API response: `{debug_info.get('api_response', 'Unknown')}`")
                    
                    if debug_info.get('available_yf_attrs'):
                        st.write("**Available yfinance attributes:**")
                        st.code(", ".join(debug_info['available_yf_attrs']))
                
                with col2:
                    st.write("**Processing Steps:**")
                    for step in debug_info.get('processing_steps', []):
                        st.write(step)
                
                if debug_info.get('error_details'):
                    st.error(f"**Error Details:** {debug_info['error_details']}")
        
        if results_df.empty:
            st.error("❌ No stocks found matching your criteria. Try adjusting your filters.")
        else:
            st.success(f"✅ Found {len(results_df)} stocks matching your criteria")
            st.caption(f"Results from: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Results tabs
            tab_labels = ["📊 Results Table", "📈 Visualizations", "📋 Summary Stats", "📥 Export"]
            if 'debug_info' in st.session_state and debug_mode:
                tab_labels.append("🐛 Debug Info")
            
            tabs = st.tabs(tab_labels)
            tab1, tab2, tab3, tab4 = tabs[:4]
            if len(tabs) > 4:
                tab5 = tabs[4]
            
            with tab1:
                st.subheader("📊 Screening Results")
                display_results_table(results_df)
            
            with tab2:
                st.subheader("📈 Visualizations")
                
                scatter_fig, pie_fig, bar_fig = create_screening_charts(results_df)
                
                if scatter_fig:
                    st.plotly_chart(scatter_fig, use_container_width=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if pie_fig:
                        st.plotly_chart(pie_fig, use_container_width=True)
                
                with col2:
                    if bar_fig:
                        st.plotly_chart(bar_fig, use_container_width=True)
            
            with tab3:
                st.subheader("📋 Summary Statistics")
                
                # Numeric columns summary
                numeric_cols = results_df.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) > 0:
                    st.write("**Numeric Fields Summary:**")
                    summary_stats = results_df[numeric_cols].describe()
                    st.dataframe(summary_stats, use_container_width=True)
                
                # Categorical columns summary
                categorical_cols = results_df.select_dtypes(include=['object']).columns
                if len(categorical_cols) > 0:
                    st.write("**Categorical Fields Summary:**")
                    for col in categorical_cols[:5]:  # Show top 5 categorical columns
                        if col in results_df.columns:
                            value_counts = results_df[col].value_counts().head(10)
                            if not value_counts.empty:
                                st.write(f"**{col}:**")
                                st.dataframe(
                                    pd.DataFrame({'Count': value_counts.values}, index=value_counts.index),
                                    use_container_width=True
                                )
            
            with tab4:
                st.subheader("📥 Export Results")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Excel Export**")
                    
                    if st.button("📊 Generate Excel Report", type="primary"):
                        excel_buffer = io.BytesIO()
                        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                            results_df.to_excel(writer, sheet_name='Screening Results', index=False)
                            
                            # Add summary sheet
                            numeric_cols = results_df.select_dtypes(include=[np.number]).columns
                            if len(numeric_cols) > 0:
                                summary_stats = results_df[numeric_cols].describe()
                                summary_stats.to_excel(writer, sheet_name='Summary Statistics')
                        
                        timestamp_str = timestamp.strftime("%Y%m%d_%H%M")
                        filename = f"stock_screening_{timestamp_str}.xlsx"
                        
                        st.download_button(
                            label="💾 Download Excel File",
                            data=excel_buffer.getvalue(),
                            file_name=filename,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                
                with col2:
                    st.markdown("**CSV Export**")
                    
                    csv_data = results_df.to_csv(index=False)
                    timestamp_str = timestamp.strftime("%Y%m%d_%H%M")
                    csv_filename = f"stock_screening_{timestamp_str}.csv"
                    
                    st.download_button(
                        label="📄 Download CSV File",
                        data=csv_data,
                        file_name=csv_filename,
                        mime="text/csv"
                    )
                    
                    st.markdown("**Summary Info**")
                    st.write(f"**Results:** {len(results_df)} stocks")
                    st.write(f"**Fields:** {len(results_df.columns)} columns")
                    st.write(f"**Generated:** {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Debug info tab
            if len(tabs) > 4:
                with tab5:
                    st.subheader("🐛 Debug Information")
                    
                    if 'debug_info' in st.session_state:
                        debug_info = st.session_state['debug_info']
                        
                        st.write("**Full Debug Information:**")
                        st.json(debug_info)
                        
                        # Add a basic connectivity test
                        if st.button("🔬 Test Basic yfinance"):
                            with st.spinner("Testing basic yfinance functionality..."):
                                try:
                                    import yfinance as yf
                                    
                                    # Test basic ticker
                                    ticker = yf.Ticker("AAPL")
                                    info = ticker.info
                                    
                                    st.success("✅ Basic yfinance working!")
                                    st.write(f"AAPL symbol: {info.get('symbol', 'N/A')}")
                                    st.write(f"AAPL name: {info.get('longName', 'N/A')}")
                                    st.write(f"AAPL price: ${info.get('currentPrice', 'N/A')}")
                                    
                                    # Test screen function existence
                                    if hasattr(yf, 'screen'):
                                        st.success("✅ yf.screen function exists!")
                                    else:
                                        st.error("❌ yf.screen function not found!")
                                        
                                    # Show available attributes
                                    attrs = [attr for attr in dir(yf) if not attr.startswith('_')]
                                    st.write("**yfinance module contents:**")
                                    st.code(", ".join(attrs))
                                    
                                except Exception as e:
                                    st.error(f"❌ Basic yfinance test failed: {e}")

def test_equity_query_import():
    """Test function to check EquityQuery availability"""
    try:
        from yfinance import EquityQuery
        return "SUCCESS: Direct import", EquityQuery
    except ImportError as e1:
        try:
            from yfinance.scrapers.equity import EquityQuery
            return "SUCCESS: From scrapers.equity", EquityQuery
        except ImportError as e2:
            try:
                import yfinance.scrapers as scrapers
                EquityQuery = getattr(scrapers, 'EquityQuery', None)
                if EquityQuery:
                    return "SUCCESS: From scrapers module", EquityQuery
                else:
                    return f"FAILED: {e1}, {e2}, EquityQuery not in scrapers", None
            except ImportError as e3:
                return f"FAILED: {e1}, {e2}, {e3}", None

if __name__ == "__main__":
    main()