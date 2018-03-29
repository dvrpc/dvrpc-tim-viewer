import logging
logFormat = "%(asctime)s:%(levelname)s:%(name)s:%(message)s"
logging.basicConfig(format = logFormat)
fileHandler = logging.FileHandler('stdout.log')
fileHandler.setFormatter(logging.Formatter(logFormat))
logger = logging.getLogger()
logger.addHandler(fileHandler)
logger.setLevel(logging.DEBUG)

import Queue
import time

import loader.database
import loader.visum
from credentials import PSQL_CNX

MODEL_PATH_TEMPLATE = r"C:\Users\model-ws\Desktop\TIM_23Full_run\TIM23_2015_Base_170612_FINAL_TMC_{tod}.ver"
MODEL_SCEN = "2015"

PSQL_SRID = 4326

MAX_QUEUE_DEPTH = 100

SINGLE_LOAD_VISUM = True
DB_THREADS = 8
OVERWRITE_EXISTING_TABLES = False

def main():
    # Initialisation
    logger.debug("Hi")
    Q = Queue.Queue()
    DM = loader.database.DatabaseManager(PSQL_CNX, Q, MAX_QUEUE_DEPTH, DB_THREADS, OVERWRITE_EXISTING_TABLES)

    # WARNING
    DM.nukeDatabase()

    spatial_ref = (PSQL_SRID, DM.getProjectionWKT(PSQL_SRID))
    VM = loader.visum.VisumManager(MODEL_PATH_TEMPLATE, MODEL_SCEN, 15, Q, spatial_ref, MAX_QUEUE_DEPTH, SINGLE_LOAD_VISUM)

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