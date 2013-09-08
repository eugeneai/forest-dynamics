import types
#from math import *



class ModelParameter:
	def __init__(self, parameters_dict=None, primitive=0):
		if parameters_dict is None:
			pass
		else:
			self.__dict__.update(parameters_dict)
		self._primitive=primitive

	def __getitem__(self, index):
		return self.Convert(lambda x, p: x[p], index)

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
	def ConvertWithNames(self, convert_func, name_convert, parameter=None):
		answer=ModelParameter(primitive=self._primitive)
		for (key,value) in self.__dict__.items():
			if key[0]=="_" and key[1]!="_":
				continue
			new_key=name_convert(value, key, parameter)
			if type(value)==types.InstanceType:
				setattr(answer, new_key, value.Convert(convert_func, parameter))
			else:
				setattr(answer, new_key, convert_func(value, parameter))
			#print
		return answer
	def Copy(self):
		return self.Convert(lambda x, p: x.__copy__())
	def __str__(self):
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

	def ForEachDo(self, leaf_func, parameter, branch_func=None, branch=None):
		"""
		branch_func must return 0 if not to go down the branches
		if branch_func==None then the search always go down to the leaves
		"""
		items=self.__dict__.items()
		items.sort()
		for (key,value) in items:
			if branch is None:
				br=[key]
			else:
				br=branch+[key]
			if type(value)==types.InstanceType:
				if branch_func is None or branch_func(br, value, parameter):
					value.ForEachDo(leaf_func, parameter, branch_func, br)
			else:
				leaf_func(br, value, parameter)
	def values(self):
		items=self.__dict__.items()
		list=[]
		for (key,value) in items:
			list.append(value)
		return list

	def __add__(self, other):
		return self.interpret(lambda x,y: x+y, [other])
	def __sub__(self, other):
		return self.interpret(lambda x,y: x-y, [other])
	def __mul__(self, other):
		return self.interpret(lambda x,y: x*y, [other])
	def __div__(self, other):
		return self.interpret(self._div_, [other])
	def _div_(self, x,y):
		try:
			return x/y
		except OverflowError:
			print "overflow :", y
			return 0
	def __abs__(self):
		return self.interpret(lambda x: abs(x), [])
	def __neg__(self):
		return self.interpret(lambda x: -x, [])
	def __pos__(self):
		return self.interpret(lambda x: x, [])
	def __int__(self):
		return self.interpret(lambda x: int(x), [])
	def __long__(self):
		return self.interpret(lambda x: long(x), [])
	def __float__(self):
		return self.interpret(lambda x: float(x), [])
	
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
			_break=0
			for other in others:
				if type(other)==types.InstanceType and other._primitive==0:
					try:
						vv=getattr(other,key)
						o.append(vv)
					except AttributeError:
						_break=1
				else:
					o.append(other)
				if _break:
					break
			if _break:
				continue

			if type(value)==types.InstanceType and not value._primitive:
				setattr(n, key, value.interpret(func, o))
			else:
				params=[value]+o
				setattr(n, key, apply(func, params))

		return n
	def save(self, file, var_name=None):
		if type(file)==types.StringType:
			f=open(file, "w")
			need_closed=1
		else:
			f=file
			need_closed=0
		if var_name:
			f.write("%s=" % var_name)
		self._repr_data(f)
		if need_closed:
			f.close()
	def _repr_data(self, file):
		file.write(repr(self))
		file.write("\n")
	def __repr__(self):
		keys=self.__dict__.keys()
		keys.sort()
		s="%s({" % self.__class__.__name__
		for key in keys:
			val=self.__dict__[key]
			s+='%s:%s,' % (repr(key), repr(val))
		s+="})"
		return s
		

#def sin(x):
#	return x.interpret(lambda x: sin(x),[])


def test():
	a=ModelParameter({"S":1, "D":2})
	b=ModelParameter({"S":20})
	#s=repr(a)
	#print s, eval(s)
	f=open("t.dta","w")
	a.save(f, "name")
	a.save(f, "name2")
	f.close
	
if __name__=="__main__":
	test()
	
	