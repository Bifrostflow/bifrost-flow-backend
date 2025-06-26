import os

import certifi
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()
ca = certifi.where()
username = os.getenv("MONGO_USERNAME")
password = os.getenv("MONGO_PASS")

uri = f"mongodb+srv://{username}:{password}@cluster0.bv1rtx0.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
# client = AsyncIOMotorClient(uri)

client = AsyncIOMotorClient(
    uri,
    tls=True,
    tlsCAFile=certifi.where()
)

db = client["bifrostflow"]  # use your DB name

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

node_collection=db["nodes"]
flow_collection=db["flow"]