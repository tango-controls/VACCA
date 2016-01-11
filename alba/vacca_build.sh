#!/bin/sh

if [ ! $1 ] ; then
 echo "Prefix Argument is Required"
 exit 1
fi

function vcp {
 if test -e ${PREFIX}/$2 ; then
   rm -rf ${PREFIX}/$2
 fi
 cp -vrf ${VACCA_DIR}/$1 ${PREFIX}/$2
}

VACCA_DIR=$(dirname $0)/../
PREFIX=$1
VACCA_LIB=lib/python/site-packages/vacca

echo "Deploying VACCA files from ${VACCA_DIR} into ${PREFIX}"

mkdir ${PREFIX}/bin
mkdir -p ${PREFIX}/doc/vacca
mkdir -p ${PREFIX}/applications/vacca
mkdir -p ${PREFIX}/lib/python/site-packages

vcp vacca ${VACCA_LIB}
vcp vaccagui lib/python/site-packages/vaccagui
vcp bin/vacca_run.py applications/vacca/vacca_run.py
vcp bin/vaccagui bin/vaccagui

#Local files are installed into applications folder
echo "vacca@controls"

# cp -rf local/config/* dist/applications/vacca/ #Folder used when custom libraries are needed
# cp -rf VaccaMAX/kits-maxiv-lib-maxiv-svgsynoptic/src dist/applications/vacca/svgsynoptic
# cp -rf VaccaMAX/lib-maxiv-maxwidgets/src dist/applications/vacca/maxwidgets
# #cp -rf local/config/default.py local/config/filters.py local/config/beamlines.py dist/lib/python/site-packages/vacca/
# #cp -rf local/config/* dist/lib/python/site-packages/vacca/ #Folder used when custom libraries are needed

if test -e ${VACCA_DIR}/alba ; then
  cp -vrf ${VACCA_DIR}/alba/config/* ${PREFIX}/applications/vacca/
  vcp alba/vacca bin/vacca
  vcp alba/vaccagui bin/vaccagui
  vcp alba/doc applications/doc
  vcp alba/extra_vacca ${VACCA_LIB}/extra
  vcp alba/desktop ${VACCA_LIB}/desktop
  
  echo "Overriding default.py"
  mv -v ${PREFIX}/applications/vacca/default.py ${PREFIX}/${VACCA_LIB}/default.py
  mv -v ${PREFIX}/applications/vacca/beamlines.py ${PREFIX}/${VACCA_LIB}/beamlines.py
  mv -v ${PREFIX}/applications/vacca/filters.py ${PREFIX}/${VACCA_LIB}/filters.py
fi

#Last touch

vcp bin/vacca_run.py applications/vacca/vacca_run.py
vcp examples applications/vacca/examples

echo "cleaning temp files"
cd ${PREFIX}
rm -rf $(find -name "*pyc" -o -name "*~" -o -name ".svn")

echo "VACCA Structure successfully merged at ${PREFIX}"

