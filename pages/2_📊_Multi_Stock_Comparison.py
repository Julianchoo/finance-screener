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

from utils.financial_analysis import compare_tickers_financials, export_financials_to_excel
from config import TICKER_LISTS, ANALYSIS_CATEGORIES, CHART_COLORS

st.set_page_config(page_title="Multi-Stock Comparison", page_icon="📊", layout="wide")

def create_comparison_chart(data, metric, years, title):
    """Create a comparison chart for multiple tickers"""
    fig = go.Figure()
    
    color_idx = 0
    for ticker, ticker_data in data.items():
        if 'Error' in ticker_data:
            continue
            
        values = []
        year_labels = []
        
        for year in sorted(years):
            if year in ticker_data and metric in ticker_data[year]:
                val = ticker_data[year][metric]
                if val is not None and not (isinstance(val, float) and np.isnan(val)):
                    values.append(val)
                    year_labels.append(year)
        
        if values:
            fig.add_trace(go.Scatter(
                x=year_labels,
                y=values,
                mode='lines+markers',
                name=ticker,
                line=dict(color=CHART_COLORS[color_idx % len(CHART_COLORS)], width=2),
                marker=dict(size=6)
            ))
            color_idx += 1
    
    fig.update_layout(
        title=title,
        xaxis_title="Year",
        yaxis_title=metric,
        template="plotly_white",
        height=400,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

def create_current_metrics_chart(data, metric, chart_type='bar'):
    """Create a chart for current valuation metrics"""
    tickers = []
    values = []
    
    for ticker, ticker_data in data.items():
        if 'Error' in ticker_data or 'Current Valuation' not in ticker_data:
            continue
        
        current_val = ticker_data['Current Valuation']
        if metric in current_val and current_val[metric] is not None:
            tickers.append(ticker)
            values.append(current_val[metric])
    
    if not values:
        return None
    
    if chart_type == 'bar':
        fig = go.Figure(data=[
            go.Bar(x=tickers, y=values, marker_color=CHART_COLORS[0])
        ])
    else:  # pie chart
        fig = go.Figure(data=[
            go.Pie(labels=tickers, values=values, hole=0.3)
        ])
    
    fig.update_layout(
        title=f"{metric} Comparison",
        template="plotly_white",
        height=400
    )
    
    return fig

def format_large_number(num):
    """Format large numbers for display"""
    if num is None or (isinstance(num, float) and np.isnan(num)):
        return "N/A"
    
    if isinstance(num, (int, float)):
        if abs(num) >= 1e9:
            return f"${num/1e9:.2f}B"
        elif abs(num) >= 1e6:
            return f"${num/1e6:.2f}M"
        elif abs(num) >= 1e3:
            return f"${num/1e3:.2f}K"
        else:
            return f"${num:.2f}"
    else:
        return str(num)

def main():
    st.title("📊 Multi-Stock Comparison")
    st.markdown("---")
    
    # Sidebar inputs
    st.sidebar.header("Comparison Parameters")
    
    # Input method selection
    input_method = st.sidebar.radio(
        "Select Input Method:",
        ["Manual Input", "Predefined Lists"],
        help="Choose how to select stocks for comparison"
    )
    
    tickers_to_analyze = []
    
    if input_method == "Manual Input":
        tickers_input = st.sidebar.text_area(
            "Enter Stock Tickers (one per line):",
            value="MSFT\nAAPL\nGOOGL\nNVDA",
            help="Enter stock tickers, one per line. For international stocks, include exchange suffix (e.g., .L, .T, .SI)"
        )
        tickers_to_analyze = [ticker.strip().upper() for ticker in tickers_input.split('\n') if ticker.strip()]
    
    else:  # Predefined Lists
        selected_list = st.sidebar.selectbox(
            "Choose Ticker List:",
            options=list(TICKER_LISTS.keys()),
            help="Select from predefined ticker collections"
        )
        
        if selected_list:
            tickers_to_analyze = TICKER_LISTS[selected_list]
            st.sidebar.write(f"**{selected_list}** ({len(tickers_to_analyze)} tickers)")
            with st.sidebar.expander("View Tickers"):
                st.write(", ".join(tickers_to_analyze))
    
    analyze_button = st.sidebar.button("🔍 Compare Stocks", type="primary")
    
    # Information section
    with st.expander("ℹ️ How to Use This Tool", expanded=False):
        st.markdown("""
        **Multi-Stock Comparison** allows you to analyze and compare multiple stocks simultaneously:
        
        **Features:**
        - 📈 Side-by-side financial metrics comparison
        - 📊 5-year historical data analysis
        - 💹 Revenue, margins, debt, and valuation metrics
        - 🎯 Current valuation comparisons
        - 📥 Excel export with comprehensive data
        
        **Input Methods:**
        - **Manual Input:** Enter any tickers you want to compare
        - **Predefined Lists:** Choose from curated lists (Tech, Pharma, REITs, etc.)
        
        **International Support:**
        - Supports global exchanges with proper suffixes
        - Handles different currencies and accounting standards
        - Works with ADRs and local listings
        """)
    
    if analyze_button and tickers_to_analyze:
        with st.spinner(f"🔍 Analyzing {len(tickers_to_analyze)} stocks..."):
            # Perform comparison analysis
            comparison_result = compare_tickers_financials(tickers_to_analyze)
            
            if not comparison_result:
                st.error("❌ Could not analyze any of the provided tickers. Please check the ticker symbols and try again.")
                return
            
            # Count successful vs failed analyses
            successful_tickers = [ticker for ticker, data in comparison_result.items() if 'Error' not in data]
            failed_tickers = [ticker for ticker, data in comparison_result.items() if 'Error' in data]
            
            if not successful_tickers:
                st.error("❌ All ticker analyses failed. Please check the ticker symbols and try again.")
                st.write("Failed tickers:", failed_tickers)
                return
            
            # Store results in session state
            st.session_state['comparison_result'] = comparison_result
            st.session_state['successful_tickers'] = successful_tickers
            st.session_state['failed_tickers'] = failed_tickers
    
    # Display results if available
    if 'comparison_result' in st.session_state:
        result = st.session_state['comparison_result']
        successful_tickers = st.session_state['successful_tickers']
        failed_tickers = st.session_state['failed_tickers']
        
        # Analysis header
        st.success(f"✅ Analysis complete! Successfully analyzed {len(successful_tickers)} stocks.")
        
        if failed_tickers:
            st.warning(f"⚠️ Failed to analyze: {', '.join(failed_tickers)}")
        
        # Get all available years
        all_years = set()
        for ticker_data in result.values():
            for key in ticker_data.keys():
                if isinstance(key, int):
                    all_years.add(key)
        sorted_years = sorted(list(all_years), reverse=True)
        
        # Company overview
        st.subheader("📋 Company Overview")
        
        overview_data = []
        for ticker in successful_tickers:
            ticker_data = result[ticker]
            current_val = ticker_data.get('Current Valuation', {})
            
            overview_data.append({
                'Ticker': ticker,
                'Company': current_val.get('shortName', ticker),
                'Current Price': f"${current_val.get('Price', 0):.2f}" if current_val.get('Price') else "N/A",
                'Market Cap': format_large_number(current_val.get('Market Cap')),
                'PE Ratio': f"{current_val.get('PE', 0):.1f}" if current_val.get('PE') else "N/A",
                'Currency': current_val.get('currency', 'USD')
            })
        
        df_overview = pd.DataFrame(overview_data)
        st.dataframe(df_overview, use_container_width=True, hide_index=True)
        
        # Tabs for different analysis sections
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📈 Financial Trends", "💰 Current Valuations", "🔢 Historical Data", "📊 Category Analysis", "📥 Export"
        ])
        
        with tab1:
            st.subheader("📈 Financial Trends Comparison")
            
            if sorted_years:
                # Key metrics comparison charts
                col1, col2 = st.columns(2)
                
                with col1:
                    revenue_chart = create_comparison_chart(result, 'Revenue', sorted_years, 'Revenue Comparison')
                    st.plotly_chart(revenue_chart, use_container_width=True)
                
                with col2:
                    income_chart = create_comparison_chart(result, 'Net Income', sorted_years, 'Net Income Comparison')
                    st.plotly_chart(income_chart, use_container_width=True)
                
                # Margin comparisons
                col1, col2 = st.columns(2)
                
                with col1:
                    gross_margin_chart = create_comparison_chart(result, 'Gross Margin %', sorted_years, 'Gross Margin % Comparison')
                    st.plotly_chart(gross_margin_chart, use_container_width=True)
                
                with col2:
                    ebitda_margin_chart = create_comparison_chart(result, 'EBITDA Margin %', sorted_years, 'EBITDA Margin % Comparison')
                    st.plotly_chart(ebitda_margin_chart, use_container_width=True)
                
                # Debt and cash flow
                col1, col2 = st.columns(2)
                
                with col1:
                    debt_equity_chart = create_comparison_chart(result, 'Debt to Equity', sorted_years, 'Debt to Equity Comparison')
                    st.plotly_chart(debt_equity_chart, use_container_width=True)
                
                with col2:
                    ocf_chart = create_comparison_chart(result, 'Operating Cash Flow', sorted_years, 'Operating Cash Flow Comparison')
                    st.plotly_chart(ocf_chart, use_container_width=True)
        
        with tab2:
            st.subheader("💰 Current Valuation Metrics")
            
            # Current metrics comparison
            col1, col2 = st.columns(2)
            
            with col1:
                market_cap_chart = create_current_metrics_chart(result, 'Market Cap', 'bar')
                if market_cap_chart:
                    st.plotly_chart(market_cap_chart, use_container_width=True)
                
                pe_chart = create_current_metrics_chart(result, 'PE', 'bar')
                if pe_chart:
                    st.plotly_chart(pe_chart, use_container_width=True)
            
            with col2:
                price_chart = create_current_metrics_chart(result, 'Price', 'bar')
                if price_chart:
                    st.plotly_chart(price_chart, use_container_width=True)
                
                # Current valuation table
                st.markdown("**Current Valuation Summary**")
                valuation_data = []
                for ticker in successful_tickers:
                    ticker_data = result[ticker]
                    current_val = ticker_data.get('Current Valuation', {})
                    
                    valuation_data.append({
                        'Ticker': ticker,
                        'Price': f"${current_val.get('Price', 0):.2f}" if current_val.get('Price') else "N/A",
                        'Market Cap': format_large_number(current_val.get('Market Cap')),
                        'PE Ratio': f"{current_val.get('PE', 0):.1f}" if current_val.get('PE') else "N/A",
                        '52W Low': f"${current_val.get('52 Low', 0):.2f}" if current_val.get('52 Low') else "N/A",
                        '52W High': f"${current_val.get('52 Week High', 0):.2f}" if current_val.get('52 Week High') else "N/A",
                        'EPS': f"${current_val.get('EPS (Current)', 0):.2f}" if current_val.get('EPS (Current)') else "N/A",
                        'DPS': f"${current_val.get('DPS (Current)', 0):.2f}" if current_val.get('DPS (Current)') else "N/A"
                    })
                
                df_valuation = pd.DataFrame(valuation_data)
                st.dataframe(df_valuation, use_container_width=True, hide_index=True)
        
        with tab3:
            st.subheader("🔢 Historical Financial Data")
            
            # Select metric category
            selected_category = st.selectbox(
                "Select Category:",
                options=list(ANALYSIS_CATEGORIES.keys()),
                help="Choose a category to view historical data"
            )
            
            if selected_category and sorted_years:
                metrics = ANALYSIS_CATEGORIES[selected_category]
                
                for metric in metrics:
                    st.markdown(f"**{metric}**")
                    
                    # Create table for this metric
                    metric_data = []
                    for year in sorted_years:
                        row = {'Year': year}
                        for ticker in successful_tickers:
                            ticker_data = result[ticker]
                            if year in ticker_data and metric in ticker_data[year]:
                                value = ticker_data[year][metric]
                                if value is not None:
                                    if isinstance(value, (int, float)) and not np.isnan(value):
                                        if abs(value) > 1e6:
                                            row[ticker] = f"{value:,.0f}"
                                        elif abs(value) > 1:
                                            row[ticker] = f"{value:,.2f}"
                                        else:
                                            row[ticker] = f"{value:.4f}"
                                    else:
                                        row[ticker] = str(value)
                                else:
                                    row[ticker] = "N/A"
                            else:
                                row[ticker] = "N/A"
                        metric_data.append(row)
                    
                    if metric_data:
                        df_metric = pd.DataFrame(metric_data)
                        st.dataframe(df_metric, use_container_width=True, hide_index=True)
                    
                    st.markdown("---")
        
        with tab4:
            st.subheader("📊 Category-wise Analysis")
            
            # Allow users to select multiple categories for comparison
            selected_categories = st.multiselect(
                "Select Categories to Compare:",
                options=list(ANALYSIS_CATEGORIES.keys()),
                default=["P&L"],
                help="Choose categories for detailed comparison"
            )
            
            for category in selected_categories:
                st.markdown(f"### {category}")
                metrics = ANALYSIS_CATEGORIES[category]
                
                # Create summary table for latest year
                if sorted_years:
                    latest_year = sorted_years[0]
                    
                    summary_data = []
                    for metric in metrics:
                        row = {'Metric': metric}
                        for ticker in successful_tickers:
                            ticker_data = result[ticker]
                            if latest_year in ticker_data and metric in ticker_data[latest_year]:
                                value = ticker_data[latest_year][metric]
                                if value is not None and not (isinstance(value, float) and np.isnan(value)):
                                    if isinstance(value, (int, float)):
                                        if abs(value) > 1e9:
                                            row[ticker] = f"{value/1e9:.2f}B"
                                        elif abs(value) > 1e6:
                                            row[ticker] = f"{value/1e6:.2f}M"
                                        elif abs(value) > 1:
                                            row[ticker] = f"{value:.2f}"
                                        else:
                                            row[ticker] = f"{value:.4f}"
                                    else:
                                        row[ticker] = str(value)
                                else:
                                    row[ticker] = "N/A"
                            else:
                                row[ticker] = "N/A"
                        summary_data.append(row)
                    
                    df_summary = pd.DataFrame(summary_data)
                    st.dataframe(df_summary, use_container_width=True, hide_index=True)
                
                st.markdown("---")
        
        with tab5:
            st.subheader("📥 Export Comparison Results")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Excel Export**")
                st.write("Download a comprehensive Excel report with all comparison data organized by categories.")
                
                if st.button("📊 Generate Excel Report", type="primary"):
                    with st.spinner("Generating Excel file..."):
                        # Create Excel file in memory
                        timestamp = dt.now().strftime("%Y%m%d_%H%M")
                        filename = f"stock_comparison_{timestamp}.xlsx"
                        
                        # Use temporary file for export
                        temp_path = f"temp_{filename}"
                        success = export_financials_to_excel(result, temp_path)
                        
                        if success and os.path.exists(temp_path):
                            with open(temp_path, 'rb') as f:
                                excel_data = f.read()
                            
                            st.download_button(
                                label="💾 Download Excel File",
                                data=excel_data,
                                file_name=filename,
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )
                            
                            # Cleanup
                            os.remove(temp_path)
                            st.success("✅ Excel file ready for download!")
                        else:
                            st.error("❌ Failed to generate Excel file.")
            
            with col2:
                st.markdown("**Summary CSV Export**")
                st.write("Download the company overview data as CSV.")
                
                if 'df_overview' in locals():
                    csv_data = df_overview.to_csv(index=False)
                    csv_filename = f"comparison_summary_{dt.now().strftime('%Y%m%d_%H%M')}.csv"
                    
                    st.download_button(
                        label="📄 Download CSV File",
                        data=csv_data,
                        file_name=csv_filename,
                        mime="text/csv"
                    )

    else:
        st.info("👆 Select stocks in the sidebar and click 'Compare Stocks' to begin your analysis.")
        
        # Show available ticker lists
        st.markdown("### 📋 Available Predefined Lists:")
        
        col1, col2 = st.columns(2)
        
        with col1:
            for i, (list_name, tickers) in enumerate(list(TICKER_LISTS.items())[:len(TICKER_LISTS)//2]):
                with st.expander(f"{list_name} ({len(tickers)} stocks)"):
                    st.write(", ".join(tickers[:10]) + ("..." if len(tickers) > 10 else ""))
        
        with col2:
            for i, (list_name, tickers) in enumerate(list(TICKER_LISTS.items())[len(TICKER_LISTS)//2:]):
                with st.expander(f"{list_name} ({len(tickers)} stocks)"):
                    st.write(", ".join(tickers[:10]) + ("..." if len(tickers) > 10 else ""))

if __name__ == "__main__":
    main()