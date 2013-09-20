#!/bin/env python2
# encoding: utf-8
from dm import *
from numpy import *
import types
import math
import xlrd

TableKind={
	101:"СОСНА",
	102:"ЕЛЬ",
	103:"ПИХТА",
	104:"ЛИСТВЕННИЦА",
	105:"КЕДР",
	107:"ИТОГО ХВОЙНЫХ",
	124:"БЕРЕЗА",
	125:"ОСИНА",
	126:"ОЛЬХА СЕРАЯ",
	131:"ТОПОЛЬ",
	132:"ИВЫ ДРЕВОВИДНЫЕ",
	133:"ИТОГО МЯГКОЛИСТВЕННЫХ",
}

TableKindTranslit={
	101:"SOSNA",
	102:"EL",
	103:"PIKHTA",
	104:"LISTVENNITSA",
	105:"KEDR",
	107:"ITOGO KHVOINYH",
	124:"BEREZA",
	125:"OSINA",
	126:"OLKHA SERAYA",
	131:"TOPOL",
	132:"IVY DREVOVIDNYYE",
	133:"ITOGO MYAKGOLISTVENNYH",
}

TableEncoding='utf-8'

ForestKind={
	101:1,
	102:1,
	103:1,
	104:1,
	105:1,
	124:1,
	125:1,
	126:1,
	131:1,
	132:1,
}

VarNames={
	"Kind":1,
	"S1":1,
	"S2":1,
	"Ssr":1,
	"Spr":1,
	"Ssp":1,
	"Sper":1,
	"SIspper":1,
	"V1":1,
	"V2":1,
	"Vsr":1,
	"Vpr":1,
	"Vsp":1,
	"Vper":1,
	"VIspper":1,
	"L01":1,
	"Lk1":1,
	"L12":1,
	"L23":1,
	"L34":1,
	"L45":1,
	"L56":1,
	"Ssp101":1,
	"Ssp102":1,
	"Ssp103":1,
	"Ssp104":1,
	"Ssp105":1,
	"Ssp124":1,
	"Ssp125":1,
	"Sper101":1,
	"Sper102":1,
	"Sper103":1,
	"Sper104":1,
	"Sper105":1,
	"Sper124":1,
	"Sper125":1,
}

Transitions={
	101:20,
	102:20,
	103:20,
	104:20,
	105:40,
	124:10,
	125:10,
	126:10,
	131:10,
	132:10,
};

kind_exchange=100

logging=0.02

def f__add__(a,b):
	return a+b

FuncTransTable={
	"__add__": lambda x,y: x+y,
	"__sub__": lambda x,y: x-y,
	"__mul__": lambda x,y: x*y,
	"__div__": lambda x,y: x/y,
#	"__float__": lambda x: float(x),
}

def SpecialName(s):
	if s=="":
		return 1
	if s[0]=="_":
		if len(s)>1 and s[1]!="_":
			return 1
		else:
			return 0
		return 1
	return 0

def Interpret(func, value):
	global FuncTransTable
	dct={}
	dct.update(value.__dict__)
	del dct["_primitive"]
	args=dct.items()
	args.sort()
	args=map(lambda x: x[1], args)	# get values
	a=[]
	for arg in args:
		if type(arg)==types.InstanceType:
			for (key,val) in arg.__dict__.items():
				if key[:2]=="__":
					res=Interpret(key, val)
					# print "val:", val, "res:", res, "key:", key
					a.append(res)
					break	# should be only one
		else:
			a.append(arg)
	return apply(FuncTransTable[func], a)	# a function call

def NewItem():
#	return DMItem(DModel.NewItem())
	return DModel.NewItem()

