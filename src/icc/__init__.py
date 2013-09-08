#@+leo-ver=5-thin
#@+node:eugeneai.20110116000634.1447: * @file __init__.py
#@@language python
#@@tabwidth -4
#@+others
#@+node:eugeneai.20110116000634.1448: ** namespace declarations
# this is a namespace package
try:
    import pkg_resources
    pkg_resources.declare_namespace(__name__)
except ImportError:
    import pkgutil
    __path__ = pkgutil.extend_path(__path__, __name__)
#@-others
#@-leo
