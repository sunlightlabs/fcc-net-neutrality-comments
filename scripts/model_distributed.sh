#!/bin/bash

export PYRO_SERIALIZERS_ACCEPTED=pickle
export PYRO_SERIALIZER=pickle

MODEL_TYPE=$1
NUM_TOPICS=$2

taskset -c 1 python -m gensim.models.${MODEL_TYPE}_worker &
taskset -c 2 python -m gensim.models.${MODEL_TYPE}_worker &
taskset -c 3 python -m gensim.models.${MODEL_TYPE}_worker &
taskset -c 0 python -m gensim.models.${MODEL_TYPE}_dispatcher &

taskset -c 0 python scripts/build_distributed_model.py $MODEL_TYPE $NUM_TOPICS
