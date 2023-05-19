import psycopg2
from config import host, user, password, db_name

try:
    connection = psycopg2.connect(
        host=host,
        user=user,
        password=password,
        database=db_name
    )
    connection.autocommit = True


    def create_db():
        with connection.cursor() as cursor:
            cursor.execute("""CREATE TABLE IF NOT EXISTS views(
            id INTEGER,
            profile_id INTEGER);""")


    def insert_db(id, profile_id):
        with connection.cursor() as cursor:
            cursor.execute("""INSERT INTO views(id, profile_id)
            VALUES(%s, %s);""", (id, profile_id,))


    def select_db(id):
        with connection.cursor() as cursor:
            cursor.execute("""SELECT profile_id FROM views WHERE id = %s""", (id,))
            viewed_id = []
            for i in cursor.fetchall():
                viewed_id.append(i[0])
        return viewed_id

    # with connection.cursor() as cursor:
    #     cursor.execute("""DROP TABLE views;
    #     """)


except Exception as e:
    print('[INFO] Error while working with PostgreSQL', e)
# finally:
# if connection:
#     connection.close()
#     print('[INFO] PostgreSQL connection closed')
