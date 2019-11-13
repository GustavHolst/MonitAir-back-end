import psycopg2
from config import config
from data.testdata import outputs

print(outputs)


user = {
     'first_name' : "Barry",
     'surname' : "Chuckle",
     'email' : "BigBoiBaz@gmail.com",
     'sensor_id' : 1,
     'username' : "BazziChuck",
     'password' : "RIP"
 }

 
def insert_user(user):
    sql = """INSERT INTO users(first_name, surname, email, sensor_id,username,password)
             VALUES(%s, %s, %s, %s, %s, %s) RETURNING *;
             SELECT * FROM users;
             """
    conn = None
    user_id = None
    try:
        # read userbase configuration
        params = config()
        # connect to the PostgreSQL userbase
        conn = psycopg2.connect(**params)
        # create a new cursor
        cur = conn.cursor()
        # execute the INSERT statement
        cur.execute(sql, (user['first_name'],user['surname'],user['email'],user['sensor_id'],user['username'],user['password']))
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

def insert_data (data):
    sql = """INSERT INTO data(reading_id,temperature,pressure,humidity,TVOC,gasBaseLine,user_id)
             VALUES(%s, %s, %s, %s, %s, %s,%s) RETURNING *;
             SELECT * FROM data;
             """
    conn = None
    reading_id = None
    try:
        print(data['af4eb1']['temp_mean'])
        params=config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute(sql,(data['af4eb1']['temp_mean'],data['af4eb1']['pressure_mean'],data['af4eb1']['humidity_mean'],data['af4eb1']['tvoc_mean'],data['af4eb1']['gas_baseline'],1))
        data = cur.fetchmany(200)
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
 
    return data

for i in outputs:
    insert_data(i)

