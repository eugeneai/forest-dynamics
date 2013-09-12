from quant import *
import types
import math
from Numeric import *
from mutils import *

DEBUG=0
if DEBUG:
	DEBUG_INSTALL=1
else:
	DEBUG_INSTALL=0

MODEL_TIME=50

if DEBUG<10:
	import mx.ODBC.Windows as ODBC
	import dme


class ForestModel:
	def __init__(self, tree_names, **keyargs):
		self.tree_names=tree_names
		self.options={}
		for k,v in keyargs.items():
			self.options[k]=v
	def install_all(self, region, t0):
		parts=[
			self.install_age_classes(),
			self.user_install(),
		]
		self.install_queries()
		self.install_basic_consts(t0)
		self.install_reaction_proc()
		self.install_basic_kb()
		parts.append(self.install_tree_kinds(region))
		if not self.options.get("NO_CULTURES", None):
			parts.append(self.install_cultures(region))
			parts.append("culture_kind(f101)")
		if not self.options.get("NO_LOGGING", None):
			parts.append(self.install_logging(region))
		if not self.options.get("NO_FIRES", None):
			parts.append(self.install_fires(region))
		parts.append(self.install_task(region, t0))
		s=""
		for part in parts:
			part=part.strip()
			if len(part)>0:
				s=s+","+part
		if len(s)>0:
			s=s[1:]
		self.install_KB(s)
	def user_install(self):
		return ""
	def install_tree_kinds(self, region_name):
		#install_predicate("tree_kind", 1)
		s=""
		for tree_name in self.tree_names:
			try:
				install_constant("f"+str(tree_name), tree_name)
			except ValueError:
				pass
			s+="tree_kind(%s,f%i) " % (region_name, tree_name)
			if tree_name!=105: # no cedra
				# Can be logged
				s+="loggable(f%i) " % tree_name
		s=s.strip().replace(" ",",")
		return s
	def install_age_classes(self):
		try:
			self._age_classes_installed
			return ""
		except AttributeError:
			pass
		install_predicate("age_class", 1)
		s=""
		for class_name in ["cult","mol1","mol2","srd","prs", "spl", "per"]:
			install_constant(class_name, class_name)
			s+="age_class(%s) " % class_name
		s=s.strip().replace(" ",",")+",after(mol1,mol2),after(mol2,srd),after(srd,prs),after(prs,spl),after(spl,per)"
		s+=",loggable_age(spl),loggable_age(per)"
		install_constant("no_forest", "no_forest")
		self._age_classes_installed=1
		return s
	def install_basic_consts(self, t0):
		try:
			self._basic_constants_installed
			return ""
		except AttributeError:
			pass
		for name in ["model_dyn", "ten_years", "forest", "forest_res", "landscape",
			"yes", "no", "forest_cultures","all","forest_fires","all_logging","forest_logging"]:
			install_constant(name, name)
		install_constant("None", '__None__')
		install_constant("logged", 'logged')
		install_constant("t0",t0)
		install_constant("nil",0.0)
		install_constant("one",1.0)
		self._basic_constants_installed=1
	def install_reaction_proc(self):
		try:
			self._reaction_proc_installed
			return ""
		except AttributeError:
			pass
		install_predicate("State",5,self.reaction_proc_state)
		install_predicate("Trans",4,self.reaction_proc_trans)
		install_predicate("Print",1,self.reaction_proc_print)
		install_predicate("DefineModel",2,self.reaction_proc_define_model)
		self._reaction_proc_installed=1
		return ""
	def install_basic_kb(self):
		translate_string("""
fm ModelDeterm()=\
  a:a,t0[Problem(a, model_dyn), Prognose(a, ten_years, t0), \
    Geosystem_Range(a, landscape), Landscape_Type(a, forest) \
     > \
      e:m,s0[ModelType(m, a, forest_res, t0), DefineModel(m,a), State(m, s0, no_forest, \
		square(a,None, no_forest, t0), None)]];
fm NoToMol()=\
  a:m,a,k,t0,s0,sq [\
    ModelType(m,a,forest_res,t0),\
	tree_kind(a,k),age_class(mol1),\
	State(m,s0,no_forest,sq,None)\
      >\
    e:s1[State(m,s1,mol1,square(a,k,mol1,t0),k), \
	    Trans(m,s0,s1,trans_time(no_forest,mol1,k,t0))\
	]\
  ];
fm Cultures()=\
	a:ck,m,a,t0,s1,s0,sq0[\
	  ModelType(m,a,forest_res,t0),\
	  State(m,s0,no_forest,sq0,None),\
	  State(m,s1,mol1,square(a,ck,mol1,t0),ck),\
	  TakesPlace(a,forest_cultures,yes),culture_kind(ck)\
	  >\
	  e: sk[\
		State(m,sk,cult,square(a,ck,cult,t0),ck),\
		Trans(m,sk,s1,trans_time(cult,mol1,ck,t0)),\
		Trans(m,s0,sk,CalcCulturesTrans(square(a,ck,cult,t0),sq0))\
	  ]\
	]
fm FiresDef()=\
	a:m,a,t0[\
	  Problem(a,forest_fires),\
	  ModelType(m,a,forest_res,t0)\
	  >\
	  FiresBaseIntensity(m,a,\
			div(\
				CalcBaseFiresIntensity(a,t0), square(a,all,all,t0)\
				)\
	  )\
	]
fm FiresProp()=\
	a:m,a,t0,s,s0,name,sq,sq_no_forest,fi,k[\
	  ModelType(m,a,forest_res,t0),\
	  State(m,s,name,sq,k),age_class(name),\
	  State(m,s0,no_forest,sq_no_forest, None),\
	  FiresBaseIntensity(m,a,fi)\
	  >\
	  Trans(m,s,s0,fi)\
	]
fm Fires()=FiresDef()&FiresProp()
fm LoggingDef()=\
	a:m,a,t0[\
	  Problem(a,forest_logging),\
	  ModelType(m,a,forest_res,t0)\
	  >\
	  LoggingIntensity(m,a,\
			div(\
				CalcLoggingIntensity(a,t0), square(a,all_logging,all_logging,t0)\
				)\
		) &\
			a:k,s0,sq_no_forest[loggable(k),\
					State(m,s0,no_forest,sq_no_forest, None)\
				>\
				e:sl[\
					State(m,sl,logged,nil,k),\
					Trans(m,sl,s0,one)\
				]\
			]\
	]
fm LoggingProp()=\
	a:m,a,t0,s,s0,name,k,sq_no_forest,li,sl,sq_logged[\
	  ModelType(m,a,forest_res,t0),\
	  State(m,s,name,square(a,k,name,t0),k),age_class(name),loggable_age(name),\
	  State(m,s0,no_forest,sq_no_forest,None),\
	  State(m,sl,logged,sq_logged,k),\
	  loggable(k),\
	  LoggingIntensity(m,a,li)\
	  >\
	  Trans(m,s,sl,li) & \
	  (\
	    Problem(a,forest_fires) \
		> \
		Trans(m,s,s0,mul(li, FireLogCf()))\
	  )\
	]
fm Logging()=LoggingDef(),LoggingProp()
fm AToB()=\
  a:m,t0,a,k,cl,cl1,s [\
    ModelType(m,a,forest_res,t0),tree_kind(a,k), age_class(cl),after(cl,cl1),\
	State(m,s,cl,square(a,k,cl,t0),k)\
      >\
    e:s1[State(m,s1,cl1,square(a,k,cl1,t0),k),Trans(m,s,s1,trans_time(cl,cl1,k,t0))] \
  ];
fm BaseBuilding()=\
  ModelDeterm() & NoToMol() & Cultures() & AToB() & Fires() & Logging();
set steps_count 100000;
#set trace 16;
#set tree_write_depth 60;
set debug_level 0;
""")
	def install_task(self, region_name, t0):
		install_constant(region_name,region_name)
		s="Problem(%s,model_dyn),Prognose(%s,ten_years,t0),Geosystem_Range(%s,landscape),Landscape_Type(%s,forest)" % (region_name,region_name,region_name,region_name)
		return s
	def install_cultures(self, region_name):
		s="TakesPlace(%s,forest_cultures,yes)" % (region_name)
		return s
	def install_logging(self, region_name):
		s="Problem(%s,forest_logging)" % region_name
		return s
	def install_fires(self, region_name):
		s="Problem(%s,forest_fires)" % region_name
		return s
	def install_KB(self, data_str):
		s="fm KB=%s & BaseBuilding()" % data_str
		print s
		translate_string(s)
	def _div(self, a,b):
		return a/b
	def _mul(self, a,b):
		return a*b
	def install_queries(self):
		install_function("square", 4, self.proc_query_square)
		install_function("trans_time", 4, self.proc_query_trans_time)
		install_function("div", 2, self._div)
		install_function("mul", 2, self._mul)
		install_function("CalcBaseFiresIntensity", 2, self.proc_query_fires_intensity)
		install_function("CalcLoggingIntensity", 2, self.proc_query_logging_square)
		install_function("CalcCulturesTrans", 2, self.proc_query_cultures_trans)
		install_function("FireLogCf", 0, self.proc_query_logging_fires_coefficient) # %was% area, year
		return ""
	def proc_query_square(self, region, kind, age, time_moment):
		if kind=='__None__':
			print "SELECT square FROM data WHERE kind='EMPTY' AND age=%s AND date=%i" % (age, time_moment)
		else:
			print "SELECT square FROM data WHERE kind=f%i AND age=%s AND date=%i" % (kind, age, time_moment)
		return 100
	def proc_query_trans_time(self, age1, age2, kind, time_moment):
		print "SELECT trans_time FROM data WHERE kind=f%i AND age=%s" % (kind, age2)
		return 1/20.0
	def reaction_proc_state(self, model, state_name, state_descr, square, kind):
		print "Installing state:", state_name, "of model", model, "descr:", state_descr, "sq:", square, "kind:", kind
	def reaction_proc_trans(self, model, begin,end, value):
		print "Installing trans of model", model, "from:", begin, "to:", end, "val:", value
	def reaction_proc_print(self, arg1):
		print "--> Printed:", arg1
	def reaction_proc_define_model(self, model_name, region_name):
		print "Defined %s as %s" % (model_name, region_name)
	def proc_query_logging_fires_coefficient(self): #, area, time_moment):
		return 0.88
	def infer(self):
		f=get_descriptor("KB",0)
		if f:
			return f.prove(trace=self.infer_trace_proc)
		else:
			raise ValueError, "cannot prove None object"
	def infer_trace_proc(self, pcf):
		global trace_no
		trace_no +=1
		print "trace--------- N", trace_no
		#pcf.print_as_tree()
		return 1
	def DoModel(self, *args):
		self.install_all(*args)
		(rc, res)=self.infer()
		bases=res.get_reduced_bases()
		fm=ForestModeller(self, starttime=0.0, endtime=MODEL_TIME)

		fm.Model()
		print "model done"
		self.conn.close()
		traj=fm.trajectories
		del fm
		return traj


