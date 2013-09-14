from icc.dme.fd.dm import *
import pyxser

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
        self.y={0:"1"}
        self.b=BB()
        self.c=C

def main():
    rc=None
    a=TestConnect()
    rc=pyxser.serialize(a, enc='utf-8')

    print rc

main()

quit()
