#!/usr/bin/env python3
"""
Quick test script for the new advanced stock screening system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.financial_analysis import advanced_screen_stocks, validate_screening_filters, build_equity_query
from config import PREDEFINED_SCREENS, ALL_SCREENING_FIELDS

def test_field_validation():
    """Test the filter validation system"""
    print("Testing filter validation...")
    
    # Valid filters in EquityQuery format
    valid_filters = [
        ('gt', ['intradaymarketcap', 10000000000]),  # Market cap > $10B
        ('lt', ['peratio.lasttwelvemonths', 15]), # PE < 15
        ('btwn', ['forward_dividend_yield', 2, 8])  # Div yield between 2-8%
    ]
    
    is_valid, error = validate_screening_filters(valid_filters)
    print(f"Valid filters test: {'PASS' if is_valid else 'FAIL'} - {error or 'No errors'}")
    
    # Invalid filters
    invalid_filters = [
        ('gt', 'invalid_field', 10),  # Invalid field name
    ]
    
    is_valid, error = validate_screening_filters(invalid_filters)
    print(f"Invalid filters test: {'PASS' if not is_valid else 'FAIL'} - {error or 'Should have error'}")

def test_query_building():
    """Test the EquityQuery building"""
    print("\nTesting query building...")
    
    filters = [
        ('gt', ['intradaymarketcap', 5000000000]),   # Market cap > $5B
        ('lt', ['peratio.lasttwelvemonths', 20])  # PE < 20
    ]
    
    try:
        query = build_equity_query(filters)
        print(f"Query building test: PASS - Built query successfully")
        print(f"Query type: {type(query)}")
    except Exception as e:
        print(f"Query building test: FAIL - {e}")

def test_predefined_screens():
    """Test predefined screen configurations"""
    print("\nTesting predefined screens...")
    
    for screen_name, screen_config in PREDEFINED_SCREENS.items():
        print(f"Screen: {screen_name}")
        print(f"  Description: {screen_config['description']}")
        print(f"  Conditions: {len(screen_config['query_conditions'])} filters")
        
        # Validate the conditions
        is_valid, error = validate_screening_filters(screen_config['query_conditions'])
        print(f"  Validation: {'PASS' if is_valid else 'FAIL'} - {error or 'Valid'}")

def test_basic_screening():
    """Test basic screening functionality"""
    print("\nTesting basic screening (this may take a moment)...")
    
    try:
        # Test with a simple filter
        filters = [('gt', ['intradaymarketcap', 10000000000])]  # Market cap > $10B
        
        results = advanced_screen_stocks(
            filters=filters,
            count=10,  # Just get 10 results for testing
            sort_field='intradaymarketcap',
            sort_asc=False
        )
        
        if results.empty:
            print("Basic screening test: FAIL - No results returned")
        else:
            print(f"Basic screening test: PASS - Got {len(results)} results")
            print(f"Columns: {list(results.columns)}")
            
            # Check if we have expected columns
            expected_cols = ['Symbol', 'Company', 'Market Cap (Billion $)']
            found_cols = [col for col in expected_cols if col in results.columns]
            print(f"Expected columns found: {len(found_cols)}/{len(expected_cols)}")
            
    except Exception as e:
        print(f"Basic screening test: FAIL - {e}")

def test_predefined_screen_execution():
    """Test executing a predefined screen"""
    print("\nTesting predefined screen execution...")
    
    try:
        results = advanced_screen_stocks(
            predefined_screen='Large Cap Value',
            count=5  # Just get 5 results
        )
        
        if results.empty:
            print("Predefined screen test: FAIL - No results returned")
        else:
            print(f"Predefined screen test: PASS - Got {len(results)} results")
            
    except Exception as e:
        print(f"Predefined screen test: FAIL - {e}")

def main():
    """Run all tests"""
    print("=" * 60)
    print("ADVANCED STOCK SCREENING SYSTEM TEST")
    print("=" * 60)
    
    test_field_validation()
    test_query_building() 
    test_predefined_screens()
    test_basic_screening()
    test_predefined_screen_execution()
    
    print("\n" + "=" * 60)
    print("Test completed! Check results above for any failures.")
    print("=" * 60)

if __name__ == "__main__":
    main()