#===========================================

trace_no=0

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

class ExcelForestModel(ForestModel):
	def __init__(self, dsn, year=1973, tree_names=[], **keyargs):
		global ForestKind
		self.dsn=dsn
		self.year=year
		if DEBUG<10:
			self.conn=ODBC.connect(dsn, user="", password="", clear_auto_commit=0)
			cursor=self.conn.cursor()
			cursor.execute('select Kind from "S%s$"' % year)
			fks=cursor.fetchall()
			if fks is None:
				raise ValueError, "wrong year is given (returned empty set)"
			tree_names=map(lambda (x,): int(x), fks)
		else:
			tree_names=[101,102,103,104,105,124,125]
		#tree_names=[101]
		if DEBUG:
			print "tree_names:", tree_names
		#raw_input("Connect debugger")
		ForestModel.__init__(self, tree_names, **keyargs)

		self.options["culture_kind"]=101 # i.e. Sosna

	def get_cultures(self, kind, age, time_moment):
		cursor=self.conn.cursor()
		cursor.execute('select year,dSk from "cultures$"')
		data=cursor.fetchone()
		Lk1=self.proc_query_trans_time("cult", "mol1", kind, time_moment)
		S=0
		year_last=int(time_moment)
		phase=1
		self.USk={}
		while data:
			y=int(data[0])
			dS=data[1]
			dS=dS/1000.0 # to make thousents of ga (kga)
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
			else:
				pass
			self.USk[y]=dS
			#print data[0], S, data[1]
			data=cursor.fetchone()
		if DEBUG:
			print "Summary of Sk (kga):", S, kind, age
		return S
		"""
		try:
			self.options["NO_CULTURES"]
			self.Sk0=0.0
			self.USk[year_last]=0.0
			print "Warning: No cultures!"
		except KeyError:
			self.Sk0=S
		del S,F101
		"""
	def get_all_square(self, region, time_moment):
		cursor=self.conn.cursor()
		cursor.execute('select S1,S2,Ssr,Spr,SIspper from "S%s$"' % time_moment)
		data=cursor.fetchone()
		s=0.0
		while data:
			s+=reduce(lambda x,y: x+y, data, 0)
			data=cursor.fetchone()
		# without cultures
		if DEBUG:
			print "all the square:", s
		return s

	def get_all_loggable_square(self, region, time_moment):
		cursor=self.conn.cursor()
		cursor.execute('select kind, SIspper from "S%s$"' % time_moment)
		data=cursor.fetchone()
		s=0.0
		while data:
			if int(data[0])!=105: # Cedra is not logged
				#print ":", data, s
				s+=data[1]
			data=cursor.fetchone()
		# without cultures
		if DEBUG:
			print "all the loggable square:", s
		return s

	def proc_query_logging_square(self, region, time_moment):
		LI=self.options.get("LOGGING_INTENSITY",None)
		if LI is not None:
			if DEBUG:
				print "all the loggable square (intens base) LI:", LI
			return LI
		cursor=self.conn.cursor()
		cursor.execute('select Year,S from "logging$"')
		data=cursor.fetchone()
		while data:
			if data[0]>=time_moment:
				s=data[1]/1000.0
				if DEBUG:
					print "all the loggable square (intens base):", s
				return s
			data=cursor.fetchone()
		raise SystemError, "cannot find logging data"

	def proc_query_square(self, region, kind, age, time_moment):
		trt=\
			{
				"mol1":"1",
				"mol2":"2",
				"srd":"sr",
				"prs":"pr",
				"per":"per",
				"spl":"Ispper", # But SIspper = sp+per !!!!!
			}
		if age=="cult":
			return self.get_cultures(kind, age, time_moment)
		if age=="all":
			return self.get_all_square("Irkutsk",time_moment)
		if age=="all_logging":
			return self.get_all_loggable_square("Irkutsk",time_moment)
		age=trt.get(age, age)
		if kind=='__None__':
			query='SELECT S0 FROM "free%s$"' % (time_moment,)
		else:
			query='SELECT S%s FROM "S%s$" WHERE Kind=%s' % \
				(age, time_moment, kind)
		cursor=self.conn.cursor()
		#print query
		try:
			_a=1
			cursor.execute(query)
			_a=0
		finally:
			if _a:
				print "Query was:", query

		(s,)=cursor.fetchone()
		if age=="Ispper":
			per=self.proc_query_square(region, kind, "per", time_moment)
			s=s-per
		#print query
		#print s
		return s
	def proc_query_trans_time(self, age1, age2, kind, time_moment):
		tr=\
			{
				"no_forest":"0",
				"cult":"k",
				"mol1":"1",
				"mol2":"2",
				"srd":"3",
				"prs":"4",
				"per":"6",
				"spl":"5",
			}
		age1=tr.get(age1,age1)
		age2=tr.get(age2,age2)
		query='SELECT L%s%s FROM "grow%s$" WHERE kind=%i' % (age1, age2, time_moment, kind)
		cursor=self.conn.cursor()
		#print query
		cursor.execute(query)
		(l,)=cursor.fetchone()
		return l

	def proc_query_cultures_trans(self, cultures_area, empty_area):
		CI=self.options.get("CULTURES_INTENSITY",None)
		if CI is None:
			return cultures_area / empty_area
		else:
			return CI / empty_area

	def proc_query_fires_intensity(self, area, time_moment):
		FI=self.options.get("FIRES_INTENSITY", None)
		if FI is not None:
			return FI*(1+self.options.get("ILL_PERCENT", 0))
		cursor=self.conn.cursor()
		cursor.execute('select Ssx, N, L, KdNsx FROM "people%s$"' % time_moment)
		(Ssx, N, L, KdNsx) = cursor.fetchone()
		cursor.execute('select KULogging, KfN, KfL, KfSsx, dUf from "fires%s$"' % time_moment)
		(KULogging, KfN, KfL, KfSsx, dUf) = cursor.fetchone()
		#antropo_fires=KfN * N + KfL * L + KfSsx * Ssx + dUf
		antropo_fires=15.013
		#print "Antropo_fires=", antropo_fires
		return antropo_fires
	def reaction_proc_state(self, model, state_name, state_descr, square, kind):
		if DEBUG_INSTALL:
			print "Installing state:", state_name, "of model", model, "descr:", state_descr, "sq:", square, "kind:", kind
		try:
			m=getattr(self, str(model))
		except AttributeError:
			setattr(self, str(model), ModelParameter())
			self.model_name=str(model)
			m=getattr(self, self.model_name)
			self.chain_head=None
		self.chain_head=dmi=dme.DMItem(square, self.chain_head)
		setattr(m, str(state_name), (dmi, (str(state_descr), str(kind))))
		#setattr(m, "_"+str(state_name)+"_descr", (str(state_descr), str(kind)))
		try:
			m._states
		except AttributeError:
			m._states={}
		m._states[(str(state_descr), str(kind))]=str(state_name)
	def reaction_proc_define_model(self, model_name, region_name):
		#region_name="m_"+region_name
		print "-->Defined %s as %s" % (model_name, region_name)
		try:
			self.model_names
		except AttributeError:
			self.model_names={}
		try:
			self.region_names
		except AttributeError:
			self.region_names={}
		model_name=str(model_name)
		region_name=region_name
		self.model_names[model_name]=region_name
		self.region_names[region_name]=model_name
		#print "Definition:", self.model_names
	def reaction_proc_trans(self, model, begin,end, value):
		if DEBUG_INSTALL:
			print "Installing trans of model", model, "from:", begin, "to:", end, "val:", value
		m=getattr(self, str(model))
		b=getattr(m, str(begin))
		e=getattr(m, str(end))
		dme.DMConnect(b[0], e[0], value)
		#print "Definition:", self.model_names
	def variable(self, name, pool_name=None):
		try:
			dic=self.variables
		except AttributeError:
			dic=self.variables={}
		if pool_name:
			dic=self.variables[pool_name] # raise error instead creating new one
		try:
			return dic[name]
		except KeyError:
			dic[name]=None
			return dic[name]
	def prepare_storage(self, obj):
		def convert(value, obj):
			return obj.__copy__()
		def convert_name(value, key, obj):
			return "_".join(value[1])
		m=getattr(self, self.model_name)
		S=m.ConvertWithNames(convert, convert_name, obj)
		return ModelParameter({self.model_name:ModelParameter({"S":S})})
	def diff(self, model2, trajectories1, trajectories2, result):
		def leaf(name, value, ((t1,t2,res), m_name, (m1,m2))):
			(name,)=name # as we know that the trajectories and model have 1 lavel.
			if name[0]=="_":
				return
			#print "-->", t1.__dict__
			m=getattr(t1, m_name).S
			a=getattr(m, name)
			md=getattr(m1, m_name)
			sdescr=getattr(md, "_"+name+"_descr")
			region_name=m1.model_names[m_name]
			m_name2=m2.region_names[region_name]
			mm2=getattr(t2, m_name2).S
			md2=getattr(m2, m_name2)
			r=getattr(res, m_name).S
			r=getattr(r, name)
			try:
				state_name=md2._states[sdescr]
			except KeyError:
				for number in range(len(r)):
					r[number]=-1e39
				return
			a2=getattr(mm2, state_name)
			for number in range(len(r)):
				r[number]=a[number]-a2[number]
		for model_name, model_descr in self.model_names.items():
			m=getattr(self, model_name)
			m.ForEachDo(leaf, ((trajectories1,trajectories2, result), model_name, (self,model2)))

