import psycopg2
from config import config


def create_tables():
    commands = (
        """
        CREATE TABLE users (
            user_id SERIAL PRIMARY KEY,
            first_name VARCHAR(40),
            surname VARCHAR(40),
            email VARCHAR(100),
            sensor_id int,
            username VARCHAR(40),
            password VARCHAR(40)
        )
        """,
        """
        CREATE TABLE data (
            reading_id SERIAL PRIMARY KEY,
            temperature FLOAT,
            pressure FLOAT,
            humidity FLOAT,
            TVOC FLOAT,
            gasBaseline FLOAT,
            user_id int,
            FOREIGN KEY (user_id)
            REFERENCES users (user_id)
            ON UPDATE CASCADE ON DELETE CASCADE

        );
        """

    )
    conn = None
    try:
        # read the connection parameters
        params = config()
        # connect to the PostgreSQL server
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        # create table one by one
        for command in commands:
            cur.execute(command)
        # close communication with the PostgreSQL database server
        cur.close()
        # commit the changes
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


if __name__ == '__main__':
    create_tables()
