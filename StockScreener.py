import yfinance as yf
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import ta
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class ScreenerConfig:
    """Configuration for stock screening"""
    min_price: float = 5.0
    max_price: float = 1000.0
    min_volume: int = 500000
    min_market_cap: float = 100_000_000  # 100M minimum
    indicator_weights: Dict[str, float] = None

    def __post_init__(self):
        if self.indicator_weights is None:
            self.indicator_weights = {
                'trend': 0.3,
                'momentum': 0.3,
                'volume': 0.2,
                'volatility': 0.2
            }

class StockScreener:
    def __init__(self):
        self.all_stocks = self._get_tradable_stocks()
        self.filter_presets = {
            'High Volume': {
                'min_volume': 1000000,
                'min_price': 10,
                'market_cap_min': 1000000000
            },
            'Most Active': {
                'min_volume': 5000000,
                'min_price': 5
            },
            'Large Cap Only': {
                'market_cap_min': 10000000000,
                'min_volume': 500000
            },
            'Penny Stocks': {
                'max_price': 5,
                'min_volume': 100000,
                'market_cap_min': 50000000
            },
            'Volatile Stocks': {
                'min_volatility': 0.03,
                'min_volume': 500000
            }
        }

    def _get_tradable_stocks(self):
        """Get list of default tradable stocks"""
        default_stocks = {
            'AAPL', 'MSFT', 'GOOGL', 'META', 'NVDA', 'AMD', 'INTC', 'CSCO',
            'TSLA', 'F', 'GM', 'TM', 'RIVN', 'LCID', 'NIO',
            'JPM', 'BAC', 'GS', 'MS', 'V', 'MA', 'PYPL',
            'AMZN', 'WMT', 'TGT', 'COST', 'HD', 'SHOP',
            'NFLX', 'DIS', 'T', 'VZ', 'TMUS', 'CMCSA',
            'XOM', 'CVX', 'COP', 'BP', 'SHEL',
            'SPY', 'QQQ', 'IWM', 'DIA'
        }
        return list(default_stocks)

    def quick_screen(self, preset: str, limit: int = 50) -> List[Dict]:
        """Quick screen based on preset filters"""
        filters = self.filter_presets[preset]
        config = ScreenerConfig(
            min_price=filters.get('min_price', 5.0),
            max_price=filters.get('max_price', 1000.0),
            min_volume=filters.get('min_volume', 500000),
            min_market_cap=filters.get('market_cap_min', 100_000_000)
        )

        return self.screen_stocks(config)[:limit]

    def screen_stocks(self, config: ScreenerConfig) -> List[Dict]:
        """Screen stocks based on configuration"""
        opportunities = []
        for symbol in self.all_stocks:
            try:
                result = self._analyze_stock(symbol, config)
                if result:
                    opportunities.append(result)
            except Exception as e:
                print(f"Error screening {symbol}: {str(e)}")
                continue

        return sorted(opportunities, key=lambda x: x['score'], reverse=True)

    def _analyze_stock(self, symbol: str, config: ScreenerConfig) -> Optional[Dict]:
        """Analyze a single stock"""
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period='3mo')

            if len(hist) < 50:
                return None

            current_price = hist['Close'].iloc[-1]
            avg_volume = hist['Volume'].mean()

            # Basic filters
            if (current_price < config.min_price or
                    current_price > config.max_price or
                    avg_volume < config.min_volume):
                return None

            # Calculate indicators
            hist['RSI'] = ta.momentum.RSIIndicator(hist['Close']).rsi()
            hist['MACD'] = ta.trend.MACD(hist['Close']).macd_diff()
            hist['ATR'] = ta.volatility.AverageTrueRange(hist['High'], hist['Low'], hist['Close']).average_true_range()

            latest = hist.iloc[-1]

            # Calculate score
            score = self._calculate_score(hist)
            recommendation = self._get_recommendation(score)

            return {
                'symbol': symbol,
                'price': current_price,
                'score': score,
                'momentum': (current_price / hist['Close'].iloc[-5] - 1) * 100,
                'volume_trend': 1 if avg_volume > hist['Volume'].mean() else -1,
                'rsi': latest['RSI'],
                'recommendation': recommendation
            }

        except Exception as e:
            print(f"Error analyzing {symbol}: {str(e)}")
            return None

    def _calculate_score(self, hist: pd.DataFrame) -> float:
        """Calculate opportunity score"""
        score = 50  # Base score
        latest = hist.iloc[-1]

        # RSI Component
        rsi = latest['RSI']
        if rsi < 30:  # Oversold
            score += 20
        elif rsi > 70:  # Overbought
            score -= 20

        # Trend Component
        if hist['Close'].iloc[-1] > hist['Close'].mean():
            score += 10

        # Volume Component
        if hist['Volume'].iloc[-1] > hist['Volume'].mean():
            score += 10

        return min(max(score, 0), 100)

    def _get_recommendation(self, score: float) -> str:
        """Generate trading recommendation based on score"""
        if score >= 80:
            return 'STRONG BUY'
        elif score >= 60:
            return 'BUY'
        elif score <= 20:
            return 'STRONG SELL'
        elif score <= 40:
            return 'SELL'
        else:
            return 'HOLD'