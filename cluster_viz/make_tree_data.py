import json, os, itertools

tree_data = json.load(open('docs.json'))
SAMPLE_THRESHOLD = tree_data['sample_threshold']
SAMPLE_SIZE = 20000

for cluster_id, docs in tree_data['docs'].iteritems():
    sample = len(docs) > SAMPLE_THRESHOLD

    if sample:
        print 'sampling %s' % cluster_id
    else:
        print 'doing %s' % cluster_id
    
    out_docs = []
    for doc_file, score in itertools.islice(docs, SAMPLE_SIZE) if sample else docs:
        print doc_file, score
        doc = json.load(open(os.path.join('data', doc_file)))
        record = {
            'id': doc['id'],
            'title': 'Comment from %s' % doc['applicant'],
            'score': score
        }
        out_docs.append(record)

    outf = open(os.path.join('tree_data', '%s.json' % cluster_id), 'wb')
    json.dump({
        'items': out_docs,
        'full_size': len(docs),
        'list_size': len(out_docs),
        'id': cluster_id,
        'sample': sample
    }, outf, indent=4)
    outf.close()