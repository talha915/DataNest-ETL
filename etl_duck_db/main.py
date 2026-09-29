from src.pipeline.database import create_database
def main():
    conn = create_database()
    conn.close()

if __name__ == "__main__":
    main()
