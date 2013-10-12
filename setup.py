from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages, Extension
from distutils import log
#import celerid.support as cs
from celerid.support import setup, Extension
import celerid, setuptools

log.set_verbosity(100)

setup(
    zip_safe = True,
	name="icc.dme",
	version="0.0.4",
	author="Evgeny Cherkashin",
	author_email="eugeneai@irnok.net",
	description="Dynamic Modelling Environment",

    packages=find_packages("src"),
    package_dir={"": "src"},
    namespace_packages=["icc"],

    install_requires=[
        "setuptools",
        "icc.xray",
        "jsonpickle",
        "xlrd",
        "pygraphviz",
        "xdot"
    ],

	ext_modules=[
        Extension("icc.dme.fd.DModel",
                  sources=["src/icc/dme/fd/C/DModel.c"],
        ),
        Extension("icc.prisnif.atp",
                  sources=["src/icc/atp/src/atp.d"],
        )
	],

    scripts = ['src/icc/icc_dme_app.py'],
    package_data = {
        'icc.dme.views': ['ui/*.glade',] #  "ui/icons/tango/16x16/*/*.png"],
        },
    license = "GNU GPL",
    keywords = "fores resources pygtk analysis tool application",

    long_description = """ """,

    # platform = "Os Independent.",
    # could also include long_description, download_url, classifiers, etc.

)
