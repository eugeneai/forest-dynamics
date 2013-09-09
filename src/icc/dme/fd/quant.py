#import quant._quant as _quant
import _quant

debug=1

def set_debug(v):
	debug=v

def wrap(address, str, cls):
	if address==0:
		return None
	return cls(_quant.ConvertFromPointer(address, str))

def wrapc(str, cls):
	if str is None:
		return None
	return cls(str)

class ForeignStruct:
	def __init__(self, this, removable=0):
		#print this
		#if this[10]=="p":
		#	ferttr
		self.this=this
		self.removable=removable
	def __del__(self):
		if self.removable:
			self.release()
	def release(self):
		pass
	__setmethods__ = {
	}
	def as_parameter(self):
		return self.this
	def __setattr__(self,name,value):
		if (name == "this") or (name == "thisown"):
			self.__dict__[name] = value
			return
		method = self.__class__.__setmethods__.get(name,None)
		if method:
			return method(self.this,value)
		try:
			return getattr(self, "set_"+name)(value)
		except AttributeError:
			self.__dict__[name] = value
	__getmethods__ = {
	}
	def __getattr__(self,name):
		method = self.__class__.__getmethods__.get(name,None)
		if method:
			return method(self.this)
		try:
			return self.__dict__[name]
		except KeyError:
			if name[:4]=="get_":
				raise AttributeError, "not found"
			#try:
			return getattr(self, "get_"+name)()
			#except AttributeError:
			#	raise AttributeError,'Attribute "%s" of class %s instance not found' % (name, self.__class__.__name__)
	def __repr__(self):
		return "<%s instance at %s>" % (self.__class__.__name__, self.this,)

class Descriptor(ForeignStruct):
	def __init__(self, this, removable=0):
		ForeignStruct.__init__(self, this, removable)
	__setmethods__ = {
		"name" : _quant.ATPDescr_name_set,
		"type" : _quant.ATPDescr_type_set,
		"arity" : _quant.ATPDescr_arity_set,
		"constructive" : _quant.ATPDescr_constructive_set,
	}
	__getmethods__ = {
		"name" : _quant.ATPDescr_name_get,
		"type" : _quant.ATPDescr_type_get,
		"arity" : _quant.ATPDescr_arity_get,
		"constructive" : _quant.ATPDescr_constructive_get,
	}
	def release(self):
		rc=_quant.atp_descr_destroy(self.this)
		self.this=None
		return rc
	def __repr__(self):
		t=self.type
		if t==_quant.ATP_TYPE_VAR:
			return self.name
		elif t==_quant.ATP_TYPE_META_VAR:
			return "<%s>" % self.name
		elif t==_quant.ATP_TYPE_CONST:
			return "%s|%s|" % (self.name, self.value)
		elif t==_quant.ATP_TYPE_FUNC:
			return "%s/%i|%s|f|cons:%i" % (self.name, self.arity, self.value,self.constructive)
		elif t==_quant.ATP_TYPE_PRED:
			return "%s/%i|%s|p|cons:%i" % (self.name, self.arity, self.value,self.constructive)
		else:
			s="%s/%i(%s)=%s" % (self.name, self.arity, self.defs, self.exp)
			return s
	def get_value(self):
		return _quant.atp_descr_get_value(self.this)
	def set_value(self, value):
		return _quant.atp_descr_set_value(self.this, value)
	def get_defs(self):
		sub=self._get_sub()
		return wrapc(_quant.sub_defs_get(sub), DefList)
	def get_exp(self):
		sub=self._get_sub()
		exp=_quant.sub_exp_get(sub)
		return wrapc(exp, ExpNode)
	def _get_data(self):
		return _quant.ATPDescr_data_get(self.this)
	def _get_sub(self):
		data=self._get_data()
		return _quant.descr_sub_get(data)
	def store(self):
		return store_descriptor(self)
	def prove(self, trace=None):
		exp=self.exp
		lnk=exp.link()
		pcf=lnk.as_pcf()
		pcf.reduce()
		print "reduced:"
		pcf.print_as_tree()
		pcf.prepare_to_inference()
		return (pcf.prove(trace), pcf)


def create_descriptor(name, descr_type, arity, value=None):
	this=_quant.atp_descr_new(name, descr_type, arity)
	d=Descriptor(this, 1)
	if not (value is None):
		d.value=value
	return d

