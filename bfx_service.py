"""
Contains all API Client sub-classes, which store exchange specific details
and feature the respective exchanges authentication method (sign()).
"""
# Import Built-ins
import logging
import json
import hashlib
import hmac
import base64
from datetime import datetime, timedelta

# Import Homebrew
from bitex.api.REST.api import APIClient

log = logging.getLogger(__name__)


class BitfinexREST(APIClient):
    def __init__(self, key=None, secret=None, api_version='v1',
                 url='https://api.bitfinex.com', timeout=5):
        super(BitfinexREST, self).__init__(url, api_version=api_version,
                                           key=key, secret=secret,
                                           timeout=timeout)

    def sign(self, url, endpoint, endpoint_path, method_verb, *args, **kwargs):
        try:
            req = kwargs['params']
        except KeyError:
            req = {}
        if self.version == 'v1':
            req['request'] = endpoint_path
            req['nonce'] = self.nonce()

            js = json.dumps(req)
            data = base64.standard_b64encode(js.encode('utf8'))
        else:
            data = '/api/' + endpoint_path + self.nonce() + json.dumps(req)
        h = hmac.new(self.secret.encode('utf8'), data, hashlib.sha384)
        signature = h.hexdigest()
        headers = {"X-BFX-APIKEY": self.key,
                   "X-BFX-SIGNATURE": signature,
                   "X-BFX-PAYLOAD": data}
        if self.version == 'v2':
            headers['content-type'] = 'application/json'

        return url, {'headers': headers}

    def get_past_trades(self, crypto, start, end):
        q = {'symbol': crypto, 'timestamp': str(start), 'until': str(end), 'reverse': 0}
        return self.query('POST', 'mytrades', authenticate=True, params=q).json()

    @staticmethod
    def convert_timestamp(date_to_convert, time_to_convert):
        datetime_utc = datetime.combine(date_to_convert, time_to_convert) - timedelta(hours=5)
        return datetime.timestamp(datetime_utc)

    @staticmethod
    def get_summary(result, active_position, crypto):
        buy_list = []
        sell_list = []
        asterisk = ''
        active_dict = {}
        is_active = False
        for x in result:
            if x[3] == 'buy':
                buy_list.append(float(x[0]) * float(x[1]) * -1)
            else:
                sell_list.append(float(x[0]) * float(x[1]))
        fee_total = sum([float(x[0]) * 0.002 for x in result])
        inactive_profit = sum(sell_list) + sum(buy_list) - fee_total
        for x in active_position:
            if x.get('symbol') == crypto:
                active_profit = inactive_profit + float(x['amount']) * float(x['base'])
                asterisk = '*'
                is_active = True
        inactive_roi = inactive_profit / (float(result[0][0]) * float(result[0][1]))
        inactive_roi = str(round(inactive_roi, 4) * 100) + '%'
        inactive_profit = asterisk + ' $' + str(round(inactive_profit, 2))
        if is_active:
            active_roi = active_profit / (float(result[0][0]) * float(result[0][1]))
            active_roi = str(round(active_roi, 4) * 100) + '%'
            active_profit = asterisk + ' $' + str(round(active_profit, 2))
            active_dict = {'profit': active_profit, 'fee total': fee_total, 'ROI': active_roi}
        inactive_dict = {'profit': inactive_profit, 'fee total': fee_total, 'ROI': inactive_roi}
        return active_dict, inactive_dict

    def get_active_positions(self, crypto_pair=None):
        all_active_positions = self.query('POST', 'positions', authenticate=True).json()
        active_positions = []
        if crypto_pair and active_positions:
            for position in all_active_positions:
                if position['symbol'] == crypto_pair:
                    active_positions.append(position)
            return active_positions
        return all_active_positions

    def get_ticker(self, crypto):
        endpoint = 'pubticker/' + crypto
        return self.query('GET', endpoint=endpoint, authenticate=False).json()
