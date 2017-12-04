import csv
import StringIO
import time

import numpy
import psycopg2 as psql
import VisumPy.helpers as h

VER_TEMPLATE = r"F:\Modeling\Model_Development\TIM2.3\TIM_23Full_run\TIM23_2015_Base_170612_FINAL_TMC_{tod}.ver"
TODs = [
    "AM",
    "MD",
    "PM",
    "NT"
]
MTXs = [
    210, # IMP
    220, # IVT
    250, # OVT
    260, # TOL
    270, # DIS
    290, # TTC
    291, # UDS
    400, # IPD
    420, # IVT
    421, # IVTT(RR)
    422, # IVTT(Sub)
    423, # IVTT(Pat)
    424, # IVTT(LRT)
    426, # IVTT(BRT)
    428, # IVTT(Bus)
    429, # IVTT(Trl)
    450, # OVT
    451, # OWTA
    460, # FAR
    480, # NTR
    481, # XIMP
    490, # JRT
]
PSQL_CONNECTION_PARAM = {
    "host": "toad",
    "port": 5432,
    "database": "postgres",
    "user": "postgres",
    "password": "sergt"
}
INSERT_BATCHSIZE = 100000

def main():
    Visum = h.CreateVisum(15)
    con = psql.connect(**PSQL_CONNECTION_PARAM)
    for tod in TODs:
        Visum.LoadVersion(VER_TEMPLATE.format(**{'tod':tod}))
        for mtxno in MTXs:
            print mtxno,
            start_time = time.time()
            tblname = "mtx_{no}_{tod}".format(**{"no":mtxno,"tod":tod})
            mtx = h.GetMatrix(Visum, mtxno)
            n,n = mtx.shape
            y = numpy.vstack((numpy.arange(n) for _ in xrange(n)))
            x = y.T.flatten()
            y = y.flatten()
            z = mtx.flatten()
            mtx_listing = numpy.array((x,y,z,), dtype = object).T
            cur.execute("""
                CREATE TABLE {0} (
                    oindex smallint,
                    dindex smallint,
                    val double precision
                )
            """.format(tblname))
            f = StringIO.StringIO()
            w = csv.writer(f)
            w.writerows(mtx_listing[numpy.where(mtx_listing[:,2] < 1e5)])
            f.seek(0)
            cur.copy_from(
                f,
                tblname,
                columns = [
                    "oindex",
                    "dindex",
                    "val"
                ],
                sep = ','
            )
            f.close()
            cur.execute("CREATE INDEX {0}_o_idx ON public.{0} (oindex ASC NULLS LAST);".format(tblname))
            cur.execute("CREATE INDEX {0}_d_idx ON public.{0} (dindex ASC NULLS LAST);".format(tblname))
            con.commit()
            print "%.2f" % (time.time() - start_time)

def __analysis__():
    # Drop 0 value cells?
    for mtxno in mtxnos:
        for tod in tods:
            tbl = "mtx_{mtxno}_{tod}".format(**{"mtxno":mtxno, "tod":tod})
            cur.execute("SELECT COUNT(*) FROM {tbl}".format(**{"tbl":tbl}))
            print tbl, cur.fetchall(),
            cur.execute("DELETE FROM {tbl} WHERE val = 0".format(**{"tbl":tbl}))
            cur.execute("SELECT COUNT(*) FROM {tbl}".format(**{"tbl":tbl}))
            print cur.fetchall()

    # Vacuuming needs to occur outside of the transaction block
    con.set_isolation_level(psql.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    for mtxno in mtxnos:
        tbl = "mtx_{mtxno}_{tod}".format(**{"mtxno":mtxno, "tod":tod})
        print tbl,
        cur.execute("VACUUM FULL VERBOSE ANALYZE {tbl}".format(**{"tbl":tbl}))
        print 'Done'
    con.set_isolation_level(psql.extensions.ISOLATION_LEVEL_DEFAULT)

    for mtxno in mtxnos:
        for tod in tods:
            tbl = "mtx_{mtxno}_{tod}".format(**{"mtxno":mtxno, "tod":tod})
            print tbl, 
            cur.execute("SELECT min(val) lbound, max(val) ubound FROM {tbl}".format(**{"tbl":tbl}))
            lbound, ubound = cur.fetchone()
            # print lbound, ubound
            # lbound, ubound = math.floor(math.log10(lbound)), math.ceil(math.log10(ubound))
            cur.execute(
                "SELECT width_bucket(val, {lbound}, {ubound}, {nbins}) bins, COUNT(*) cnt FROM {tbl} GROUP BY bins ORDER BY bins".format(**{
                    # "lbound": 0.0,
                    # "ubound": 10 ** ubound,
                    # "nbins": int(ubound),
                    # "tbl": tbl,
                    "lbound": 0,
                    "ubound": 10000,
                    "nbins": 20,
                    "tbl": tbl,
                })
            )
            histogram = cur.fetchall()
            print histogram

if __name__ == "__main__":
    main()