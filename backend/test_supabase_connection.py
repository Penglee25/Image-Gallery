from supabase import create_client, Client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase: Client = create_client(url, key)

def test_connection():
    try:
        # Simple test: list all tables (from the 'public' schema)
        response = supabase.table("images").select("*").limit(1).execute()
        print("✅ Connection successful!")
        print("Fetched data:", response.data)
    except Exception as e:
        print("❌ Connection failed:", str(e))

if __name__ == "__main__":
    test_connection()
