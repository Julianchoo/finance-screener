import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="Financial Analysis Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    st.title("📊 Financial Analysis Dashboard")
    st.markdown("---")
    
    st.markdown("""
    ## Welcome to Your Comprehensive Financial Analysis Tool
    
    This dashboard provides powerful financial analysis capabilities across multiple asset types and analysis methods.
    
    ### 🔍 Analysis Tools Available:
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **📈 Single Stock Deep Dive**
        - Comprehensive 10-year financial analysis
        - P&L, Balance Sheet, Cash Flow metrics
        - Historical PE ratios (year-end vs current price)
        - Dividend analysis and payout ratios
        - Excel export functionality
        
        **📊 Multi-Stock Comparison** 
        - Compare multiple stocks side-by-side
        - 5-year historical financial metrics
        - Revenue, margins, and debt analysis
        - Valuation metrics comparison
        - Batch Excel export
        """)
    
    with col2:
        st.markdown("""
        **🎯 ETF Analysis**
        - ETF characteristics and holdings
        - Expense ratios and dividend yields
        - Top holdings breakdown with weights
        - Performance tracking and strategy analysis
        - Investment thesis summaries
        
        **🔎 Stock Screening**
        - Batch analysis of predefined ticker lists
        - Market cap ranking and filtering
        - Multi-year performance metrics
        - International market coverage
        - Sector-specific analysis
        """)
    
    st.markdown("---")
    
    # Quick stats section
    st.markdown("### 📋 Quick Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Analysis Types", "4", help="Different analysis modules available")
    
    with col2:
        st.metric("Market Coverage", "Global", help="US, UK, Singapore, Japan, Europe markets")
    
    with col3:
        st.metric("Data Source", "Yahoo Finance", help="Real-time and historical financial data")
    
    with col4:
        st.metric("Export Format", "Excel", help="Formatted Excel reports with charts")
    
    st.markdown("---")
    
    # Instructions
    st.markdown("""
    ### 🚀 Getting Started
    
    1. **Choose an Analysis Tool** - Select from the sidebar navigation
    2. **Enter Your Parameters** - Input ticker symbols, time periods, etc.
    3. **Run Analysis** - Click analyze to generate insights
    4. **Export Results** - Download Excel reports for further analysis
    
    ### 💡 Tips for Best Results
    - Use standard ticker symbols (e.g., MSFT, AAPL, GOOGL)
    - For international stocks, include exchange suffix (e.g., .L for London, .T for Tokyo)
    - Check data availability before running extensive analyses
    - Export results for offline analysis and record keeping
    """)
    
    st.markdown("---")
    
    # Footer
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <small>Financial Analysis Dashboard | Data provided by Yahoo Finance | 
        Built with Streamlit 📊</small>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()