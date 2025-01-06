class PatternDetector:
    def __init__(self, data):
        self.data = data

    def get_all_signals(self):
        """Combines all relevant signals into one actionable dictionary"""
        signals = {
            'ma_signals': self.ma_crossover(),
            'momentum': self.calculate_momentum(),
            'trend_strength': self.calculate_trend_strength()
        }
        return signals

    def ma_crossover(self):
        """Simplified moving average crossover detection"""
        signals = []
        prev_row = None

        for index, row in self.data.iterrows():
            if prev_row is not None:
                if prev_row['20_avg'] < prev_row['50_avg'] and row['20_avg'] > row['50_avg']:
                    signals.append({
                        'date': index,
                        'type': 'BUY',
                        'strength': 'Strong',
                        'reason': 'Bullish MA Crossover'
                    })
                elif prev_row['20_avg'] > prev_row['50_avg'] and row['20_avg'] < row['50_avg']:
                    signals.append({
                        'date': index,
                        'type': 'SELL',
                        'strength': 'Strong',
                        'reason': 'Bearish MA Crossover'
                    })
            prev_row = row
        return signals

    def calculate_momentum(self):
        """Calculate price momentum"""
        return (self.data['Close'].pct_change(5) * 100).iloc[-1]  # 5-day momentum

    def calculate_trend_strength(self):
        """Calculate trend strength using moving averages"""
        last_price = self.data['Close'].iloc[-1]
        ma_20 = self.data['20_avg'].iloc[-1]
        ma_50 = self.data['50_avg'].iloc[-1]

        if last_price > ma_20 > ma_50:
            return ('Bullish', 'Strong')
        elif last_price > ma_20 and ma_20 < ma_50:
            return ('Bullish', 'Weak')
        elif last_price < ma_20 < ma_50:
            return ('Bearish', 'Strong')
        else:
            return ('Bearish', 'Weak')