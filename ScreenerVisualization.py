import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

class ScreenerVisualization:
    @staticmethod
    def plot_opportunities(opportunities: list):
        """Create interactive scatter plot of opportunities"""
        df = pd.DataFrame(opportunities)

        # Create scatter plot
        fig = px.scatter(df,
                         x='market_cap',
                         y='score',
                         color='recommendation',
                         size='avg_volume',
                         hover_data=['symbol', 'price'],
                         title='Trading Opportunities Overview',
                         labels={'market_cap': 'Market Cap ($)',
                                 'score': 'Opportunity Score',
                                 'recommendation': 'Recommendation'},
                         color_discrete_map={
                             'STRONG BUY': 'green',
                             'BUY': 'lightgreen',
                             'HOLD': 'gray',
                             'SELL': 'pink',
                             'STRONG SELL': 'red'
                         })

        fig.update_layout(
            xaxis_type='log',
            height=600,
            width=800
        )

        return fig

    @staticmethod
    def create_indicator_heatmap(opportunities: list):
        """Create heatmap of technical indicators"""
        # Extract indicator data
        indicator_data = []
        for opp in opportunities[:20]:  # Top 20 opportunities
            indicators = {
                'symbol': opp['symbol'],
                'RSI': opp['indicators']['rsi'],
                'MACD': opp['indicators']['macd'],
                'ADX': opp['indicators']['adx'],
                'Volume Trend': opp['signals']['volume']['volume_trend']
            }
            indicator_data.append(indicators)

        df = pd.DataFrame(indicator_data)
        df.set_index('symbol', inplace=True)

        # Create heatmap
        fig = go.Figure(data=go.Heatmap(
            z=df.values,
            x=df.columns,
            y=df.index,
            colorscale='RdYlGn'
        ))

        fig.update_layout(
            title='Technical Indicator Heatmap',
            height=500,
            width=800
        )

        return fig

    @staticmethod
    def display_top_opportunities(opportunities: list, n: int = 10):
        """Display detailed cards for top opportunities"""
        for i, opp in enumerate(opportunities[:n]):
            with st.expander(f"#{i+1} {opp['symbol']} (Score: {opp['score']:.0f}/100)"):
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("### Key Metrics")
                    st.markdown(f"""
                    - Price: ${opp['price']:.2f}
                    - Market Cap: ${opp['market_cap']:,.0f}
                    - Volume: {opp['avg_volume']:,.0f}
                    """)

                with col2:
                    st.markdown("### Technical Indicators")
                    st.markdown(f"""
                    - RSI: {opp['indicators']['rsi']:.1f}
                    - MACD: {opp['indicators']['macd']:.3f}
                    - ADX: {opp['indicators']['adx']:.1f}
                    """)

                # Add recommendation with color
                rec_color = {
                    'STRONG BUY': 'green',
                    'BUY': 'lightgreen',
                    'HOLD': 'gray',
                    'SELL': 'pink',
                    'STRONG SELL': 'red'
                }[opp['recommendation']]

                st.markdown(f"### Recommendation: "
                            f"<span style='color: {rec_color}'>"
                            f"{opp['recommendation']}</span>",
                            unsafe_allow_html=True)

    @staticmethod
    def plot_score_distribution(opportunities: list):
        """Plot distribution of opportunity scores"""
        scores = [opp['score'] for opp in opportunities]
        fig = px.histogram(scores,
                           nbins=20,
                           title='Distribution of Opportunity Scores',
                           labels={'value': 'Score', 'count': 'Number of Stocks'})

        fig.update_layout(
            showlegend=False,
            height=400,
            width=800
        )

        return fig