BD_NAME="bd_les"
"""
P1	Доля спелых и перестойных лесов в лесной площади, %;
-----------------------------
P2	Доля спелых и перестойных лесов в покрытой лесной растительностью площади, %;
P3	Средний запас древесины в спелых и перестойных лесах, кбм/га;
P4	Средний запас древесины в спелых и перестойных лесах, возможных для эксплуатации, кбм/га;
P5	Средний запас древесины в спелых и перестойных хвойных лесах, возможных для эксплуатации, кбм/га;
P6	Доля спелых и перестойных лесов, возможных для эксплуатации, в покрытой лесной растительностью площади, %;
P7	Доля спелых и перестойных хвойных лесов, возможных для эксплуатации, в покрытой лесной растительностью площади, %;
P8	Средний запас древесины  на землях, покрытых лесной растительностью, кбм/га;
P9	Доля хвойных лесов в покрытой лесной растительностью площади, %;
-----------------------------
P10	Доля сосняков в покрытой лесной растительностью площади, %;
P11	Доля ельников в покрытой лесной растительностью площади, %;
P12	Доля пихтарников в покрытой лесной растительностью площади, %;
P13	Доля лиственничников в покрытой лесной растительностью площади, %;
P14	Доля кедровников в покрытой лесной растительностью площади, %;

P15	Доля березняков в покрытой лесной растительностью площади, %;
P16	Доля осинников в покрытой лесной растительностью площади, %;
-----------------------------
P17	Средний возраст лесов, лет;
P18	Средний возраст хвойных лесов, лет;
P19	Средний возраст лиственных лесов, лет;
P20	Доля лесов искусственного происхождения;
-----------------------------
P21	Фонд лесовосстановления (в процентах к лесным землям);
-----------------------------
P22	Доля лесов первой группы, %;
P23	Доля лесов второй группы, %;
P24	Доля лесов третьей группы, %;
P25	Доля лесов, возможных для эксплуатации;
P26	Доля хвойных молодняков в возрасте до 20 лет, %;
----------------------------------------------------------------
P27	Общий средний прирост, кбм/га;
P28	Средний годичный прирост древесины хвойных пород, кбм/га;
P29	Средний годичный прирост древесины мягколиственных пород, кбм/га;
P30	Средний бонитет хвойных лесов;
P31	Средний бонитет лиственных лесов;
P32	Средняя полнота хвойных лесов;
P33	Средняя полнота лиственных лесов;
P34	Давность лесоустройства;
P35	Общий размер отпуска ликвидной древесины с 1 га покрытых лесной растительностью земель, кбм.
"""
# Доля молодников лиственных берется в 2 раза больше и отнимается от доли всех лиственных
FOREST_KIND=[101,102,103,104,105,124,125]
"""
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
"""

