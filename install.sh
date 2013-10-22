#!/bin/bash

PYTHON_VERSION=2
PYTHON=python$PYTHON_VERSION
VIRT_PREF="(dme)"

ICC_DME_BRANCH="master"
PYGOBJECT_V="3.8.3"
CAIRO_V="1.10.0"


# DEBUG="1"
DEBUG="" 

if [ "x$DEBUG" == "x" ] ; then
    if [ "x$1" == "x" ] ; then
        echo "The program is installed into a directory."
        echo "Please supply the name of the directory as"
        echo "the first parameter of the install.sh script."
        exit 1
    fi
TARGET_DIR=$1
else
    TARGET_DIR="python-test"
fi

ROOT=$PWD
FULL_TARGET="$ROOT/$TARGET_DIR"

echo "Ok, installing into $FULL_TARGET"

export LC_ALL=C

if [ ! -e $TARGET_DIR/bin/activate ]; then
    VE=virtualenv$PYTHON_VERSION
    VE=$(which $VE)
    if [ "x$VE" = "x" ] ; then
        echo "There are no virtualenv executable."
        echo "Please install it in your distribution or"
        echo "read http://www.virtualenv.org/"
        exit 0
    fi
    #if [ ! -x "$VE" ]; then
    #    echo "Virtualenv script is found but it is not"
    #    echo "executable. please check $VE."
    #fi
    echo "Installing virtual environment into $TARGET_DIR"
    $VE $TARGET_DIR --prompt=$VIRT_PREF
fi

. $TARGET_DIR/bin/activate

git submodule init
git submodule update

cd submodules
cd jsonpickle
python setup.py install
cd ../DME
python setup.py develop
cd ../py-prisnif
    ./install.sh
cd ../..

tmp=tmp-install

mkdir -p $tmp

cd $tmp

pip install numpy

$PYTHON -c "import cairo"
rc=$?

if [ $rc -ne 0 ]; then
    echo "Installing Cairo."
    wget -c http://cairographics.org/releases/py2cairo-$CAIRO_V.tar.bz2
    tar xjvf py2cairo-$CAIRO_V.tar.bz2
    cd py2cairo-$CAIRO_V
    ./waf configure --prefix=$FULL_TARGET
    ./waf build
    ./waf install
    cd ..
    rm -rf py2cairo-$CAIRO_V
fi

$PYTHON -c "import gi"
rc=$?
if [ $rc -ne 0 ]; then

    echo "Installing PyGTK3."

    wget -c http://ftp.gnome.org/pub/GNOME/sources/pygobject/3.8/pygobject-$PYGOBJECT_V.tar.xz
    tar xJf pygobject-$PYGOBJECT_V.tar.xz
    cd pygobject-$PYGOBJECT_V
    PYTHON=$FULL_TARGET/bin/$PYTHON ./configure --prefix=$FULL_TARGET
    make install
    cd ..
    rm -rf pygobject-$PYGOBJECT_V
fi

$PYTHON -c "import pyxser"
rc=$?
if [ $rc -ne 0 ]; then

    echo "Installing pyxser."

    pip install https://github.com/eugeneai/pyxser/archive/master.zip
fi

cd ..


$PYTHON -c "import icc.xray"
rc=$?
if [ $rc -ne 0 ]; then
#    pip install https://github.com/eugeneai/dispersive/archive/$ICC_DME_BRANCH.zip
    cd submodules/dispersive
    $PYTHON setup.py develop
    cd ../..
fi

cd submodules/xdot
$PYTHON setup.py install
cd ../..

$PYTHON setup.py develop

rm -rf tmp-install