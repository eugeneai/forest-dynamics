#!/bin/bash

if [ "x$1" == "x" ] ; then
    echo "The program ins installed into a directory."
    echo "Please supply the name of the directory as"
    echo "the first parameter of the install.sh script."
    exit 1
fi

TARGET_DIR=$1

echo "Ok, installing into $TARGET_DIR"
