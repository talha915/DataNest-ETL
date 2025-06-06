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
        print(f"❌ Error while creating table: {e}") 

def insert_records(conn, data):
    try:
        print(f"🔄 Inserting data into table.....")
        weather = data['current']
        location = data['location']
        cursor = conn.cursor()
        cursor.execute("""
            insert into dev.raw_weather_data (
                city,
                temperature,
                weather_description,
                wind_speed,
                time,
                inserted_at,
                utc_offset              
            )
            VALUES (%s, %s, %s, %s, %s, NOW(), %s)                
        """, (
                location["name"],
                weather["temperature"],
                weather["weather_descriptions"][0],
                weather["wind_speed"],
                location["localtime"],
                location["utc_offset"]    
            )
        )
        conn.commit()
        print(f"✅ Data Inserted successfully!")
    except Exception as e:
        print(f"❌ Error while inserting data in table: {e}")     

def main():
    try:
        data = mock_fetch_data()
        conn = connect_to_db()
        create_table(conn)      
        insert_records(conn, data)
    except Exception as e:
        print(f"❌ Error : {e}")    

main()        