import yfinance as yf
import pandas as pd
import numpy as np
import openpyxl
from datetime import datetime as dt
import warnings
warnings.filterwarnings('ignore')

# =====================================================
# SINGLE STOCK ANALYSIS FUNCTIONS
# =====================================================

def get_yearly_price_data(ticker, year):
    """
    Get opening price, closing price, and average volume for a specific year.
    
    Args:
        ticker: yfinance Ticker object
        year: Year to analyze (int)
    
    Returns:
        dict: Contains opening_price, closing_price, avg_volume
    """
    try:
        start_date = f"{year}-01-01"
        end_date = f"{year+1}-01-01"
        
        hist = ticker.history(start=start_date, end=end_date)
        
        if hist.empty:
            return {
                'opening_price': np.nan,
                'closing_price': np.nan,
                'avg_volume': np.nan
            }
        
        opening_price = hist['Open'].iloc[0]
        closing_price = hist['Close'].iloc[-1]
        avg_volume = hist['Volume'].mean()
        
        return {
            'opening_price': opening_price,
            'closing_price': closing_price,
            'avg_volume': avg_volume
        }
    
    except Exception as e:
        print(f"Error getting price data for {year}: {e}")
        return {
            'opening_price': np.nan,
            'closing_price': np.nan,
            'avg_volume': np.nan
        }

def calculate_yoy_growth(current_value, previous_value):
    """
    Calculate Year-over-Year growth percentage.
    
    Args:
        current_value: Current year value
        previous_value: Previous year value
    
    Returns:
        float: YoY growth percentage (or None if cannot be calculated)
    """
    if pd.notna(current_value) and pd.notna(previous_value) and previous_value != 0:
        return ((current_value - previous_value) / abs(previous_value)) * 100
    return None

def calculate_ratios(data_dict, year):
    """
    Calculate derived metrics and ratios for a given year.
    
    Args:
        data_dict: Dictionary containing financial data for the year
        year: Year being processed
    
    Returns:
        dict: Updated dictionary with calculated ratios
    """
    try:
        # Calculate margins
        revenue = data_dict.get('Revenue', np.nan)
        if pd.notna(revenue) and revenue != 0:
            data_dict['Gross Margin %'] = (data_dict.get('Gross Profit', 0) / revenue) * 100
            data_dict['EBITDA Margin %'] = (data_dict.get('EBITDA', 0) / revenue) * 100
            data_dict['EBIT Margin %'] = (data_dict.get('EBIT', 0) / revenue) * 100
            data_dict['Net Margin %'] = (data_dict.get('Net Income', 0) / revenue) * 100
        else:
            data_dict['Gross Margin %'] = np.nan
            data_dict['EBITDA Margin %'] = np.nan
            data_dict['EBIT Margin %'] = np.nan
            data_dict['Net Margin %'] = np.nan
        
        # Calculate Debt-to-Equity
        total_debt = (data_dict.get('Short Term Debt', 0) or 0) + (data_dict.get('Long Term Debt', 0) or 0)
        total_equity = data_dict.get('Total Equity', np.nan)
        if pd.notna(total_equity) and total_equity != 0:
            data_dict['Debt to Equity'] = total_debt / total_equity
        else:
            data_dict['Debt to Equity'] = np.nan
        
        # Calculate per-share metrics
        shares = data_dict.get('Shares Outstanding', np.nan)
        if pd.notna(shares) and shares != 0:
            dividend_payment = abs(data_dict.get('Dividend Payment', 0) or 0)
            data_dict['Dividend Per Share'] = dividend_payment / shares
        else:
            data_dict['Dividend Per Share'] = np.nan
        
        # Calculate PE Ratio using year-end price and EPS
        closing_price = data_dict.get('Closing Price', np.nan)
        eps = data_dict.get('EPS', np.nan)
        if pd.notna(closing_price) and pd.notna(eps) and eps != 0:
            data_dict['PE Ratio (Year-End Price)'] = closing_price / eps
        else:
            data_dict['PE Ratio (Year-End Price)'] = np.nan
        
        # Calculate Dividend Yield
        dps = data_dict.get('Dividend Per Share', np.nan)
        if pd.notna(closing_price) and pd.notna(dps) and closing_price != 0:
            data_dict['Dividend Yield %'] = (dps / closing_price) * 100
        else:
            data_dict['Dividend Yield %'] = np.nan
        
        # Calculate Payout Ratio
        if pd.notna(eps) and pd.notna(dps) and eps != 0:
            data_dict['Payout Ratio %'] = (dps / eps) * 100
        else:
            data_dict['Payout Ratio %'] = np.nan
        
        return data_dict
    
    except Exception as e:
        print(f"Error calculating ratios for {year}: {e}")
        return data_dict

