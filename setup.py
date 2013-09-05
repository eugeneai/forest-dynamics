from distutils.core import setup, Extension




setup(
	name="DME",
	version="0.0.2",
	author="Evgeny Cherkashin",
	author_email="eugeneai@icc.ru",
	description="Dynamic Modelling Environment",
	packages=['dme'],
	package_dir={'dme':'LIB'},
	ext_modules=[Extension( "dme.DModel",
		sources=["SRC/DModel.c"],
		)
	]
)