def install_constant(name, value=None):
	d=create_descriptor(name, _quant.ATP_TYPE_CONST, 0, value)
	d.store()
	return d

def install_function(name, argn, value=None):
	d=create_descriptor(name, _quant.ATP_TYPE_FUNC, argn, value)
	d.store()
	return d

def install_predicate(name, argn, value=None):
	d=create_descriptor(name, _quant.ATP_TYPE_PRED, argn, value)
	d.store()
	return d

def get_descriptor(name, arity=0):
	return wrapc(_quant.atp_descr_global_lookup(name,arity), Descriptor)

def store_descriptor(descr):
	old=get_descriptor(descr.name, descr.arity)
	if old:
		print "Warning: there are already registered descriptor with the same params '%s' (skipping new one)" % old
		return
		# raise ValueError, "there are already registered descriptor with the same params '%s'" % old
	_quant.atp_descr_global_store(descr.this)
	descr.removable=0

class GNode(ForeignStruct):
	def __init__(self, this, clss):
		ForeignStruct.__init__(self, this)
		self.clss=clss
	__setmethods__ = {
		"cnext" : _quant._GNode_next_set,
		"cprev" : _quant._GNode_prev_set,
		"cparent" : _quant._GNode_parent_set,
		"cchildren" : _quant._GNode_children_set,
	}
	__getmethods__ = {
	#	"cdata" : _quant._GNode_data_get,
		"cnext" : _quant._GNode_next_get,
		"cprev" : _quant._GNode_prev_get,
		"cparent" : _quant._GNode_parent_get,
		"cchildren" : _quant._GNode_children_get,
	}
	def get_nchildren(self):
		return _quant.g_node_n_children(self.this)
	def _get_data(self, string_SWIG_type):
		return _quant.ConvertFromPointer(_quant._GNode_data_get(self.this), string_SWIG_type)
	def get_children(self):
		return wrapc(self.cchildren, self.clss[2])
	def get_prev(self):
		return wrapc(self.cprev, self.clss[1])
	def get_next(self):
		return wrapc(self.cnext, self.clss[1])
	def get_parent(self):
		return wrapc(self.cparent, self.clss[0])

class ExpNode(GNode):
	def __init__(self, this):
		GNode.__init__(self, this, (ExpNode,ExpNode,ExpNode))
	def get_data(self):
		return wrapc(self._get_data("_p_ATPExpData"), ExpData)
	def __repr__(self):
		data=self.get_data()

		defs=data.get_defs()
		sgn=data.sign
		s=""
		if sgn==_quant.ATP_SIGN_PC_E:
			s+="E:"+repr(defs)
		elif sgn==_quant.ATP_SIGN_PC_A:
			s+="A:"+repr(defs)
		elif sgn==_quant.ATP_SIGN_PRED or sgn==_quant.ATP_SIGN_SUB:
			if data.defs:
				s+=s+repr(defs)
		if sgn==_quant.ATP_SIGN_PC_E  or sgn==_quant.ATP_SIGN_PC_A:
			s+=" ["
		curr=self.children
		nc=self.nchildren
		ss=chr(sgn)+" "
		ncurr=1
		while curr:
			s+=repr(curr)
			if ncurr!=nc:
				s+=ss
			curr=curr.next
			ncurr+=1

		if sgn==_quant.ATP_SIGN_PC_E  or sgn==_quant.ATP_SIGN_PC_A:
			s+=" ]"
		return s
	def link(self):
		return wrapc(_quant.atp_exp_node_link(self.this), ExpNode)
	def as_pcf(self):
		return wrapc(_quant.atp_exp_node_2_pcf(self.this), PCFNode)


class ExpData(ForeignStruct):
	__setmethods__ = {
		"csign" : _quant.ATPExpData_sign_set,
#		"data" : _quant.ATPExpData_data_set,
	}
	__getmethods__ = {
		"csign" : _quant.ATPExpData_sign_get,
#		"data" : _quant.ATPExpData_data_get,
	}
	def get_defs(self):
		return DefList(_quant.ATPExpData_data_get(self.this))
	def get_sign(self):
		return ord(self.csign)

