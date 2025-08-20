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

from utils.financial_analysis import analyze_etfs
from config import TICKER_LISTS, ETF_METRICS, CHART_COLORS

st.set_page_config(page_title="ETF Analysis", page_icon="🎯", layout="wide")

def create_holdings_pie_chart(etf_data):
    """Create a pie chart showing top 10 holdings breakdown"""
    holdings = []
    weights = []
    
    # Use holdings data if available, otherwise fall back to individual fields
    if etf_data.get('Holdings Data'):
        holdings_data = etf_data['Holdings Data']
        for holding in holdings_data:
            if holding['name'] and holding['name'] != 'N/A' and holding['weight'] > 0:
                holdings.append(holding['name'][:25] + '...' if len(holding['name']) > 25 else holding['name'])
                weights.append(holding['weight'])
    else:
        # Fallback to original logic for top 3
        for i in range(1, 4):
            holding_name = etf_data.get(f'Top {i} Holding')
            holding_weight = etf_data.get(f'Weight {i}', 0)
            if holding_name and holding_name != 'N/A':
                holdings.append(holding_name)
                weights.append(holding_weight)
    
    # Add "Other" category
    total_shown = sum(weights)
    if total_shown < 100:
        holdings.append('Other Holdings')
        weights.append(100 - total_shown)
    
    if not holdings:
        return None
    
    fig = go.Figure(data=[
        go.Pie(
            labels=holdings,
            values=weights,
            hole=0.4,
            textinfo='label+percent',
            textposition='outside'
        )
    ])
    
    fig.update_layout(
        title=f"Top Holdings Breakdown - {etf_data.get('Name', 'ETF')}",
        template="plotly_white",
        height=500,
        showlegend=len(holdings) > 8  # Show legend if many holdings
    )
    
    return fig

def create_comparison_chart(etfs_data, metric, chart_type='bar'):
    """Create comparison chart for multiple ETFs"""
    etf_names = []
    values = []
    
    for etf in etfs_data:
        if etf.get(metric) is not None:
            name = etf.get('Name', etf.get('Ticker', 'Unknown'))[:30]  # Truncate long names
            etf_names.append(name)
            values.append(etf[metric])
    
    if not values:
        return None
    
    if chart_type == 'bar':
        fig = go.Figure(data=[
            go.Bar(
                x=etf_names,
                y=values,
                marker_color=CHART_COLORS[0]
            )
        ])
        
        fig.update_layout(
            title=f"{metric} Comparison",
            xaxis_title="ETF",
            yaxis_title=metric,
            template="plotly_white",
            height=400,
            xaxis={'tickangle': 45}
        )
    else:  # horizontal bar
        fig = go.Figure(data=[
            go.Bar(
                x=values,
                y=etf_names,
                orientation='h',
                marker_color=CHART_COLORS[0]
            )
        ])
        
        fig.update_layout(
            title=f"{metric} Comparison",
            xaxis_title=metric,
            yaxis_title="ETF",
            template="plotly_white",
            height=max(400, len(etf_names) * 40)
        )
    
    return fig

def format_number(value, metric_type='currency'):
    """Format numbers based on metric type"""
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return "N/A"
    
    if metric_type == 'currency':
        if abs(value) >= 1e9:
            return f"${value/1e9:.2f}B"
        elif abs(value) >= 1e6:
            return f"${value/1e6:.2f}M"
        elif abs(value) >= 1e3:
            return f"${value/1e3:.2f}K"
        else:
            return f"${value:.2f}"
    elif metric_type == 'percentage':
        return f"{value:.2f}%"
    elif metric_type == 'ratio':
        return f"{value:.2f}"
    else:
        return f"{value:.2f}"

