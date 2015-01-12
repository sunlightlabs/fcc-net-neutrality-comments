import os
import sys
import gzip
import cStringIO

from boto.s3.connection import S3Connection
from boto.s3.key import Key

sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)),
                             os.path.pardir))

import settings

conn = S3Connection()
bucket = conn.get_bucket(settings.S3_BUCKET)

base = sys.argv[1]
for j in os.listdir(base):
    print "uploading", j

    k = Key(bucket)
    k.key = os.path.join(sys.argv[1], j)

    gzdata = cStringIO.StringIO()
    gzfile = gzip.GzipFile(fileobj=gzdata, mode="wb")

    gzfile.write(open(os.path.join(base, j)).read())
    gzfile.close()

    gzdata.seek(0)

    k.set_metadata('Content-Type', 'application/json')
    k.set_metadata('Content-Encoding', 'gzip')
    k.set_contents_from_file(gzdata)
    k.set_acl('public-read')