class GISForestModel(ForestModel):
	def __init__(self, dsn, regions, last_year=2050, tree_names=[], **keyargs):
		global ForestKind
		self.dsn=dsn
		self.last_year=last_year
		tree_names=FOREST_KIND
		self.regions=regions
		self.conn=ODBC.connect(dsn=dsn, user="", password="")

		ForestModel.__init__(self, tree_names, **keyargs)

		self.options["culture_kind"]=101 # i.e. Sosna

	def _div(self, a,b):
		return a
	def get_value(self, region, *args):
		s=reduce(lambda x,y: x+","+y, args)
		cursor=self.conn.cursor()
		query="select %s from bd_les_o where LESX='%s'" % (s, region[3:])
		#print query
		cursor.execute(query)
		data=cursor.fetchone()
		if len(data)==1:
			return data[0]
		return data
	def get_cultures(self, region, kind, age, time_moment):
		return self.get_value(region, "P20")
	def get_all_square(self, region, time_moment):
		return 100.0
	def get_all_loggable_square(self, region, time_moment):
		return self.get_value(region, "P6")
	def proc_query_logging_square(self, region, time_moment):
		return 0.007
	def proc_query_square(self, region, kind, age, time_moment):
		trt={
			101:"P10",
			102:"P11",
			103:"P12",
			104:"P13",
			105:"P14",
			124:"P15",
			125:"P16",
		}
		if age=="cult":
			return self.get_cultures(region, kind, age, time_moment)
		if age=="all":
			return self.get_all_square(region, time_moment)
		if age=="all_logging":
			return self.get_all_loggable_square(region, time_moment)
		if kind=='__None__':
			return self.get_value(region,"P21")
		name=trt[kind]
		s=self.get_value(region, name)
		m=self.get_value(region,"P26")
		if kind in [101, 102, 103, 104, 105]:
			if age=="mol1":
				s=m*s/100.0
			elif age=="per":
				s=(100-m)*s/100.0
		else:
			m*=1.2	# empirical
			if m>100:
				m=100
			if age=="mol1":
				s=m*s/100.0
			elif age=="per":
				s=(100-m)*s/100.0
		#print "Square ->>> :", s, m, kind, age
		return s
		#raise "Untrearted combination %s %s" % (repr(kind), repr(age))

	def proc_query_trans_time(self, age1, age2, kind, time_moment):
		tbl={
			"no_forest":(1/20.0),
			"mol1":(1/(4*20.0)),
			"cult":(0.07518797)
		}
		base=tbl[age1]
		if kind in [101, 102, 103, 104]:
			return base
		elif kind==105:
			return base/2
		else:
			return base*2
	def proc_query_fires_intensity(self, area, time_moment):
		return 0.002 # Antropofires
	def reaction_proc_define_model(self, model_name, region_name):
		#print "Defined %s as %s" % (model_name, region_name)
		try:
			self.model_names
		except AttributeError:
			self.model_names={}
		try:
			self.region_names
		except AttributeError:
			self.region_names={}
		model_name=str(model_name)
		region_name=int(region_name[3:])
		self.model_names[model_name]=region_name
		self.region_names[region_name]=model_name
		#print "Definition:", self.model_names
	def reaction_proc_state(self, model, state_name, state_descr, square, kind):
		#print "Installing state:", state_name, "of model", model, "descr:", state_descr, "sq:", square
		model_name=str(model)
		try:
			m=getattr(self, model_name)
		except AttributeError:
			setattr(self, model_name, ModelParameter())
			m=getattr(self, model_name)
			try:
				self.chain_head
			except AttributeError:
				self.chain_head=None
		self.chain_head=dmi=dme.DMItem(square, self.chain_head)
		setattr(m, str(state_name), dmi)
		setattr(m, "_"+str(state_name)+"_descr", (str(state_descr), str(kind)))
		try:
			m._states
		except AttributeError:
			m._states={}
		m._states[(str(state_descr), str(kind))]=str(state_name)
	def reaction_proc_trans(self, model, begin,end, value):
		#print "Installing trans of model", model, "from:", begin, "to:", end, "val:", value
		m=getattr(self, str(model))
		b=getattr(m, str(begin))
		e=getattr(m, str(end))
		dme.DMConnect(b, e, value)
	def prepare_storage(self, obj):
		def convert(value, obj):
			return obj.__copy__()
		rc={}
		for model_name in self.model_names.keys():
			m=getattr(self, model_name)
			S=m.Convert(convert,obj)
			rc[model_name]=ModelParameter({"S":S})
		return ModelParameter(rc)
	def install_age_classes(self):
		try:
			self._age_classes_installed
			return ""
		except AttributeError:
			pass
		install_predicate("age_class", 1)
		s=""
		for class_name in ["cult","mol1","per"]:
			install_constant(class_name, class_name)
			s+="age_class(%s) " % class_name
		s=s.strip().replace(" ",",")+",after(mol1,per),loggable_age(per)"
		install_constant("no_forest", "no_forest")
		self._age_classes_installed=1
		return s
	def install_queries(self):
		install_function("square", 4, self.proc_query_square)
		install_function("trans_time", 4, self.proc_query_trans_time)
		install_function("div", 2, self._div)
		install_function("mul", 2, self._mul)
		install_function("CalcBaseFiresIntensity", 2, self.proc_query_fires_intensity)
		install_function("CalcLoggingIntensity", 2, self.proc_query_logging_square)
		install_function("FireLogCf", 0, self.proc_query_logging_fires_coefficient) # %was% area, year
		return ""
	def install_all(self):
		parts=[
			self.install_age_classes(),
			self.user_install(),
		]
		self.install_queries()
		self.install_basic_consts(0)
		self.install_reaction_proc()
		self.install_basic_kb()
		for region in self.regions:
			region="reg%i" % region
			parts.append(self.install_tree_kinds(region))
			if not self.options.get("NO_CULTURES", None):
				parts.append(self.install_cultures(region))
				parts.append("culture_kind(f101)")
			if not self.options.get("NO_LOGGING", None):
				parts.append(self.install_logging(region))
			if not self.options.get("NO_FIRES", None):
				parts.append(self.install_fires(region))
			parts.append(self.install_task(region, 0))
		#s=s.strip().replace(" ",",")
		s=""
		for part in parts:
			part=part.strip()
			if len(part)>0:
				s=s+","+part
		if len(s)>0:
			s=s[1:]
		self.install_KB(s)
	def diff(self, model2, trajectories1, trajectories2, result):
		def leaf(name, value, ((t1,t2,res), m_name, (m1,m2))):
			(name,)=name # as we know that the trajectories and model have 1 lavel.
			if name[0]=="_":
				return
			#print "-->", t1.__dict__
			m=getattr(t1, m_name).S
			a=getattr(m, name)
			md=getattr(m1, m_name)
			sdescr=getattr(md, "_"+name+"_descr")
			region_name=m1.model_names[m_name]
			m_name2=m2.region_names[region_name]
			mm2=getattr(t2, m_name2).S
			md2=getattr(m2, m_name2)
			r=getattr(res, m_name).S
			r=getattr(r, name)
			try:
				state_name=md2._states[sdescr]
			except KeyError:
				for number in range(len(r)):
					r[number]=-1e39
				return
			a2=getattr(mm2, state_name)
			for number in range(len(r)):
				r[number]=a[number]-a2[number]
		for model_name, model_descr in self.model_names.items():
			m=getattr(self, model_name)
			m.ForEachDo(leaf, ((trajectories1,trajectories2, result), model_name, (self,model2)))