class ModelParameter:
    def __init__(self, parameters_dict=None, primitive=0):
		if parameters_dict is None:
			pass
		else:
			self.__dict__.update(parameters_dict)
			self._keys=parameters_dict.keys()
		self._primitive=primitive

    def keys(self):
        return self._keys

    def item(self, key):
        return getattr(self, key)

    def Convert(self, convert_func, parameter=None):
		answer=ModelParameter(primitive=self._primitive)
		for (key,value) in self.__dict__.items():
			if key[0]=="_" and key[1]!="_":
				continue
			#print "key:", key,
			if type(value)==types.InstanceType:
				setattr(answer, key, value.Convert(convert_func, parameter))
			else:
				setattr(answer, key, convert_func(value, parameter))
			#print
		return answer

    def __repr__(self):
		return self.ReprTree("")

    def ReprTree(self, branchName):
		s=""
		items=self.__dict__.items()
		items.sort()
		for (key,value) in items:
			if key[0]=="_" and key[1]!="_":
				continue
			if branchName is None:
				name=key
			else:
				name=".".join([branchName,key])
			if type(value)==types.InstanceType:
				#print "name:", key, value
				s+=value.ReprTree(name)
			else:
				s+="%s: %s\n" % (name, str(value))
		return s

    def ForEachDo(self, leaf_func, parameter=None, branch_func=None, branch=None):
        """
        branch_func must return 0 if not to go down the branches
        if branch_func==None then the search always go down to the leaves
        """
        items=self.__dict__.items()
        items.sort()
        for (key,value) in items:
            if key.startswith("_"):
                continue
            if branch is None:
                br=[key]
            else:
                br=branch+[key]
            if type(value)==types.InstanceType:
                if branch_func is None or branch_func(br, value, parameter):
					value.ForEachDo(leaf_func, parameter, branch_func, br)
            else:
				leaf_func(br, value, parameter)

    def __add__(self, other):
		return self.interpret("__add__", [other])
    def __sub__(self, other):
		return self.interpret("__sub__", [other])
    def __mul__(self, other):
		return self.interpret("__mul__", [other])
    def __div__(self, other):
		return self.interpret("__div__", [other])
#	def __float__(self, other):
#		return self.interpret("__float__", [other])

    def dive(self, func, others):
		items=self.__dict__.items()
		items.sort()
		n=ModelParameter()
		for (key,value) in items:
			if key[0]=="_" and key[1]!="_":
				continue
			o=[]
			for other in others:
				if type(other)==types.InstanceType and other._primitive==0:
					o.append(getattr(other,key))
				else:
					o.append(other)

			if type(value)==types.InstanceType and not value._primitive:
				setattr(n, key, value.dive(func, o))
			else:
				params=[value]+o
				#print "params:", params
				dict={}
				for i in range(len(params)):
					dict["a%s" % str(i)]=params[i]

				setattr(n, key, ModelParameter({func: ModelParameter(dict)}, primitive=1))

		return n

    def interpret(self, func, others):
		items=self.__dict__.items()
		items.sort()
		n=ModelParameter()
		for (key,value) in items:
			if key[0]=="_" and key[1]!="_":
				continue
			o=[]
			for other in others:
				if type(other)==types.InstanceType and other._primitive==0:
					o.append(getattr(other,key))
				else:
					o.append(other)

			if type(value)==types.InstanceType and not value._primitive:
				setattr(n, key, value.interpret(func, o))
			else:
				params=[value]+o
				setattr(n, key, apply(FuncTransTable[func], params))

		return n


