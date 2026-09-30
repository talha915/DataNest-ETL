from db.connection import SpotifyDB

def main():
    db = SpotifyDB()

    db.create_schemas()

    db.close()


if __name__ == "__main__":
    main()
