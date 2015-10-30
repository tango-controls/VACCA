#!/bin/sh

if [ -e generate-sphinx.sh ] ; then
 TARGET=$(pwd)
 cd ..
else
 TARGET=$(pwd)/autodoc
fi

CMD="sphinx-apidoc -F -e -o $TARGET vacca"
$CMD
cd $TARGET
make html
ln -s _build/html