class TreeKind:
	def __init__(self, data_row, descrs):
		self.AcceptData(data_row, descrs)
		self.initialize()

	def AcceptData(self, data, descrs):
		global VarNames
		pos=0
		for descr in descrs:
			name=descr
			try:
				VarNames[name]
				self.__dict__[name]=data[pos]
			except KeyError:
				pass
			pos += 1

	def AcceptNaturalTransitionConstants(self, data, descrs):
		return self.AcceptData(data, descrs)

	def AcceptInterchangeConstants(self, data, descrs):
		return self.AcceptData(data, descrs)

	def initialize(self):
		self.normalize()
		# figuring out average concentration
		self.R1=self.V1/self.S1
		self.R2=self.V2/self.S2
		self.Rsr=self.Vsr/self.Ssr
		self.Rpr=self.Vpr/self.Spr
		self.Rsp=self.Vsp/self.Ssp
		self.Rper=self.Vper/self.Sper
		self.RIspper=self.VIspper/self.SIspper	# just for a case
		# building model graph

	def normalize(self):
		try:
			self.SIspper=self.Ssp+self.Sper
		except AttributeError:
			self.Ssp=self.SIspper-self.Sper
		try:
			self.VIspper=self.Vsp+self.Vper
		except AttributeError:
			self.Vsp=self.VIspper-self.Vper
		self.Kind=int(self.Kind)

	def __str__(self):
		return "Forest: "+str(self.Kind)+"\n dict: "+str(self.__dict__)+"\n"

	def __repr__(self):
		return self.__str__()

	def _build(self, value):
		node=NewItem()
		node.value=value
		node.initValue=value
		return node

	def _conn(self, n1, n2, value):
		edge=NewItem()
		edge.value=value
		edge.initValue=value
		edge.next=n1.another
		n1.another=edge
		edge.another=n2

	def BuildModel(self, no_forest, othernodes=None):
		global Transitions
		#trans=1.0/Transitions[self.Kind]
		self.trajectories=None
		self.model=ModelParameter({"S":ModelParameter(), "V":ModelParameter()})
		self.model.S.I=self._build(self.S1); self._conn(no_forest,self.model.S.I, self.L01); # zero state!!!
		self.model._first=self.model.S.I
		self.model.S.II=self._build(self.S2); self._conn(self.model.S.I,self.model.S.II, self.L12)
		self.model.S.I.next=self.model.S.II
		self.model.S.Sr=self._build(self.Ssr); self._conn(self.model.S.II,self.model.S.Sr, self.L23)
		self.model.S.II.next=self.model.S.Sr
		self.model.S.Pr=self._build(self.Spr); self._conn(self.model.S.Sr,self.model.S.Pr, self.L34)
		self.model.S.Sr.next=self.model.S.Pr
		self.model.S.Sp=self._build(self.Ssp); self._conn(self.model.S.Pr,self.model.S.Sp, self.L45)
		self.model.S.Pr.next=self.model.S.Sp
		self.model.S.Per=self._build(self.Sper); self._conn(self.model.S.Sp,self.model.S.Per, self.L56)
		self.model.S.Sp.next=self.model.S.Per

		self.model.S.Per.next=othernodes

		return self.model

	def PrepareStorage(self, obj):
		S=ModelParameter({
			"I":obj.__copy__(),
			"II":obj.__copy__(),
			"Sr":obj.__copy__(),
			"Pr":obj.__copy__(),
			"Sp":obj.__copy__(),
			"Per":obj.__copy__()
		})
		V=ModelParameter({
			"I":obj.__copy__(),
			"II":obj.__copy__(),
			"Sr":obj.__copy__(),
			"Pr":obj.__copy__(),
			"Sp":obj.__copy__(),
			"Per":obj.__copy__()
		})
		return ModelParameter({"S":S,"V":V})

	def FillInValues(self, number, struct):
		S=struct.S
		MS=self.model.S
		#print number, struct, sel.model
		S.I[number]=MS.I.value; S.II[number]=MS.II.value; S.Sr[number]=MS.Sr.value;
		S.Pr[number]=MS.Pr.value; S.Sp[number]=MS.Sp.value; S.Per[number]=MS.Per.value;
		V=struct.V
		MV=self.model.V
		V.I[number]=MV.I; 	V.II[number]=MV.II; V.Sr[number]=MV.Sr;
		V.Pr[number]=MV.Pr; V.Sp[number]=MV.Sp; V.Per[number]=MV.Per;

	def Reset(self):
		pass

	def AfterStates(self, modeller):
		assert 1
		self.model.V.I	= self.R1 * self.model.S.I.value
		self.model.V.II	= self.R2 * self.model.S.II.value
		self.model.V.Sr	= self.Rsr * self.model.S.Sr.value
		self.model.V.Pr	= self.Rpr * self.model.S.Pr.value
		self.model.V.Sp	= self.Rsp * self.model.S.Sp.value
		self.model.V.Per= self.Rper * self.model.S.Per.value


	def BeforeStates(self, modeller):
		pass


