from __future__ import absolute_import, division, print_function, unicode_literals

from hydroffice.soundspeed.formats import readers, writers

print("Readers:")
for rdr in readers:
    print("> %s" % rdr)

print("\nWriters:")
for wtr in writers:
    print("> %s" % wtr)
