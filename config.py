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

# =====================================================
# STOCK SCREENER FIELD CONFIGURATION
# =====================================================

# Essential screening fields (most commonly used)
ESSENTIAL_SCREENING_FIELDS = {
    # Trading & Market Data
    'marketcap': {
        'display_name': 'Market Cap',
        'category': 'Market Data',
        'data_type': 'numeric',
        'format': 'billions',
        'comparison_ops': ['gt', 'lt', 'gte', 'lte', 'btwn']
    },
    'volume': {
        'display_name': 'Volume',
        'category': 'Market Data', 
        'data_type': 'numeric',
        'format': 'number',
        'comparison_ops': ['gt', 'lt', 'gte', 'lte', 'btwn']
    },
    'price': {
        'display_name': 'Stock Price',
        'category': 'Market Data',
        'data_type': 'numeric',
        'format': 'currency',
        'comparison_ops': ['gt', 'lt', 'gte', 'lte', 'btwn']
    },
    
    # Valuation Metrics
    'trailingpe': {
        'display_name': 'P/E Ratio (Trailing)',
        'category': 'Valuation',
        'data_type': 'numeric',
        'format': 'ratio',
        'comparison_ops': ['gt', 'lt', 'gte', 'lte', 'btwn']
    },
    'forwardpe': {
        'display_name': 'P/E Ratio (Forward)',
        'category': 'Valuation',
        'data_type': 'numeric',
        'format': 'ratio',
        'comparison_ops': ['gt', 'lt', 'gte', 'lte', 'btwn']
    },
    'pegratio': {
        'display_name': 'PEG Ratio',
        'category': 'Valuation',
        'data_type': 'numeric',
        'format': 'ratio',
        'comparison_ops': ['gt', 'lt', 'gte', 'lte', 'btwn']
    },
    'pricetobook': {
        'display_name': 'Price-to-Book',
        'category': 'Valuation',
        'data_type': 'numeric',
        'format': 'ratio',
        'comparison_ops': ['gt', 'lt', 'gte', 'lte', 'btwn']
    },
    
    # Profitability & Growth
    'trailingeps': {
        'display_name': 'EPS (Trailing)',
        'category': 'Profitability',
        'data_type': 'numeric',
        'format': 'currency',
        'comparison_ops': ['gt', 'lt', 'gte', 'lte', 'btwn']
    },
    'revenuegrowth': {
        'display_name': 'Revenue Growth',
        'category': 'Growth',
        'data_type': 'numeric',
        'format': 'percentage',
        'comparison_ops': ['gt', 'lt', 'gte', 'lte', 'btwn']
    },
    'earningsgrowth': {
        'display_name': 'Earnings Growth',
        'category': 'Growth', 
        'data_type': 'numeric',
        'format': 'percentage',
        'comparison_ops': ['gt', 'lt', 'gte', 'lte', 'btwn']
    },
    
    # Dividend Metrics
    'dividendyield': {
        'display_name': 'Dividend Yield',
        'category': 'Dividend',
        'data_type': 'numeric',
        'format': 'percentage',
        'comparison_ops': ['gt', 'lt', 'gte', 'lte', 'btwn']
    },
    'payoutratio': {
        'display_name': 'Payout Ratio',
        'category': 'Dividend',
        'data_type': 'numeric',
        'format': 'percentage',
        'comparison_ops': ['gt', 'lt', 'gte', 'lte', 'btwn']
    },
    
    # Financial Health
    'debttoequity': {
        'display_name': 'Debt-to-Equity',
        'category': 'Financial Health',
        'data_type': 'numeric',
        'format': 'ratio',
        'comparison_ops': ['gt', 'lt', 'gte', 'lte', 'btwn']
    },
    'returnonequity': {
        'display_name': 'ROE',
        'category': 'Financial Health',
        'data_type': 'numeric',
        'format': 'percentage',
        'comparison_ops': ['gt', 'lt', 'gte', 'lte', 'btwn']
    },
    
    # Geographic/Exchange Filters
    'exchange': {
        'display_name': 'Exchange',
        'category': 'Geographic',
        'data_type': 'categorical',
        'comparison_ops': ['eq', 'is-in']
    },
    'sector': {
        'display_name': 'Sector',
        'category': 'Geographic',
        'data_type': 'categorical', 
        'comparison_ops': ['eq', 'is-in']
    }
}