class ManyGISForestModel(GISForestModel):
	def __init__(self, dsn, **keyargs):
		conn=ODBC.connect(dsn=dsn, user="", password="")
		c=conn.cursor()
		c.execute("select P34, LESX from bd_les_o")
		all=c.fetchall()
		n=[]
		for (year, name) in all:
			try:
				if int(year)>0:
					n.append(int(name))
			except ValueError:
				pass
		#print n
		#n=[11252218,11252207]
		#n=[11252218]
		GISForestModel.__init__(self, dsn, n, **keyargs)
	def print_something(self, number, trajectories):
		def leaf(name, value, (parameter, m_name, number, model, descr, cursor)):
			(name,)=name # as we know that the trajectories and model have 1 lavel.
			if name[0]=="_":
				return
			m=getattr(parameter, m_name).S
			a=getattr(m, name)
			md=getattr(model, m_name)
			sdescr=getattr(md, "_"+name+"_descr")
			#print name, getattr(md, "_"+name+"_descr"), descr, a[number]
			#a[number]=value.value
			if sdescr[0]=='no_forest':
				query="update bd_les set P21=%s where LESX='%i'" % (a[number], descr)
			elif sdescr[0]=='cult':
				query="update bd_les set P20=%s where LESX='%i'" % (a[number], descr)
			elif sdescr[0]=='mol1' and int(sdescr[1]) in [101,102,103,104,105]:
				query="update bd_les set P26=P26+%s where LESX='%i'" % (a[number], descr)
			else:
				tr={
					101:"P10",
					102:"P11",
					103:"P12",
					104:"P13",
					105:"P14",
					124:"P15",
					125:"P16",
				}
				field_name=tr[int(sdescr[1])]
				query="update bd_les set %s=%s+%s where LESX='%i'" % (field_name, field_name, a[number], descr)
			#print query
			cursor.execute(query)
		for model_name, model_descr in self.model_names.items():
			m=getattr(self, model_name)
			cursor=self.conn.cursor()
			cursor.execute("update bd_les set P10=0, P11=0, P12=0, P13=0, P14=0, P15=0, P16=0, P26=0  where LESX='%i'" % model_descr)
			m.ForEachDo(leaf, (trajectories, model_name, number, self, model_descr, cursor))
			cursor.execute("update bd_les set P1=P10+P11+P12+P13+P14+P15+P16 where LESX='%i'" % model_descr)
			self.conn.commit()

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

