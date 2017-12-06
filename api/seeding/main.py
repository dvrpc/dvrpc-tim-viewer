import Queue
import time

import loader.database
import loader.visum

MODEL_PATH_TEMPLATE = r"D:\William\Documents\_DVRPC_Mini14\DV_38_125_pruned_toynetwork_{tod}.ver"

class Sponge:
    def __init__(self, **kwds):
        for k, v in kwds.iteritems():
            setattr(self, k, v)

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
    VM = loader.visum.VisumManager(MODEL_PATH_TEMPLATE, 15, Q)

    D.start()
    VM.start()

    VM.join()
    Q.put({"cmd": "exit"})
    D.join()

if __name__ == "__main__":
    main()