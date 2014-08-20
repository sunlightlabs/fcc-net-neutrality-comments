#! /bin/bash 
SAVEIFS=$IFS
IFS=$(echo -en "\n\b")

doctype=1
parent=$1

for dir in `find $1 -type d`
do
	docid=1
	for file in `find $dir -maxdepth 1 -type f -name *.json`
	# Smallest first
	# for file in `ls -ASr $dir | grep $filemask`
	# Largest first
	# for file in `ls -ASR $dir | grep $filemask`
	# Unsorted
	# for file in `ls -A $dir | grep $filemask
	do
		group=${dir#$parent/}
		title=$(basename $file)
		text=$(jq .text $file)
		command="curl -sS -X POST -H \"Expect:\" -d \"title=$title\" -d \"group=$group\" --data-urlencode text=$text 0.0.0.0:8080/document/$doctype/$docid/"
		#echo $command
		eval $command > /dev/null
		docid=$(($docid+1))
		# NPROC=$(($NPROC+1))
		# if [ "$NPROC" -ge 4 ]; then
		# 	  wait
		# 	  NPROC=0
		# fi
	done
	doctype=$(($doctype+1))
done
IFS=$SAVEIFS


