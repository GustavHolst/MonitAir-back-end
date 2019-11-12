import psycopg2
from config import config

def create_tables():
    commands = [(
        """
        CREATE TABLE data (
            reading_id SERIAL PRIMARY KEY,
            temperature FLOAT,
            pressure FLOAT,
            humidity FLOAT,
            TVOC FLOAT,
            gasBaseline FLOAT,
            user_id int
        );
        """
    )]
    conn = None
    try:
        # read the connection parameters
        params = config()
        # connect to the PostgreSQL server
        conn = psycopg2.connect(dbname= params['database'],user = params['user'],password = params['password'])
        cur = conn.cursor()
        # create table one by one
        for command in commands:
            print(command)
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