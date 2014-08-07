#!/bin/bash

tail stats/reasonable_length_files.csv | cut -d , -f 1 | xargs -P0 -n1 -I {} python models/pos_tagger.py data/json/processed {}