class GArray(ForeignStruct):
	def __init__(self, this, elem_size):
		ForeignStruct.__init__(self, this)
		self._size_=elem_size
	__setmethods__ = {
		"data" : _quant._GArray_data_set,
		"len" : _quant._GArray_len_set,
	}
	__getmethods__ = {
		"data" : _quant._GArray_data_get,
		"len" : _quant._GArray_len_get,
	}
	def __len__(self):
		return self.len
	def __getitem__(self, index):
		return _quant.g_array_index_p(self.this, index, self._size_)
	def __repr__(self):
		s="%s([" % self.__class__.__name__
		for index in range(len(self)):
			s=s+repr(self[index])+", "
		return s+"])"

class DefList(GArray):
	def __init__(self, this):
		GArray.__init__(self, this, elem_size=_quant.cvar.ATPDef_size)
	def __getitem__(self, index):
		return wrap(GArray.__getitem__(self, index), "_p_ATPDef", Def)
	def __repr__(self):
		s=""
		l=len(self)
		for index in range(l):
			s+=repr(self[index])+"_"+str(index)
			if index+1<l:
				s+=", "
			else:
				s+=" "
		return s
	def reduced(self, skip_free_func=1):
		answer=[]
		for i in range(len(self)):
			item=self[i]
			if skip_free_func:
				if item.type==_quant.ATP_TYPE_FUNC:
					continue
			red=item.reduced(number=i)
			if red is None:
				pass
			else:
				answer.append(red)
		return answer


class RefList(GArray):
	def __init__(self, this):
		GArray.__init__(self, this, elem_size=_quant.cvar.ATPRef_size)
	def __getitem__(self, index):
		return wrap(GArray.__getitem__(self, index), "_p_ATPRef", Ref)
	def __repr__(self):
		s=""
		l=len(self)
		for index in range(l):
			s+=repr(self[index])
			if index+1<l:
				s+=", "
		return s
	def reduced(self):
		answer=[]
		for i in range(len(self)):
			item=self[i]
			red=item.reduced()
			if 0: #red is None:
				pass
			else:
				answer.append(red)
		return answer

class Def(ForeignStruct):
	__setmethods__ = {
		"type" : _quant.ATPDef_type_set,
		"info" : _quant.ATPDef_info_set,
		#"args" : _quant.ATPDef_args_set,
	}
	__getmethods__ = {
		"type" : _quant.ATPDef_type_get,
		"info" : lambda x: Info(_quant.ATPDef_info_get(x)),
		#"args" : lambda x: RefList(_quant.ATPDef_args_get(x)),
	}
	def get_args(self):
		#return RefList(_quant.ATPDef_args_get(self.this))
		args=_quant.ATPDef_args_get(self.this)
		if args is None:
			return None
		return RefList(args)
	def __repr__(self):
		t=self.type
		if t==_quant.ATP_TYPE_NULL:
			return repr(None)
		elif t==_quant.ATP_TYPE_VAR:
			return self.info.name
		elif t==_quant.ATP_TYPE_META_VAR:
			return "M_"+self.info.name
		elif t==_quant.ATP_TYPE_CONST:
			#return "%s |%s| " % (self.info.descr.name, repr(self.info.descr.value))
			return "%s" % (repr(self.info.descr.value))
		elif t==_quant.ATP_TYPE_FUNC:
			return "%s(%s)" % (self.info.descr.name, self.args)
		elif t==_quant.ATP_TYPE_PRED:
			return "%s(%s)" % (self.info.descr.name, self.args)
		elif t==_quant.ATP_TYPE_SUB:
			return "%s(%s)" % (self.info.descr.name, self.args)
		else:
			return "<%s instance at %s type: %i, info: %s, args: %s>" % (self.__class__.__name__, self.this, self.type, self.info, self.args)
	def reduced(self, number):
		t=self.type
		if t==_quant.ATP_TYPE_NULL:
			return None
		elif t==_quant.ATP_TYPE_VAR:
			return Var(self.info.name+"_"+str(number))
		elif t==_quant.ATP_TYPE_META_VAR:
			return Var("meta_"+self.info.name+"_"+str(number))
		elif t==_quant.ATP_TYPE_CONST:
			return self.info.descr.value
		elif t==_quant.ATP_TYPE_FUNC:
			rargs=self.args.reduced()
			val=self.info.descr.value
			if val:
				try:
					_a=1
					answer=apply(val, rargs)
					_a=0
				finally:
					if _a:
						print "Argument were:", rargs,"obtained from:", self
				return answer
			return Func(self.info.descr.name, rargs)
		elif t==_quant.ATP_TYPE_PRED:
			rargs=self.args.reduced()
			val=self.info.descr.value
			if val:
				try:
					_a=1
					answer=apply(val, rargs)
					_a=0
				finally:
					if _a:
						print "Argument were:", rargs,"obtained from:", self
				return answer
			return Pred(self.info.descr.name, rargs)
		elif t==_quant.ATP_TYPE_SUB:
			return None
		else:
			return None


