import motor.motor_asyncio
from config import settings
import asyncio

# Use Motor's async client
client = motor.motor_asyncio.AsyncIOMotorClient(settings.mongo_db_uri)
db = client.aura_db

# Collections
users_collection = db["users"]
projects_collection = db["projects"]
scan_results_collection = db["scan_results"]

async def create_indexes():
    """Create database indexes for better query performance"""
    try:
        # Users: index on email (unique)
        await users_collection.create_index("email", unique=True)
        
        # Projects: index on userId and createdAt for sorting
        await projects_collection.create_index([("userId", 1), ("createdAt", -1)])
        await projects_collection.create_index([("userId", 1), ("projectName", 1)], unique=True)
        
        # Scan Results: index on projectId and createdAt for history queries
        await scan_results_collection.create_index([("projectId", 1), ("createdAt", -1)])
        
        print("Database indexes created successfully")
    except Exception as e:
        print(f"Error creating indexes: {e}")

# Initialize indexes on startup
def init_db():
    """Initialize database indexes"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(create_indexes())
    loop.close()