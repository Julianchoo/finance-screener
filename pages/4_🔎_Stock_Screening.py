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

from utils.financial_analysis import screen_stocks
from config import TICKER_LISTS, SCREENING_YEARS, PERFORMANCE_THRESHOLDS, CHART_COLORS

st.set_page_config(page_title="Stock Screening", page_icon="🔎", layout="wide")

def apply_filters(df, filters):
    """Apply screening filters to the dataframe"""
    filtered_df = df.copy()
    
    # Market cap filter
    if filters.get('min_market_cap'):
        filtered_df = filtered_df[filtered_df['Market Cap (Billion $)'] >= filters['min_market_cap']]
    
    if filters.get('max_market_cap'):
        filtered_df = filtered_df[filtered_df['Market Cap (Billion $)'] <= filters['max_market_cap']]
    
    # PE Ratio filter
    if filters.get('min_pe'):
        filtered_df = filtered_df[filtered_df['PE Ratio'] >= filters['min_pe']]
    
    if filters.get('max_pe'):
        filtered_df = filtered_df[(filtered_df['PE Ratio'] <= filters['max_pe']) | (filtered_df['PE Ratio'].isna())]
    
    # Dividend yield filter
    if filters.get('min_dividend_yield'):
        filtered_df = filtered_df[filtered_df['TTM Dividend Yield (%)'] >= filters['min_dividend_yield']]
    
    # Exchange filter
    if filters.get('exchanges'):
        filtered_df = filtered_df[filtered_df['Exchange'].isin(filters['exchanges'])]
    
    # Currency filter
    if filters.get('currencies'):
        filtered_df = filtered_df[filtered_df['Currency'].isin(filters['currencies'])]
    
    return filtered_df

def create_screening_chart(df, x_col, y_col, size_col=None, color_col=None):
    """Create a scatter plot for screening analysis"""
    # Remove rows with missing data
    plot_df = df.dropna(subset=[x_col, y_col])
    
    if plot_df.empty:
        return None
    
    # Determine available hover data columns
    hover_cols = []
    if 'Company' in plot_df.columns:
        hover_cols.append('Company')
    if 'Symbol' in plot_df.columns:
        hover_cols.append('Symbol')
    elif 'Ticker' in plot_df.columns:
        hover_cols.append('Ticker')
    
    fig = px.scatter(
        plot_df,
        x=x_col,
        y=y_col,
        size=size_col if size_col and size_col in plot_df.columns else None,
        color=color_col if color_col and color_col in plot_df.columns else None,
        hover_data=hover_cols if hover_cols else None,
        title=f"{y_col} vs {x_col}",
        template="plotly_white"
    )
    
    fig.update_layout(height=500)
    
    return fig

def create_top_performers_chart(df, metric, n_top=10):
    """Create a chart showing top performers for a metric"""
    # Sort by metric and take top n
    sorted_df = df.nlargest(n_top, metric)
    
    if sorted_df.empty:
        return None
    
    fig = go.Figure(data=[
        go.Bar(
            x=sorted_df[metric],
            y=sorted_df['Company'].str[:30],  # Truncate long company names
            orientation='h',
            marker_color=CHART_COLORS[0]
        )
    ])
    
    fig.update_layout(
        title=f"Top {n_top} Companies by {metric}",
        xaxis_title=metric,
        yaxis_title="Company",
        template="plotly_white",
        height=400
    )
    
    return fig

def highlight_performers(df):
    """Add performance indicators to the dataframe"""
    df_highlighted = df.copy()
    
    # Add performance indicators
    conditions = []
    
    # High PE flag
    if 'PE Ratio' in df.columns:
        df_highlighted['High PE'] = df_highlighted['PE Ratio'] > PERFORMANCE_THRESHOLDS['HIGH_PE']
        conditions.append('High PE')
    
    # High dividend yield flag
    if 'TTM Dividend Yield (%)' in df.columns:
        df_highlighted['High Yield'] = df_highlighted['TTM Dividend Yield (%)'] > 5.0
        conditions.append('High Yield')
    
    # Large cap flag
    if 'Market Cap (Billion $)' in df.columns:
        df_highlighted['Large Cap'] = df_highlighted['Market Cap (Billion $)'] > 50
        conditions.append('Large Cap')
    
    return df_highlighted, conditions