class Info(ForeignStruct):
	__setmethods__ = {
		"name" : _quant.ATPInfo_name_set,
		#"descr" : _quant.ATPInfo_descr_set,
	}
	__getmethods__ = {
		"name" : _quant.ATPInfo_name_get,
		#"descr" : lambda x: Descriptor(_quant.ATPInfo_descr_get(x)),
	}
	def get_descr(self):
		descr=_quant.ATPInfo_descr_get(self.this)
		d=Descriptor(descr)
		return d
	def __repr__(self):
		#return "<%s instance at %s name: %s, descr: %s>" % (self.__class__.__name__, self.this, self.name, self. descr)
		return "<%s instance at %s name: %s>" % (self.__class__.__name__, self.this, self.name)


class Ref(ForeignStruct):
#	__setmethods__ = {
#		"owner" : _quant.ATPRef_owner_set,
#		"offset" : _quant.ATPRef_offset_set,
#	}
	__getmethods__ = {
		"owner" : lambda x: DefList(_quant.ATPRef_owner_get(x)),
		"cowner" : _quant.ATPRef_owner_get,
		"offset" : _quant.ATPRef_offset_get,
	}
	def unref(self):
		owner=self.cowner
		offset=self.offset
		addr=_quant.g_array_index_p(owner, offset, _quant.cvar.ATPDef_size)
		object=_quant.ConvertFromPointer(addr, "_p_ATPDef")
		return Def(object)
	def get_def(self):
		return self.unref()
	def __repr__(self):
		return repr(self.unref())+"_"+str(self.offset)
	def reduced(self):
		return self.unref().reduced(self.offset)

class PCFNode(GNode):
	def __init__(self, this, clss=None):
		if clss is None:
			clss=(PCFNode, PCFNode, PCFNode)
		GNode.__init__(self, this, clss)
	def _get_data(self, string_SWIG_type):
		addr=_quant._GNode_data_get(self.this)
		if addr==1:
			addr=0
		return _quant.ConvertFromPointer(addr, string_SWIG_type)
	def get_data(self):
		return wrapc(self._get_data("_p__GArray"), DefList)
	def get_defs(self):
		return self.get_data()
	def __repr__(self):
		return self._repr_()
	def _repr_data(self, data):
		return repr(data)
	def next_sgn(self, prev):
		if prev=="A":
			return "E"
		else:
			return "A"
	def tran_sgn(self, sgn):
		return sgn
	def _repr_(self, sgn="A"):
		defs=self.get_data()
		sgn1=self.tran_sgn(sgn)
		s="%s: %s " % (sgn1, self._repr_data(defs))
		nc=self.nchildren
		if nc > 1:
			s+="( "
			ss="; "
		else:
			ss=" "
		curr=self.children
		nsgn=self.next_sgn(sgn)
		cc=1
		while curr:
			s+=curr._repr_(nsgn)
			if cc<nc:
				s+=ss
			curr=curr.next
		if nc > 1:
			s+=") "
		return s
	def print_as_tree(self, sgn="A", level=0):
		tabs="    "*level
		defs=self.get_data()
		sgn1=self.tran_sgn(sgn)
		s=tabs+"%s: %s " % (sgn1, self._repr_data(defs))
		print s
		#print tabs, "|"

		curr=self.children
		nsgn=self.next_sgn(sgn)
		while curr:
			curr.print_as_tree(nsgn, level+1)
			curr=curr.next
	def reduce(self):
		return _quant.atp_pcf_reduce(self.this)
	def prepare_to_inference(self):
		answer=_quant.atp_pcf_prepare_to_inference(self.this)
		self.clss=(PCFNode, PCFNode, Base)
		self.prepared=1
		return answer
	def is_prepared(self):
		try:
			return self.prepared
		except AttributeError:
			return 0
	def prove(self, trace=None):
		if not self.is_prepared():
			self.prepare_to_inference()
		ex=1
		while ex:
			rc=_quant.atp_pcf_root_step(self.this)
			if trace:
				answer = apply(trace, (self,))
				if not answer:
					break
			ex=rc==_quant.ATP_STEP_SUCCESS
		return rc
	def get_reduced_defs(self):
		defs=self.get_defs()
		if defs is None:
			return []
		return defs.reduced()
	def get_reduced_bases(self):
		if not self.is_prepared():
			self.prepare_to_inference()
		answer=[]
		curr=self.children
		while curr:
			answer.append(curr.get_reduced_defs())
			curr=curr.next
		return answer

