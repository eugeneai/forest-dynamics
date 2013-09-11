from zope.interface import implements
from interfaces import *

class Project(object):
    implements(IProject)
    def __init__(self):
        self.test_attr="test"