class ForestModel:
    def __init__(self, filename, year_id, Snel=0.0, Sempty=0.0, options=None):
        global ForestKind
        if options is None:
            self.options={}
        else:
            self.options=options

        xl=xlrd.open_workbook(filename, formatting_info=True)
        self.filename=filename

        s_page=xl.sheet_by_name("S%s" % year_id)
        g_page=xl.sheet_by_name("grow%s" % year_id)

        self.kinds=[]

        for rn in range(s_page.nrows):
            row=s_page.row_values(rn)
            if rn==0:
                s_struct=row
                continue
            try:
                ForestKind[int(row[0])]
                self.kinds.append(TreeKind(row, s_struct))
            except KeyError:
                pass

        self.normalize()

        for rn in range(g_page.nrows):
            row=g_page.row_values(rn)
            if rn==0:
                g_struct=row
                continue
            try:
                kind=self.kinds[int(row[0])] #hack!!!!
                kind.AcceptNaturalTransitionConstants(row, g_struct)
            except KeyError:
                pass

        del g_struct, s_struct
        del s_page, g_page

        f_page = xl.sheet_by_name("free%s" % year_id)
        struct = f_page.row_values(0)
        data = f_page.row_values(1)
        self.Sn=data[0]	# hack
        self.S0=data[1]	# hack
        self.n20=data[2]	# hack
        del f_page, data, struct

        c_page= xl.sheet_by_name("cultures")
        #cursor.execute('select year,dSk from "cultures$"')


        F101=self.kinds[101]
        Lk1=F101.Lk1
        S=0
        year_last=int(year_id)
        phase=1
        self.USk={}

        for rn in range(c_page.nrows):
            if rn==0: continue
            data = c_page.row_values(rn)

            y=int(data[0])
            dS=data[1]
            dS=dS/1000.0 # to make thousants of ga (kga)
            if y>year_last:
                phase=3
            if phase==1:
                y_p=y
                phase=2
                S=dS
            elif phase==2:
                y_t=y
                dy=y_t-y_p
                S = S - S * (Lk1**dy) + dS	#dSk
                y_p=y_t

            self.USk[y]=dS
            #print data[0], S, data[1]

        # print "Summary of Sk (kga):", S

        try:
            self.options["NO_CULTURES"]
            self.Sk0=0.0
            self.USk[year_last]=0.0
            print "Warning: No cultures!"
        except KeyError:
            self.Sk0=S
        del S,F101

        del data, c_page

        i_page = xl.sheet_by_name("interchange%s" % year_id)

        for rn in range(i_page.nrows):
            data=i_page.row_values(rn)
            if rn==0:
                struct=data
                continue
            try:
                kind=int(data[0])
                F=self.kinds[kind]
                F.AcceptInterchangeConstants(data,struct)
            except KeyError:
                pass
        del i_page, data

        l_page = xl.sheet_by_name('logging')
        self.ULogging={}
        for rn in range(l_page.nrows):
            data=l_page.row_values(rn)
            if rn==0: continue
            self.ULogging[int(data[0])]=data[1] / 1000.0	# conversion to kga
        del l_page, data

        # Cultural activity of habitants
        data=xl.sheet_by_name("people%s" % year_id).row_values(1)
        self.Sall=data[0]	# Al squaresl of the region (thousands of ga)
        self.Ssx=data[1]	# Agricultural squares (thousands of ga)
        self.N=data[2]		# No of habitants (thousants)
        self.L=data[3]		# Length of roads (km)
        self.KdN=data[4]	# Trend of habitants grow, i.e., N_{i+1} = KdN*N_{i}
        self.KNn=data[5]	# Activity of habitants to get therritory from forest
        self.KdNsx=data[6]  # How mush kgas to take by 1 thousants of habitants
        del data

		# fires
        data=xl.sheet_by_name("fires%s" % year_id).row_values(1)
        self.KULogging=data[0]	# How much to fire when logging (0.88)
        self.KfN=data[1]			# Fires due to habitants
        self.KfL=data[2]			# Fires due to transport
        self.KfSsx=data[3]		# Fires due to Agricultural interprises
        self.dUf=data[4]			# Fires due to DRY storm
        del data


    def BuildModel(self, species=None):

        self.model=ModelParameter()
        if species is None:
            species=self.kinds.keys()

        # Transition from nonforest territory (S.Nel) to territory without (w/o) forest (S.O)
        self.model.S=self.S=ModelParameter()
        self.model.S.O=self.S.O=DMItem(self.S0)
        self.model.S.Nel=self.S.Nel=DMItem(self.Sn, self.S.O, self.S.O, self.n20)
        head=self.S.Nel
        # Natural forest grow
        for s in species:
            mdl=self.kinds[s]
            path=mdl.BuildModel(self.S.O, head)
            setattr(self.model,"f"+str(s),mdl.model)
            head=path._first
            del path._first

		# Forest curtures
        self.F101=self.kinds[101]
        self.F101.Sk=self.Sk0
        self.F101.model.S.K=DMItem(self.F101.Sk, head, self.F101.model.S.I, self.F101.Lk1)
        head=self.F101.model.S.K

		# Kind exchange
        try:
            self.options["NO_INTERCHANGE"]
            print "Warning no species interchange!"
        except KeyError:
            for s1 in species:
                m1=getattr(self.model, "f"+str(s1))
                k1=self.kinds[s1]
                for s2 in species:
                    k2=self.kinds[s2]
                    m2=getattr(self.model, "f"+str(s2))
                    DMConnect(m1.S.Per, m2.S.Sr, getattr(k1, "Sper%i" % s2))
                    DMConnect(m1.S.Sp, m2.S.Sr, getattr(k1, "Ssp%i" % s2))

        return head	# of the nodelist

    def Reset(self):
		for kind in self.kinds.values():
			kind.Reset()

    def PrepareStorage(self, obj):
		m=ModelParameter({"S":ModelParameter({"O":obj.__copy__(),"Nel":obj.__copy__()})})
		for (name,value) in self.kinds.items():
			setattr(m, "f"+str(name), value.PrepareStorage(obj))
			if name==101:
				m.f101.S.K=obj.__copy__()
		return m

    def BeforeStates(self, modeller):
		for kind in self.kinds.values():
			kind.BeforeStates(modeller)

    def AfterStates(self, modeller):
		for kind in self.kinds.values():
			kind.AfterStates(modeller)
		if modeller.step_no>0:
			try:
				self.options["NO_CULTURES"]
			except KeyError:
				self.CalculateCultures(modeller.dt)
			try:
				self.options["NO_GET"]
			except KeyError:
				self.CalculateGetTerritory(modeller.dt)
			try:
				self.options["NO_LOGGING"]
			except KeyError:
				self.CalculateLogging(modeller.dt)
			try:
				self.options["NO_FIRES"]
			except KeyError:
				self.CalculateFires(modeller.dt)
			self.Ssx += self.GetDSsx(modeller.dt)
			self.N += self.GetDN(modeller.dt)

    def normalize(self):
        d={}
        for kind in self.kinds:
            d[kind.Kind]=kind

        self.kinds=d

    def CalculateCultures(self, dt):
        uk = self.USk[1973] * dt
        self.S.O.value -= uk
        self.F101.model.S.K.value += uk

    def CalculateLogging(self, dt):
		Sper=0
		Ssp=0
		for (key, val) in self.kinds.items():
			if key!=105:	# Kedr
				Sper += val.model.S.Per.value
				Ssp += val.model.S.Sp.value

		Srub=self.ULogging[1975] * dt
		Sall=Sper + Ssp
		for (key, val) in self.kinds.items():
			if key!=105:	# Kedr
				dSper=Srub * val.model.S.Per.value / Sall
				dSsp=Srub * val.model.S.Sp.value / Sall
				val.model.S.Per.value -= dSper
				val.model.S.Sp.value -= dSsp
				self.S.O.value += dSper+dSsp

    def CalculateFires(self, dt):
		S=0
		states=["I","II", "Sr", "Pr", "Sp", "Per"]

		for (key, val) in self.kinds.items():
			v = val.model.S
			for state in states:
				s=getattr(v, state).value
				S += s
			if key==101:	# Sosna cultres
				S += v.K.value

		Sfires= self.KULogging * self.ULogging[1975] +\
			self.KfN * self.N + self.KfL * self.L + self.KfSsx * self.Ssx + self.dUf

		Sfires *= dt

		for (key, val) in self.kinds.items():
			v = val.model.S
			for state in states:
				n=getattr(v, state)
				ds=Sfires * n.value / S
				n.value -= ds
				self.S.O.value += ds

			if key==101:	# Sosna cultres
				ds=Sfires * v.K.value / S
				v.K.value -= ds
				self.S.O.value += ds

    def FillInValues(self, number, struct):
		for (name,kind) in self.kinds.items():
			kind.FillInValues(number, getattr(struct,"f"+str(name)))
		struct.S.O[number]=self.S.O.value
		struct.S.Nel[number]=self.S.Nel.value

    def GetDSsx(self, dt):
		return self.GetDN(dt) * self.KdNsx

    def GetDN(self, dt):
		# print self.N, self.KdN, dt
		dN = self.N * self.KdN * dt
		return dN

    def CalculateGetTerritory(self, dt):
		dSN=self.KNn * self.GetDN(dt)
		dS=self.GetDSsx(dt)
		dS += dSN

		states=["I","II", "Sr", "Pr", "Sp", "Per"]

		S=self.S.O.value
		for (key, val) in self.kinds.items():
			v = val.model.S
			for state in states:
				s=getattr(v, state).value
				S += s
			if key==101:	# Sosna cultres
				S += v.K.value

		for (key, val) in self.kinds.items():
			v = val.model.S
			for state in states:
				n=getattr(v, state)
				ds=dS * n.value / S
				n.value -= ds
				self.S.Nel.value += ds

			if key==101:	# Sosna cultres
				ds=dS * v.K.value / S
				v.K.value -= ds
				self.S.Nel.value += ds

		ds=self.S.O.value * dS / S
		self.S.Nel.value += ds
		self.S.O.value -= ds


	#def __del__(self):
	#	del self.conn