class PosList(GArray):
	def __init__(self, this):
		GArray.__init__(self, this, _quant.cvar.guint_size) # size of int
	def __repr__(self):
		s=""
		for i in range(len(self)):
			s+=str(self[i])+","
		return s
	def __getitem__(self, index):
		addr=GArray.__getitem__(self, index)
		return _quant.guint_at_address(addr)

class PCFData(ForeignStruct):
	"""
	__setmethods__ = {
		"defs" : _quantc.ATPPCFData_defs_set,
		"pos" : _quantc.ATPPCFData_pos_set,
		"lo_edge" : _quantc.ATPPCFData_lo_edge_set,
		"hi_edge" : _quantc.ATPPCFData_hi_edge_set,
		"attrs" : _quantc.ATPPCFData_attrs_set,
	}
	"""
	__getmethods__ = {
		"cdefs" : _quant.ATPPCFData_defs_get,
		"cpos" : _quant.ATPPCFData_pos_get,
		"lo_edge" : _quant.ATPPCFData_lo_edge_get,
		"hi_edge" : _quant.ATPPCFData_hi_edge_get,
		#"attrs" : _quantc.ATPPCFData_attrs_get,
	}
	def get_defs(self):
		return wrapc(self.cdefs, DefList)
	def get_pos(self):
		return wrapc(self.cpos, PosList)
	def __repr__(self):
		s=repr(self.get_defs())+"["+repr(self.get_pos())+"] lo: %i hi: %i" % (self.lo_edge, self.hi_edge)
		return s



class Base(PCFNode):
	def __init__(self, this):
		PCFNode.__init__(self, this, (PCFNode, Base, Quest))
	def get_data(self):
		return wrapc(self._get_data("_p_ATPPCFData"), PCFData)
	def _repr_data(self, data):
		if debug:
			return repr(data)
		else:
			return repr(data.get_defs())
	def get_defs(self):
		return self.get_data().get_defs()
	def tran_sgn(self, prev):
		return "B"

class Quest(PCFNode):
	def __init__(self, this):
		PCFNode.__init__(self, this, (Base, Quest, PCFNode))
	def _repr_data(self, data):
		if debug:
			return repr(data)
		else:
			return repr(data.get_defs())
	def get_data(self):
		return wrapc(self._get_data("_p_ATPPCFData"), PCFData)
	def get_defs(self):
		return self.get_data().get_defs()
	def tran_sgn(self, prev):
		return "Q"

def reduce_read_lines(strings):
	"""Get "\"-delimited strings together replacing "\" by " "
	"""
	result=[]
	prev=0
	for str in strings:
		next=0
		s=str.strip()
		if s=="":
			prev=0
			continue
		if s[0]=="#":
			prev=0
			continue
		if s[-1]=="\\":
			s=s[:-1]+" "
			s=" "+s
			next=1
		if prev:
			result[-1]+=s
		else:
			result.append(s)
		prev=next
	return result

class Var:
	def __init__(self, name):
		self.name=name
	def __repr__(self):
		return self.name
	def __str__(self):
		return self.__repr__()

class Pred(Var):
	def __init__(self, name, args):
		Var.__init__(self, name)
		self.args=args
	def __repr__(self):
		return "%s%s" % (self.name, repr(tuple(self.args)))
class Func (Pred):
	pass

# translation

def translate_string_prim(str):
	return _quant.translate_input(str)
def translate_lines(lines):
	sl=reduce_read_lines(lines)
	for str in sl:
		translate_string_prim(str)
def translate_string(str):
	ls=str.splitlines()
	translate_lines(ls)

