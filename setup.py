from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, Extension

setup(
	name="DME",
	version="0.0.3",
	author="Evgeny Cherkashin",
	author_email="eugeneai@icc.ru",
	description="Dynamic Modelling Environment",
	packages=['dme'],
	package_dir={'dme':'src'},
	ext_modules=[Extension( "dme.DModel",
		sources=["src/C/DModel.c"],
		)
	]
)
