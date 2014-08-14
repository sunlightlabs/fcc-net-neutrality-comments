import os, sys, subprocess, tempfile, gzip, cStringIO
from boto.s3.connection import S3Connection
from boto.s3.key import Key

conn = S3Connection()
bucket = conn.get_bucket("openinternet.widgets.sunlightfoundation.com")

base = sys.argv[1]
for f in os.listdir(base):
    combined = os.path.join(base, f)
    if os.path.isdir(combined):
        for j in os.listdir(combined):
            print "uploading", j

            k = Key(bucket)
            k.key = os.path.join("data", j)

            gzdata = cStringIO.StringIO()
            gzfile = gzip.GzipFile(fileobj=gzdata, mode="wb")

            gzfile.write(open(os.path.join(combined, j)).read())
            gzfile.close()

            gzdata.seek(0)

            k.set_metadata('Content-Type', 'application/json')
            k.set_metadata('Content-Encoding', 'gzip')
            k.set_contents_from_file(gzdata)
            k.set_acl('public-read')