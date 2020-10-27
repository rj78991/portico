import requests
from datetime import date
import pandas as pd
from conversions import \
    time_to_millis_since_epoch, \
    millis_since_epoch_to_time, \
    make_numeric


class Adaptor(object):
    URI_PriceHistory = "https://api.tdameritrade.com/v1/marketdata/{0}/pricehistory"
    URI_OptionChain = "https://api.tdameritrade.com/v1/marketdata/chains"
    URI_Fundamentals = "https://api.tdameritrade.com/v1/instruments"
    FLD_PriceHstory = [
        'symbol', 'datetime',
        'open', 'high', 'low', 'close', 'volume']
    FLD_OptionChain_Terms = [
        'symbol',
        'description', 'exchangeName', 'putCall', 'strikePrice', 'expirationDate', 'expirationType',
        'lastTradingDay', 'multiplier', 'settlementType', 'deliverableNote', 'isIndexOption', 'nonStandard', 'mini', 'weekly']
    FLD_OptionChain_Value = [
        'symbol',
        'bid', 'ask', 'last', 'mark', 'bidSize', 'askSize', 'bidAskSize', 'lastSize', 'highPrice', 'lowPrice',
        'openPrice', 'closePrice', 'totalVolume', 'tradeDate', 'tradeTimeInLong', 'quoteTimeInLong', 'netChange',
        'volatility', 'delta', 'gamma', 'theta', 'vega', 'rho', 'openInterest', 'timeValue', 'theoreticalOptionValue',
        'theoreticalVolatility', 'optionDeliverablesList', 'daysToExpiration', 'percentChange', 'markChange',
        'markPercentChange']

    def __init__(self, api_key):
        self._api_key = api_key
