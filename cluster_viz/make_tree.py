from collections import defaultdict
import csv, json, operator

SAMPLE_THRESHOLD = 150000
SAMPLE_SIZE = 20000

# map out the parent-child relationships
children = defaultdict(set)
levels = defaultdict(set)
for row in csv.DictReader(open("cluster_tree_table.csv")):
    if row['level_0']:
        path = [row['level_%s' % i] for i in range(7)] + ['7-%s' % row['cluster']]
        
        for i in range(7):
            children[path[i]].add(path[i+1])
            levels[i].add(path[i])

# add all the items to the leaves
docs = defaultdict(list)
keywords = defaultdict(list)
tree_data = json.load(open("clustered_docs.json"))
for node_id, node_data in tree_data.iteritems():
    docs['7-%s' % node_id] = sorted(node_data['doc_id'], key=lambda d: d[1], reverse=True)
    keywords['7-%s' % node_id] = sorted(node_data['keywords'], key=lambda k: k[1], reverse=True)

# roll it up
for level in range(6,-1,-1):
    for node_id in levels[level]:
        doc_lists = [docs[child_id] for child_id in children[node_id]]
        docs[node_id] = sorted(reduce(operator.add, doc_lists), key=lambda d: d[1], reverse=True)

        keyword_lists = [keywords[child_id] for child_id in children[node_id]]
        keywords[node_id] = sorted(reduce(operator.add, keyword_lists), key=lambda k: k[1], reverse=True)

def get_subtree(node_id):
    node = {
        'id': node_id,
        'size': len(docs[node_id]),
        'keywords': [k[0] for k in keywords[node_id][:5]]
    }
    node['sample'] = node['size'] > SAMPLE_THRESHOLD

    node_children = [get_subtree(child_id) for child_id in sorted(children[node_id], key=lambda c: int(c.split('-')[1]))]
    filtered_children = [child for child in node_children if child]
    
    if filtered_children:
        node['children'] = filtered_children
    
    if node['size'] > 0:
        return node
    else:
        return None

tree = get_subtree('0-1')['children']
print json.dumps(tree, indent=4)

outf1 = open('tree.json', 'wb')
json.dump(tree, outf1, indent=4)
outf1.close()

outf2 = open('docs.json', 'wb')
json.dump({'docs': docs, 'sample_threshold': SAMPLE_THRESHOLD}, outf2, indent=4)
outf2.close()