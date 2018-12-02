#!/bin/bash

export NOW=$(date +%Y%m%d%H%M%S)
export THIS=$(basename $0)
export RUNAS=$(whoami)
export WHEREAMI=$(dirname $0)

SUBDIR="${1}"

PLANS="${WHEREAMI}/plans"

if [ -z "${SUBDIR}" ]
then
	echo "subdir not provided" && exit 99
fi

if [ -d "${PLANS}/${SUBDIR}" ]
then
	echo "found subdir ${PLANS}/${SUBDIR}"
else
	echo "could not find subdir ${PLANS}/${SUBDIR}"
fi

#echo "# ${SUBDIR^}" > ${WHEREAMI}/${SUBDIR}/README.md
#echo >> ${WHEREAMI}/${SUBDIR}/README.md

for YAML in $(ls ${PLANS}/${SUBDIR}/*.yaml)
do

	filename=$(basename $YAML)
	extension="${filename##*.}"
	filename="${filename%.*}"
	
	echo $filename
	
	if [ -d ${PLANS}/${SUBDIR}/${filename} ]
	then
		rm -rf ${PLANS}/${SUBDIR}/${filename}
	fi
	
	set -x
	python ${WHEREAMI}/src/main.py --output ${PLANS}/${SUBDIR}/${filename}  --config ${PLANS}/${SUBDIR}/${filename}.yaml --save
	set +x

done


