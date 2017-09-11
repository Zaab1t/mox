#!/usr/bin/env bash

DIR=$(dirname ${BASH_SOURCE[0]})

cd $DIR

source ../python-env/bin/activate

python load.py
