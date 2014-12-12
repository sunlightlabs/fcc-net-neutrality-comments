import json, sys, re
colors = {'PRO': ["#0f8c79", "#074a3f"], 'ANTI': ['#bd2d28', '#5e1614'], '???': ['#978F80', '#5B564D']}
j = json.load(open(sys.argv[1]))

# count
from collections import Counter
from colour import Color

pa_count = Counter()
for item in j:
    pa_count[item['pro_anti']] += 1

for pa, count in pa_count.items():
    if count > len(colors[pa]):
        colors[pa] = [str(c) for c in Color(colors[pa][0]).range_to(Color(colors[pa][1]), count)]

transform_id = lambda i: re.sub(r'[^a-z0-9_-]', '', re.sub(r'\s+', '_', i.lower()))

for item in j:
    item['color'] = colors[item['pro_anti']].pop(0)
    item['id'] = transform_id(item['id'])
    item['pro_anti']
print json.dumps(j, indent=4)
