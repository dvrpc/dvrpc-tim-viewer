import StringIO
import csv
import re

buffer = StringIO.StringIO()
with open(r"C:\Users\model-ws\Desktop\visum_attr_assignment_output.net", "rb") as io:
    buffer.writelines([line for line in io if not line.startswith('*')])
buffer.seek(0)

r = csv.reader(buffer, delimiter = ";")
layout = [line for line in r]

regex_pattern = re.compile(r"\(([a-zA-Z0-9_\-]*,)?AH(,[a-zA-Z0-9_\-]*,?)?\)")

new_layout = []
for fields in layout:
    if len(fields) > 0 and fields[0].startswith('$'):
        _fields = []
        for f in fields:
            if re.search(regex_pattern, f):
                continue
            if "_DSEG" in f:
                continue
            if "_PRTSYS" in f:
                continue
            if "FLOWBUNDLE" in f:
                continue
            _fields.append(f)
        # new_layout.append([f for f in fields if (not re.search(regex_pattern, f)) and (not "_DSEG" in f)])
        new_layout.append(_fields)
    else:
        new_layout.append(fields)

with open(r"C:\Users\model-ws\Desktop\visum_attr_assignment_output_ap.net", "wb") as io:
    w = csv.writer(io, delimiter = ";")
    w.writerows(new_layout)

####

ptrn = re.compile(r"^\-?[0-9]+(\.[0-9]*)?(?=[a-zA-Z])")

tables = []
with open(r"C:\Users\model-ws\Desktop\trunc_assignment_output_am.net", "rb") as io:
    r = csv.reader(io, delimiter = ";")
    table = []
    for row in r:
        if len(row) == 0:
            tables.append(table)
            table = []
            continue
        if not row[0].startswith('*'):
            table.append(row)

# units = set()
# for fields in data:
#     units.update([re.sub(ptrn, "", f) for f in fields if re.search(ptrn, f)])

for i, table in enumerate(tables):
    transposed_table = zip(*table)
    for j, column in enumerate(transposed_table):
        nfields = len(column[1:])
        if nfields > 0:
            if nfields == sum(1 for c in column[1:] if re.search(ptrn, c)):
                unit = re.compile(r"%s$" % re.sub(ptrn, "", column[1]))
                transposed_table[j] = [column[0]] + [re.sub(unit, "", c) for c in column[1:]]
    tables[i] = zip(*transposed_table)
