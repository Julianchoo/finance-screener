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

from utils.financial_analysis import get_single_stock_analysis, export_single_stock_to_excel
from config import SINGLE_STOCK_METRICS, CHART_COLORS

st.set_page_config(page_title="Single Stock Analysis", page_icon="📈", layout="wide")

def create_metrics_chart(data, metric_name, years):
    """Create a line chart for a specific metric over years"""
    values = []
    year_labels = []
    
    for year in sorted(years):
        if year in data and metric_name in data[year]:
            val = data[year][metric_name]
            if pd.notna(val):
                values.append(val)
                year_labels.append(year)
    
    if not values:
        return None
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=year_labels,
        y=values,
        mode='lines+markers',
        name=metric_name,
        line=dict(color=CHART_COLORS[0], width=3),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title=f"{metric_name} Trend",
        xaxis_title="Year",
        yaxis_title=metric_name,
        template="plotly_white",
        height=400
    )
    
    return fig

def create_comparison_chart(data, metrics, years, title):
    """Create a multi-line chart comparing multiple metrics"""
    fig = go.Figure()
    
    for i, metric in enumerate(metrics):
        values = []
        year_labels = []
        
        for year in sorted(years):
            if year in data and metric in data[year]:
                val = data[year][metric]
                if pd.notna(val):
                    values.append(val)
                    year_labels.append(year)
        
        if values:
            fig.add_trace(go.Scatter(
                x=year_labels,
                y=values,
                mode='lines+markers',
                name=metric,
                line=dict(color=CHART_COLORS[i % len(CHART_COLORS)], width=2),
                marker=dict(size=6)
            ))
    
    fig.update_layout(
        title=title,
        xaxis_title="Year",
        yaxis_title="Value",
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

def main():
    st.title("📈 Single Stock Deep Dive Analysis")
    st.markdown("---")
    
    # Sidebar inputs
    st.sidebar.header("Analysis Parameters")
    ticker_input = st.sidebar.text_input(
        "Enter Stock Ticker:",
        value="MSFT",
        help="Enter a stock ticker symbol (e.g., MSFT, AAPL, GOOGL). For international stocks, include exchange suffix (e.g., .L for London, .T for Tokyo)"
    ).strip().upper()
    
    years_back = st.sidebar.slider(
        "Years to Analyze:",
        min_value=3,
        max_value=15,
        value=10,
        help="Number of years back to analyze"
    )
    
    analyze_button = st.sidebar.button("🔍 Analyze Stock", type="primary")
    
    # Information section
    with st.expander("ℹ️ How to Use This Tool", expanded=False):
        st.markdown("""
        **Single Stock Analysis** provides comprehensive financial analysis for any publicly traded stock:
        
        **Features:**
        - 📊 Complete P&L, Balance Sheet, and Cash Flow analysis
        - 📈 Historical trends and ratio calculations  
        - 💰 Two PE ratio calculations: year-end price vs current price
        - 💵 Dividend analysis and payout ratios
        - 📋 Excel export with formatted reports
        
        **International Stocks:**
        - London: Add .L (e.g., ULVR.L)
        - Tokyo: Add .T (e.g., 8001.T)  
        - Singapore: Add .SI (e.g., D05.SI)
        - And many more exchanges supported
        
        **Tips:**
        - Use standard ticker symbols as they appear on Yahoo Finance
        - Longer time periods provide better trend analysis
        - Export results to Excel for detailed offline analysis
        """)
    
    if analyze_button and ticker_input:
        with st.spinner(f"🔍 Analyzing {ticker_input}..."):
            # Perform analysis
            analysis_result = get_single_stock_analysis(ticker_input, years_back)
            
            if analysis_result is None:
                st.error(f"❌ Could not analyze {ticker_input}. Please check the ticker symbol and try again.")
                return
            
            # Store results in session state
            st.session_state['analysis_result'] = analysis_result
            st.session_state['current_ticker'] = ticker_input
    
    # Display results if available
    if 'analysis_result' in st.session_state:
        result = st.session_state['analysis_result']
        ticker = st.session_state['current_ticker']
        company_info = result['company_info']
        yearly_data = result['yearly_data']
        analysis_years = result['analysis_years']
        
        # Company header
        st.success(f"✅ Analysis complete for **{company_info['Company Name']}** ({ticker})")
        
        # Company overview
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Current Price", f"${company_info.get('Current Price', 'N/A')}")
        with col2:
            st.metric("Currency", company_info.get('Currency', 'USD'))
        with col3:
            st.metric("Exchange", company_info.get('Exchange', 'Unknown'))
        with col4:
            st.metric("Years Analyzed", len(analysis_years))
        
        # Tabs for different sections
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Overview", "💰 Financial Metrics", "📈 Trends", "🔢 Detailed Data", "📥 Export"
        ])
        
        with tab1:
            st.subheader("📊 Financial Overview")
            
            # Key metrics overview
            if analysis_years and analysis_years[-1] in yearly_data:
                latest_year = analysis_years[-1]
                latest_data = yearly_data[latest_year]
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        f"Revenue ({latest_year})", 
                        f"${latest_data.get('Revenue', 0):,.0f}" if pd.notna(latest_data.get('Revenue')) else "N/A"
                    )
                    st.metric(
                        f"Net Income ({latest_year})", 
                        f"${latest_data.get('Net Income', 0):,.0f}" if pd.notna(latest_data.get('Net Income')) else "N/A"
                    )
                
                with col2:
                    st.metric(
                        f"EPS ({latest_year})", 
                        f"${latest_data.get('EPS', 0):.2f}" if pd.notna(latest_data.get('EPS')) else "N/A"
                    )
                    st.metric(
                        f"PE Ratio (Current Price)", 
                        f"{latest_data.get('PE Ratio (Current Price)', 0):.1f}" if pd.notna(latest_data.get('PE Ratio (Current Price)')) else "N/A"
                    )
                
                with col3:
                    st.metric(
                        f"Dividend Per Share ({latest_year})", 
                        f"${latest_data.get('Dividend Per Share', 0):.2f}" if pd.notna(latest_data.get('Dividend Per Share')) else "N/A"
                    )
                    st.metric(
                        f"Debt to Equity ({latest_year})", 
                        f"{latest_data.get('Debt to Equity', 0):.2f}" if pd.notna(latest_data.get('Debt to Equity')) else "N/A"
                    )
        
        with tab2:
            st.subheader("💰 Financial Metrics by Category")
            
            # Create metrics tables for each category
            for category, metrics in SINGLE_STOCK_METRICS.items():
                if category == 'Company Information':
                    continue  # Skip company info as it's shown above
                
                st.markdown(f"**{category}**")
                
                # Prepare data for this category
                category_data = []
                for metric in metrics:
                    row = {'Metric': metric}
                    for year in analysis_years:
                        if year in yearly_data:
                            value = yearly_data[year].get(metric, np.nan)
                            if pd.notna(value):
                                if isinstance(value, (int, float)):
                                    if abs(value) > 1e6:  # Large numbers
                                        row[str(year)] = f"{value:,.0f}"
                                    elif abs(value) > 1:
                                        row[str(year)] = f"{value:,.2f}"
                                    else:
                                        row[str(year)] = f"{value:.4f}"
                                else:
                                    row[str(year)] = str(value)
                            else:
                                row[str(year)] = "N/A"
                        else:
                            row[str(year)] = "N/A"
                    category_data.append(row)
                
                if category_data:
                    df_category = pd.DataFrame(category_data)
                    st.dataframe(df_category, use_container_width=True, hide_index=True)
                st.markdown("---")
        
        with tab3:
            st.subheader("📈 Financial Trends")
            
            # Revenue and Net Income trend
            col1, col2 = st.columns(2)
            
            with col1:
                revenue_chart = create_metrics_chart(yearly_data, 'Revenue', analysis_years)
                if revenue_chart:
                    st.plotly_chart(revenue_chart, use_container_width=True)
            
            with col2:
                income_chart = create_metrics_chart(yearly_data, 'Net Income', analysis_years)
                if income_chart:
                    st.plotly_chart(income_chart, use_container_width=True)
            
            # Margin trends
            margin_metrics = ['Gross Margin %', 'EBITDA Margin %', 'EBIT Margin %', 'Net Margin %']
            margins_chart = create_comparison_chart(yearly_data, margin_metrics, analysis_years, "Profitability Margins Trend")
            st.plotly_chart(margins_chart, use_container_width=True)
            
            # PE Ratios comparison
            pe_metrics = ['PE Ratio (Year-End Price)', 'PE Ratio (Current Price)']
            pe_chart = create_comparison_chart(yearly_data, pe_metrics, analysis_years, "PE Ratios Comparison")
            st.plotly_chart(pe_chart, use_container_width=True)
            
            # EPS and Dividend trends
            col1, col2 = st.columns(2)
            
            with col1:
                eps_chart = create_metrics_chart(yearly_data, 'EPS', analysis_years)
                if eps_chart:
                    st.plotly_chart(eps_chart, use_container_width=True)
            
            with col2:
                div_chart = create_metrics_chart(yearly_data, 'Dividend Per Share', analysis_years)
                if div_chart:
                    st.plotly_chart(div_chart, use_container_width=True)
        
        with tab4:
            st.subheader("🔢 Complete Financial Data")
            
            # Create comprehensive dataframe
            all_data = []
            for category, metrics in SINGLE_STOCK_METRICS.items():
                for metric in metrics:
                    row = {'Category': category, 'Metric': metric}
                    
                    if category == 'Company Information':
                        # Company info is same for all years
                        value = company_info.get(metric, '')
                        for year in analysis_years:
                            row[str(year)] = value
                    else:
                        # Yearly data
                        for year in analysis_years:
                            if year in yearly_data:
                                value = yearly_data[year].get(metric, np.nan)
                                row[str(year)] = value
                            else:
                                row[str(year)] = np.nan
                    
                    all_data.append(row)
            
            df_complete = pd.DataFrame(all_data)
            
            # Format numeric columns only
            formatted_complete = df_complete.copy()
            
            # Format numeric columns
            for col in formatted_complete.columns:
                if col not in ['Category', 'Metric']:
                    formatted_complete[col] = formatted_complete[col].apply(
                        lambda x: f"{x:,.2f}" if isinstance(x, (int, float)) and pd.notna(x) else str(x) if pd.notna(x) else "N/A"
                    )
            
            st.dataframe(formatted_complete, use_container_width=True, hide_index=True)
        
        with tab5:
            st.subheader("📥 Export Analysis Results")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Excel Export**")
                st.write("Download a comprehensive Excel report with all financial metrics organized by category.")
                
                if st.button("📊 Generate Excel Report", type="primary"):
                    with st.spinner("Generating Excel file..."):
                        # Create Excel file in memory
                        excel_buffer = io.BytesIO()
                        timestamp = dt.now().strftime("%Y%m%d_%H%M")
                        filename = f"{ticker}_financial_analysis_{timestamp}.xlsx"
                        
                        # Use temporary file for export
                        temp_path = f"temp_{filename}"
                        success = export_single_stock_to_excel(result, temp_path)
                        
                        if success and os.path.exists(temp_path):
                            with open(temp_path, 'rb') as f:
                                excel_buffer.write(f.read())
                            
                            st.download_button(
                                label="💾 Download Excel File",
                                data=excel_buffer.getvalue(),
                                file_name=filename,
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )
                            
                            # Cleanup
                            os.remove(temp_path)
                            st.success("✅ Excel file ready for download!")
                        else:
                            st.error("❌ Failed to generate Excel file.")
            
            with col2:
                st.markdown("**CSV Export**")
                st.write("Download the detailed data as a CSV file for further analysis.")
                
                if len(all_data) > 0:
                    csv_buffer = df_complete.to_csv(index=False)
                    csv_filename = f"{ticker}_financial_data_{dt.now().strftime('%Y%m%d_%H%M')}.csv"
                    
                    st.download_button(
                        label="📄 Download CSV File",
                        data=csv_buffer,
                        file_name=csv_filename,
                        mime="text/csv"
                    )

    else:
        st.info("👆 Enter a stock ticker in the sidebar and click 'Analyze Stock' to begin your analysis.")
        
        # Show example tickers
        st.markdown("""
        ### 💡 Example Tickers to Try:
        
        **US Stocks:** MSFT, AAPL, GOOGL, NVDA, TSLA, JNJ, JPM, XOM  
        **UK Stocks:** ULVR.L, BP.L, SHEL.L, AZN.L, LGEN.L  
        **Japanese Stocks:** 7203.T, 8001.T, 6758.T, 9984.T  
        **European Stocks:** ASML, SAP, NOVN.SW, MC.PA  
        """)

if __name__ == "__main__":
    main()