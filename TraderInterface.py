import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from StockScreener import StockScreener

class BeginnerTraderInterface:
    def __init__(self):
        st.set_page_config(page_title="MarketPulse - Beginner Day Trading", layout="wide")
        self.initialize_session_state()

    def initialize_session_state(self):
        if 'account_size' not in st.session_state:
            st.session_state.account_size = 10000.0
        if 'risk_per_trade' not in st.session_state:
            st.session_state.risk_per_trade = 1.0

    def run(self):
        self.show_sidebar()
        st.title("🚀 MarketPulse Trading Assistant")
        st.markdown("### Your Guide to Smart Trading Decisions")

        tab1, tab2 = st.tabs(["Single Stock Analysis", "Find Opportunities"])

        with tab1:
            self.show_single_stock_analysis()

        with tab2:
            self.show_opportunity_finder()

    def show_single_stock_analysis(self):
        with st.expander("New to Trading? Start Here!", expanded=True):
            self.show_quick_start_guide()

        col1, col2 = st.columns([2, 1])

        with col1:
            symbol = st.text_input("Enter Stock Symbol (e.g., AAPL, MSFT)", "AAPL").upper()
            if st.button("Analyze Stock"):
                with st.spinner("Analyzing stock..."):
                    self.analyze_stock(symbol)

        with col2:
            self.show_risk_calculator()

    def show_opportunity_finder(self):
        st.markdown("### Find Trading Opportunities")

        col1, col2 = st.columns(2)
        with col1:
            filter_type = st.selectbox(
                "Select Screening Type",
                ["High Volume", "Most Active", "Large Cap Only", "Penny Stocks", "Volatile Stocks"]
            )

        with col2:
            num_results = st.slider("Number of Results", 5, 50, 20)

        if st.button("🔍 Find Trading Opportunities"):
            with st.spinner("Scanning market for opportunities..."):
                try:
                    screener = StockScreener()
                    opportunities = screener.quick_screen(filter_type, limit=num_results)

                    if opportunities:
                        st.markdown("### Top Trading Opportunities")
                        for opp in opportunities:
                            self.display_opportunity(opp)
                    else:
                        st.warning("No opportunities found matching the criteria.")
                except Exception as e:
                    st.error(f"Error finding opportunities: {str(e)}")

    def display_opportunity(self, opp):
        """Display a single trading opportunity"""
        color = {
            'STRONG BUY': 'green',
            'BUY': 'lightgreen',
            'HOLD': 'orange',
            'SELL': 'pink',
            'STRONG SELL': 'red'
        }[opp['recommendation']]

        st.markdown(f"""
        **{opp['symbol']}** (Score: {opp['score']:.0f}/100)
        - Price: ${opp['price']:.2f}
        - RSI: {opp['rsi']:.1f}
        - Momentum: {opp['momentum']:.1f}%
        - Recommendation: <span style='color: {color}'>{opp['recommendation']}</span>
        """, unsafe_allow_html=True)

        if opp['recommendation'] in ['STRONG BUY', 'BUY']:
            position_size = self.calculate_position_size(opp['price'])
            st.markdown(f"""
            **Suggested Trade Setup:**
            - Position Size: {position_size['shares']} shares (${position_size['total']:.2f})
            - Stop Loss: ${position_size['stop_loss']:.2f}
            - Target: ${position_size['target']:.2f}
            """)

    def show_sidebar(self):
        with st.sidebar:
            st.header("📊 Account Settings")
            st.session_state.account_size = st.number_input(
                "Account Size ($)",
                min_value=100.0,
                max_value=1000000.0,
                value=st.session_state.account_size
            )

            st.session_state.risk_per_trade = st.slider(
                "Risk Per Trade (%)",
                min_value=0.5,
                max_value=2.0,
                value=st.session_state.risk_per_trade,
                step=0.1
            )

            st.markdown("---")
            st.header("📚 Learning Resources")

            with st.expander("Understanding Indicators"):
                st.markdown("""
                - **RSI (Relative Strength Index)**
                  - Below 30: Oversold (potential buy)
                  - Above 70: Overbought (potential sell)
                
                - **Momentum**
                  - Shows price change speed
                  - Positive: Upward trend
                  - Negative: Downward trend
                
                - **Volume**
                  - High volume confirms trends
                  - Low volume suggests weak moves
                """)

            with st.expander("Risk Management"):
                st.markdown("""
                1. Never risk more than 1-2% per trade
                2. Always set stop losses
                3. Use position sizing calculator
                4. Have a clear exit strategy
                5. Keep a trading journal
                """)

    def show_quick_start_guide(self):
        st.markdown("""
        #### 🎯 Trading Checklist:
        1. **Choose Your Market**
           - Use the stock screener to find opportunities
           - Focus on liquid stocks with good volume
        
        2. **Analyze Before Trading**
           - Check RSI for overbought/oversold conditions
           - Confirm trends with volume
           - Look for clear entry points
        
        3. **Manage Your Risk**
           - Calculate position size using the calculator
           - Set stop losses before entering trades
           - Never risk more than your preset limit
        
        4. **Have a Clear Plan**
           - Know your entry price
           - Set your stop loss
           - Define your target
           - Stick to your plan!
        
        Remember: Focus on learning and consistency, not just profits!
        """)

    def show_risk_calculator(self):
        st.markdown("### 💰 Risk Calculator")

        entry_price = st.number_input("Entry Price ($)", min_value=0.01, value=100.0)

        position = self.calculate_position_size(entry_price)

        st.markdown("#### Trade Summary")
        st.markdown(f"""
        - Risk Amount: ${position['risk_amount']:.2f}
        - Shares: {position['shares']}
        - Total Position: ${position['total']:.2f}
        - Stop Loss: ${position['stop_loss']:.2f}
        - Target: ${position['target']:.2f}
        """)

        if position['total'] > st.session_state.account_size:
            st.warning("⚠️ Warning: Position size exceeds account size!")

    def calculate_position_size(self, entry_price: float) -> dict:
        """Calculate position size and related metrics"""
        risk_amount = st.session_state.account_size * (st.session_state.risk_per_trade / 100)
        stop_loss = entry_price * 0.95  # 5% stop loss
        risk_per_share = entry_price - stop_loss
        shares = int(risk_amount / risk_per_share)
        total = shares * entry_price
        target = entry_price * 1.15  # 15% target

        return {
            'risk_amount': risk_amount,
            'shares': shares,
            'total': total,
            'stop_loss': stop_loss,
            'target': target
        }

    def analyze_stock(self, symbol):
        try:
            screener = StockScreener()
            result = screener._analyze_stock(symbol, screener.filter_presets['High Volume'])

            if result:
                st.markdown("### 📈 Analysis Results")
                self.display_opportunity(result)

                # Show additional analysis
                st.markdown("### 📊 Technical Analysis")
                col1, col2 = st.columns(2)

                with col1:
                    st.metric(
                        "Trend Strength",
                        "Bullish" if result['momentum'] > 0 else "Bearish",
                        f"{result['momentum']:.1f}%"
                    )

                with col2:
                    rsi_status = "Oversold" if result['rsi'] < 30 else "Overbought" if result['rsi'] > 70 else "Neutral"
                    st.metric("RSI Status", rsi_status, f"{result['rsi']:.1f}")

            else:
                st.error(f"Could not analyze {symbol}. Please check the symbol and try again.")

        except Exception as e:
            st.error(f"Error analyzing {symbol}: {str(e)}")

if __name__ == "__main__":
    interface = BeginnerTraderInterface()
    interface.run()