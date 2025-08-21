# Configuration file for Financial Analysis Streamlit App

# App Settings
APP_TITLE = "Financial Analysis Dashboard"
DEFAULT_YEARS_BACK = 10
DEFAULT_COMPARISON_YEARS = 5
DOWNLOAD_PATH = "downloads"

# Predefined Ticker Lists
TICKER_LISTS = {
    "Small Caps": ["ABCL", "FUBO", "HNST", "SG", "CDLR", "KULR", "ROOT", "ONDS", "LGCY", "GAMB"],
    
    "Laggards": ["DLO", "NVO", "EVO.ST", "GOOGL", "UNH", "BABA", "PDD", "ASML"],
    
    "Japanese Trading Companies": [
        "8001.T", "ITOCY", "IOC.F",  # ITOCHU Corporation
        "8002.T", "MARUY", "MARA.F",  # Marubeni Corporation  
        "8058.T", "MSBHF", "MBI.F", "0Q0J.L",  # Mitsubishi Corporation
        "8031.T", "MITSY", "MTS1.F",  # Mitsui & Co., Ltd.
        "8053.T", "SSUMY", "SUMB.F",  # Sumitomo Corporation
        "0LAF.L"  # Sumitomo Mitsui Financial Group
    ],
    
    "Shipping/Navieras": ["MAERSK-B.CO", "HLAG.DE", "1919.HK", "ZIM", "TEN", "EAT", "SBLK", "GSL", "PSHG"],
    
    "Japanese Holdings": ["8053.T", "8031.T", "8058.T", "8002.T", "8001.T"],
    
    "Tech Giants": ["MSFT", "AMZN", "AAPL", "GOOG", "NVDA", "META", "TSLA", "AVGO"],
    
    "Pharma": [
        "LLY", "NVO", "JNJ", "ABBV", "RHHBY", "NVS", "AZN", "MRK", "AMGN", "GILD",
        "PFE", "VRTX", "BMY", "CSLLY", "REGN", "ALNY", "BAYRY", "TAK", "TEVA", "BIIB"
    ],
    
    "Singapore REITs": [
        "C38U.SI", "A17U.SI", "N2IU.SI", "M44U.SI", "ME8U.SI", 
        "AJBU.SI", "J69U.SI", "C2PU.SI", "AW9U.SI", "ACV.SI"
    ],
    
    "FTSE 100": [
        "BATS.L", "PSN.L", "BTRW.L", "ICG.L", "SN.L", "WTB.L", "RR.L", "IMI.L", "BKG.L", "STJ.L",
        "AHT.L", "SSE.L", "BARC.L", "SPX.L", "AAF.L", "PCT.L", "SMIN.L", "WEIR.L", "NWG.L", "LGEN.L",
        "TW.L", "IMB.L", "CNA.L", "GAW.L", "MRO.L", "CTEC.L", "PSH.L", "SGRO.L", "HSBA.L", "BT-A.L",
        "CRDA.L", "KGF.L", "FCIT.L", "HWDN.L", "LAND.L", "DCC.L", "BP.L", "CCEP.L", "TSCO.L", "MNG.L",
        "SMT.L", "AV.L", "HLMA.L", "VOD.L", "PHNX.L", "IAG.L", "SHEL.L", "UU.L", "ITRK.L", "SBRY.L",
        "GSK.L", "CCH.L", "ENT.L", "STAN.L", "BNZL.L", "SVT.L", "ABF.L", "JD.L", "SDR.L", "DPLM.L",
        "IHG.L", "DGE.L", "UTG.L", "SGE.L", "INF.L", "HSX.L", "RMV.L", "NG.L", "LMP.L", "ALW.L",
        "AZN.L", "MNDI.L", "CPG.L", "NXT.L", "LLOY.L", "REL.L", "EXPN.L", "AUTO.L", "HIK.L", "BEZ.L",
        "HLN.L", "PSON.L", "MKS.L", "BA.L", "RIO.L", "BAB.L", "ULVR.L", "III.L", "LSEG.L", "RKT.L",
        "EDV.L", "PRU.L", "FRES.L", "RTO.L", "ADM.L", "EZJ.L", "ANTO.L", "AAL.L", "GLEN.L", "WPP.L"
    ],
    
    "UK Dividend Stocks": [
        "MNG.L", "LGEN.L", "PHNX.L", "TW.L", "BATS.L", 
        "RIO.L", "BP.L", "WPP.L", "LAND.L", "SDR.L"
    ],
    
    "High Yield ETFs": ["QDVO", "BALI", "JEPI", "QQQI", "GPIX", "SPYI", "GPIQ", "JEPQ"],
    
    "European Dividend Stocks": [
        "ULVR.L", "NOVN.SW", "ENEL.MI", "IMB.L", "ZURN.SW", 
        "MUV2.DE", "BN.PA", "TSCO.L", "TE.PA"
    ]
}

