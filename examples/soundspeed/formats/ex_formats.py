from __future__ import absolute_import, division, print_function, unicode_literals

from hydroffice.soundspeed.formats import readers, writers

print("Readers:")
fmts = list()
for rdr in readers:
    print("> %s" % rdr)
    if len(rdr.ext):
        fmts.append("%s(*.%s)" % (rdr.desc, " *.".join(rdr.ext)))

print("%s;;All files (*.*)" % ";;".join(fmts))

print("\nWriters:")
for wtr in writers:
    print("> %s" % wtr)
