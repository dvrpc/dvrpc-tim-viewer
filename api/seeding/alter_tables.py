NET_OBJ_ATTRS = {
    ("zones", lambda V:V.Net.Zones): [
        "area_type",
        "empres",
        "grpqrts",
        "statefp00",
        "population",
        "total_employment",
        "k-12",
        "univ",
        "households",
        "basic_emp",
        "other_emp",
        "ag_mining",
        "construction",
        "manufacturing",
        "wholesale_trade",
        "retail_trade",
        "transport_wh_util",
        "fire",
        "public_admin",
        "armed_forces",
        "stu_school",
        "eds-meds",
        "pop_dens",
        "emp_dens",
        "bike",
        "loinc",
        "lu_mix2_1",
        "attract",
        "rail",
        "busstop",
        "vehpp",
        "park_rec",
        "atype1",
        "atype2",
        "atype3",
        "rtl_dens",
        "connect",
        "hh_0-35k_0workers",
        "hh_0-35k_1worker",
        "hh_0-35k_2workers",
        "hh_0-35k_3_plus_workers",
        "hhs_over_35k_0workers",
        "hhs_over_35k_1worker",
        "hhs_over_35k_2workers",
        "hhs_over_35k_3_plus_workers",
        "hh_0-35k_1person",
        "hh_0-35k_2person",
        "hh_0-35k_3person",
        "hh_0-35k_4_plus_person",
        "hhs_over_35k_1person",
        "hhs_over_35k_2person",
        "hhs_over_35k_3person",
        "hhs_over_35k_4_plus_person",
        "stu_colleg",
    ]
}

for (name, netobj), attrs in NET_OBJ_ATTRS.iteritems():
    pg_fields = []

    payload = netobj(Visum).GetMultipleAttributes(attrs)
    for i, values in enumerate(zip(*payload)):
        attr = attrs[i].replace('-','_')
        dtype = None
        try:
            notallints = False in [(v % 1.0) == 0.0 for v in values]
        except:
            dtype = 'text'
        else:
            if notallints:
                dtype = 'double precision'
            else:
                dtype = 'integer'
        pg_fields.append((attr, dtype))

    print ",".join(map(lambda (f,d):"ADD COLUMN {0} {1}".format(f, d), pg_fields))
    print ",".join(zip(*pg_fields)[0])

# meta_netobj