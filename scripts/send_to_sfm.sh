#! /bin/bash

fname=$1
#nfile=$2

title=$(basename $fname)
text=$(jq .text $fname)

command="curl -sS -X POST -H \"Expect:\" -d \"title=$title\" -d \"group=monkees\" --data-urlencode text=$text 0.0.0.0:8080/document/1/"
eval $command > /dev/null
