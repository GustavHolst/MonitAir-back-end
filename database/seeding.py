import psycopg2
from config import config
 

data = {
     'first_name' : "Barry",
     'surname' : "Chuckle",
     'email' : "BigBoiBaz@gmail.com",
     'sensor_id' : 1,
     'username' : "BazziChuck",
     'password' : "RIP"
 }

data2 = [
     "Barry",
     "Chuckle",
     "BigBoiBaz@gmail.com",
     1,
     "BazziChuck",
     "RIP"

 ]
 
def insert_data(data):
    """ Insert new user into users table"""
    sql = """INSERT INTO users(first_name, surname, email, sensor_id,username,password)
             VALUES(%s, %s, %s, %s, %s, %s) RETURNING *;
             SELECT * FROM users;
             """
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
        cur.execute(sql, (data['first_name'],data['surname'],data['email'],data['sensor_id'],data['username'],data['password']))
        # get the generated id back
        users = cur.fetchmany(100)
        # commit the changes to the database
        conn.commit()
        # close communication with the database
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
 
    return users

print(insert_data(data))