def main():
    st.title("🎯 ETF Analysis & Comparison")
    st.markdown("---")
    
    # Sidebar inputs
    st.sidebar.header("ETF Analysis Parameters")
    
    # Input method selection
    input_method = st.sidebar.radio(
        "Select Input Method:",
        ["Manual Input", "High Yield ETFs"],
        help="Choose how to select ETFs for analysis"
    )
    
    etfs_to_analyze = []
    
    if input_method == "Manual Input":
        etfs_input = st.sidebar.text_area(
            "Enter ETF Tickers (one per line):",
            value="SPY\nQQQ\nVTI\nIWM",
            help="Enter ETF tickers, one per line"
        )
        etfs_to_analyze = [ticker.strip().upper() for ticker in etfs_input.split('\n') if ticker.strip()]
    
    else:  # High Yield ETFs
        if "High Yield ETFs" in TICKER_LISTS:
            etfs_to_analyze = TICKER_LISTS["High Yield ETFs"]
            st.sidebar.write(f"**High Yield ETFs** ({len(etfs_to_analyze)} ETFs)")
            with st.sidebar.expander("View ETFs"):
                st.write(", ".join(etfs_to_analyze))
    
    analyze_button = st.sidebar.button("🎯 Analyze ETFs", type="primary")
    
    # Information section
    with st.expander("ℹ️ How to Use This Tool", expanded=False):
        st.markdown("""
        **ETF Analysis** provides comprehensive analysis of Exchange-Traded Funds:
        
        **Features:**
        - 🎯 ETF characteristics (expense ratios, yields, categories)
        - 🏢 Top holdings breakdown with weights
        - 💰 Performance metrics and price tracking
        - 📊 Comparative analysis across multiple ETFs
        - 📈 Dividend yields and payout analysis
        
        **Metrics Analyzed:**
        - **Expense Ratios:** Cost of ownership
        - **Dividend Yields:** Income generation potential
        - **Top Holdings:** Underlying investments and concentrations
        - **Performance:** Price changes and NAV tracking
        - **Strategy:** Investment thesis and approach
        
        **Best For:**
        - Income-focused ETF comparison
        - Understanding ETF composition
        - Cost analysis across similar funds
        - Dividend yield comparison
        """)
    
    if analyze_button and etfs_to_analyze:
        with st.spinner(f"🎯 Analyzing {len(etfs_to_analyze)} ETFs..."):
            # Perform ETF analysis
            analysis_results = analyze_etfs(etfs_to_analyze)
            
            if not analysis_results:
                st.error("❌ Could not analyze any of the provided ETF tickers. Please check the symbols and try again.")
                return
            
            # Store results in session state
            st.session_state['etf_results'] = analysis_results
            st.session_state['analyzed_etfs'] = etfs_to_analyze
    
    # Display results if available
    if 'etf_results' in st.session_state:
        results = st.session_state['etf_results']
        analyzed_etfs = st.session_state['analyzed_etfs']
        
        # Analysis header
        st.success(f"✅ Successfully analyzed {len(results)} ETFs")
        
        # ETF overview table
        st.subheader("📋 ETF Overview")
        
        overview_data = []
        for etf in results:
            overview_data.append({
                'Ticker': etf.get('Ticker', 'N/A'),
                'Name': etf.get('Name', 'N/A'),
                'Current Price': format_number(etf.get('Current Price'), 'currency'),
                'Expense Ratio': f"{etf.get('Expense Ratio', 0):.2f}%" if etf.get('Expense Ratio') else "N/A",
                'ETF Dividend Yield': f"{etf.get('Dividend Yield (%)', 0):.2f}%" if etf.get('Dividend Yield (%)') else "N/A",
                'Aggregate PE': f"{etf.get('Aggregate PE', 0):.1f}" if etf.get('Aggregate PE') else "N/A",
                'Agg Div Yield': f"{etf.get('Aggregate Dividend Yield (%)', 0):.2f}%" if etf.get('Aggregate Dividend Yield (%)') else "N/A",
                '3Y CAGR': f"{etf.get('3Y Price CAGR (%)', 0):+.1f}%" if etf.get('3Y Price CAGR (%)') else "N/A",
                'Top Holdings': etf.get('Top Holdings Count', 0),
                'Category': etf.get('Category', 'N/A')
            })
        
        df_overview = pd.DataFrame(overview_data)
        st.dataframe(df_overview, use_container_width=True, hide_index=True)
        
        # Tabs for different analysis sections
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Key Metrics", "🏢 Holdings Analysis", "💹 Performance", "🔢 Detailed Data", "📥 Export"
        ])
        
        with tab1:
            st.subheader("📊 Key ETF Metrics Comparison")
            
            # Expense Ratio comparison
            col1, col2 = st.columns(2)
            
            with col1:
                expense_chart = create_comparison_chart(results, 'Expense Ratio')
                if expense_chart:
                    st.plotly_chart(expense_chart, use_container_width=True)
            
            with col2:
                yield_chart = create_comparison_chart(results, 'Dividend Yield (%)')
                if yield_chart:
                    st.plotly_chart(yield_chart, use_container_width=True)
            
            # PE Ratio and Market Cap (if available)
            col1, col2 = st.columns(2)
            
            with col1:
                pe_chart = create_comparison_chart(results, 'PE')
                if pe_chart:
                    st.plotly_chart(pe_chart, use_container_width=True)
            
            with col2:
                # Market cap chart (horizontal for better readability)
                market_cap_chart = create_comparison_chart(results, 'Market Cap', 'horizontal')
                if market_cap_chart:
                    st.plotly_chart(market_cap_chart, use_container_width=True)
            
            # Enhanced metrics summary table with aggregate data
            st.markdown("**Enhanced Metrics Summary**")
            metrics_data = []
            for etf in results:
                metrics_data.append({
                    'Ticker': etf.get('Ticker', 'N/A'),
                    'ETF PE': f"{etf.get('PE', 0):.1f}" if etf.get('PE') else "N/A",
                    'Agg PE': f"{etf.get('Aggregate PE', 0):.1f}" if etf.get('Aggregate PE') else "N/A",
                    'Expense Ratio': f"{etf.get('Expense Ratio', 0):.2f}%" if etf.get('Expense Ratio') else "N/A",
                    'ETF Div Yield': f"{etf.get('Dividend Yield (%)', 0):.2f}%" if etf.get('Dividend Yield (%)') else "N/A",
                    'Agg Div Yield': f"{etf.get('Aggregate Dividend Yield (%)', 0):.2f}%" if etf.get('Aggregate Dividend Yield (%)') else "N/A",
                    '3Y CAGR': f"{etf.get('3Y Price CAGR (%)', 0):+.1f}%" if etf.get('3Y Price CAGR (%)') else "N/A",
                    'Market Cap': format_number(etf.get('Market Cap')),
                    'Holdings': etf.get('Top Holdings Count', 0)
                })
            
            df_metrics = pd.DataFrame(metrics_data)
            st.dataframe(df_metrics, use_container_width=True, hide_index=True)
            
            # Add comparison charts for aggregate metrics
            st.markdown("---")
            col1, col2 = st.columns(2)
            
            with col1:
                agg_pe_chart = create_comparison_chart(results, 'Aggregate PE')
                if agg_pe_chart:
                    st.plotly_chart(agg_pe_chart, use_container_width=True)
            
            with col2:
                agg_div_chart = create_comparison_chart(results, 'Aggregate Dividend Yield (%)')
                if agg_div_chart:
                    st.plotly_chart(agg_div_chart, use_container_width=True)
        
        with tab2:
            st.subheader("🏢 Holdings Analysis")
            
            # Individual ETF holdings breakdown
            selected_etf = st.selectbox(
                "Select ETF for Holdings Breakdown:",
                options=[etf.get('Ticker', 'N/A') for etf in results],
                help="Choose an ETF to view its top holdings"
            )
            
            if selected_etf:
                etf_data = next((etf for etf in results if etf.get('Ticker') == selected_etf), None)
                
                if etf_data:
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        holdings_chart = create_holdings_pie_chart(etf_data)
                        if holdings_chart:
                            st.plotly_chart(holdings_chart, use_container_width=True)
                    
                    with col2:
                        st.markdown("**Top Holdings Details**")
                        
                        # Display comprehensive holdings table
                        if etf_data.get('Holdings Data'):
                            holdings_data = etf_data['Holdings Data']
                            holdings_detail = []
                            
                            for holding in holdings_data:
                                holdings_detail.append({
                                    'Rank': holding['rank'],
                                    'Symbol': holding['symbol'] if holding['symbol'] else "N/A",
                                    'Name': holding['name'][:30] + '...' if len(str(holding['name'])) > 30 else holding['name'],
                                    'Weight (%)': f"{holding['weight']:.2f}%" if holding['weight'] else "N/A",
                                    'P/E': f"{holding['pe']:.1f}" if holding['pe'] else "N/A",
                                    'Div Yield (%)': f"{holding['dividend_yield']:.2f}%" if holding['dividend_yield'] else "N/A"
                                })
                            
                            if holdings_detail:
                                df_holdings = pd.DataFrame(holdings_detail)
                                st.dataframe(df_holdings, use_container_width=True, hide_index=True)
                        else:
                            # Fallback to original format
                            holdings_detail = []
                            for i in range(1, 4):
                                holding = etf_data.get(f'Top {i} Holding')
                                weight = etf_data.get(f'Weight {i}')
                                
                                if holding and holding != 'N/A':
                                    pe_key = f'Top {i} P/E' if i == 1 else None
                                    pe_val = etf_data.get(pe_key) if pe_key else None
                                    
                                    holdings_detail.append({
                                        'Rank': i,
                                        'Holding': holding,
                                        'Weight (%)': f"{weight:.2f}%" if weight else "N/A",
                                        'P/E': f"{pe_val:.1f}" if pe_val else "N/A"
                                    })
                            
                            if holdings_detail:
                                df_holdings = pd.DataFrame(holdings_detail)
                                st.dataframe(df_holdings, use_container_width=True, hide_index=True)
                        
                        # Investment strategy
                        if etf_data.get('Strategy'):
                            st.markdown("**Investment Strategy**")
                            strategy_text = etf_data['Strategy']
                            if len(strategy_text) > 300:
                                strategy_text = strategy_text[:300] + "..."
                            st.write(strategy_text)
            
            # Enhanced Holdings comparison across ETFs
            st.markdown("---")
            st.markdown("**Holdings Concentration & Aggregate Metrics Comparison**")
            
            concentration_data = []
            for etf in results:
                # Calculate concentration metrics
                total_top3 = 0
                total_top5 = 0
                total_top10 = 0
                
                if etf.get('Holdings Data'):
                    holdings = etf['Holdings Data']
                    for i, holding in enumerate(holdings):
                        weight = holding['weight'] if holding['weight'] else 0
                        if i < 3:
                            total_top3 += weight
                        if i < 5:
                            total_top5 += weight
                        if i < 10:
                            total_top10 += weight
                else:
                    # Fallback calculation
                    for i in range(1, 4):
                        weight = etf.get(f'Weight {i}', 0)
                        if weight:
                            total_top3 += weight
                
                concentration_data.append({
                    'Ticker': etf.get('Ticker', 'N/A'),
                    'ETF Name': etf.get('Name', 'N/A')[:30] + '...' if len(etf.get('Name', '')) > 30 else etf.get('Name', 'N/A'),
                    'Top 3 (%)': f"{total_top3:.1f}%",
                    'Top 5 (%)': f"{total_top5:.1f}%" if total_top5 > 0 else "N/A",
                    'Top 10 (%)': f"{total_top10:.1f}%" if total_top10 > 0 else "N/A",
                    'Agg PE': f"{etf.get('Aggregate PE', 0):.1f}" if etf.get('Aggregate PE') else "N/A",
                    'Agg Div (%)': f"{etf.get('Aggregate Dividend Yield (%)', 0):.1f}%" if etf.get('Aggregate Dividend Yield (%)') else "N/A",
                    '3Y CAGR (%)': f"{etf.get('3Y Price CAGR (%)', 0):+.1f}%" if etf.get('3Y Price CAGR (%)') else "N/A",
                    'Holdings': etf.get('Top Holdings Count', 0)
                })
            
            df_concentration = pd.DataFrame(concentration_data)
            st.dataframe(df_concentration, use_container_width=True, hide_index=True)
        
        with tab3:
            st.subheader("💹 Performance Analysis")
            
            # Performance metrics
            performance_data = []
            for etf in results:
                current_price = etf.get('Current Price')
                price_12m_ago = etf.get('Price 12 Months Ago')
                nav_price = etf.get('Nav Price')
                
                # Calculate performance if data is available
                performance = None
                if current_price and price_12m_ago:
                    performance = ((current_price - price_12m_ago) / price_12m_ago) * 100
                
                # NAV vs Market Price discount/premium
                nav_discount = None
                if nav_price and current_price:
                    nav_discount = ((current_price - nav_price) / nav_price) * 100
                
                performance_data.append({
                    'Ticker': etf.get('Ticker', 'N/A'),
                    'Current Price': format_number(current_price, 'currency'),
                    'NAV Price': format_number(nav_price, 'currency'),
                    'NAV Discount/Premium': f"{nav_discount:+.2f}%" if nav_discount is not None else "N/A",
                    '12M Performance': f"{performance:+.2f}%" if performance is not None else "N/A",
                    'Price 12M Ago': format_number(price_12m_ago, 'currency')
                })
            
            df_performance = pd.DataFrame(performance_data)
            st.dataframe(df_performance, use_container_width=True, hide_index=True)
            
            # Performance charts
            col1, col2 = st.columns(2)
            
            with col1:
                # 12-month performance chart
                perf_values = []
                etf_names = []
                
                for etf in results:
                    current_price = etf.get('Current Price')
                    price_12m_ago = etf.get('Price 12 Months Ago')
                    
                    if current_price and price_12m_ago:
                        performance = ((current_price - price_12m_ago) / price_12m_ago) * 100
                        perf_values.append(performance)
                        etf_names.append(etf.get('Ticker', 'N/A'))
                
                if perf_values:
                    fig_perf = go.Figure(data=[
                        go.Bar(
                            x=etf_names,
                            y=perf_values,
                            marker_color=['green' if x > 0 else 'red' for x in perf_values]
                        )
                    ])
                    
                    fig_perf.update_layout(
                        title="12-Month Performance (%)",
                        xaxis_title="ETF",
                        yaxis_title="Performance (%)",
                        template="plotly_white",
                        height=400
                    )
                    
                    st.plotly_chart(fig_perf, use_container_width=True)
            
            with col2:
                # 3-year CAGR chart
                cagr_values = []
                etf_names_cagr = []
                
                for etf in results:
                    cagr = etf.get('3Y Price CAGR (%)')
                    if cagr is not None:
                        cagr_values.append(cagr)
                        etf_names_cagr.append(etf.get('Ticker', 'N/A'))
                
                if cagr_values:
                    fig_cagr = go.Figure(data=[
                        go.Bar(
                            x=etf_names_cagr,
                            y=cagr_values,
                            marker_color=['green' if x > 0 else 'red' for x in cagr_values]
                        )
                    ])
                    
                    fig_cagr.update_layout(
                        title="3-Year Price CAGR (%)",
                        xaxis_title="ETF",
                        yaxis_title="CAGR (%)",
                        template="plotly_white",
                        height=400
                    )
                    
                    st.plotly_chart(fig_cagr, use_container_width=True)
            
            # Current Price vs NAV comparison
            st.markdown("---")
            col1, col2 = st.columns(2)
            
            with col1:
                # Current Price vs NAV
                nav_values = []
                current_values = []
                etf_names_nav = []
                
                for etf in results:
                    nav_price = etf.get('Nav Price')
                    current_price = etf.get('Current Price')
                    
                    if nav_price and current_price:
                        nav_values.append(nav_price)
                        current_values.append(current_price)
                        etf_names_nav.append(etf.get('Ticker', 'N/A'))
                
                if nav_values:
                    fig_nav = go.Figure()
                    
                    fig_nav.add_trace(go.Bar(
                        name='NAV Price',
                        x=etf_names_nav,
                        y=nav_values,
                        marker_color=CHART_COLORS[0]
                    ))
                    
                    fig_nav.add_trace(go.Bar(
                        name='Market Price',
                        x=etf_names_nav,
                        y=current_values,
                        marker_color=CHART_COLORS[1]
                    ))
                    
                    fig_nav.update_layout(
                        title="NAV vs Market Price",
                        xaxis_title="ETF",
                        yaxis_title="Price ($)",
                        template="plotly_white",
                        height=400,
                        barmode='group'
                    )
                    
                    st.plotly_chart(fig_nav, use_container_width=True)
        
        with tab4:
            st.subheader("🔢 Complete ETF Data")
            
            # Full data table with all metrics
            st.dataframe(
                pd.DataFrame(results),
                use_container_width=True,
                hide_index=True
            )
        
        with tab5:
            st.subheader("📥 Export ETF Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Excel Export**")
                st.write("Download complete ETF analysis as Excel file.")
                
                if st.button("📊 Generate Excel Report", type="primary"):
                    # Create Excel file
                    df_export = pd.DataFrame(results)
                    
                    excel_buffer = io.BytesIO()
                    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                        df_export.to_excel(writer, sheet_name='ETF Analysis', index=False)
                        
                        # Auto-adjust column widths
                        worksheet = writer.sheets['ETF Analysis']
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
                    filename = f"etf_analysis_{timestamp}.xlsx"
                    
                    st.download_button(
                        label="💾 Download Excel File",
                        data=excel_buffer.getvalue(),
                        file_name=filename,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            
            with col2:
                st.markdown("**CSV Export**")
                st.write("Download ETF data as CSV for further analysis.")
                
                csv_data = pd.DataFrame(results).to_csv(index=False)
                csv_filename = f"etf_data_{dt.now().strftime('%Y%m%d_%H%M')}.csv"
                
                st.download_button(
                    label="📄 Download CSV File",
                    data=csv_data,
                    file_name=csv_filename,
                    mime="text/csv"
                )

    else:
        st.info("👆 Select ETFs in the sidebar and click 'Analyze ETFs' to begin your analysis.")
        
        # Show example ETFs
        st.markdown("""
        ### 💡 Popular ETF Categories to Analyze:
        
        **Broad Market:** SPY, QQQ, VTI, IWM, VEA, VWO  
        **High Yield:** JEPI, JEPQ, SPYI, QDVO, BALI  
        **Sector Specific:** XLF, XLK, XLE, XLV, XLI  
        **International:** EFA, EEM, VGK, VPL, IEFA  
        **Bond/Income:** AGG, BND, LQD, HYG, TLT  
        """)

if __name__ == "__main__":
    main()