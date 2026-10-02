import hashlib
from pathlib import Path

def calculate_file_hash(file_path: str) -> str:
    
    with Path(file_path).open("rb") as file:
        return hashlib.file_digest(file, "sha256").hexdigest()
