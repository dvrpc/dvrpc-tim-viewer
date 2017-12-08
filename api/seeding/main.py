import Queue
import time

import loader.database
import loader.visum

MODEL_PATH_TEMPLATE = r"D:\William\Documents\_DVRPC_Mini14\DV_38_125_pruned_toynetwork_{tod}.ver"

PSQL_CNX = {
    "host": "localhost",
    "port": 5432,
    "database": "postgres",
    "user": "postgres",
    "password": "sergt",
}
PSQL_SRID = 4326

def main():
    # Initialisation
    Q = Queue.Queue()
    D = loader.database.Database(PSQL_CNX, Q)
    time.sleep(1)
    spatial_ref = (PSQL_SRID, D.getProjectionWKT(PSQL_SRID))
    VM = loader.visum.VisumManager(MODEL_PATH_TEMPLATE, 15, Q, spatial_ref)

    # Start Database IO Agent
    D.start()
    # Start Visum data streamer
    VM.start()
    VM.join()
    # When data has been exported from Visum, flag shutdown
    Q.put(None)
    # Wait for DB Agent to finish doing its thing
    D.join()

if __name__ == "__main__":
    main()