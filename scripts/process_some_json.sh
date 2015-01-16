#!/bin/bash

num_cores=$1
num_files=$2

echo "listing raw documents\n"

find data/json/raw -type f | xargs -n1 -I {} basename {} .json | sort > persistence/raw_document_ids

processed_num=$(wc -l persistence/raw_document_ids)

echo "... $processed_num documents processed already\n\n"

echo "listing already-processed documents\n"

find data/json/processed -type f | xargs -n1 -I {} basename {} .json | sort > persistence/processed_document_ids

processed_num=$(wc -l persistence/processed_document_ids)

echo "... $processed_num documents processed already\n\n"

comm -13 persistence/processed_document_ids persistence/raw_document_ids > persistence/to_be_processed

head -n $2 persistence/to_be_processed | xargs -P $num_cores -n1 -I {} python models/pos_tagger.py data/json/processed data/json/raw/{}.json

rm persistence/to_be_processed
