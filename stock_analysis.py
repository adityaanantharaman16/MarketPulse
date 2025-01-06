from MarketAnalyzer import MarketAnalyzer
from datetime import datetime, timedelta
import pytz

def get_latest_market_date():
    """Get the most recent market date, accounting for weekends and current time"""
    est = pytz.timezone('US/Eastern')
    current_time = datetime.now(est)

    # If it's weekend, adjust to last Friday
    while current_time.weekday() > 4:  # 5 is Saturday, 6 is Sunday
        current_time -= timedelta(days=1)

    # Format the date as string
    return current_time.strftime('%Y-%m-%d')

def compare_stocks(symbol1, symbol2, start_date):
    """Compare two stocks and generate trading advice for both"""

    # Get latest market date
    end_date = get_latest_market_date()
    print(f"\nAnalyzing from {start_date} to {end_date}")

    # Analyze first stock
    print(f"\nAnalyzing {symbol1}...")
    analyzer1 = MarketAnalyzer(symbol1, start_date, end_date, '1d')
    analyzer1.get_data()
    results1 = analyzer1.analyze_all()

    # Analyze second stock
    print(f"\nAnalyzing {symbol2}...")
    analyzer2 = MarketAnalyzer(symbol2, start_date, end_date, '1d')
    analyzer2.get_data()
    results2 = analyzer2.analyze_all()

    print(f"\n=== Comparing {symbol1} vs {symbol2} ===")

    # Get trading advice for both stocks
    print(f"\n{symbol1} Analysis:")
    advice1 = analyzer1.get_trade_advice(portfolio_value=10000)

    print(f"\n{symbol2} Analysis:")
    advice2 = analyzer2.get_trade_advice(portfolio_value=10000)

    # Print current prices for verification
    print(f"\nCurrent Prices:")
    print(f"{symbol1}: ${analyzer1.data['Close'].iloc[-1]:.2f}")
    print(f"{symbol2}: ${analyzer2.data['Close'].iloc[-1]:.2f}")

    return analyzer1, analyzer2

if __name__ == "__main__":
    # Calculate dates
    end_date = get_latest_market_date()
    # Start date 6 months ago
    start_date = (datetime.strptime(end_date, '%Y-%m-%d') - timedelta(days=180)).strftime('%Y-%m-%d')

    print(f"Analysis Period: {start_date} to {end_date}")

    # Compare semiconductor stocks
    print("\n=== Semiconductor Comparison ===")
    nvda, amd = compare_stocks('NVDA', 'AMD', start_date)

    # Compare cloud computing stocks
    print("\n=== Cloud Computing Comparison ===")
    amzn, msft = compare_stocks('AMZN', 'MSFT', start_date)

    # Compare EV stocks
    print("\n=== EV Market Comparison ===")
    tsla, f = compare_stocks('TSLA', 'F', start_date)