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
    FLD_Option_Terms = [
        'symbol',
        'description', 'exchangeName', 'putCall', 'strikePrice', 'expirationDate', 'expirationType',
        'lastTradingDay', 'multiplier', 'settlementType', 'deliverableNote', 'isIndexOption', 'nonStandard', 'mini', 'weekly']
    FLD_Option_Value = [
        'symbol',
        'bid', 'ask', 'last', 'mark', 'bidSize', 'askSize', 'bidAskSize', 'lastSize', 'highPrice', 'lowPrice',
        'openPrice', 'closePrice', 'totalVolume', 'tradeDate', 'tradeTimeInLong', 'quoteTimeInLong', 'netChange',
        'volatility', 'delta', 'gamma', 'theta', 'vega', 'rho', 'openInterest', 'timeValue', 'theoreticalOptionValue',
        'theoreticalVolatility', 'optionDeliverablesList', 'daysToExpiration', 'percentChange', 'markChange',
        'markPercentChange']

    def __init__(self, api_key):
        self._api_key = api_key

    def get_price_history(
            self,
            symbol,
            start_date=None,
            end_date=None,
            period_type=None,
            period=None,
            frequency_type=None,
            frequency=None,
            need_extended_hours_data=False
    ):
        """
        Retrieve historical prices for symbol.

        :param symbol: underlying symbol
        :param period_type: day, month, year or ytd
        :param period: integer, number of periods
              day: 1, 2, 3, 4, 5, 10*
            month: 1*, 2, 3, 6
             year: 1*, 2, 3, 5, 10, 15, 20
              ytd: 1*
        :param frequency_type: minute, daily, weekly, monthly
              day: minute*
            month: daily, weekly*
             year: daily, weekly, monthly*
              ytd: daily, weekly*
        :param frequency: number of frequency units per candle
            minute: 1*, 5, 10, 15, 30
             daily: 1*
            weekly: 1*
            monthly: 1*
        :param start_date: period start date
        :param end_date: period end date
        :param need_extended_hours_data: true of extended hours data is required
        :return: data frame of candles
        """
        params = {'apikey': self._api_key, }

        if start_date:
            params['startDate'] = time_to_millis_since_epoch(start_date)
            params['endDate'] = time_to_millis_since_epoch(end_date or date.today())
        params['periodType'] = period_type
        params['period'] = period
        params['frequencyType'] = frequency_type
        params['frequency'] = frequency
        if not need_extended_hours_data:
            params['needExtendedHoursData'] = 'false'

        response = requests.get(
            url=self.URI_PriceHistory.format(symbol.strip()),
            params=params
        )
        response = response.json()

        if 'error' in response:
            raise RuntimeError(response['error'])
        if response['empty']:
            return pd.DataFrame()
        candles = pd.DataFrame.from_records(response['candles'])
        make_numeric(candles)
        candles['datetime'] = candles['datetime'].apply(millis_since_epoch_to_time)
        return candles.set_index('datetime')

    @staticmethod
    def enrich_options_data(options_map):
        """
        Convert values expressed as time since epoch values to datetime.date,
        include these values as additional columns.

        :param options_map: options chain organized as {expiry => options for each strike]
        :return:
        """
        options = []
        for expiry_date in options_map:
            for strike in options_map[expiry_date]:
                if options_map[expiry_date][strike]:
                    option = options_map[expiry_date][strike][0]
                    options.append(option)
                    option['weekly'] = 'Weekly' in option['description']
                    option['tradeDateTime'] = millis_since_epoch_to_time(option['tradeTimeInLong'])
                    option['quoteDateTime'] = millis_since_epoch_to_time(option['quoteTimeInLong'])
                    option['expirationDate'] = millis_since_epoch_to_time(option['expirationDate'])
                    option['lastTradingDay'] = millis_since_epoch_to_time(option['lastTradingDay'])

        return options

    def get_option_chain(self, symbol, include_quotes=True):
        """
        Retrieve option chain.

        :param symbol: underlying symbol
        :param include_quotes: True => include price data
        :return:  three data frames - (underlying info, option indicative, option values)
        """
        response = requests.get(
            url=self.URI_OptionChain,
            params={
                'apikey': self._api_key,
                'symbol': symbol,
                'includeQuotes': 'TRUE' if include_quotes else 'FALSE',
            }
        )

        if not response.content:
            raise RuntimeError('no content: {0}'.format(symbol))
        content = response.json()
        if content['status'].upper() == 'FAILED':
            raise RuntimeError('failed: {0}'.format(symbol))

        options = pd.DataFrame.from_records(
            Adaptor.enrich_options_data(content['putExpDateMap']) +
            Adaptor.enrich_options_data(content['callExpDateMap'])
        )
        option_terms = options.reindex(columns=Adaptor.FLD_Option_Terms)
        option_value = options.reindex(columns=Adaptor.FLD_Option_Value)
        make_numeric(option_value)

        underlying = pd.Series(content['underlying'])
        underlying['quoteDateTime'] = millis_since_epoch_to_time(underlying['quoteTime'])
        underlying['tradeDateTime'] = millis_since_epoch_to_time(underlying['tradeTime'])

        return pd.DataFrame([underlying]), option_terms, option_value

    def get_fundamentals(self, symbol):
        """
        Get fundamental data for symbol.
        :param symbol: underlying symbol
        :return: data values as pd.Series
        """
        response = requests.get(
            url=self.URI_Fundamentals,
            params={
                'apikey': self._api_key,
                'symbol': symbol,
                'projection': 'fundamental',
            }
        )
        response = response.json()

        if 'error' in response:
            raise RuntimeError(response['error'])

        return pd.Series(response[symbol]['fundamental'])