class ForestModeller:
    def __init__(self,
                 forest_model,
                 starttime=0.0,
                 endtime=1.0,
                 interval=1.0,
                 subdivisions=10.0):
        self.forest_model=forest_model
        self.starttime=starttime
        self.endtime=endtime
        self.interval=interval
        self.subdivisions=subdivisions
        self.dt=self.interval/self.subdivisions
        #print "Values_to_store:", self.values_to_watch
        self.model_head=self.forest_model.BuildModel()
        self.Reset()

    def Reset(self):
		self.time_moment=self.starttime
		self.step_no=0
		self.forest_model.Reset()
		self.forest_model.AfterStates(self)
		self.prepareStorage()

    def prepareStorage(self):
        i=(self.endtime-self.starttime) / self.interval
        self.range=int(math.ceil(i))+1
        self.time=arange(self.range, dtype=float_)*self.interval + self.starttime
        self.trajectories=self.forest_model.PrepareStorage(zeros(self.range, dtype=float_))
        self.FillInValues(0)

    def FillInValues(self, number):
		self.forest_model.FillInValues(number, self.trajectories)

    def StepInterval(self):
		for n in range(self.subdivisions):
			self.forest_model.BeforeStates(self)
			self.model_head.step(self.dt, 1)
			self.forest_model.AfterStates(self)
		self.step_no+=1
		return self.step_no

    def Model(self):
		while (self.StepInterval()<self.range): self.FillInValues(self.step_no)
		self.trajectories.time=self.time

    def _makeLegends(self, gpm, legends):
		def _leaf_func(fields, value, parameter):
			(legends, time, gpm)=parameter
			name=fields[-1]
			if name!="time" and not SpecialName(name):
				title=".".join(fields)
				legends.append(gpm.Data(time, value, title=title))
		def _branch_func(fields, value, parameter):
			(legends, time, gpm)=parameter
			name=fields[-1]
			global Interpret
			if name[0:2]=="__":	# specail function
				result=Interpret(name, value)
				legends.append(gpm.Data(time, result, title=".".join(fields)))
				return 0
			else:
				return 1

		_legends=[]
		legends.ForEachDo(_leaf_func, (_legends, self.trajectories.time, gpm), branch_func=_branch_func)
		return _legends


    def Gnuplot(self, device, file=None, legends=None, initial_text=""):
		import Gnuplot
		gp=Gnuplot.Gnuplot(debug=0)
		gp("set terminal %s monochrome" % device)
		gp(initial_text)
		gp("set data style linespoints")
		if file is None:
			pass
		else:
			gp("set output '%s'" % file)
		if legends is None:
			legends=self.trajectories

		_legends=self._makeLegends(Gnuplot, legends)
		apply(gp.plot, _legends)
		gp.reset()
		del gp



