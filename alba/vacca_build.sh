#!/bin/sh

if [ ! $1 ] ; then
 echo "Prefix Argument is Required"
 exit 1
fi

VACCA_DIR=$(dirname $0)/../
PREFIX=$1

echo "Deploying VACCA files from ${VACCA_DIR} into ${PREFIX}"

mkdir ${PREFIX}/bin
mkdir -p ${PREFIX}/doc/vacca
mkdir -p ${PREFIX}/applications/vacca
mkdir -p ${PREFIX}/lib/python/site-packages/vacca

function vcp {
 cp -vrf ${VACCA_DIR}/$1 ${PREFIX}/$2
}

vcp bin/vacca_run.py applications/vacca
vcp examples applications/
vcp vacca lib/python/site-packages

#Local customization from local SVN

if ! test -e ${VACCA_DIR}/local ; then
  
fi
