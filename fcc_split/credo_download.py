import os, json, sys, operator, urllib, urllib2
from pyquery import PyQuery as pq

def all_files(dir):
    return reduce(operator.add, [[os.path.join(x[0], y) for y in x[2]] for x in os.walk(dir)])

credo_dir = sys.argv[1]

if __name__ == "__main__":
    json_files = [f for f in all_files(credo_dir) if f.endswith('.json') and '-' not in os.path.basename(f)]
    for filename in json_files:
        meta = json.load(open(filename))

        page = pq(urllib2.urlopen("http://apps.fcc.gov/ecfs/comment/view?id=" + meta['id']).read())

        print 'Processing %s...' % filename
        for number, href in enumerate([a.attr('href').strip() for a in page.find('.tableDiv a[href*=document]').items()]):
            print "Downloading %s..." % number
            urllib.urlretrieve("http://apps.fcc.gov" + str(href), os.path.join(os.path.dirname(filename), str(meta['id']) + "-" + str(number) + ".pdf"))