# Market Suffixes for Reference
MARKET_SUFFIXES = {
    "London Stock Exchange": ".L",
    "Tokyo Stock Exchange": ".T", 
    "Singapore Exchange": ".SI",
    "Hong Kong Exchange": ".HK",
    "Euronext Amsterdam": ".AS",
    "Frankfurt Stock Exchange": ".F or .DE",
    "Euronext Paris": ".PA",
    "Milan Stock Exchange": ".MI",
    "Swiss Exchange": ".SW",
    "Stockholm Stock Exchange": ".ST",
    "Copenhagen Stock Exchange": ".CO",
    "Brussels Stock Exchange": ".BR",
    "Thailand Stock Exchange": ".BK",
    "NASDAQ": " (no suffix)",
    "NYSE": " (no suffix)"
}

# Analysis Categories for Multi-Stock Comparison
ANALYSIS_CATEGORIES = {
    "P&L": [
        'Revenue', 'Gross Profit', 'Gross Margin %', 'SG&A', 'Operating Income', 'Operating Margin %',
        'EBITDA', 'EBITDA Margin %', 'EBIT', 'EBIT Margin %', 'Net Income', 'Net Margin %',
        'Diluted EPS', 'Basic Average Shares'
    ],
    "Balance Sheet": [
        'Total Assets', 'Total Liabilities Net Minority Interest', 'Total Debt', 'Total Equity Gross Minority Interest',
        'Debt to Equity', 'Debt to Cash', 'Cash And Cash Equivalents'
    ],
    "Cash Flow": [
        'Operating Cash Flow', 'Investing Cash Flow', 'Financing Cash Flow', 'Dividend Payment'
    ],
    "Valuation (Historical)": [
        'DPS', 'Cash per Share'
    ],
    "Valuation (Current)": [
        'Market Cap', 'Price', '52 Low', '52 Week High', 'PE',
        'EPS (Current)', 'DPS (Current)', 'Payout Ratio', 'shortName', 'currency'
    ]
}

# Single Stock Analysis Metric Groups
SINGLE_STOCK_METRICS = {
    'Company Information': [
        'Company Name', 'Ticker', 'Current Price', 'Currency', 'Exchange', 'Trailing Dividend Yield'
    ],
    'P&L Statement': [
        'Revenue', 'Gross Profit', 'Gross Margin %', 'EBITDA', 'EBITDA Margin %',
        'EBIT', 'EBIT Margin %', 'EBT', 'Net Income', 'Net Margin %', 'EPS'
    ],
    'Cash Flow Statement': [
        'Operating Cash Flow', 'Investing Cash Flow', 'Financing Cash Flow', 'Dividend Payment'
    ],
    'Balance Sheet': [
        'Current Assets', 'Fixed Assets', 'Short Term Debt', 'Long Term Debt', 'Total Equity', 'Debt to Equity'
    ],
    'Trading Information': [
        'Opening Price', 'Closing Price', 'Average Volume', 'Shares Outstanding',
        'PE Ratio (Year-End Price)', 'PE Ratio (Current Price)', 'Dividend Per Share', 
        'Dividend Yield %', 'Payout Ratio %'
    ]
}

# ETF Analysis Categories
ETF_METRICS = [
    "Ticker", "Name", "Currency", "PE", "Expense Ratio", "Category", "Sector", "Market Cap",
    "Managing Company", "Dividend Yield (%)", "Top 1 Holding", "Weight 1", "Top 1 P/E",
    "Top 2 Holding", "Weight 2", "Top 3 Holding", "Weight 3", "Current Price",
    "Nav Price", "Price 12 Months Ago", "Strategy"
]

# Stock Screening Default Years
SCREENING_YEARS = [2024, 2023, 2022, 2021, 2020]

# File Export Settings
EXCEL_ENGINE = 'openpyxl'
CSV_ENCODING = 'utf-8'

# Color Scheme for Charts
CHART_COLORS = [
    '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
    '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
]

# Performance Thresholds
PERFORMANCE_THRESHOLDS = {
    'HIGH_PE': 25,
    'LOW_PE': 10,
    'HIGH_DEBT_EQUITY': 0.5,
    'HIGH_MARGIN': 15,
    'LOW_MARGIN': 5
}