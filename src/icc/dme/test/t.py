#! /usr/bin/env python

import DModel as d

a=d.NewItem()
b=d.NewItem()

a.next=b
b.next=a




del a
del b
d.Finalize(2)