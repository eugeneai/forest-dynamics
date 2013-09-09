from Numeric import *
from mutils import *
from scenarios2 import *
import mx.ODBC.Windows as ODBC

def get_volume(dsn, year):
	conn=ODBC.connect(dsn=dsn, user="", password="")
	cursor=conn.cursor()
	query='select kind, V1 as mol1, V2 as mol2, Vsr as srd, Vpr as prs, VIspper as spl_per, Vper as per from "S%s$"' % year
	#print query
	cursor.execute(query)
	#print cursor.description
	#print cursor.fetchall()
	rc=ModelParameter()
	data=cursor.fetchone()
	s=0
	while data:
		(kind, mol1, mol2, srd, prs, spl_per, per)=data
		spl=spl_per - per
		kind=int(kind)
		setattr(rc, "mol1_%i" % kind, mol1)
		setattr(rc, "mol2_%i" % kind, mol2)
		setattr(rc, "srd_%i" % kind, srd)
		setattr(rc, "prs_%i" % kind, prs)
		setattr(rc, "spl_%i" % kind, spl)
		setattr(rc, "per_%i" % kind, per)
		s+=mol1+ mol2+ srd+ prs+ spl_per
		data=cursor.fetchone()
	print "Summ vol:", s
	return ModelParameter({"V":rc})

START_VOL=get_volume("forest",1973)
START_VOL.save("START_VOL.py","START_VOL")

def concentration(vol, traj):
	s=scen_low_low_low_low.m_59[0]
	return float(vol.V)/float(s.S)

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

ages=("mol1","mol2","per","prs","spl","srd")
spel_pers=("per","spl")
kinds=("101","102","103","104","105","124","125")

M_NAME="m_59"

def get_S(traj):
	return getattr(traj, M_NAME)

def make_attr(age, kind):
	return age+"_"+kind

def biomass(traj):
	conc=concentration(START_VOL, traj)
	#print conc
	S=get_S(traj)
	S=S.S * conc
	#print S - START_VOL.V
	#print S
	summ=0 # S.cult_101.__copy__()
	for age in ages:
		for kind in kinds:
			summ+=getattr(S, make_attr(age, kind))
	return ModelParameter({"V":summ})

def free_area(traj):
	S=get_S(traj)
	S=S.S
	return ModelParameter({"S":S.no_forest___None__})

def spel_per(traj):
	S=get_S(traj)
	S=S.S
	summ=0 #zeros(51)#S.cult_101.__copy__()
	for age in spel_pers:
		for kind in kinds:
			summ+=getattr(S, make_attr(age, kind))
	return ModelParameter({"S":summ})

def write_data(file, varname, descr, traj):
	name=get_name(varname, descr)
	traj.save(file, name)
	# graphics

def coexistance(traj):
	traj=traj.Copy()
	S=get_S(traj)
	S=S.S
	#summ=S.cult_101.__copy__()
	for kind in kinds:
		all=0.0
		if kind=="101":
			all+=S.cult_101
		for age in ages:
			all+=getattr(S, make_attr(age, kind))
		if kind=="101":
			S.cult_101 /= all
		for age in ages:
			setattr(S, make_attr(age, kind), getattr(S, make_attr(age, kind)) / all)
	del S.no_forest___None__
	return traj

def logging_vol(traj):
	conc=concentration(START_VOL, traj)
	traj=traj.Copy()
	S=get_S(traj)
	S=S.S
	rc=ModelParameter()
	for kind in kinds:
		attr=make_attr("logged", kind)
		spl=make_attr("spl", kind)
		per=make_attr("per", kind)
		if kind<>"105": # 105 is not loggable
			logged=getattr(S, attr)
			sspl=getattr(S, spl)
			sper=getattr(S, per)
			s=sspl+sper
			cspl=getattr(conc, spl)
			cper=getattr(conc, per)
			v=logged*((cspl * sspl / s) + (cper * sper / s))
			#v=logged * cspl
			setattr(rc, attr, v)
	return ModelParameter({"V":rc})

def open1(name, mode):
	f=open(name, mode)
	f.write("from mutils import *\nfrom Numeric import *\n")
	return f

def main():
	pname="scen_"
	n=1
	(name, descr)=get_first_scen(pname)
	fbio=open1("biomass.py","w")
	ffree=open1("free.py","w")
	fsp=open1("spelper.py","w")
	#fco=open1("coex.py","w")
	flog=open1("logging.py","w")
	while n:
		print name
		val=globals()[name]
		write_data(fbio, "biomass_", descr, biomass(val))
		write_data(ffree, "free_", descr, free_area(val))
		write_data(fsp, "spelper_", descr, spel_per(val))
		#write_data(fco, "coex_", descr, coexistance(val))
		write_data(flog, "logging_", descr, logging_vol(val))

		try:
			(name, descr)=get_next_scen(pname, descr)
		except RuntimeError:
			n=0
	fbio.close()
	fsp.close()
	ffree.close()
	#fco.close()
	flog.close()

if __name__=="__main__":
	main()
