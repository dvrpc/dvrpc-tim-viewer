import Queue
import time

import loader.database
import loader.visum

PSQL_CNX = {
    "host": "toad",
    "port": 5432,
    "database": "postgres",
    "user": "postgres",
    "password": "sergt",
}

def main():
    Q = Queue.Queue()
    D = loader.database.Database(PSQL_CNX, Q)
    VM = loader.visum.VisumManager(15)

    D.start()

    time.sleep(1)
    Q.put({0:0})
    time.sleep(1)
    Q.put({"cmd": "exit"})


    D.join()

if __name__ == "__main__":
    main()