"""
biggles_colors={
			#0xRRGGBB
	"red": 0x0f
	"green": 0x
	"blue": 0x
	"": 0x
	"": 0x
	"": 0x
	"": 0x
	"": 0x
	"": 0x
}
"""

biggles_point_types=[
	"none",
	"dot",
	"plus",
	"asterisk",
	"circle",
	"cross",
	"square",
	"triangle",
	"diamond",
	"star",
	"inverted triangle",
	"starburst",
	"fancy plus",
	"fancy cross",
	"fancy square",
	"fancy diamond",
]

biggles_line_types=[
	"solid",			"dotted",
	"dotdashed",		"shortdashed",
	"longdashed",	"dotdotdashed",
	"dotdotdotdashed"
]

class ForestModeller:
	def __init__(self,
			forest_model,
			starttime=0.0,
			endtime=1.0,
			interval=1.0,
			subdivisions=1.0):
		self.forest_model=forest_model
		self.starttime=starttime
		self.endtime=endtime
		self.interval=interval
		self.subdivisions=subdivisions
		self.dt=self.interval/self.subdivisions
		#print "Values_to_store:", self.values_to_watch
		self.model_head=self.forest_model.chain_head
		self.Reset()

	def Reset(self):
		self.time_moment=self.starttime
		self.step_no=0
		#self.forest_model.Reset()
		#self.forest_model.AfterStates(self)
		self.prepareStorage()

	def prepareStorage(self):
		i=(self.endtime-self.starttime) / self.interval
		self.range=int(math.ceil(i))+1
		self.time=arange(self.range, typecode=Float)*self.interval + self.starttime
		self.trajectories=self.forest_model.prepare_storage(zeros(self.range,Float))
		#self.trajectories=ModelParameter()
		self.fill_in_values(0)

	def fill_in_values(self, number):
		def leaf(name, value, (trajectories, m_name, number)):
			(name,)=name # as we know that the trajectories and model have 1 lavel.
			if name[0]=="_":
				return
			descr="_".join(value[1])
			m=getattr(trajectories, m_name).S
			a=getattr(m, descr)
			a[number]=value[0].value
			#print "---", name, value.value
		for model_name in self.forest_model.model_names.keys():
			m=getattr(self.forest_model, model_name)
			m.ForEachDo(leaf, (self.trajectories, model_name, number))

	def StepInterval(self):
		for n in range(self.subdivisions):
			#self.forest_model.BeforeStates(self)
			self.model_head.step(self.dt, 1)
			#self.forest_model.AfterStates(self)
		self.step_no+=1
		return self.step_no

	def Model(self):
		while (self.StepInterval()<self.range):
			self.fill_in_values(self.step_no)
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

