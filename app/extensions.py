import os

from pymongo import MongoClient

client = MongoClient(
    host=os.environ.get("DB_HOST"),  # Docker
    # host="localhost", # Localhost
    port=int("27017"),  # os.environ.get("DB_PORT") = "tcp://172.17.0.2:27017"
    username=os.environ.get("DB_USERNAME"),
    password=os.environ.get("DB_PASSWORD"),
    authSource="admin"
)
db = client["reports_engine"]  # os.environ.get("DB_NAME") = "/flask/db"
