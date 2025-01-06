from PatternDetector import PatternDetector
from analysis_components import VolumeAnalyzer, TechnicalAnalyzer, RiskAnalyzer
from TradeAdvisor import TradeAdvisor
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import time

class MarketAnalyzer:
    def __init__(self, symbol, start_date, end_date, interval):
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.interval = interval
        self.data = None

        # Initialize analysis components
        self.volume_analyzer = VolumeAnalyzer()
        self.technical_analyzer = TechnicalAnalyzer()
        self.risk_analyzer = RiskAnalyzer()

        # Analysis results storage
        self.analysis_results = {}

    def get_data(self, max_retries=3):
        """Fetches data with retry mechanism and proper error handling"""
        for attempt in range(max_retries):
            try:
                ticker = yf.Ticker(self.symbol)
                self.data = ticker.history(
                    start=self.start_date,
                    end=self.end_date,
                    interval=self.interval
                )

                if self.data.empty:
                    raise ValueError(f"No data retrieved for {self.symbol}")

                print(f"Successfully downloaded data for {self.symbol} from {self.start_date} to {self.end_date}")
                return self.data

            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"Attempt {attempt + 1} failed. Retrying in 2 seconds...")
                    time.sleep(2)
                else:
                    raise Exception(f"Failed to download data for {self.symbol} after {max_retries} attempts: {str(e)}")

    def analyze_all(self):
        """Runs all analysis components"""
        if self.data is None:
            raise ValueError("No data available. Use get_data() first.")

        # Run moving averages (existing functionality)
        self.moving_averages()

        # Run new analysis components
        self.analysis_results['volume'] = self.volume_analyzer.analyze(self.data)
        self.analysis_results['technical'] = self.technical_analyzer.analyze(self.data)
        self.analysis_results['risk'] = self.risk_analyzer.analyze(self.data)

        return self.analysis_results

    def moving_averages(self):
        """Existing moving averages calculation"""
        if self.data is None or self.data.empty:
            raise ValueError('No data available. Use get_data() first.')

        if len(self.data) < 50:
            raise ValueError('Not enough data points for 50-day moving average')

        self.data['20_avg'] = self.data['Close'].rolling(window=20).mean()
        self.data['50_avg'] = self.data['Close'].rolling(window=50).mean()

        print('Successfully calculated 20-day and 50-day moving averages.')
        return self.data

    def get_trading_signals(self):
        """Generates trading signals based on all analysis components"""
        if not self.analysis_results:
            self.analyze_all()

        signals = []

        # Volume-based signals
        for divergence in self.analysis_results['volume']['volume_price_divergence']:
            signals.append({
                'date': divergence['date'],
                'type': f"Volume-Price {divergence['type']} divergence",
                'price': divergence['price']
            })

        # Technical signals (example with RSI)
        rsi = self.analysis_results['technical']['rsi']
        overbought = rsi[rsi > 70].index
        oversold = rsi[rsi < 30].index

        for date in overbought:
            signals.append({
                'date': date,
                'type': 'RSI Overbought',
                'price': self.data.loc[date, 'Close']
            })

        for date in oversold:
            signals.append({
                'date': date,
                'type': 'RSI Oversold',
                'price': self.data.loc[date, 'Close']
            })

        return signals

    def get_trade_advice(self, portfolio_value: float = 10000, risk_tolerance: str = 'moderate'):
        """Get trading advice for amateur investors"""
        if not self.analysis_results:
            self.analyze_all()

        advisor = TradeAdvisor(risk_tolerance=risk_tolerance)
        current_price = self.data['Close'].iloc[-1]

        advice = advisor.analyze_trading_opportunity(
            self.analysis_results,
            current_price,
            portfolio_value
        )

        # Print friendly format
        print("\n=== Trading Advice ===")
        print(f"Current Price: ${current_price:.2f}")
        print(f"\nRecommended Action: {advice['action']}")
        print(f"Confidence Level: {advice['confidence']}%")
        print("\nReasoning:")
        for reason in advice['reasoning']:
            print(f"- {reason}")

        print(f"\nRisk Management:")
        print(f"- Stop Loss: ${advice['stop_loss']}")
        print(f"- Target Price: ${advice['target_price']}")
        print(f"- Recommended Position: {advice['recommended_shares']} shares (${advice['max_position_value']:.2f})")
        print(f"- Risk per Share: ${advice['risk_per_share']}")
        print(f"- Potential Profit per Share: ${advice['potential_profit_per_share']}")

        if advice['alerts']:
            print("\nImportant Alerts:")
            for alert in advice['alerts']:
                print(f"- {alert}")

        return advice

    def plot_data(self, comparison_data=None, comparison_symbol=None, show_volume=True):
        """Enhanced plotting with volume and additional indicators"""
        if self.data is None or self.data.empty:
            raise ValueError('No data available for plotting')

        # Create figure with subplots
        fig = plt.figure(figsize=(15, 10))

        # Price plot
        ax1 = plt.subplot2grid((3, 1), (0, 0), rowspan=2)
        ax1.plot(self.data.index, self.data['Close'], label=f'{self.symbol} Price')
        if '20_avg' in self.data.columns:
            ax1.plot(self.data.index, self.data['20_avg'],
                     label='20-day MA', linestyle='--')
        if '50_avg' in self.data.columns:
            ax1.plot(self.data.index, self.data['50_avg'],
                     label='50-day MA', linestyle='--')

        # Volume plot
        if show_volume:
            ax2 = plt.subplot2grid((3, 1), (2, 0), sharex=ax1)
            ax2.bar(self.data.index, self.data['Volume'], alpha=0.5)
            ax2.set_ylabel('Volume')

        plt.tight_layout()
        plt.show()
        print('Successfully plotted stock data with indicators.')

if __name__ == "__main__":
    try:
        # Set up date range
        start_date = '2020-01-01'
        end_date = datetime.now().strftime('%Y-%m-%d')

        # Create and configure analyzer
        analyzer = MarketAnalyzer('NVDA', start_date, end_date, '1d')
        analyzer.get_data()

        # Run analysis
        results = analyzer.analyze_all()

        # Get trading signals
        signals = analyzer.get_trading_signals()

        # Print some results
        print("\n=== Analysis Results ===")
        print(f"\nVolatility: {results['risk']['volatility']:.2%}")
        print(f"95% VaR: {results['risk']['var_95']:.2%}")
        print(f"Max Drawdown: {results['risk']['max_drawdown']:.2%}")

        print("\n=== Trading Signals ===")
        for signal in signals[-5:]:  # Show last 5 signals
            print(f"Date: {signal['date']}, Type: {signal['type']}, Price: ${signal['price']:.2f}")

        # Plot the data
        analyzer.plot_data(show_volume=True)

        # Get trading advice
        print("\nGenerating Trading Advice for a $10,000 portfolio...")
        analyzer.get_trade_advice(portfolio_value=10000, risk_tolerance='moderate')

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise