#! /usr/bin/env python

import DModel as d

# print "methods:", d.__dict__

agr1=[]
agr2=[]

a=d.NewItem()
b=d.NewItem()
a.next=b
a.initValue=1
b.initValue=2
a.value=1
b.value=2
agr2.append(b)
agr1.append(agr2)
agr1.append(a)
agr1.append((1,))

print agr1, agr2

ab=d.NewItem()
ba=d.NewItem()

ab.another=b
ab.value=0.1
ba.another=a
ba.value=0.2

a.another=ab
b.another=ba


print a.value, b.value
# 1 2

numit=5000

for i in range(numit):
    a.step(0.1, 1)
print a.value, b.value, d.total(agr1,0)

a.value=a.initValue
b.value=b.initValue

a.step(0.1,numit);
print a.value, b.value, d.total(agr1,0)

del a
del b
del ab
del ba
d.Finalize()
del d

# 1.3 1.7