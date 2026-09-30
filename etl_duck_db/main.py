from src.db.connection import SpotifyDB
from src.bronze.spotify_bronze import BronzeLayer
from src.silver.spotify_silver import SilverLayer

def main():
    db = SpotifyDB()

    db.create_schemas()

    bronze = BronzeLayer(db)

    bronze.ingest("data/dataset.txt", "spotify_listen")

    silver = SilverLayer(db)
    silver.transform_spotify_listen()

    db.close()


if __name__ == "__main__":
    main()