# Advanced screening fields (accessible via expansion)
ADVANCED_SCREENING_FIELDS = {
    # Additional Valuation
    'pricetosales': {
        'display_name': 'Price-to-Sales',
        'category': 'Valuation',
        'data_type': 'numeric',
        'format': 'ratio',
        'comparison_ops': ['gt', 'lt', 'gte', 'lte', 'btwn']
    },
    'enterprisevalue': {
        'display_name': 'Enterprise Value',
        'category': 'Valuation',
        'data_type': 'numeric',
        'format': 'billions',
        'comparison_ops': ['gt', 'lt', 'gte', 'lte', 'btwn']
    },
    'evebitda': {
        'display_name': 'EV/EBITDA',
        'category': 'Valuation',
        'data_type': 'numeric',
        'format': 'ratio',
        'comparison_ops': ['gt', 'lt', 'gte', 'lte', 'btwn']
    },
    
    # Profitability Margins
    'grossmargins': {
        'display_name': 'Gross Margin',
        'category': 'Profitability',
        'data_type': 'numeric',
        'format': 'percentage',
        'comparison_ops': ['gt', 'lt', 'gte', 'lte', 'btwn']
    },
    'operatingmargins': {
        'display_name': 'Operating Margin',
        'category': 'Profitability',
        'data_type': 'numeric',
        'format': 'percentage',
        'comparison_ops': ['gt', 'lt', 'gte', 'lte', 'btwn']
    },
    'ebitdamargins': {
        'display_name': 'EBITDA Margin',
        'category': 'Profitability',
        'data_type': 'numeric',
        'format': 'percentage',
        'comparison_ops': ['gt', 'lt', 'gte', 'lte', 'btwn']
    },
    'profitmargins': {
        'display_name': 'Net Profit Margin',
        'category': 'Profitability',
        'data_type': 'numeric',
        'format': 'percentage',
        'comparison_ops': ['gt', 'lt', 'gte', 'lte', 'btwn']
    },
    
    # Financial Health
    'currentratio': {
        'display_name': 'Current Ratio',
        'category': 'Financial Health',
        'data_type': 'numeric',
        'format': 'ratio',
        'comparison_ops': ['gt', 'lt', 'gte', 'lte', 'btwn']
    },
    'quickratio': {
        'display_name': 'Quick Ratio',
        'category': 'Financial Health',
        'data_type': 'numeric',
        'format': 'ratio',
        'comparison_ops': ['gt', 'lt', 'gte', 'lte', 'btwn']
    },
    'returnonassets': {
        'display_name': 'ROA',
        'category': 'Financial Health',
        'data_type': 'numeric',
        'format': 'percentage',
        'comparison_ops': ['gt', 'lt', 'gte', 'lte', 'btwn']
    },
    
    # Technical Indicators
    'beta': {
        'display_name': 'Beta',
        'category': 'Technical',
        'data_type': 'numeric',
        'format': 'ratio',
        'comparison_ops': ['gt', 'lt', 'gte', 'lte', 'btwn']
    },
    'movingaverage50': {
        'display_name': '50-Day MA',
        'category': 'Technical',
        'data_type': 'numeric',
        'format': 'currency',
        'comparison_ops': ['gt', 'lt', 'gte', 'lte', 'btwn']
    },
    'movingaverage200': {
        'display_name': '200-Day MA',
        'category': 'Technical',
        'data_type': 'numeric',
        'format': 'currency',
        'comparison_ops': ['gt', 'lt', 'gte', 'lte', 'btwn']
    },
    
    # ESG & Quality
    'totaleslriskscore': {
        'display_name': 'ESG Risk Score',
        'category': 'ESG',
        'data_type': 'numeric',
        'format': 'score',
        'comparison_ops': ['gt', 'lt', 'gte', 'lte', 'btwn']
    },
    
    # Additional Geographic
    'country': {
        'display_name': 'Country',
        'category': 'Geographic',
        'data_type': 'categorical',
        'comparison_ops': ['eq', 'is-in']
    },
    'region': {
        'display_name': 'Region',
        'category': 'Geographic', 
        'data_type': 'categorical',
        'comparison_ops': ['eq', 'is-in']
    }
}

# Combine all screening fields
ALL_SCREENING_FIELDS = {**ESSENTIAL_SCREENING_FIELDS, **ADVANCED_SCREENING_FIELDS}

# Field categories for UI organization
SCREENING_CATEGORIES = {
    'Market Data': 'Basic market metrics like price, volume, market cap',
    'Valuation': 'Price-based ratios and valuation metrics',
    'Profitability': 'Earnings and margin metrics',
    'Growth': 'Growth rates for revenue, earnings, etc.',
    'Dividend': 'Dividend-related metrics',
    'Financial Health': 'Balance sheet strength indicators', 
    'Technical': 'Technical analysis indicators',
    'ESG': 'Environmental, Social, Governance scores',
    'Geographic': 'Location and exchange-based filters'
}

# Default screen queries for quick access
PREDEFINED_SCREENS = {
    'Large Cap Value': {
        'description': 'Large companies with attractive valuations',
        'query_conditions': [
            ('gt', ['marketcap', 10000000000]),  # > $10B market cap
            ('lt', ['trailingpe', 15]),  # PE < 15
            ('gt', ['dividendyield', 2])  # Dividend yield > 2%
        ]
    },
    'High Growth': {
        'description': 'Companies with strong growth metrics',
        'query_conditions': [
            ('gt', ['revenuegrowth', 15]),  # Revenue growth > 15%
            ('gt', ['earningsgrowth', 20]),  # Earnings growth > 20%
            ('lt', ['pegratio', 2])  # PEG ratio < 2
        ]
    },
    'Dividend Aristocrats': {
        'description': 'High-quality dividend paying stocks',
        'query_conditions': [
            ('gt', ['dividendyield', 3]),  # Dividend yield > 3%
            ('lt', ['payoutratio', 0.8]),  # Payout ratio < 80%
            ('gt', ['marketcap', 5000000000])  # Market cap > $5B
        ]
    },
    'Quality Small Caps': {
        'description': 'Well-managed smaller companies',
        'query_conditions': [
            ('btwn', ['marketcap', 1000000000, 10000000000]),  # Market cap $1B - $10B
            ('gt', ['returnonequity', 15]),  # ROE > 15%
            ('lt', ['debttoequity', 0.5])  # Debt/Equity < 0.5
        ]
    }
}