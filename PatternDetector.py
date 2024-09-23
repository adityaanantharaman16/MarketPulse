class PatternDetector:
    def __init__(self, data, comparison_data=None):
        self.data = data
        self.comparison_data = comparison_data

    def smt_divergence(self):
        if self.comparison_data is None:
            print('There is no comparison data for SMT divergence detection.')
            return[]

        signals = []

        for i in range(1, len(self.data)):
            if self.data['Close'].iloc[i] > self.data['Close'].iloc[i-1] and \
                self.comparison_data['Close'].iloc[i] < self.comparison_data['Close'].iloc[i-1]:
                signals.append((self.data.index[i], 'Bullish SMT Divergence.'))

            elif self.data['Close'].iloc[i] < self.data['Close'].iloc[i-1] and \
                self.comparison_data['Close'].iloc[i] > self.comparison_data['Close'].iloc[i-1]:
                signals.append((self.data.index[i], 'Bearish SMT Divergence.'))

        return signals

    def inverse_fvg(self):
        signals = []

        for i in range(2, len(self.data)):
            if self.data['Low'].iloc[i] > self.data['High'].iloc[i-2]:
                signals.append((self.data.index[i], 'Inverse FVG - Bearish Gap'))

            elif self.data['High'].iloc[i] < self.data['Low'].iloc[i-2]:
                signals.append((self.data.index[i], 'Inverse FVG - Bullish Gap'))

        return signals

    def ma_crossover(self):
        signals = []
        prev_row = None

        for index, row in self.data.iterrows():
            if prev_row is not None:
                if prev_row['20_avg'] < prev_row['50_avg'] and row['20_avg'] > row['50_avg']:
                    signals.append((index, 'Bullish Crossover'))
                elif prev_row['20_avg'] > prev_row['50_avg'] and row['20_avg'] < row['50_avg']:
                    signals.append((index, 'Bearish Crossover'))
            prev_row = row

        return signals
