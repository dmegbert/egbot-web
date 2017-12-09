import os
from pymongo import MongoClient


class EgbotDAO(object):
    def __init__(self):
        self.password = os.environ.get('MONGOPW')
        self.user = os.environ.get('MONGOUSER')
        self.connection_string = """mongodb://""" + self.user + """:""" + self.password + """@crypt-shard-00-00-31pwj.mongodb.net:27017,
                                    crypt-shard-00-01-31pwj.mongodb.net:27017,crypt-shard-00-02-31pwj.mongodb.net:27017/test?ssl=true&
                                    replicaSet=crypt-shard-0&authSource=admin"""
        self.client = MongoClient(self.connection_string,
                                  connectTimeoutMS=30000,
                                  socketTimeoutMS=None,
                                  socketKeepAlive=True)
        self.db = self.client['egbot-result']

    def get_collection_names(self):
        return self.client['egbot-result'].collection_names()

    def get_all_trials_by_crypto(self):
        collection_names = self.get_collection_names()
        trials_dict = {crypto: [] for crypto in collection_names}
        for collection in collection_names:
            mongo_collection = self.db[collection]
            for doc in mongo_collection.find({}, {'_id': 0, 'trial start': 1}):
                trials_dict[collection].append(doc['trial start'])
            trials_dict[collection] = list(set(trials_dict[collection]))
        return trials_dict

    def get_order_data_for_trial(self, crypto, trial):
        orders = []
        collection = self.db[crypto]
        for doc in collection.find({"trial start": {"$eq": trial}}):
            slip = (float(doc['avg_execution_price']) - float(doc['price'])) / float(doc['price']) * 100
            slip = round(slip, 4)
            slip = str(slip)
            slip = slip + '%'
            order_dict = {
                'Average Execution Price': doc['avg_execution_price'],
                'Amount': doc['executed_amount'],
                'Time': doc['timestamp'],
                'Type': doc['side'],
                'Price Entered': doc['price'],
                'Slippage': slip
            }
            orders.append(order_dict)
        return orders
