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
        return conn
    except Exception as e:
        print(f"❌ Error while connecting to database: {e}")  
        raise          


def create_table(conn):
    try:
        print(f"🔄 Creating table.....")
        cursor = conn.cursor()
        cursor.execute("""
            Create schema if not exists dev;
            create table if not exists dev.raw_weather_data (
                       id serial primary key,
                       city text,
                       temperature float,
                       weather_description text,
                       wind_speed float,
                       time timestamp,
                       inserted_at timestamp default now(),
                       utc_offset text             
            );           
        """)
        conn.commit()
        print(f"✅ Table created successfully!")
    except Exception as e:
        print(f"❌ Error while creating tables: {e}") 

conn = connect_to_db()
create_table(conn)        