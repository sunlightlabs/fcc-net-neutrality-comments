#!/bin/bash

num_cores=$1

find data/json/raw -type f -size -10k | xargs -P $num_cores -n1 -I {} python models/pos_tagger.py data/json/processed {}

find data/json/processed -type f | xargs -n1 -I {} basename {} .json | sort > persistence/processed_document_ids
