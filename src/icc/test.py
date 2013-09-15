from icc.dme.fd.dm import *
import sys
import jsonpickle

class BB(object):
    """
    """

    def __init__(self, ):
        """
        """



class TestConnect(object):
    """Test Class
    """

    def __init__(self):
        """Init
        """
        A=DMItem(1)
        B=DMItem(2)
        C=DMConnect(A, B, 0.1)
        self.y={0:BB()}
        self.z=self.y.items()
        self.b=BB()
        #self.c=C

def main():
    rc=None
    a=TestConnect()
    rc=jsonpickle.encode(a)
    print (rc)
    b=jsonpickle.decode(rc)
    print b.b

    """
    rc=gnosis.xml.pickle.dumps(a)
    print rc
    b=gnosis.xml.pickle.loads(rc)
    print b.__class__
    """


main()

quit()
