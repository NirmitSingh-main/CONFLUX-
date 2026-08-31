from pathlib import Path
import sys

sys.path.append(
    str(Path(__file__).resolve().parents[2])
)

from backend.database.database import create_tables


if __name__ == "__main__":
    print("Creating CONFLUX database...")

    create_tables()

    print("Database created successfully.")