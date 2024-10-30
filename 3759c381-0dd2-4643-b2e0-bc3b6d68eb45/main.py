from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import RSI, MACD
from surmount.logging import log
from surmount.data import CboeVolatilityIndexVix

class TradingStrategy(Strategy):
    def __init__(self):
        self.ticker = "SPY"  # Example ticker, choose based on preference/risk appetite
        self.data_list = [CboeVolatilityIndexVix()]

    @property
    def interval(self):
        return "1day"  # Daily intervals for the analysis

    @property
    def assets(self):
        return [self.ticker]

    @property
    def data(self):
        return self.data_list

    def run(self, data):
        # Initialize allocation to zero
        allocation_dict = {self.ticker: 0}

        # Ensure data for both indicators is available
        if not data or "ohlcv" not in data or self.ticker not in data["ohlcv"]:
            return TargetAllocation(allocation_dict)
        
        # VIX data to gauge market sentiment
        vix_data = data[("cboe_volatility_index_vix",)]

        # Checking the latest VIX value to understand current market volatility
        # VIX above 30 is generally considered as high volatility
        if vix_data[-1]['value'] > 30:
            # High market volatility - consider trading

            # Technical Indicator: RSI
            rsi_values = RSI(self.ticker, data["ohlcv"], length=14)

            # Technical Indicator: MACD
            macd_values = MACD(self.ticker, data["ohlcv"], fast=12, slow=26)

            # Simplified trading signal based on RSI and MACD
            if rsi_values[-1] < 30 and macd_values["MACD"][-1] > macd_values["signal"][-1]:
                # Bullish signals: Low RSI and MACD crosses above signal line
                log("Going long due to low RSI and bullish MACD")
                allocation_dict[self.ticker] = 1  # Full allocation
            elif rsi_values[-1] > 70 and macd_values["MACD"][-1] < macd_values["signal"][-1]:
                # Bearish signals but we only take long positions in this strategy, hence no action
                log("Bearish signals observed, staying out of the market")
                allocation_dict[self.ticker] = 0  # No allocation
        else:
            # Low market volatility - lesser trading opportunity for a risky strategy
            log("Market volatility low, holding off trades")

        return TargetAllocation(allocation_dict)