def get_single_stock_analysis(ticker_symbol, years_back=10):
    """
    Comprehensive financial analysis of a single stock over specified years.
    
    Args:
        ticker_symbol: Stock ticker (e.g., 'MSFT')
        years_back: Number of years to analyze (default 10)
    
    Returns:
        dict: Complete financial analysis data
    """
    print(f"Analyzing {ticker_symbol}...")
    
    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info
        
        # Basic company information
        company_info = {
            'Company Name': info.get('longName', ticker_symbol),
            'Ticker': ticker_symbol,
            'Current Price': info.get('currentPrice', np.nan),
            'Currency': info.get('currency', 'USD'),
            'Exchange': info.get('fullExchangeName', 'Unknown'),
            'Trailing Dividend Yield': info.get('trailingAnnualDividendYield', np.nan)
        }
        
        print(f"Company: {company_info['Company Name']}")
        
        # Get financial statements
        financials = ticker.financials
        balance_sheet = ticker.balance_sheet
        cashflow = ticker.cashflow
        
        # Determine available years
        current_year = dt.now().year
        target_years = list(range(current_year - years_back + 1, current_year + 1))
        
        # Get all available years from financial statements
        available_years = set()
        if not financials.empty:
            available_years.update(financials.columns.year)
        if not balance_sheet.empty:
            available_years.update(balance_sheet.columns.year)
        if not cashflow.empty:
            available_years.update(cashflow.columns.year)
        
        # Filter to target years that have data
        analysis_years = [year for year in target_years if year in available_years]
        analysis_years.sort()
        
        print(f"Analyzing years: {analysis_years}")
        
        yearly_data = {}
        
        for year in analysis_years:
            print(f"Processing {year}...")
            year_data = {'Year': year}
            
            # Helper function to get data for specific year
            def get_financial_data(df, item_name, year):
                if df.empty or item_name not in df.index:
                    return np.nan
                year_cols = [col for col in df.columns if col.year == year]
                if not year_cols:
                    return np.nan
                return df.loc[item_name, year_cols[0]]
            
            # P&L Statement data
            year_data['Revenue'] = get_financial_data(financials, 'Total Revenue', year)
            year_data['Gross Profit'] = get_financial_data(financials, 'Gross Profit', year)
            year_data['EBITDA'] = get_financial_data(financials, 'EBITDA', year)
            year_data['EBIT'] = get_financial_data(financials, 'EBIT', year)
            
            # Try different names for EBT (Earnings Before Tax)
            ebt = get_financial_data(financials, 'Pretax Income', year)
            if pd.isna(ebt):
                ebt = get_financial_data(financials, 'Income Before Tax', year)
            year_data['EBT'] = ebt
            
            year_data['Net Income'] = get_financial_data(financials, 'Net Income', year)
            year_data['EPS'] = get_financial_data(financials, 'Diluted EPS', year)
            year_data['Shares Outstanding'] = get_financial_data(financials, 'Basic Average Shares', year)
            
            # Cash Flow data
            year_data['Operating Cash Flow'] = get_financial_data(cashflow, 'Operating Cash Flow', year)
            year_data['Investing Cash Flow'] = get_financial_data(cashflow, 'Investing Cash Flow', year)
            year_data['Financing Cash Flow'] = get_financial_data(cashflow, 'Financing Cash Flow', year)
            year_data['Dividend Payment'] = get_financial_data(cashflow, 'Cash Dividends Paid', year)
            
            # Balance Sheet data
            total_assets = get_financial_data(balance_sheet, 'Total Assets', year)
            current_assets = get_financial_data(balance_sheet, 'Current Assets', year)
            
            year_data['Current Assets'] = current_assets
            year_data['Fixed Assets'] = total_assets - current_assets if pd.notna(total_assets) and pd.notna(current_assets) else np.nan
            
            # Try different debt naming conventions
            short_debt = get_financial_data(balance_sheet, 'Current Debt', year)
            if pd.isna(short_debt):
                short_debt = get_financial_data(balance_sheet, 'Current Debt And Capital Lease Obligation', year)
            year_data['Short Term Debt'] = short_debt
            
            year_data['Long Term Debt'] = get_financial_data(balance_sheet, 'Long Term Debt', year)
            
            # Try different equity naming conventions
            total_equity = get_financial_data(balance_sheet, 'Total Equity Gross Minority Interest', year)
            if pd.isna(total_equity):
                total_equity = get_financial_data(balance_sheet, 'Stockholders Equity', year)
            year_data['Total Equity'] = total_equity
            
            # Get trading information
            price_data = get_yearly_price_data(ticker, year)
            year_data['Opening Price'] = price_data['opening_price']
            year_data['Closing Price'] = price_data['closing_price']
            year_data['Average Volume'] = price_data['avg_volume']
            
            # Calculate ratios and derived metrics
            year_data = calculate_ratios(year_data, year)
            
            # Calculate PE Ratio using current price and historical EPS
            current_price = company_info.get('Current Price', np.nan)
            eps = year_data.get('EPS', np.nan)
            if pd.notna(current_price) and pd.notna(eps) and eps != 0:
                year_data['PE Ratio (Current Price)'] = current_price / eps
            else:
                year_data['PE Ratio (Current Price)'] = np.nan
            
            yearly_data[year] = year_data
        
        result = {
            'company_info': company_info,
            'yearly_data': yearly_data,
            'analysis_years': analysis_years
        }
        
        print(f"Analysis complete for {ticker_symbol}")
        return result
    
    except Exception as e:
        print(f"Error analyzing {ticker_symbol}: {e}")
        return None