if __name__=="__main__":
	# Quantum (begin)

	F=ForestModel("forest", "1973",
#		options={"NO_LOGGING":None, "NO_FIRES":None, "NO_INTERCHANGE":None}
#		options={"NO_INTERCHANGE":None}
#		options={"NO_INTERCHANGE":None,"NO_LOGGING":None, "NO_FIRES":None, "NO_GET":None}
		options={"NO_INTERCHANGE":None,"NO_FIRES":None, "NO_GET":None}
	)
	Modeller=ForestModeller(F,
		endtime=50., starttime=0., interval=5., subdivisions=100)
	control=Modeller.model_head.total
	Modeller.Model()

	# Quantum (end)

	plot=ModelParameter(
		{
			"Sfree":Modeller.trajectories.S.O,
			"Snel":Modeller.trajectories.S.Nel
		}
	)

	def All(kind):
		return kind.I+kind.II+kind.Sr+kind.Pr+kind.Sp+kind.Per

	plot_max=ModelParameter(
		{
			"Sos":All(Modeller.trajectories.f101.S),
			"El":All(Modeller.trajectories.f102.S),
			"Pikhta":All(Modeller.trajectories.f103.S),
			"Listvennica":All(Modeller.trajectories.f104.S),
			"Kedr":All(Modeller.trajectories.f105.S),
			"Bereza":All(Modeller.trajectories.f124.S),
			"Osina":All(Modeller.trajectories.f125.S),
			"Free":(Modeller.trajectories.S)
		}
	)

	log_y_init="set logscale y"

	Modeller.Gnuplot("postscript","graph.eps", plot)
	Modeller.Gnuplot("postscript","S.eps", Modeller.trajectories.S)
	Modeller.Gnuplot("postscript","F101_S.eps", Modeller.trajectories.f101.S, initial_text=log_y_init)
#	Modeller.Gnuplot("postscript","Max.eps", plot_max, initial_text=log_y_init)
	Modeller.Gnuplot("postscript","Max.eps", plot_max)
	Modeller.Gnuplot("postscript","F101_V.eps", Modeller.trajectories.f101.V, initial_text=log_y_init)
	print "Control of total square:", abs(control-Modeller.model_head.total), " total:", Modeller.model_head.total

	"""
	# no cultures
	FN=ForestModel("forest", "1973",  options={"NO_CULTURES":1})
	ModellerN=ForestModeller(FN,
		endtime=100., starttime=0., interval=10., subdivisions=100)
	ModellerN.Model()
	plot2=ModelParameter(
		{
			"Sfree":ModellerN.trajectories.S.O,
			"Snel":ModellerN.trajectories.S.Nel
		}
	)

	ModellerN.Gnuplot("postscript","graph2.eps", plot2)
	ModellerN.Gnuplot("postscript","graph21.eps", plot2-plot)
	"""


	DModel.Finalize(1)
