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
import pytz
import math

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
        for x in result:
            if x[3] == 'Buy':
                buy_list.append(float(x[0]) * float(x[1]) * -1)
            else:
                sell_list.append(float(x[0]) * float(x[1]))
        fee_total = sum([float(x[5]) for x in result])
        profit = sum(sell_list) + sum(buy_list) + fee_total
        for x in active_position:
            if x.get('symbol') == crypto:
                profit = profit + float(x['amount']) * float(x['base'])
                asterisk = '*'
        roi = profit / (float(result[0][0]) * float(result[0][1]))
        roi = str(round(roi, 4) * 100) + '%'
        profit = asterisk + ' $' + str(round(profit, 2))
        return {'profit': profit, 'fee total': fee_total, 'ROI': roi}

    def get_active_positions(self):
        return self.query('POST', 'positions', authenticate=True).json()

    def get_ticker(self, crypto):
        endpoint = 'pubticker/' + crypto
        return self.query('GET', endpoint=endpoint, authenticate=False).json()
