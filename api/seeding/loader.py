import threading
import Queue

import psycopg2 as psql

PSQL_CNX = {
    "host": "toad",
    "port": 5432,
    "database": "postgres",
    "user": "postgres",
    "password": "sergt",
}

class Database(threading.Thread):
    def __init__(self, db_credentials):
        super(Database, self).__init__()
        self.db_credentials = db_credentials
    def run(self):
        with psql.connect(**self.db_credentials) as con:
            cur = con.cursor()
            cur.execute("SELECT COUNT(*) FROM mtx_210_am")
            (cnt,) = cur.fetchone()
            print "OK", cnt

def main():
    d = Database(PSQL_CNX)
    d.isDaemon = True
    d.start()
    d.join()
    

if __name__ == "__main__":
    main()