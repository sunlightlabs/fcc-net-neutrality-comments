import json, os, itertools, math, sys, re

prefix = sys.argv[1] if len(sys.argv) > 1 else None

tree_data = json.load(open('%s_docs.json' % prefix if prefix else 'docs.json'))
applicants = json.load(open('applicants.json'))
links_name = '%s_links.json' % prefix if prefix else 'links.json'
links = json.load(open(links_name)) if os.path.exists(links_name) else None
PAGE_SIZE = 1000

transform_id = lambda i: re.sub(r'[^a-z0-9_-]', '', re.sub(r'\s+', '_', i.lower()))

for cluster_id, docs in tree_data.iteritems():
    transformed_id = transform_id(cluster_id)
    docs = [doc for doc in docs if doc is not None]
    ndocs = len(docs)
    npages = int(math.ceil(float(ndocs) / PAGE_SIZE))

    for page_num in xrange(npages):
        print "page %s/%s of %s" % (page_num, npages, cluster_id)
        
        out_docs = []
        for doc_id in docs[page_num * PAGE_SIZE:(page_num + 1) * PAGE_SIZE]:
            record = {
                'id': doc_id,
                'title': 'Comment from %s' % applicants[doc_id],
            }
            out_docs.append(record)

        outf = open(os.path.join('%s_data' % prefix if prefix else 'tree_data', '%s-p%s.json' % (transformed_id, page_num)), 'wb')
        outs = {
            'items': out_docs,
            'full_size': ndocs,
            'page_size': len(out_docs),
            'id': transformed_id,
            'page': page_num,
            'next': ('%s-p%s.json' % (transformed_id, (page_num + 1))) if (page_num + 1) < npages else None
        }
        if links:
            outs['links'] = links[cluster_id] if links[cluster_id] and not (type(links[cluster_id][0]) is float and math.isnan(links[cluster_id][0])) else []
        json.dump(outs, outf, indent=4)
        outf.close()