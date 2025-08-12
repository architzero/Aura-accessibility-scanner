import os
import motor.motor_asyncio
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv("MONGO_DB_URI")

# Use Motor's async client
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = client.aura_db

# Collections remain the same
users_collection = db["users"]
projects_collection = db["projects"]
scan_results_collection = db["scan_results"]