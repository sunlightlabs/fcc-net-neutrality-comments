import json, operator, os

tree = json.load(open("tree.json"))
CUTOFF = 100

def tree_walk(nodes):
    for node in nodes:
        if node['size'] <= CUTOFF:
            # we output a thing
            items = item_walk(node)
            out_items = []

            for item in items:
                ii = json.load(open(os.path.join("data", item)))
                oi = {
                    'id': ii['id'],
                    'title': 'Comment from %s' % ii['applicant']
                }
                out_items.append(oi)

            outf = open(os.path.join("tree_data", "%s.json" % node['id']), "wb")
            json.dump({
                'id': node['id'],
                'items': out_items
            }, outf)
            outf.close()

            print items

        if 'children' in node:
            tree_walk(node['children'])

def item_walk(node):
    if 'items' in node:
        return node['items']
    elif 'children' in node:
        return reduce(operator.add, [item_walk(child) for child in node['children']])
    else:
        return []

tree_walk(tree)