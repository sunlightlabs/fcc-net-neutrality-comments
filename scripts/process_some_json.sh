#!/bin/bash

num_cores=$1
num_files=$2

find data/json/raw -type f -size -10k | head -n $2 | xargs -P $num_cores -n1 -I {} python models/pos_tagger.py data/json/processed {}
