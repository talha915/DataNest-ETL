import psycopg2
from api_request import mock_fetch_data

def connect_to_db():
    try:
        print(f"🔄 Connecting to the postgresql database.....")
        conn = psycopg2.connect(
            host="localhost",
            port="5000",
            dbname="db",
            user="db_user",
            password="db_password"
        )
        print(f"✅ Connection established successfully!")
    except Exception as e:
        print(f"❌ Error while connecting to database: {e}")    


connect_to_db()        