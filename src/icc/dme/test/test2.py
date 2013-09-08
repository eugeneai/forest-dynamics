#! /usr/bin/env python

import DModel as d


#nodes=8000*10*5
nodes=80000
numit=10

print "Preparing", nodes, "nodes..."

head=None
prev=None

nn= 0.1/nodes

tot=[]

for i in range(nodes):
    n=d.NewItem()
    if not head:
	head=n
    else:
	prev.next=n
	e=d.NewItem()
	prev.another=e
	prev.value=i
#	print prev.value
	e.value = i * nn
	e.another=n

    tot.append(n)    
    prev=n
    
    if i % 10000 == 0: print i

#del n    
#del prev
#del e
    
    
print "done."

print "agr:", d.total(tot), " whole:", head.total

head.step(0.1, numit)

print "end agr:", d.total(tot), " whole:", head.total

head.reset()

print "end agr after reset:", d.total(tot), " whole:", head.total

del head
del e
del n
del prev

d.Finalize() 