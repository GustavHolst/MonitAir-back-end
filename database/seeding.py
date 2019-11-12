import psycopg2
from config import config
 

data = {
     'firstname' : "Barry",
     'surname' : "Chuckle",
     'email' : "BigBoiBaz@gmail.com",
     'sensor_id' : 1,
     'username' : "BazziChuck"
 }
 
def insert_data(data):
    """ Insert new user into users table"""
    sql = """INSERT INTO user(firstname, surname, email, sensor_id,username,password)
             VALUES(%s) RETURNING user_id;"""
    conn = None
    user_id = None
    try:
        # read database configuration
        params = config()
        # connect to the PostgreSQL database
        conn = psycopg2.connect(**params)
        # create a new cursor
        cur = conn.cursor()
        # execute the INSERT statement
        cur.execute(sql, (data.firstname,data.surname,data.email,data.sensor_id,data.username,data.password))
        # get the generated id back
        user_id = cur.fetchone()[0]
        # commit the changes to the database
        conn.commit()
        # close communication with the database
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
 
    return user_id