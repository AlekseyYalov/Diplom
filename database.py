import psycopg2
from config import host, user, password, db_name


try:
    connection = psycopg2.connect(
        host = host,
        user = user,
        password = password,
        database = db_name
    )
    connection.autocommit = True

    with connection.cursor() as cursor:
        cursor.execute("""CREATE TABLE IF NOT EXISTS views(
        id SERIAL,
        profile_id INTEGER PRIMARY KEY);
        """)

    # with connection.cursor() as cursor:
    #     cursor.execute("""DROP TABLE views;
    #     """)



except Exception as _ex:
    print('[INFO] Error while working with PostgreSQL', _ex)
finally:
    if connection:
        connection.close()
        print('[INFO] PostgreSQL connection closed')
