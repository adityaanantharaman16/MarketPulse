from PatternDetector import PatternDetector


class MarketAnalyzer:
    def __init__(self, symbol, start_date, end_date, interval):
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.interval = interval
        self.data = None

    def get_data(self):
        import yfinance as yf

        self.data = yf.download(self.symbol, start=self.start_date, end=self.end_date, interval=self.interval)
        print(f"Data for {self.symbol} from {self.start_date} to {self.end_date}")
        return self.data

    def moving_averages(self):
        import pandas as pd

        # Checks if data is obtained
        if self.data is None:
            raise ValueError('No data available. Use get_data() first.')

        # Calculates moving averages in short time frames(20 days and 50 days).
        self.data['20_avg'] = self.data['Close'].rolling(window=20).mean()
        self.data['50_avg'] = self.data['Close'].rolling(window=50).mean()
        print('Data for 20-day and 50-day moving averages.')
        return self.data

    def plot_data(self, comparison_data=None, comparison_symbol=None):
        import matplotlib.pyplot as plt

        # Checks if moving averages are calculated
        if '20_avg' not in self.data.columns or '50_avg' not in self.data.columns:
            raise ValueError('Moving averages not calculated. Use moving_averages() first.')

        fig, ax1 = plt.subplots(figsize=(14, 7))

        # Plotting data of primary stock
        ax1.plot(self.data.index, self.data['Close'], label=f'{self.symbol} CLosing Price', color='blue')
        ax1.plot(self.data.index, self.data['20_avg'], label=f'{self.symbol} 20-day Moving Average',
                 color='orange')
        ax1.plot(self.data.index, self.data['50_avg'], label=f'{self.symbol} 50-day Moving Average',
                 color='green')

        ax1.set_xlabel('Date')
        ax1.set_ylabel(f'{self.symbol} Price')
        ax1.tick_params(axis='y')
        ax1.legend(loc='upper left')

        if comparison_data is not None and comparison_symbol is not None:
            # Creates second axis y for the comparison stock
            ax2 = ax1.twinx()
            ax2.plot(comparison_data.index, comparison_data['Close'], label=f'{comparison_symbol} Closing Price',
                     color='purple')
            ax2.plot(comparison_data.index, comparison_data['20_avg'],
                     label=f'{comparison_symbol} 20-day Moving Average',
                     color='red')
            ax2.plot(comparison_data.index, comparison_data['50_avg'],
                     label=f'{comparison_symbol} 50-day Moving Average',
                     color='brown')

            ax2.set_ylabel(f'{comparison_symbol} Price')
            ax2.tick_params(axis='y')
            ax2.legend(loc='upper right')

            plt.title(f'{self.symbol} vs {comparison_symbol} Stock Price with Moving Averages')
        else:
            plt.title(f'{self.symbol} Stock Price with Moving Averages')

        plt.show()
        print('Stock data plotted with moving averages.')


if __name__ == "__main__":

    # Creates MarketAnalyzer instance
    analyzer = MarketAnalyzer(symbol='AAPL', start_date='2020-01-01', end_date='2024-08-13', interval='1d')

    # Gets historical data
    analyzer.get_data()

    # Calculates moving averages
    analyzer.moving_averages()

    # Same done for comparison data
    comp_analyzer = MarketAnalyzer(symbol='AMZN', start_date='2020-01-01', end_date='2024-08-13', interval='1d')
    comp_analyzer.get_data()
    comp_analyzer.moving_averages()

    # Creates PatternDetector instance
    detector = PatternDetector(analyzer.data, comparison_data=comp_analyzer.data)

    # Detection for SMT Divergence
    print("\n--- SMT Divergence Signals ---")
    smt_signals = detector.smt_divergence()
    for signal in smt_signals:
        print(f'Date: {signal[0]}, Signal: {signal[1]}, {analyzer.symbol} Close: '
              f'{analyzer.data["Close"].loc[signal[0]]}, {comp_analyzer.symbol} Close: '
              f'{comp_analyzer.data["Close"].loc[signal[0]]}')

    # Detection for Inverse Fair Value Gap
    print("\n--- Inverse Fair Value Gap Signals ---")
    fvg_signals = detector.inverse_fvg()
    for signal in fvg_signals:
        print(
            f'Date: {signal[0]}, Signal: {signal[1]}, {analyzer.symbol} Close: {analyzer.data["Close"].loc[signal[0]]}')

    # Detection for Moving Average Crossover
    print("\n--- Moving Average Crossover Signals ---")
    ma_signals = detector.ma_crossover()
    for signal in ma_signals:
        print(
            f'Date: {signal[0]}, Signal: {signal[1]}, {analyzer.symbol} Close: {analyzer.data["Close"].loc[signal[0]]}')

    # Plot
    analyzer.plot_data()
