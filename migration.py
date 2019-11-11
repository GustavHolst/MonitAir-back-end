import psycopg2
from config import config

def create_tables():
    commands = (
        """
        CREATE TABLE data (
            reading_id SERIAL PRIMARY KEY,
            temperature FLOAT,
            pressure FLOAT,
            humidity FLOAT,
            TVOC FLOAT,
            gasBaseline Float
        )
        """
    )
    conn = None
    try:
        params=config()