colors=[
	0x000000,
	0x0000FF,
	0x00FF00,
	0x00FFFF,
	0xFF0000,
	0xFF00FF,
	0xFFFF00,
	0x000080,
	0x008000,
	0x008080,
	0x800000,
	0x800080,
	0x808000
]

def _makeBigglesLegends(gpm, legends, model):
	def _leaf_func(fields, value, (legends, time, gpm, model)):
		name=fields[-1]
		if name!="time" and not SpecialName(name):
			if value[0]<-1e37:
				return
			m=getattr(model, fields[0])
			try:
				(descr, kind)=getattr(m, "_"+name+"_descr")
				title=".".join([descr,kind])
			except AttributeError:
				title=".".join(fields)

			#n=len(legends) / 2
			n=len(legends) % (len(biggles_line_types)*len(colors))
			color=colors[n % len(colors)]
			#print color, type(color)
			line_type=biggles_line_types[n / len(colors)]
			#l=gpm.Curve(time, value, type=line_type, color=color, linewidth=3)
			l=(abs(value[-1]), time, value, line_type, color, 3, title)
			#l.label=title
			legends.append(l)
	def _branch_func(fields, value, (legends, time, gpm, model)):
		name=fields[-1]
		global Interpret
		if name[0:2]=="__":	# specail function
			result=Interpret(name, value)
			l=gpm.Data(time, result) # colors...
			l.title=".".join(fields)
			legends.append(l)
			return 0
		else:
			return 1

	_legends=[]
	legends.ForEachDo(_leaf_func, (_legends, legends.time, gpm, model), branch_func=_branch_func)
	return _legends

def Bigglesplot(device, file, legends, model, initial_text="", title=""):
	import biggles
	p=biggles.FramedPlot()
	#p(initial_text)
	#p("set data style linespoints")
	p.title=title
	p.xlabel=r'$t$'
	p.ylabel='Square'
	if legends is None:
		legends=self.trajectories

	_legends=_makeBigglesLegends(biggles, legends, model)
	_legends.sort()
	_legends.reverse()
	new=[]
	for l in _legends:
		(skip, time, value, line_type, color, width, title)=l
		ll=biggles.Curve(time, value, type=line_type, color=color, linewidth=width)
		ll.label=title
		p.add(ll)
		new.append(ll)
	scale=0.2
	k=biggles.PlotKey( 1.1, 1, new )
	p.add(k)
	if file:
		p.write_eps(file)
	else:
		p.show()
	del p

scen_data_begin=\
	(
		{"low":15.013, "middle":195.172, "high":375.332}, # fires
		{"low":1.230, "middle":19.356, "high":37.482}, # cultures
		{"low":63.300, "middle":166.657, "high":242.908}, # logging
		{"low":0.0, "middle":0.75, "high":1.50}, # illness
	)
	
scen_data=\
	(
		{"low":15.013, "lm":75.066, "ml":135.119, "middle":195.172, "high":375.332}, # fires
		{"low":1.230, "middle":19.356,"mh":25.398, "hm":31.440, "high":37.482}, # cultures
		{"low":63.300, "middle":166.657, "high":242.908}, # logging
		{"low":0.0, "middle":0.75, "high":1.50}, # illness
	)

