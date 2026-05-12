import pymongo as pm
from pymongo import MongoClient

# connect to mongodb project
client = MongoClient('mongodb+srv://nova:2oyIpZLPfJMysdKI@cluster0.gp3j6cm.mongodb.net/?appName=Cluster0')

# return mongodb database
db = client['sample_restaurants']
collection = db['restaurants']

# access collection
collection = db['test']

# verify connection is sucessful
print("Connected successfully!")

print(collection.bulk_write)