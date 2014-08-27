from glob import iglob
import json
import os
flocs = iglob('data/json/raw/*.json')
applicants = {}
for floc in flocs:
    with open(floc, 'r') as fin:
        jd = json.load(fin)
        applicants[jd['id'].strip()] = jd.get('applicant', '')

with open('cluster_viz/applicants.json','w') as fout:
    json.dump(applicants, fout)
