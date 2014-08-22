import json, os, itertools, math

tree_data = json.load(open('docs.json'))
applicants = json.load(open('applicants.json'))
PAGE_SIZE = 1000

for cluster_id, docs in tree_data.iteritems():
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

        outf = open(os.path.join('tree_data', '%s-p%s.json' % (cluster_id, page_num)), 'wb')
        json.dump({
            'items': out_docs,
            'full_size': ndocs,
            'page_size': len(out_docs),
            'id': cluster_id,
            'page': page_num,
            'next': ('%s-p%s.json' % (cluster_id, (page_num + 1))) if (page_num + 1) < npages else None
        }, outf, indent=4)
        outf.close()