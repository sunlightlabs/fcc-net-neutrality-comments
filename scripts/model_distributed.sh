#!/bin/bash

export PYRO_SERIALIZERS_ACCEPTED=pickle
export PYRO_SERIALIZER=pickle

MODEL_TYPE=$1
NUM_TOPICS=$2
NUM_CORES=$3

default_suffix=''
FNAME_SUFFIX=${4:-$default_suffix}

PID_FILE='/tmp/gensim_pids'

python -m Pyro4.naming -n 0.0.0.0 &
echo $! > $PID_FILE

for i in `seq 1 $NUM_CORES`
do
	taskset -c $i python -m gensim.models.${MODEL_TYPE}_worker &
	echo $! >> $PID_FILE
done

taskset -c 0 python -m gensim.models.${MODEL_TYPE}_dispatcher &
echo $! >> $PID_FILE

taskset -c 0 python scripts/build_distributed_model.py $MODEL_TYPE $NUM_TOPICS $FNAME_SUFFIX

while read p;
do
    kill $p;
done <$PID_FILE
