from typing import Dict, List
import pandas as pd
import numpy as np


class TradeAdvisor:
    def __init__(self, risk_tolerance: str = 'moderate'):
        self.risk_tolerance = risk_tolerance
        self.position_sizes = {
            'conservative': 0.02,
            'moderate': 0.05,
            'aggressive': 0.10
        }

    def analyze_trading_opportunity(self, analysis_results: Dict,
                                    current_price: float,
                                    portfolio_value: float = 10000) -> Dict:
        rsi = analysis_results['technical']['rsi'].iloc[-1]

        volatility = analysis_results['risk']['volatility']
        var_95 = analysis_results['risk']['var_95']

        max_position = portfolio_value * self.position_sizes[self.risk_tolerance]

        stop_loss = current_price * (1 + var_95)
        target_price = current_price + (current_price - stop_loss) * 2

        signal = self.generate_signal(rsi, analysis_results)

        recommended_shares = int(max_position / current_price)

        return {
            'action': signal['action'],
            'confidence': signal['confidence'],
            'reasoning': signal['reasoning'],
            'stop_loss': round(stop_loss, 2),
            'target_price': round(target_price, 2),
            'recommended_shares': recommended_shares,
            'max_position_value': round(max_position, 2),
            'risk_per_share': round(current_price - stop_loss, 2),
            'potential_profit_per_share': round(target_price - current_price, 2),
            'alerts': self.generate_alerts(analysis_results)
        }

    def generate_signal(self, rsi: float, analysis_results: Dict) -> Dict:
        confidence = 0
        reasons = []

        if rsi < 30:
            confidence += 2
            reasons.append("RSI indicates oversold condition.")
        elif rsi > 70:
            confidence -= 2
            reasons.append("RSI indicates overbought condition")

            if 'moving_average_signal' in analysis_results.get('technical', {}):
                if analysis_results['technical']['moving_average_signal'] == 'bullish':
                    confidence += 1
                    reasons.append("Moving averages show bullish trend")
                elif analysis_results['technical']['moving_average_signal'] == 'bearish':
                    confidence -= 1
                    reasons.append("Moving averages show bearish trend")

            if confidence >= 2:
                action = "BUY"
            elif confidence <= -2:
                action = "SELL"
            else:
                action = "HOLD"

            confidence_pct = min(abs(confidence) * 25, 100)

            return {
                'action': action,
                'confidence': confidence_pct,
                'reasoning': reasons
            }

    def generate_alerts(self, analysis_results: Dict) -> List[str]:
        alerts = []

        if analysis_results['risk']['volatility'] > 0.4:
            alerts.append("⚠️ High volatility - consider smaller position size")

        rsi = analysis_results['technical']['rsi'].iloc[-1]
        if rsi < 20:
            alerts.append("💡 Extremely oversold - strong buy signal but high risk")
        elif rsi > 80:
            alerts.append("💡 Extremely overbought - consider taking profits")

        if 'volume' in analysis_results:
            if 'high_volume_days' in analysis_results['volume']:
                if analysis_results['volume']['high_volume_days']:
                    alerts.append("📈 High volume detected - increased signal strength")

        return alerts

    def get_holding_advice(self,
                           current_price: float,
                           entry_price: float,
                           stop_loss: float,
                           target_price: float) -> str:
        profit_loss_pct = (current_price - entry_price) / entry_price * 100

        if current_price <= stop_loss:
            return (f"⚠️ SELL: Stop loss ({stop_loss:.2f}) has been hit."
                    f" Current loss: {profit_loss_pct:.1f}%")

        if current_price >= target_price:
            return (f"🎯 Consider taking profits. Target price reached."
                    f" Current profit: {profit_loss_pct:.1f}%")

        if profit_loss_pct > 0:
            return f"✅ Hold position. Currently profitable: {profit_loss_pct:.1f}%"
        else:
            return f"⚠️ Hold position but monitor closely. Current loss: {profit_loss_pct:.1f}%"


    def get_trade_advice(self, portfolio_value: float = 10000):
        advisor = TradeAdvisor(risk_tolerance='moderate')
        current_price = self.data['Close'].iloc[-1]

        advice = advisor.analyze_trading_opportunity(
            self.analysis_results,
            current_price,
            portfolio_value
        )

        return advice