def main():
    st.title("🔎 Stock Screening & Analysis")
    st.markdown("---")
    
    # Sidebar inputs
    st.sidebar.header("Screening Parameters")
    
    # Select ticker list
    selected_list = st.sidebar.selectbox(
        "Choose Stock List:",
        options=list(TICKER_LISTS.keys()),
        help="Select from predefined ticker collections"
    )
    
    if selected_list:
        tickers_to_screen = TICKER_LISTS[selected_list]
        st.sidebar.write(f"**{selected_list}** ({len(tickers_to_screen)} stocks)")
        
        with st.sidebar.expander("View Tickers"):
            st.write(", ".join(tickers_to_screen))
    
    # Years selection
    selected_years = st.sidebar.multiselect(
        "Select Years to Analyze:",
        options=SCREENING_YEARS,
        default=SCREENING_YEARS[:3],  # Default to last 3 years
        help="Choose years for historical analysis"
    )
    
    screen_button = st.sidebar.button("🔍 Screen Stocks", type="primary")
    
    # Filtering options
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Filters")
    
    # Market cap filters
    min_market_cap = st.sidebar.number_input(
        "Min Market Cap (Billion $):",
        min_value=0.0,
        value=0.0,
        step=1.0,
        help="Minimum market capitalization"
    )
    
    max_market_cap = st.sidebar.number_input(
        "Max Market Cap (Billion $):",
        min_value=0.0,
        value=1000.0,
        step=10.0,
        help="Maximum market capitalization"
    )
    
    # PE Ratio filters
    col1, col2 = st.sidebar.columns(2)
    with col1:
        min_pe = st.sidebar.number_input("Min PE:", min_value=0.0, value=0.0, step=1.0)
    with col2:
        max_pe = st.sidebar.number_input("Max PE:", min_value=0.0, value=100.0, step=5.0)
    
    # Dividend yield filter
    min_dividend_yield = st.sidebar.number_input(
        "Min Dividend Yield (%):",
        min_value=0.0,
        max_value=50.0,
        value=0.0,
        step=0.5
    )
    
    # Information section
    with st.expander("ℹ️ How to Use This Tool", expanded=False):
        st.markdown("""
        **Stock Screening** enables batch analysis and filtering of stock lists:
        
        **Features:**
        - 🎯 Predefined stock collections (sectors, regions, strategies)
        - 📊 Multi-year financial metrics analysis
        - 🔍 Advanced filtering by valuation, size, and performance
        - 📈 Visual analysis with scatter plots and rankings
        - 📋 Sortable and exportable results
        
        **Screening Criteria:**
        - **Market Cap:** Filter by company size
        - **PE Ratios:** Find value or growth stocks
        - **Dividend Yields:** Income-focused screening
        - **Geographic/Exchange:** Regional focus
        - **Performance Metrics:** Historical analysis
        
        **Best For:**
        - Finding stocks matching specific criteria
        - Comparing stocks within sectors or regions
        - Identifying value or dividend opportunities
        - Portfolio construction and research
        """)
    
    if screen_button and selected_list and selected_years:
        with st.spinner(f"🔍 Screening {len(tickers_to_screen)} stocks..."):
            # Perform stock screening
            screening_results = screen_stocks(tickers_to_screen, selected_years)
            
            if screening_results.empty:
                st.error("❌ Could not analyze any of the provided stocks. Please check the ticker symbols and try again.")
                return
            
            # Store results in session state
            st.session_state['screening_results'] = screening_results
            st.session_state['screening_years'] = selected_years
            st.session_state['screened_list'] = selected_list
    
    # Display results if available
    if 'screening_results' in st.session_state:
        results_df = st.session_state['screening_results']
        screening_years = st.session_state['screening_years']
        screened_list = st.session_state['screened_list']
        
        # Apply filters
        filters = {
            'min_market_cap': min_market_cap if min_market_cap > 0 else None,
            'max_market_cap': max_market_cap if max_market_cap < 1000 else None,
            'min_pe': min_pe if min_pe > 0 else None,
            'max_pe': max_pe if max_pe < 100 else None,
            'min_dividend_yield': min_dividend_yield if min_dividend_yield > 0 else None
        }
        
        filtered_df = apply_filters(results_df, filters)
        
        # Analysis header
        st.success(f"✅ Successfully screened {len(results_df)} stocks from **{screened_list}**")
        
        if len(filtered_df) != len(results_df):
            st.info(f"🔍 Applied filters: {len(filtered_df)} stocks match your criteria")
        
        # Key metrics overview
        if not filtered_df.empty:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                avg_market_cap = filtered_df['Market Cap (Billion $)'].mean()
                st.metric("Avg Market Cap", f"${avg_market_cap:.1f}B")
            
            with col2:
                avg_pe = filtered_df['PE Ratio'].mean()
                st.metric("Avg PE Ratio", f"{avg_pe:.1f}")
            
            with col3:
                avg_dividend = filtered_df['TTM Dividend Yield (%)'].mean()
                st.metric("Avg Div Yield", f"{avg_dividend:.1f}%")
            
            with col4:
                exchanges = filtered_df['Exchange'].nunique()
                st.metric("Exchanges", exchanges)
        
        # Tabs for different analysis sections
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Screening Results", "📈 Visual Analysis", "🏆 Top Performers", "💰 Financial Metrics", "📥 Export"
        ])
        
        with tab1:
            st.subheader("📊 Screening Results")
            
            # Highlight performers
            highlighted_df, conditions = highlight_performers(filtered_df)
            
            # Display options
            col1, col2, col3 = st.columns(3)
            
            with col1:
                sort_by = st.selectbox(
                    "Sort By:",
                    options=['Market Cap (Billion $)', 'PE Ratio', 'TTM Dividend Yield (%)', 'Latest Price'],
                    index=0
                )
            
            with col2:
                sort_ascending = st.selectbox("Sort Order:", options=['Descending', 'Ascending'], index=0)
                ascending = sort_ascending == 'Ascending'
            
            with col3:
                show_conditions = st.multiselect(
                    "Show Performance Flags:",
                    options=conditions,
                    help="Add performance indicator columns"
                )
            
            # Sort the dataframe
            display_df = highlighted_df.sort_values(sort_by, ascending=ascending)
            
            # Select columns to display
            base_columns = [
                'Company', 'Symbol', 'Currency', 'Exchange', 'Latest Price',
                'Market Cap (Billion $)', 'PE Ratio', 'EPS', 'TTM Dividend Yield (%)',
                'Dividend Rate', 'Debt to Equity', 'Volume'
            ]
            
            display_columns = base_columns + show_conditions
            available_columns = [col for col in display_columns if col in display_df.columns]
            
            # Format the dataframe for display
            formatted_df = display_df[available_columns].copy()
            
            # Apply formatting
            if 'Latest Price' in formatted_df.columns:
                formatted_df['Latest Price'] = formatted_df['Latest Price'].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "N/A")
            
            if 'Market Cap (Billion $)' in formatted_df.columns:
                formatted_df['Market Cap (Billion $)'] = formatted_df['Market Cap (Billion $)'].apply(lambda x: f"${x:.2f}B" if pd.notna(x) else "N/A")
            
            st.dataframe(formatted_df, use_container_width=True, hide_index=True)
        
        with tab2:
            st.subheader("📈 Visual Analysis")
            
            if not filtered_df.empty:
                # Scatter plot options
                col1, col2 = st.columns(2)
                
                with col1:
                    x_axis = st.selectbox(
                        "X-Axis:",
                        options=['Market Cap (Billion $)', 'PE Ratio', 'TTM Dividend Yield (%)', 'EPS'],
                        index=0
                    )
                
                with col2:
                    y_axis = st.selectbox(
                        "Y-Axis:",
                        options=['Latest Price', 'TTM Dividend Yield (%)', 'PE Ratio', 'Debt to Equity'],
                        index=0
                    )
                
                # Create scatter plot
                scatter_chart = create_screening_chart(
                    filtered_df, 
                    x_axis, 
                    y_axis, 
                    size_col='Market Cap (Billion $)',
                    color_col='Exchange'
                )
                
                if scatter_chart:
                    st.plotly_chart(scatter_chart, use_container_width=True)
                
                # Distribution charts
                col1, col2 = st.columns(2)
                
                with col1:
                    # PE Ratio distribution
                    if 'PE Ratio' in filtered_df.columns:
                        pe_data = filtered_df['PE Ratio'].dropna()
                        if not pe_data.empty:
                            fig_pe_dist = px.histogram(
                                pe_data,
                                title="PE Ratio Distribution",
                                nbins=20,
                                template="plotly_white"
                            )
                            st.plotly_chart(fig_pe_dist, use_container_width=True)
                
                with col2:
                    # Market Cap distribution
                    if 'Market Cap (Billion $)' in filtered_df.columns:
                        mcap_data = filtered_df['Market Cap (Billion $)'].dropna()
                        if not mcap_data.empty:
                            fig_mcap_dist = px.histogram(
                                mcap_data,
                                title="Market Cap Distribution",
                                nbins=20,
                                template="plotly_white"
                            )
                            st.plotly_chart(fig_mcap_dist, use_container_width=True)
        
        with tab3:
            st.subheader("🏆 Top Performers")
            
            # Top performers by different metrics
            col1, col2 = st.columns(2)
            
            with col1:
                # Top by Market Cap
                top_mcap_chart = create_top_performers_chart(filtered_df, 'Market Cap (Billion $)', 10)
                if top_mcap_chart:
                    st.plotly_chart(top_mcap_chart, use_container_width=True)
            
            with col2:
                # Top by Dividend Yield
                top_div_chart = create_top_performers_chart(filtered_df, 'TTM Dividend Yield (%)', 10)
                if top_div_chart:
                    st.plotly_chart(top_div_chart, use_container_width=True)
            
            # Top performers table
            st.markdown("**Top 10 by Market Cap**")
            top_mcap_df = filtered_df.nlargest(10, 'Market Cap (Billion $)')[
                ['Company', 'Symbol', 'Market Cap (Billion $)', 'PE Ratio', 'TTM Dividend Yield (%)']
            ].copy()
            
            # Format for display
            top_mcap_df['Market Cap (Billion $)'] = top_mcap_df['Market Cap (Billion $)'].apply(lambda x: f"${x:.2f}B")
            top_mcap_df['PE Ratio'] = top_mcap_df['PE Ratio'].apply(lambda x: f"{x:.1f}" if pd.notna(x) else "N/A")
            top_mcap_df['TTM Dividend Yield (%)'] = top_mcap_df['TTM Dividend Yield (%)'].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "N/A")
            
            st.dataframe(top_mcap_df, use_container_width=True, hide_index=True)
        
        with tab4:
            st.subheader("💰 Multi-Year Financial Metrics")
            
            if screening_years:
                # Revenue analysis
                st.markdown("**Revenue Analysis (Billion $)**")
                revenue_columns = [col for col in filtered_df.columns if 'Revenue' in col and 'Billion' in col]
                if revenue_columns:
                    revenue_df = filtered_df[['Company', 'Symbol'] + revenue_columns].copy()
                    
                    # Format revenue columns
                    for col in revenue_columns:
                        revenue_df[col] = revenue_df[col].apply(lambda x: f"${x:.2f}B" if pd.notna(x) and x != 0 else "N/A")
                    
                    st.dataframe(revenue_df, use_container_width=True, hide_index=True)
                
                st.markdown("---")
                
                # Net Income analysis
                st.markdown("**Net Income Analysis (Billion $)**")
                income_columns = [col for col in filtered_df.columns if 'Net Income' in col and 'Billion' in col]
                if income_columns:
                    income_df = filtered_df[['Company', 'Symbol'] + income_columns].copy()
                    
                    # Format income columns
                    for col in income_columns:
                        income_df[col] = income_df[col].apply(lambda x: f"${x:.2f}B" if pd.notna(x) and x != 0 else "N/A")
                    
                    st.dataframe(income_df, use_container_width=True, hide_index=True)
                
                st.markdown("---")
                
                # Dividend analysis
                st.markdown("**Dividend Analysis**")
                dividend_columns = [col for col in filtered_df.columns if 'Dividends' in col]
                if dividend_columns:
                    dividend_df = filtered_df[['Company', 'Symbol', 'Dividend Rate', 'Payout Ratio'] + dividend_columns].copy()
                    
                    # Format dividend rate and payout ratio
                    dividend_df['Dividend Rate'] = dividend_df['Dividend Rate'].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "N/A")
                    dividend_df['Payout Ratio'] = dividend_df['Payout Ratio'].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "N/A")
                    
                    st.dataframe(dividend_df, use_container_width=True, hide_index=True)
        
        with tab5:
            st.subheader("📥 Export Screening Results")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Excel Export**")
                st.write("Download complete screening results as Excel file.")
                
                if st.button("📊 Generate Excel Report", type="primary"):
                    # Create Excel file
                    excel_buffer = io.BytesIO()
                    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                        # Main results
                        filtered_df.to_excel(writer, sheet_name='Screening Results', index=False)
                        
                        # Summary statistics
                        summary_stats = filtered_df.describe()
                        summary_stats.to_excel(writer, sheet_name='Summary Statistics')
                        
                        # Auto-adjust column widths for main sheet
                        worksheet = writer.sheets['Screening Results']
                        for column in worksheet.columns:
                            max_length = 0
                            column = [cell for cell in column]
                            for cell in column:
                                try:
                                    if len(str(cell.value)) > max_length:
                                        max_length = len(str(cell.value))
                                except:
                                    pass
                            adjusted_width = min(max_length + 2, 50)
                            worksheet.column_dimensions[column[0].column_letter].width = adjusted_width
                    
                    timestamp = dt.now().strftime("%Y%m%d_%H%M")
                    filename = f"{screened_list}_screening_{timestamp}.xlsx"
                    
                    st.download_button(
                        label="💾 Download Excel File",
                        data=excel_buffer.getvalue(),
                        file_name=filename,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            
            with col2:
                st.markdown("**CSV Export**")
                st.write("Download filtered results as CSV for further analysis.")
                
                csv_data = filtered_df.to_csv(index=False)
                csv_filename = f"{screened_list}_screening_{dt.now().strftime('%Y%m%d_%H%M')}.csv"
                
                st.download_button(
                    label="📄 Download CSV File",
                    data=csv_data,
                    file_name=csv_filename,
                    mime="text/csv"
                )
                
                # Show screening summary
                st.markdown("**Screening Summary**")
                st.write(f"**List:** {screened_list}")
                st.write(f"**Total Stocks:** {len(results_df)}")
                st.write(f"**After Filters:** {len(filtered_df)}")
                st.write(f"**Years Analyzed:** {', '.join(map(str, screening_years))}")

    else:
        st.info("👆 Select a stock list in the sidebar and click 'Screen Stocks' to begin your analysis.")
        
        # Show available lists
        st.markdown("### 📋 Available Stock Lists:")
        
        col1, col2 = st.columns(2)
        
        with col1:
            for i, (list_name, tickers) in enumerate(list(TICKER_LISTS.items())[:len(TICKER_LISTS)//2]):
                with st.expander(f"{list_name} ({len(tickers)} stocks)"):
                    st.write(", ".join(tickers[:15]) + ("..." if len(tickers) > 15 else ""))
        
        with col2:
            for i, (list_name, tickers) in enumerate(list(TICKER_LISTS.items())[len(TICKER_LISTS)//2:]):
                with st.expander(f"{list_name} ({len(tickers)} stocks)"):
                    st.write(", ".join(tickers[:15]) + ("..." if len(tickers) > 15 else ""))

if __name__ == "__main__":
    main()