from Numeric import *
from mutils import *
from biomass import *
from free import *
from spelper import *
from logging import *

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
		#print "No more scenarios"
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

LAST=50

def biomass (name):
	name="biomass_"+name
	val=globals()[name]
	print val.V[LAST],

def free(name):
	name="free_"+name
	val=globals()[name]
	print val.S[LAST],
	
def spel_per(name):
	name="spelper_"+name
	val=globals()[name]
	print val.S[LAST],


def logging(name): 
	name="logging_"+name
	val=globals()[name]
	#print val
	v=val.V
	vv=v.logged_101 + v.logged_102 + v.logged_103 + v.logged_104+v.logged_125 + v.logged_124
	s=0
	for vi in vv:
		s+=vi
	print s,

def do_etwas(name, descr):
	print name, # the variable part of the variable
	biomass (name)
	free(name)
	spel_per(name)
	logging(name)
	print

def main():
	(name, descr)=get_first_scen('')
	while 1:
		do_etwas(name, descr)
		try:
			(name, descr)=get_next_scen('', descr)
		except RuntimeError:
			return

if __name__=="__main__":
	import sys
	f=open("_result.txt","w")
	stdout=sys.stdout
	sys.stdout=f
	main()
	print
	print "Legend:"
	print "Senario_name V_biomass S_free S_spel_per Sum_logging"
	sys.stdout=stdout
	f.close()

