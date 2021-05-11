#!/bin/bash

set -e

export NOW=$(date +%Y%m%d%H%M%S)
export THIS=$(basename $0)
export RUNAS=$(whoami)
export WHEREAMI=$(dirname $0)

${WHEREAMI}/.venv/Scripts/python ${WHEREAMI}/src/main.py --output out/dev  --config example.yaml --save --verbose
#python ${WHEREAMI}/src/main.py --output out/dev  --config example.yaml --save --verbose



