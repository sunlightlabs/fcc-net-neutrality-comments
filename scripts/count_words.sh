#!/bin/bash

for fn in `find data/json/raw -type f`; do cat $fn | jq .text | wc -w; done
