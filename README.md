# 📊 Financial Analysis Dashboard

A comprehensive Streamlit web application for financial analysis and stock research, built from your existing Jupyter notebooks.

## 🚀 Features

### 📈 Single Stock Deep Dive
- Comprehensive 10-year financial analysis
- P&L, Balance Sheet, Cash Flow metrics
- **Enhanced PE ratios**: Year-end price vs Current price calculations
- Dividend analysis and payout ratios
- Interactive charts and Excel export

### 📊 Multi-Stock Comparison
- Compare multiple stocks side-by-side
- 5-year historical financial metrics
- Revenue, margins, and debt analysis
- Valuation metrics comparison
- Batch Excel export

### 🎯 ETF Analysis
- ETF characteristics and holdings breakdown
- Expense ratios and dividend yields
- Top holdings analysis with weights
- Performance tracking and strategy summaries

### 🔎 Stock Screening
- Batch analysis of predefined ticker lists
- Advanced filtering by valuation and performance
- Visual analysis with scatter plots
- Market cap ranking and sector analysis

## 📋 Installation & Setup

1. **Clone/Download the project files**
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Streamlit app:**
   ```bash
   streamlit run app.py
   ```

4. **Open your browser** and navigate to `http://localhost:8501`

## 🏗️ Project Structure

```
Financial Analysis/
├── app.py                           # Main Streamlit application
├── requirements.txt                 # Python dependencies
├── config.py                       # Configuration and ticker lists
├── utils/
│   ├── __init__.py
│   └── financial_analysis.py       # Core analysis functions
└── pages/
    ├── 1_📈_Single_Stock_Analysis.py
    ├── 2_📊_Multi_Stock_Comparison.py
    ├── 3_🎯_ETF_Analysis.py
    └── 4_🔎_Stock_Screening.py
```

## 🌍 International Market Support

The app supports global stock exchanges with proper ticker suffixes:

- **London Stock Exchange**: `.L` (e.g., ULVR.L, BP.L)
- **Tokyo Stock Exchange**: `.T` (e.g., 8001.T, 7203.T)
- **Singapore Exchange**: `.SI` (e.g., D05.SI, C38U.SI)
- **Hong Kong Exchange**: `.HK` (e.g., 1919.HK)
- **European Exchanges**: `.PA`, `.DE`, `.SW`, `.AS`, etc.
- **US Markets**: No suffix needed (MSFT, AAPL, etc.)

## 📊 Predefined Stock Lists

The app includes curated ticker lists for:

- **Technology**: FAANG and major tech companies
- **Healthcare/Pharma**: Global pharmaceutical giants
- **International**: Japanese trading companies, UK dividend stocks
- **Sectors**: Shipping, REITs, Financial services
- **Investment Themes**: Small caps, high-yield ETFs, dividend aristocrats

## 🎯 Key Improvements from Notebooks

1. **Enhanced PE Ratios**: Now includes both year-end and current price PE calculations
2. **Interactive Visualization**: Plotly charts for trend analysis
3. **Advanced Filtering**: Screen stocks by multiple criteria
4. **Export Functionality**: Download Excel and CSV reports
5. **Real-time Analysis**: Fresh data fetching with caching
6. **User-friendly Interface**: Intuitive navigation and help sections

## 📈 Usage Tips

1. **Single Stock Analysis**: Great for detailed company research
2. **Multi-Stock Comparison**: Perfect for sector analysis or stock selection
3. **ETF Analysis**: Ideal for understanding fund compositions and costs
4. **Stock Screening**: Excellent for finding stocks matching specific criteria

## 🔧 Troubleshooting

### Common Issues:

1. **ModuleNotFoundError**: Make sure all dependencies are installed
   ```bash
   pip install -r requirements.txt
   ```

2. **Data not loading**: Check your internet connection and ticker symbols

3. **Excel export errors**: Ensure you have write permissions in the download folder

4. **Slow performance**: Some analyses involve multiple API calls - be patient

### Data Limitations:

- Data sourced from Yahoo Finance (free tier)
- Historical data availability varies by ticker
- Some international stocks may have limited data
- Real-time data may have slight delays

## 🚀 Running in Production

For deployment on cloud platforms:

1. **Streamlit Cloud**: Push to GitHub and deploy directly
2. **Heroku**: Add `setup.sh` and `Procfile` for deployment
3. **Local Network**: Use `streamlit run app.py --server.address 0.0.0.0`

## 📝 Customization

- **Add new ticker lists**: Edit `config.py` → `TICKER_LISTS`
- **Modify analysis years**: Adjust `SCREENING_YEARS` in config
- **Change chart colors**: Update `CHART_COLORS` in config
- **Add new metrics**: Extend the analysis functions in `utils/financial_analysis.py`

## 📊 Data Sources

- **Primary**: Yahoo Finance via `yfinance` library
- **Currency**: Multi-currency support (USD, GBP, JPY, EUR, etc.)
- **Exchanges**: Global coverage including major markets
- **Update Frequency**: Real-time during market hours

## 🤝 Contributing

Feel free to enhance the application by:
- Adding new analysis features
- Improving visualizations
- Adding more international market support
- Optimizing performance

## 📄 License

This project is for educational and personal use. Please respect data provider terms of service.

---

**Happy Analyzing!** 📈📊🎯🔍