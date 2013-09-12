from Numeric import *
from mutils import *
from biomass import *
from free import *
from spelper import *

def open1(name, mode):
	f=open(name, mode)
	f.write("from mutils import *\nfrom Numeric import *\n")
	return f

next_data={
	"low":(0,"middle"),
	"middle":(0,"high"),
	"high":(1,"low"),
}

def get_next_descr(prev):
	answer=[]
	p=list(prev)
	p.reverse()
	carry=1
	for d in p:
		if carry:
			(carry, next)=next_data[d]
		else:
			next=d
		answer.append(next)

	if carry:
		print "No more scenarios"
		raise RuntimeError, "no more scenarios"

	answer.reverse()
	return tuple(answer)

def get_name(name, descr):
	return name+"_".join(list(descr))

def get_first_scen(name):
	descr=("low","low","low","low")
	return (get_name(name,descr),descr)

def get_next_scen(name,prev_descr):
	descr=get_next_descr(prev_descr)
	return (get_name(name,descr), descr)

def biomass ():
	pname="biomass_"
	(name, descr)=get_first_scen(pname)
	n=1
	f=open1("biomass_good.py", "w")
	while n:
		bio=globals()[name]
		prev=None
		skip=0
		for i in range(len(bio.V)):
			v=bio.V[i]
			if prev is None:
				prev=v
				continue
			if v<prev:
				skip=1
				break
			prev=v
		if not skip:
			print "saved", name
			bio.save(f,name)
		else:
			print "Skip", name
		try:
			(name, descr)=get_next_scen(pname, descr)
		except RuntimeError:
			n=0
	f.close()

def free():
	pname="free_"
	(name, descr)=get_first_scen(pname)
	n=1
	f=open1("free_good.py", "w")
	while n:
		sq=globals()[name]
		prev=None
		skip=0
		for i in range(len(sq.S)):
			v=sq.S[i]
			if prev is None:
				prev=v
				continue
			if v>prev:
				skip=1
				break
			prev=v
		if not skip:
			print "saved", name
			sq.save(f,name)
		else:
			print "Skip", name
		try:
			(name, descr)=get_next_scen(pname, descr)
		except RuntimeError:
			n=0
	f.close()

def spel_per():
	pname="spelper_"
	(name, descr)=get_first_scen(pname)
	n=1
	f=open1("spelper_good.py", "w")
	while n:
		sq=globals()[name]
		prev=None
		skip=0
		for i in range(len(sq.S)):
			v=sq.S[i]
			if prev is None:
				prev=v
				continue
			if v<prev:
				skip=1
				break
			prev=v
		if not skip:
			print "saved", name
			sq.save(f,name)
		else:
			print "Skip", name
		try:
			(name, descr)=get_next_scen(pname, descr)
		except RuntimeError:
			n=0
	f.close()

from logging import *

def logging(): #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
	# неуменьшение объема рубок
	LS=62.0
	pname="logging_"
	(name, descr)=get_first_scen(pname)
	n=1
	f=open1("logging_good.py", "w")
	l=51
	while n:
		sq=globals()[name]
		prev=None
		skip=0
		v=sq.V
		vv=v.logged_101 + v.logged_102 + v.logged_103 + v.logged_104+v.logged_125 + v.logged_124
		vv[0]=vv[1]
		#print vv
		#v=LS-v
		#print v
		for i in range(51):
			v=vv[i]
			if prev is None:
				prev=v
				continue
			if v<prev:
				skip=1
				break
			prev=v
		if not skip:
			print "saved", name
			vv=ModelParameter({"V":vv})
			vv.save(f,name)
		else:
			print "Skip", name
		try:
			(name, descr)=get_next_scen(pname, descr)
		except RuntimeError:
			n=0

	f.close()

from coex import *
PART_MAX=1
def check(v, (amin, amax)):
	for a in v:
		a=abs(a)
		#print "->", amin, a, amax
		if a <= amax and a>=amin :
			continue
		return 0
	return 1

def checkall(v):
	for a in v.__dict__.keys():
		k=a
		if k[0]=="_":
			continue
		a=v.__dict__[a]
		#print "->", k
		range=prep(a[0])
		if not check(a, range):
			return 0
	return 1 
	
def prep(v):
	v=abs(v)
	return (v-v*PART_MAX, v+v*PART_MAX)
	
def coexistance():
	pname="coex_"
	(name, descr)=get_first_scen(pname)
	n=1
	f=open1("coex_good.py", "w")
	while n:
		sq=globals()[name].m_59
		del sq.S.logged_101,sq.S.logged_102,sq.S.logged_103,sq.S.logged_104,sq.S.logged_124,sq.S.logged_125
		del sq.S.cult_101
		prev=None
		skip=0
		
		v=sq.S
		skip= not checkall(v)
		if not skip:
			print "saved", name
			sq.save(f,name)
		else:
			print "Skip", name
		try:
			(name, descr)=get_next_scen(pname, descr)
		except RuntimeError:
			n=0
	f.close()


if __name__=="__main__":
	#biomass()
	#free()
	#spel_per()
	#logging()
	coexistance()