def export_single_stock_to_excel(analysis_data, output_filename):
    """
    Export single stock analysis to Excel with proper formatting.
    
    Args:
        analysis_data: Result from get_single_stock_analysis()
        output_filename: Path for Excel file
    
    Returns:
        bool: Success status
    """
    if not analysis_data:
        print("No data to export")
        return False
    
    try:
        company_info = analysis_data['company_info']
        yearly_data = analysis_data['yearly_data']
        analysis_years = analysis_data['analysis_years']
        
        # Define the structure of metrics in order
        metric_groups = {
            'Company Information': {
                'Company Name': 'company_info',
                'Ticker': 'company_info',
                'Current Price': 'company_info',
                'Currency': 'company_info',
                'Exchange': 'company_info'
            },
            'P&L Statement': {
                'Revenue': 'yearly',
                'Gross Profit': 'yearly',
                'Gross Margin %': 'yearly',
                'EBITDA': 'yearly',
                'EBITDA Margin %': 'yearly',
                'EBIT': 'yearly',
                'EBIT Margin %': 'yearly',
                'EBT': 'yearly',
                'Net Income': 'yearly',
                'Net Margin %': 'yearly',
                'EPS': 'yearly'
            },
            'Cash Flow Statement': {
                'Operating Cash Flow': 'yearly',
                'Investing Cash Flow': 'yearly',
                'Financing Cash Flow': 'yearly',
                'Dividend Payment': 'yearly'
            },
            'Balance Sheet': {
                'Current Assets': 'yearly',
                'Fixed Assets': 'yearly',
                'Short Term Debt': 'yearly',
                'Long Term Debt': 'yearly',
                'Total Equity': 'yearly',
                'Debt to Equity': 'yearly'
            },
            'Trading Information': {
                'Opening Price': 'yearly',
                'Closing Price': 'yearly',
                'Average Volume': 'yearly',
                'Shares Outstanding': 'yearly',
                'PE Ratio (Year-End Price)': 'yearly',
                'PE Ratio (Current Price)': 'yearly',
                'Dividend Per Share': 'yearly',
                'Dividend Yield %': 'yearly',
                'Payout Ratio %': 'yearly'
            }
        }
        
        # Prepare data for DataFrame
        data_for_df = []
        
        for group_name, metrics in metric_groups.items():
            for metric_name, data_type in metrics.items():
                row = {'Category': group_name, 'Metric': metric_name}
                
                if data_type == 'company_info':
                    value = company_info.get(metric_name, '')
                    for year in analysis_years:
                        row[str(year)] = value
                else:
                    for year in analysis_years:
                        if year in yearly_data:
                            row[str(year)] = yearly_data[year].get(metric_name, np.nan)
                        else:
                            row[str(year)] = np.nan
                
                data_for_df.append(row)
        
        # Create DataFrame
        df = pd.DataFrame(data_for_df)
        df.set_index(['Category', 'Metric'], inplace=True)
        
        # Export to Excel
        with pd.ExcelWriter(output_filename, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Financial Analysis')
            
            workbook = writer.book
            worksheet = writer.sheets['Financial Analysis']
            
            # Auto-adjust column widths
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
        
        print(f"Excel file exported successfully: {output_filename}")
        return True
        
    except Exception as e:
        print(f"Error exporting to Excel: {e}")
        return False

# =====================================================
# MULTI-STOCK COMPARISON FUNCTIONS  
# =====================================================

def _convert_na_to_none(data):
    """
    Recursively converts pd.NA values within a dictionary or list to None.
    Also converts numpy.nan to None as json.dumps cannot serialize it.
    """
    if isinstance(data, dict):
        return {k: _convert_na_to_none(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [_convert_na_to_none(elem) for elem in data]
    elif pd.isna(data):
        return None
    elif isinstance(data, float) and np.isnan(data):
        return None
    else:
        return data

def compare_tickers_financials(tickers):
    """
    Compares key financial metrics for a list of tickers over the last 5 fiscal years.
    
    Args:
        tickers (list): A list of stock ticker symbols
    
    Returns:
        dict: Financial data for each ticker
    """
    all_tickers_data = {}
    current_year_actual = dt.now().year

    for ticker_symbol in tickers:
        print(f"Fetching data for {ticker_symbol}...")
        ticker = yf.Ticker(ticker_symbol)
        ticker_data = {}

        try:
            # Fetch financial statements and info
            financials = ticker.financials
            balance_sheet = ticker.balance_sheet
            cashflow = ticker.cashflow
            info = ticker.info
            
            if info:
                print(f"  {info.get('shortName', ticker_symbol)}")

            # Get available years
            available_years_financials = []
            if not financials.empty:
                available_years_financials = sorted(list(financials.columns.year.unique()), reverse=True)
            
            available_years_bs = []
            if not balance_sheet.empty:
                available_years_bs = sorted(list(balance_sheet.columns.year.unique()), reverse=True)

            available_years_cf = []
            if not cashflow.empty:
                available_years_cf = sorted(list(cashflow.columns.year.unique()), reverse=True)

            # Combine all available years and get the most recent unique 5
            all_available_years = sorted(list(set(available_years_financials + available_years_bs + available_years_cf)), reverse=True)
            years_to_compare = [year for year in all_available_years if year <= current_year_actual][:5]
            
            if not years_to_compare:
                print(f"No historical financial data found for {ticker_symbol}.")
                all_tickers_data[ticker_symbol] = {'Error': 'No historical financial data found.'}
                continue

            for year in years_to_compare:
                year_data = {}
                
                # Helper to get the latest financial statement column for a given year
                def get_latest_column_for_year(df, target_year):
                    if df.empty:
                        return None
                    matching_dates = [col for col in df.columns if col.year == target_year]
                    if matching_dates:
                        return max(matching_dates)
                    return None

                # P&L Metrics
                financials_col = get_latest_column_for_year(financials, year)
                if financials_col and financials_col in financials.columns:
                    year_data['Revenue'] = financials.loc['Total Revenue', financials_col] if 'Total Revenue' in financials.index else pd.NA
                    year_data['Gross Profit'] = financials.loc['Gross Profit', financials_col] if 'Gross Profit' in financials.index else pd.NA
                    
                    if pd.notna(year_data['Gross Profit']) and pd.notna(year_data['Revenue']) and year_data['Revenue'] != 0:
                        year_data['Gross Margin %'] = (year_data['Gross Profit'] / year_data['Revenue'])
                    else:
                        year_data['Gross Margin %'] = pd.NA
                    
                    year_data['SG&A'] = financials.loc['Selling General And Administration', financials_col] if 'Selling General And Administration' in financials.index else pd.NA
                    year_data['EBITDA'] = financials.loc['EBITDA', financials_col] if 'EBITDA' in financials.index else pd.NA
                    year_data['EBIT'] = financials.loc['EBIT', financials_col] if 'EBIT' in financials.index else pd.NA
                    year_data['Operating Income'] = financials.loc['Operating Income', financials_col] if 'Operating Income' in financials.index else pd.NA
                    year_data['Net Income'] = financials.loc['Net Income', financials_col] if 'Net Income' in financials.index else pd.NA

                    # Calculate margins
                    if pd.notna(year_data['EBITDA']) and pd.notna(year_data['Revenue']) and year_data['Revenue'] != 0:
                        year_data['EBITDA Margin %'] = (year_data['EBITDA'] / year_data['Revenue'])
                    else:
                        year_data['EBITDA Margin %'] = pd.NA
                
                    if pd.notna(year_data['EBIT']) and pd.notna(year_data['Revenue']) and year_data['Revenue'] != 0:
                        year_data['EBIT Margin %'] = (year_data['EBIT'] / year_data['Revenue'])
                    else:
                        year_data['EBIT Margin %'] = pd.NA
                        
                    if pd.notna(year_data['Operating Income']) and pd.notna(year_data['Revenue']) and year_data['Revenue'] != 0:
                        year_data['Operating Margin %'] = (year_data['Operating Income'] / year_data['Revenue'])
                    else:
                        year_data['Operating Margin %'] = pd.NA

                    if pd.notna(year_data['Net Income']) and pd.notna(year_data['Revenue']) and year_data['Revenue'] != 0:
                        year_data['Net Margin %'] = (year_data['Net Income'] / year_data['Revenue'])
                    else:
                        year_data['Net Margin %'] = pd.NA

                    year_data['Diluted EPS'] = financials.loc['Diluted EPS', financials_col] if 'Diluted EPS' in financials.index else pd.NA
                    year_data['Basic Average Shares'] = financials.loc['Basic Average Shares', financials_col] if 'Basic Average Shares' in financials.index else pd.NA
                else:
                    # Initialize P&L metrics with NA if data is missing
                    year_data.update({
                        'Revenue': pd.NA, 'Gross Profit': pd.NA, 'Gross Margin %': pd.NA,
                        'SG&A': pd.NA, 'Operating Income': pd.NA, 'Operating Margin %': pd.NA,
                        'EBITDA': pd.NA, 'EBITDA Margin %': pd.NA, 'EBIT': pd.NA, 'EBIT Margin %': pd.NA,
                        'Net Income': pd.NA, 'Net Margin %': pd.NA, 'Diluted EPS': pd.NA, 'Basic Average Shares': pd.NA
                    })

                # Balance Sheet Metrics
                balance_sheet_col = get_latest_column_for_year(balance_sheet, year)
                if balance_sheet_col and balance_sheet_col in balance_sheet.columns:
                    year_data['Total Assets'] = balance_sheet.loc['Total Assets', balance_sheet_col] if 'Total Assets' in balance_sheet.index else pd.NA
                    year_data['Total Liabilities Net Minority Interest'] = balance_sheet.loc['Total Liabilities Net Minority Interest', balance_sheet_col] if 'Total Liabilities Net Minority Interest' in balance_sheet.index else pd.NA
                    
                    long_term_debt = balance_sheet.loc['Long Term Debt', balance_sheet_col] if 'Long Term Debt' in balance_sheet.index else pd.NA
                    
                    short_term_debt = pd.NA
                    if 'Current Debt And Capital Lease Obligation' in balance_sheet.index:
                        short_term_debt = balance_sheet.loc['Current Debt And Capital Lease Obligation', balance_sheet_col]
                    
                    if pd.isna(short_term_debt) and 'Current Debt' in balance_sheet.index:
                        short_term_debt = balance_sheet.loc['Current Debt', balance_sheet_col]

                    total_debt = (long_term_debt if pd.notna(long_term_debt) else 0) + (short_term_debt if pd.notna(short_term_debt) else 0)
                    year_data['Total Debt'] = total_debt

                    total_equity = balance_sheet.loc['Total Equity Gross Minority Interest', balance_sheet_col] if 'Total Equity Gross Minority Interest' in balance_sheet.index else pd.NA
                    year_data['Total Equity Gross Minority Interest'] = total_equity
                    
                    # Debt to Equity
                    if pd.notna(total_equity) and total_equity != 0:
                        year_data['Debt to Equity'] = total_debt / total_equity
                    else:
                        year_data['Debt to Equity'] = pd.NA
                    
                    cash_and_equivalents = balance_sheet.loc['Cash And Cash Equivalents', balance_sheet_col] if 'Cash And Cash Equivalents' in balance_sheet.index else pd.NA
                    year_data['Cash And Cash Equivalents'] = cash_and_equivalents
                    
                    # Debt to Cash
                    if pd.notna(cash_and_equivalents) and cash_and_equivalents != 0:
                        year_data['Debt to Cash'] = total_debt / cash_and_equivalents
                    else:
                        year_data['Debt to Cash'] = pd.NA
                else:
                    year_data.update({
                        'Total Assets': pd.NA, 'Total Liabilities Net Minority Interest': pd.NA,
                        'Total Debt': pd.NA, 'Total Equity Gross Minority Interest': pd.NA,
                        'Debt to Equity': pd.NA, 'Debt to Cash': pd.NA,
                        'Cash And Cash Equivalents': pd.NA
                    })

                # Cash Flow Metrics
                cashflow_col = get_latest_column_for_year(cashflow, year)
                if cashflow_col and cashflow_col in cashflow.columns:
                    year_data['Operating Cash Flow'] = cashflow.loc['Operating Cash Flow', cashflow_col] if 'Operating Cash Flow' in cashflow.index else pd.NA
                    year_data['Investing Cash Flow'] = cashflow.loc['Investing Cash Flow', cashflow_col] if 'Investing Cash Flow' in cashflow.index else pd.NA
                    year_data['Financing Cash Flow'] = cashflow.loc['Financing Cash Flow', cashflow_col] if 'Financing Cash Flow' in cashflow.index else pd.NA
                    year_data['Dividend Payment'] = cashflow.loc['Cash Dividends Paid', cashflow_col] if 'Cash Dividends Paid' in cashflow.index else pd.NA
                else:
                    year_data.update({
                        'Operating Cash Flow': pd.NA, 'Investing Cash Flow': pd.NA,
                        'Financing Cash Flow': pd.NA, 'Dividend Payment': pd.NA
                    })
                
                # Valuation metrics
                if pd.notna(year_data['Dividend Payment']) and pd.notna(year_data['Basic Average Shares']) and year_data['Basic Average Shares'] != 0:
                    year_data['DPS'] = year_data['Dividend Payment'] / year_data['Basic Average Shares']
                else:
                    year_data['DPS'] = pd.NA

                if pd.notna(year_data['Cash And Cash Equivalents']) and pd.notna(year_data['Basic Average Shares']) and year_data['Basic Average Shares'] != 0:
                    year_data['Cash per Share'] = year_data['Cash And Cash Equivalents'] / year_data['Basic Average Shares']
                else:
                    year_data['Cash per Share'] = pd.NA
                
                ticker_data[year] = year_data

            # Current Valuation
            current_valuation = {}
            if info:
                current_valuation['Market Cap'] = info.get('marketCap')
                current_valuation['Price'] = info.get('currentPrice')
                current_valuation['52 Low'] = info.get('fiftyTwoWeekLow')
                current_valuation['52 Week High'] = info.get('fiftyTwoWeekHigh')
                current_valuation['PE'] = info.get('trailingPE')
                current_valuation['shortName']= info.get('shortName')
                current_valuation['currency'] = info.get('currency')
                
                dps_current = info.get('dividendRate')
                eps_current = info.get('trailingEps')

                current_valuation['EPS (Current)'] = eps_current
                current_valuation['DPS (Current)'] = dps_current

                if pd.notna(dps_current) and pd.notna(eps_current) and eps_current != 0:
                    current_valuation['Payout Ratio'] = dps_current / eps_current
                else:
                    current_valuation['Payout Ratio'] = pd.NA

            if current_valuation:
                ticker_data['Current Valuation'] = current_valuation

            all_tickers_data[ticker_symbol] = _convert_na_to_none(ticker_data)

        except Exception as e:
            print(f"Error fetching data for {ticker_symbol}: {e}")
            all_tickers_data[ticker_symbol] = {'Error': f"Could not retrieve data: {str(e)}"}
            all_tickers_data[ticker_symbol] = _convert_na_to_none(all_tickers_data[ticker_symbol])

    return all_tickers_data

def export_financials_to_excel(financials_data, output_filename="financial_comparison.xlsx"):
    """
    Exports the financial comparison data to an Excel file.
    
    Args:
        financials_data (dict): The output from compare_tickers_financials
        output_filename (str): The name of the Excel file to create
    
    Returns:
        bool: Success status
    """
    if not financials_data:
        print("No data provided to export to Excel.")
        return False

    # Define metric order
    metric_order = {
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
            'EPS (Current)', 'DPS (Current)', 'Payout Ratio','shortName','currency'
        ]
    }

    # Collect all unique years
    all_years = set()
    for ticker_data in financials_data.values():
        for key in ticker_data.keys():
            if isinstance(key, int):
                all_years.add(key)
    sorted_years = sorted(list(all_years), reverse=True)

    # Prepare data for DataFrame
    processed_data = {}

    for ticker_symbol, ticker_metrics in financials_data.items():
        if 'Error' in ticker_metrics:
            print(f"Skipping {ticker_symbol} due to error: {ticker_metrics['Error']}")
            continue

        for year_or_type, metrics_dict in ticker_metrics.items():
            if year_or_type == 'Current Valuation':
                category = "Valuation (Current)"
                for metric_name in metric_order[category]:
                    value = metrics_dict.get(metric_name, None)
                    row_key = (category, metric_name, 'Current')
                    if row_key not in processed_data:
                        processed_data[row_key] = {}
                    processed_data[row_key][ticker_symbol] = value
            elif isinstance(year_or_type, int):
                year = year_or_type
                for category, metrics_list in metric_order.items():
                    if category == "Valuation (Current)":
                        continue
                    for metric_name in metrics_list:
                        value = metrics_dict.get(metric_name, None)
                        row_key = (category, metric_name, year)
                        if row_key not in processed_data:
                            processed_data[row_key] = {}
                        processed_data[row_key][ticker_symbol] = value

    # Create DataFrame
    df = pd.DataFrame.from_dict(processed_data, orient='index')
    df.index.names = ['Category', 'Metric', 'Year/Type']
    df = df.sort_index(level=[0, 1, 2], ascending=[True, True, False])

    # Reindex columns for consistent ticker order
    all_present_tickers = list(financials_data.keys())
    valid_tickers = [t for t in all_present_tickers if 'Error' not in financials_data.get(t, {})]
    if valid_tickers:
        df = df.reindex(columns=valid_tickers)

    try:
        df.to_excel(output_filename)
        print(f"Financial data successfully exported to '{output_filename}'")
        return True
    except Exception as e:
        print(f"Error exporting data to Excel: {e}")
        return False

# =====================================================
# ETF ANALYSIS FUNCTIONS
# =====================================================

def analyze_etfs(tickers):
    """
    Analyze a list of ETF tickers and return comprehensive information.
    
    Args:
        tickers (list): List of ETF ticker symbols
    
    Returns:
        list: List of ETF analysis dictionaries
    """
    records = []
    
    for symbol in tickers:
        print(f"Getting {symbol}")
        try:
            etf = yf.Ticker(symbol)
            info = etf.info
            name = info.get("longName")
            print(f"  {name}")

            # Core metrics
            pe = info.get("trailingPE")
            expense_ratio = info.get("netExpenseRatio")
            category = info.get("category")
            currency = info.get("currency")
            sector = info.get("sector")
            market_cap = info.get("marketCap")
            managing_company = info.get("fundFamily")
            nav_price = info.get("navPrice")
            div_yield = info.get('dividendYield')

            # Top holdings (expand to top 10)
            holdings_data = []
            aggregate_pe_sum = 0
            aggregate_pe_weight = 0
            aggregate_div_sum = 0
            aggregate_div_weight = 0
            
            try:
                tops = etf.funds_data.top_holdings
                
                # Extract up to 10 holdings
                for i in range(min(10, len(tops))):
                    holding_name = tops.iloc[i]["Name"]
                    # Fix percentage - data appears to be in decimal format, convert to percentage
                    holding_weight = float(tops.iloc[i]["Holding Percent"]) * 100 if not pd.isna(tops.iloc[i]["Holding Percent"]) else 0
                    
                    # Get individual stock metrics for aggregation
                    holding_symbol = tops.index[i] if i < len(tops.index) else None
                    holding_pe = None
                    holding_div_yield = None
                    
                    if holding_symbol:
                        try:
                            stock_info = yf.Ticker(holding_symbol).info
                            holding_pe = stock_info.get("trailingPE")
                            # Get dividend yield - need to determine actual format from yfinance
                            raw_div_yield = stock_info.get("dividendYield")
                            print(f"DEBUG: {holding_symbol} raw dividendYield: {raw_div_yield}, weight: {holding_weight}%")
                            
                            # Convert to decimal format for calculations
                            if raw_div_yield is not None:
                                # yfinance likely returns in percentage format (2.5 = 2.5%), convert to decimal
                                holding_div_yield = raw_div_yield / 100 if raw_div_yield > 0 else 0
                            else:
                                holding_div_yield = None
                            
                            # Aggregate calculations (weighted averages)
                            if holding_pe and holding_weight > 0:
                                aggregate_pe_sum += holding_pe * (holding_weight / 100)
                                aggregate_pe_weight += (holding_weight / 100)
                            
                            if holding_div_yield and holding_weight > 0:
                                # holding_div_yield is already in decimal format (0.025 = 2.5%)
                                # Weight needs to be converted to decimal (5% = 0.05)
                                weight_decimal = holding_weight / 100
                                contribution = holding_div_yield * weight_decimal
                                
                                aggregate_div_sum += contribution
                                aggregate_div_weight += weight_decimal
                                
                        except Exception as e:
                            print(f"Error getting metrics for {holding_symbol}: {e}")
                    
                    holdings_data.append({
                        'rank': i + 1,
                        'symbol': holding_symbol,
                        'name': holding_name,
                        'weight': holding_weight,
                        'pe': holding_pe,
                        'dividend_yield': holding_div_yield * 100 if holding_div_yield else None  # Convert decimal back to percentage for display
                    })
                
                # Calculate aggregate metrics
                aggregate_pe = aggregate_pe_sum / aggregate_pe_weight if aggregate_pe_weight > 0 else None
                
                # Calculate weighted average dividend yield and convert to percentage
                if aggregate_div_weight > 0:
                    # aggregate_div_sum is already weighted, just convert to percentage
                    aggregate_div_yield = (aggregate_div_sum / aggregate_div_weight) * 100
                else:
                    aggregate_div_yield = None
                
            except Exception as e:
                print(f"Error getting holdings data for {symbol}: {e}")
                holdings_data = []
                aggregate_pe = None
                aggregate_div_yield = None

            # Price data
            hist = etf.history(period="1y")
            current_price = hist['Close'].iloc[-1] if not hist.empty else None
            price_12m_ago = hist['Close'].iloc[0] if not hist.empty else None
            
            # Calculate 3-year earnings CAGR for the ETF itself
            earnings_cagr = None
            try:
                hist_3y = etf.history(period="3y")
                if not hist_3y.empty and len(hist_3y) > 252 * 2:  # At least 2 years of data
                    price_3y_ago = hist_3y['Close'].iloc[0]
                    if price_3y_ago and current_price:
                        earnings_cagr = ((current_price / price_3y_ago) ** (1/3) - 1) * 100
            except:
                earnings_cagr = None

            # Strategy
            thesis = info.get("longBusinessSummary")

            # Build record with all new data
            record = {
                "Ticker": symbol,
                "Name": name,
                "Currency": currency,
                "PE": pe,
                "Expense Ratio": expense_ratio,
                "Category": category,
                "Sector": sector,
                "Market Cap": market_cap,
                "Managing Company": managing_company,
                "Dividend Yield (%)": div_yield,
                "Current Price": current_price,
                "Nav Price": nav_price,
                "Price 12 Months Ago": price_12m_ago,
                "Strategy": thesis,
                # New aggregate metrics
                "Aggregate PE": aggregate_pe,
                "Aggregate Dividend Yield (%)": aggregate_div_yield,
                "3Y Price CAGR (%)": earnings_cagr,
                # Holdings data
                "Holdings Data": holdings_data,
                "Top Holdings Count": len(holdings_data)
            }
            
            # Add individual holding data for backward compatibility and easy access
            for i in range(min(10, len(holdings_data))):
                holding = holdings_data[i]
                record[f"Top {i+1} Holding"] = holding['name']
                record[f"Top {i+1} Symbol"] = holding['symbol']
                record[f"Weight {i+1}"] = holding['weight']
                record[f"Top {i+1} P/E"] = holding['pe']
                record[f"Top {i+1} Div Yield"] = holding['dividend_yield']
            
            records.append(record)
            
        except Exception as e:
            print(f"Error analyzing {symbol}: {e}")
            continue

    return records

# =====================================================
# STOCK SCREENING FUNCTIONS
# =====================================================

def screen_stocks(tickers, years=[2024, 2023, 2022, 2021, 2020]):
    """
    Screen multiple stocks with key financial metrics across specified years.
    
    Args:
        tickers (list): List of stock ticker symbols
        years (list): Years to analyze
    
    Returns:
        pandas.DataFrame: Comprehensive stock screening results
    """
    # Define basic metrics
    basic_metrics = {
        'Symbol': lambda info: info.get('symbol'),
        'Currency': lambda info: info.get('currency'),
        'Exchange': lambda info: info.get('fullExchangeName'),
        'Latest Price': lambda info: info.get('currentPrice'),
        'PE Ratio': lambda info: info.get('trailingPE'),
        'EPS': lambda info: info.get('trailingEps'),
        'TTM Dividend Yield (%)': lambda info: info.get('trailingAnnualDividendYield') or 0,
        'Dividend Rate': lambda info: info.get('dividendRate', 0),
        'Debt to Equity': lambda info: info.get('debtToEquity') or 0,
        'Shares Outstanding': lambda info: info.get('sharesOutstanding', 0),
        'Market Cap (Billion $)': lambda info: info.get('marketCap', 0) / 1e9,
        'Volume': lambda info: info.get('volume'),
        '52-Week High': lambda info: info.get('fiftyTwoWeekHigh'),
        '52-Week Low': lambda info: info.get('fiftyTwoWeekLow'),
        'Dividend Yield L5Y (%)': lambda info: info.get('fiveYearAvgDividendYield') or 0,
        'Price/52-Week Low': lambda info: (
            info.get('currentPrice') / info.get('fiftyTwoWeekLow')
            if info.get('currentPrice') and info.get('fiftyTwoWeekLow') else None
        ),
    }

    rows = []
    
    for ticker in tickers:
        try:
            print(f"Getting data on {ticker}")
            stock = yf.Ticker(ticker)
            info = stock.info
        
            # Start each row with company name
            row = {'Company': info.get('longName', ticker)}
        
            # Basic metrics
            for name, fn in basic_metrics.items():
                row[name] = fn(info)
        
            # Annual financials
            fin = stock.financials
            
            # Check if financials are available
            if fin.empty:
                print(f"No financials available for {ticker}")
                continue
                
            rev_series = fin.loc['Total Revenue'] if 'Total Revenue' in fin.index else pd.Series()
            net_series = fin.loc['Net Income'] if 'Net Income' in fin.index else pd.Series()
        
            # Dividend history
            div_series = stock.dividends
        
            # Process each year
            for year in years:
                # Revenue in billions
                rev_vals = rev_series[rev_series.index.year == year] if not rev_series.empty else pd.Series()
                row[f'Revenue {year} (Billion $)'] = rev_vals.iloc[0] / 1e9 if not rev_vals.empty else 0
        
                # Net Income in billions
                net_vals = net_series[net_series.index.year == year] if not net_series.empty else pd.Series()
                row[f'Net Income {year} (Billion $)'] = net_vals.iloc[0] / 1e9 if not net_vals.empty else 0
        
                # Dividends total for the year
                year_divs = div_series[div_series.index.year == year].sum() if not div_series.empty else 0
                row[f'Dividends {year}'] = year_divs
        
            rows.append(row)
        
        except Exception as e:
            print(f"Error processing {ticker}: {e}")
            continue

    # Create DataFrame
    if not rows:
        return pd.DataFrame()
        
    # Generate columns dynamically
    columns = [
        'Company'
    ] + list(basic_metrics.keys()) + [
        f'Revenue {y} (Billion $)' for y in years
    ] + [
        f'Net Income {y} (Billion $)' for y in years
    ] + [
        f'Dividends {y}' for y in years
    ]

    df = pd.DataFrame(rows, columns=columns)
    
    # Calculate additional metrics
    df["Payout Ratio"] = df["Dividend Rate"] / df["EPS"]
    
    # Sort by market cap if available
    if 'Market Cap (Billion $)' in df.columns:
        df = df.sort_values('Market Cap (Billion $)', ascending=False)

    return df