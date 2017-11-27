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
        q = {'symbol': crypto, 'timestamp': str(start), 'until': str(end)}
        return self.query('POST', 'mytrades', authenticate=True, params=q).json()

    @staticmethod
    def convert_timestamp(date_to_convert, time_to_convert):
        datetime_utc = datetime.combine(date_to_convert, time_to_convert) - timedelta(hours=5)
        return datetime.timestamp(datetime_utc)

    def check_open_position(self, crypto):
        pass

    @staticmethod
    def get_summary():
        result = [['1649.1', '0.1', '1511514702.0', 'Buy', 'USD', '-0.32982', 99144887, 5430517432],
                  ['1623.2', '0.1', '1511514331.0', 'Sell', 'USD', '-0.32464', 99139252, 5430391958]]
        buy_list = []
        sell_list = []
        for x in result:
            if x[3] is 'Buy':
                buy_list.append(float(x[0]) * float(x[1]) * -1)
            else:
                sell_list.append(float(x[0]) * float(x[1]))
        fee_total = sum([float(x[5]) for x in result])
        profit = sum(sell_list) + sum(buy_list) + fee_total
        roi = profit / (float(result[0][0]) * float(result[0][1]))
        return roi
