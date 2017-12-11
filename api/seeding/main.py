import logging
logging.basicConfig(format = "%(asctime)s:%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
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

MAX_QUEUE_DEPTH = 100

SINGLE_LOAD_VISUM = True
DB_THREADS = 4
OVERWRITE_EXISTING_TABLES = False

def main():
    # Initialisation
    logger.debug("Hi")
    Q = Queue.Queue()
    DM = loader.database.DatabaseManager(PSQL_CNX, Q, MAX_QUEUE_DEPTH, DB_THREADS, OVERWRITE_EXISTING_TABLES)

    # WARNING
    DM.nukeDatabase()

    spatial_ref = (PSQL_SRID, DM.getProjectionWKT(PSQL_SRID))
    VM = loader.visum.VisumManager(MODEL_PATH_TEMPLATE, 15, Q, spatial_ref, MAX_QUEUE_DEPTH, SINGLE_LOAD_VISUM)

    # Start Database IO Agent Manager
    DM.start()
    # Start Visum data streamer
    VM.start()
    VM.join()
    logger.debug("visum.VisumManager(): Finished")
    # When data has been exported from Visum, flag shutdown
    Q.put(None)
    # Wait for DB Agents to finish doing its thing
    DM.join()
    logger.debug("Bye")

if __name__ == "__main__":
    main()