def quant_init():
	_quant.quant_init()

def quant_done():
	_quant.quant_done()

def trace(pcf):
	print "trace"
	pcf.print_as_tree()
	return 1
def test():
	quant_init()
	c=create_descriptor("one", _quant.ATP_TYPE_CONST, 0, 1)
	c.store()
	c=create_descriptor("two", _quant.ATP_TYPE_CONST, 0, 2)
	c.store()
	c=create_descriptor("three", _quant.ATP_TYPE_CONST, 0, 3)
	c.store()
	c=create_descriptor("four", _quant.ATP_TYPE_CONST, 0, 4)
	c.store()
	translate_string("""set steps_count 10000;
set trace 15;
set tree_write_depth 60;
set debug_level 3;
""")
	#translate_string("fm a=p(one)&(a:x[p(x)>q(x)]) & (q(one)>n(one)) & (n(one)>write(p1(one)))")
	#translate_string("fm a=p(f(one))&(a:x[p(f(x))>p(g(x))] & a:x[p(f(x))>p(f(f(x)))])")
	#translate_string("fm a=p(one, two)&(a:x[p(one,x)>e:y,z[p(y,f(z))]])")
	#translate_string("fm a=p(one, two)&(a:x[p(one,x)>e:y,z[p(y,f(x))]])")
	#translate_string("fm a=p(one), p(two) & (a:x,y[p(x),p(y)>q(x,y)])")
	translate_string("fm a=p(one), p(two) & (a:x,y[p(x,y)>q(x,y)])")
	#translate_string("fm a=p(one), p(two), p(three), p(four) & (a:x,y[p(x),p(y)>e:z[q(x,y)]])")
	#translate_string("fm a=e:o,o1[p(one), p(two), after(one, two), after(two, three), l(o,one, f(o, one)), l(o1,two, f(o1,one)) & (a:x,y,x1,s0[p(x),l(s0,x,f(s0,y)),after(y,x1)>e:s[l(s,x,f(s,x1))]])]")

	#translate_string("fm a=e:x,y[p(f(x)),p(f(y)) & a:y[p(f(y))>q(f(y))]]")
	#translate_string("fm a=e:x,y[p(x),p(y) & a:y[p(y)>q(y)]]")
	#translate_string("fm a=e:x,[p(f(x)) & (p(f(x))>q(f(x)))]")
	#translate_string("fm a=e:x,y,z[a(y),a(z),p(x) & a:y,x[p(x),a(y) > c(x,y)]]")
	#translate_string("fm a=e:a,b[p(one,a),p(two,b)&(a:x[p(one,x)>q(x)])]")
	#translate_string("fm a=e:x,y,z,k[p(x,y), p(y,z) & a:a,b,c[p(a,b),p(b,c)>q(a,b,c)]]")
	#!!!!!!!!!translate_string("fm a=p & (p>q)")
	#translate_string("fm a=e:[p(one),p(two),p(three),p(four) & a:x[b(x,two)>q(x)]]")
	#descr_b=get_descriptor("b",2)
	#descr_b.constructive=1
	#print "descr_b:", descr_b
	descr=get_descriptor("a", 0)
	dp2=get_descriptor("p",2)
	dp2.constructive=1
	print dp2
	kb=descr.exp
	lnk=kb.link()
	pcf=lnk.as_pcf()
	pcf.reduce()
	pcf.print_as_tree()
	pcf.prove(trace)
	#pcf.print_as_tree()
	bases=pcf.get_reduced_bases()
	print bases


	raise SystemExit, "exit"
	f=open("fwin.fpc")
	lines=f.readlines()
	lines=reduce_read_lines(lines)
	for line in lines:
		print line
		_quant.translate_input(line)
	f.close()

	descr=get_descriptor("Cultures", 9)
	descr=get_descriptor("KB")
	square=get_descriptor("Square",2)
	square.value="12345"
	print
	print "square:",  square
	kb=descr.exp
	lnk=kb.link()
	pcf=lnk.as_pcf()
	pcf.reduce()
	#pcf.print_as_tree()
	pcf.prepare_to_inference()
	print "before --------------"
	pcf.print_as_tree()
	print "start proving --------------"
	pcf.prove()
	print "end proving --------------"
	pcf.print_as_tree()


if __name__=="__main__":
	test()
