import sys, re, json, csv, urllib2
from collections import Counter

prefix = 'form_r2'
csv_url = 'https://docs.google.com/spreadsheets/d/1MOHC07E024GvMvUFO57Ihxr0j2itM_HkEJeDBjTmT0U/export?format=csv&gid=1111195116&single=true'

# ES setup
from elasticsearch import Elasticsearch
es = Elasticsearch(['localhost:9201',])

def node_phrase_query(node_id, key_phrase):
    qbody = {
        "fields": [],
        "size": 1000,
        "from": 0,
        "query": {
            "bool": {
                "must": [
                    {"match_phrase": {"text": key_phrase}},
                    {"match_phrase": {"clusters": node_id}}
                ]
            }
        }
    }
    return qbody

def search_node_phrase(n, p):
    body = node_phrase_query(n,p)
    ids = []

    # grab the first page
    res = es.search(index='fcc_comments_part_two', body=body)
    ids.extend([item['_id'] for item in res['hits']['hits']])

    # figure out how many pages there should be
    page_range = int(res['hits']['total'] / 1000) + 1

    for pnum in range(1, page_range):
        body['from'] = pnum * 1000
        res = es.search(index='fcc_comments_part_two', body=body)
        ids.extend([item['_id'] for item in res['hits']['hits']])
    
    return ids

# start fetching stuff

all_rows = list(csv.DictReader(urllib2.urlopen(csv_url)))

# we only care about the ones that have a keyphrase
rows = [row for row in all_rows if row['keyphrase'].strip()]

# first standardize empty campaigns, and count
campaign_count = Counter()
for row in rows:
    if row['campaign'].strip() in ('', '???'):
        row['campaign'] = 'UNKNOWN'

    campaign_count[row['campaign']] += 1

# make the tree data
tree_data = []
link_data = {}
doc_data = {}
so_far = Counter()
for row in rows:
    label = row['campaign']
    if campaign_count[row['campaign']] > 1:
        so_far[row['campaign']] += 1
        label = '%s %s' % (label, so_far[row['campaign']])
    
    if row['campaign'] == "UNKNOWN":
        # wrap in parens
        label = '(%s)' % label

    print "Working on %s..." % label

    ids = search_node_phrase(row['node'], row['keyphrase'])

    tree_data.append({
        'id': label,
        'keywords': [label],
        'pro_anti': row['position'],
        'size': len(ids),
        'children': []
    })

    print len(ids), row['keyphrase_count']

    link_data[label] = [row['url']] if row['url'] else []
    doc_data[label] = ids

tree_file = open("%s_tree.json" % prefix, "wb")
json.dump(tree_data, tree_file, indent=4)
tree_file.close()

link_file = open("%s_links.json" % prefix, "wb")
json.dump(link_data, link_file, indent=4)
link_file.close()

doc_file = open("%s_docs.json" % prefix, "wb")
json.dump(doc_data, doc_file)
doc_file.close()