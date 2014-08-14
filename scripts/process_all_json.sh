#!/bin/bash

num_cores=$1

tail -n+2 stats/reasonable_length_files.csv | cut -d , -f 2 | xargs -P $num_cores -n1 -I {} python models/pos_tagger.py data/json/processed {}
