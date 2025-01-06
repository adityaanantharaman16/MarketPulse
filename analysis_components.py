from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
from typing import Dict, List, Optional


class AnalysisComponent(ABC):
    @abstractmethod
    def analyze(self, data: pd.DataFrame) -> Dict:
        pass

class VolumeAnalyzer(AnalysisComponent):
    def analyze(self, data: pd.DataFrame) -> Dict:
        analysis = {}

        data['volume_ma'] = data['Volume'].rolling(window=20).mean()

        data['vpt'] = (data['Close'] - data['Close'].shift(1)) / \
                      data['Close'].shift(1) * data['Volume']

        data['vpt'] = data['vpt'].cumsum()

        analysis['high_volume_days'] = self.detect_high_volume_days(data)
        analysis['volume_price_divergence'] = self.detect_volume_price_divergence(data)

        return analysis

    def detect_high_volume_days(self, data: pd.DataFrame) -> List[str]:
        volume_mean = data['Volume'].mean()
        volume_std = data['Volume'].std()
        high_volume_days = data[data['Volume'] > volume_mean + 2 * volume_std].index
        return high_volume_days.tolist()

    def detect_volume_price_divergence(self, data: pd.DataFrame) -> List[Dict]:
        divergences = []

        price_trend = data['Close'].rolling(window=5).mean().diff()
        volume_trend = data['Volume'].rolling(window=5).mean().diff()

        for i in range(len(data) - 1):
            if price_trend.iloc[i] > 0 and volume_trend.iloc[i] < 0:
                divergences.append({
                    'date': data.index[i],
                    'type': 'bearish',
                    'price': data['Close'].iloc[i],
                    'volume': data['Volume'].iloc[i]
                })
            elif price_trend.iloc[i] < 0 and volume_trend.iloc[i] > 0:
                divergences.append({
                    'date': data.index[i],
                    'type': 'bullish',
                    'price': data['Close'].iloc[i],
                    'volume': data['Volume'].iloc[i]
                })
        return divergences


class TechnicalAnalyzer(AnalysisComponent):
    def analyze(self, data: pd.DataFrame) -> Dict:
        analysis = {}

        analysis['rsi'] = self.calculate_rsi(data)

        analysis['bollinger_bands'] = self.calculate_bollinger_bands(data)

        analysis['macd'] = self.calculate_macd(data)

        return analysis

    def calculate_rsi(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def calculate_bollinger_bands(self, data: pd.DataFrame, period: int = 20) -> Dict:
        sma = data['Close'].rolling(window=period).mean()
        std = data['Close'].rolling(window=period).std()
        return {
            'upper': sma + (std * 2),
            'middle': sma,
            'lower': sma - (std * 2)
        }

    def calculate_macd(self, data: pd.DataFrame) -> Dict:
        exp1 = data['Close'].ewm(span=12, adjust=False).mean()
        exp2 = data['Close'].ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()
        return {
            'macd': macd,
            'signal': signal,
            'histogram': macd - signal
        }


class RiskAnalyzer(AnalysisComponent):
    def analyze(self, data: pd.DataFrame) -> Dict:
        analysis = {}

        analysis['volatility'] = self.calculate_volatility(data)

        analysis['var_95'] = self.calculate_var(data, confidence=0.95)
        analysis['var_99'] = self.calculate_var(data, confidence=0.99)

        analysis['max_drawdown'] = self.calculate_max_drawdown(data)

        return analysis

    def calculate_volatility(self, data: pd.DataFrame, window: int = 20) -> float:
        returns = data['Close'].pct_change()
        return returns.std() * np.sqrt(252)

    def calculate_var(self, data: pd.DataFrame, confidence: float) -> float:
        returns = data['Close'].pct_change().dropna()
        return np.percentile(returns, (1 - confidence) * 100)

    def calculate_max_drawdown(self, data: pd.DataFrame) -> float:
        rolling_max = data['Close'].expanding().max()
        drawdowns = data['Close'] / rolling_max - 1
        return drawdowns.min()