def get_values(descr):
	answer=[]
	for i in range(len(scen_data)):
		d=scen_data[i]
		answer.append(d[descr[i]])
	return answer

next_data={
	"low":(0,"lm"),
	"lm":(0,"ml"),
	"ml":(0,"middle"),
	"middle":(0,"mh"),
	"mh":(0,"hm"),
	"hm":(0,"high"),
	"high":(1,"low"),
}

def filter_true(comb):
	return 1
	
def filter_simple(comb):
	for c in comb:
		if not c in ["low","middle","high"]:
			return 0
	return 1
	
def filter1(comb):
	(a,b,c,d)=comb
	if d!="low":
		return 0
	return 1

def get_next_descr(prev, filter):
	answer=[]
	p=list(prev)
	n=1
	
	while n:
		p.reverse()
		carry=1
		for d in p:
			if carry:
				(carry, next)=next_data[d]
			else:
				next=d
			answer.append(next)
		if carry:
			raise RuntimeError, "no more scenarios"
		answer.reverse()
		n=not filter(answer)
		if n:
			p=answer
			answer=[]
	
	return tuple(answer)

def get_first_scen(filter):
	descr=("low","low","low","low")
	while 1:
		while not filter(descr):
			descr=get_next_descr(descr, filter)
		try:
			return (get_values(descr),descr)
		except KeyError:
			pass
		descr=get_next_descr(descr, filter)

def get_next_scen(prev_descr, filter):
	descr=get_next_descr(prev_descr, filter)
	while 1:
		while not filter(descr):
			descr=get_next_descr(descr, filter)
		try:
			return (get_values(descr),descr)
		except KeyError:
			pass
		descr=get_next_descr(descr, filter)

def generate_scenario((FI,CI,LI,IP), file, (PN_FI,PN_CI,PN_LI,PN_IP)):
	year=1973
	#FI=0
	#CI=0
	#LI=6.33
	#IP=0
	Region="Irkutsk"
	quant_init()
	natural=ExcelForestModel(dsn="forest", year=year, NO_FIRES=0, NO_LOGGING=0, NO_CULTURES=0,
		FIRES_INTENSITY=FI, CULTURES_INTENSITY=CI, LOGGING_INTENSITY=LI, ILL_PERCENT=IP)
	t1=natural.DoModel(Region, year)
	quant_done()
	data_name="_".join([PN_FI,PN_CI,PN_LI,PN_IP])
	file_name=file.name+data_name
	Bigglesplot("postscript","%s.eps" % file_name, t1, natural)
	#print t1
	t1.save(file,"scen_%s" % data_name)

def main():
	(scen, descr)=get_first_scen(filter1)
	n=1
	f=open("scenarios.dta","w")
	while n:
		print (scen,descr)
		generate_scenario(scen, f, descr)
		#sqd
		#break #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
		try:
			(scen,descr)=get_next_scen(descr, filter1)
		except RuntimeError:
			n=0
	f.close()

def main1():
	quant_init()
	f1=ManyGISForestModel("forest_gis", NO_FIRES=0, NO_LOGGING=0, NO_CULTURES=0)
	t1=f1.DoModel()
	quant_done()
	#quant_init()
	#f2=ManyGISForestModel("forest_gis", NO_FIRES=1, NO_LOGGING=1, NO_CULTURES=1)
	#t2=f2.DoModel()
	#quant_done()
	#r=t1.Copy()
	#f1.diff(f2, t1, t2, r)
	#Bigglesplot("postscript","test.eps", r)
	f1.print_something(50, t1)
	print t1

def main3():
	year=1973
	Region="Irkutsk"
	quant_init()
	natural=ExcelForestModel(dsn="forest", year=year, NO_FIRES=0, NO_LOGGING=1, NO_CULTURES=1)
	t1=natural.DoModel(Region, year)
	Bigglesplot("postscript","natural.eps", t1, natural)
	quant_done()
	quant_init()
	f2=ExcelForestModel(dsn="forest", year=year, NO_FIRES=0, NO_LOGGING=1, NO_CULTURES=0)
	t2=f2.DoModel(Region, year)
	Bigglesplot("postscript","natural+cult.eps", t2,f2)
	quant_done()
	r=t2.Copy()
	f2.diff(natural, t2, t1, r)
	Bigglesplot("postscript","natural+cult-natural.eps", r,f2)
	# ND-Logging wo/Cultures
	quant_init()
	f3=ExcelForestModel(dsn="forest", year=year, NO_FIRES=0, NO_LOGGING=0, NO_CULTURES=1)
	t3=f3.DoModel(Region, year)
	quant_done()
	Bigglesplot("postscript","logging_wo_cult.eps", t3,f3)
	e1=t3.Copy()
	f3.diff(natural, t3, t1, e1)
	Bigglesplot("postscript","logging-natural_wo_cult.eps", e1,f3)
	# (ED-Logging+cultures)-(ED-Logging_wo_cultures)
	quant_init()
	f4=ExcelForestModel(dsn="forest", year=year, NO_FIRES=0, NO_LOGGING=0, NO_CULTURES=0)
	t4=f4.DoModel(Region, year)
	quant_done()
	e2=t4.Copy()
	f4.diff(natural, t4, t1, e2)
	Bigglesplot("postscript","natural-(logging+cult.eps)", e1,f3)
	e3=e2.Copy()
	f4.diff(f3, e2, e1, e3)
	Bigglesplot("postscript","with_cultures.ps", e1,f3)

main()
