from zope.interface import implements
from interfaces import *

from icc.dme.fd import *
from icc.rake.views import get_user_config_option, set_user_config_option

class Project(object):

    implements(IProject)

    def __init__(self):
        self.setup_test_model()

    def setup_test_model(self):
        excel_file=get_user_config_option("source", type='string', keys='data_source')
        if excel_file == None:
            raise ValueError, "Forest data source is not supplied"
        self.fm = ForestModel(excel_file, "1973",
#		options={"NO_LOGGING":None, "NO_FIRES":None, "NO_INTERCHANGE":None}
#		options={"NO_INTERCHANGE":None}
#		options={"NO_INTERCHANGE":None,"NO_LOGGING":None, "NO_FIRES":None, "NO_GET":None}
		options={"NO_INTERCHANGE":None,"NO_FIRES":None, "NO_GET":None}
        )
