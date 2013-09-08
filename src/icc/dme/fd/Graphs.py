from mutils import *
from biomass_good import *
from spelper_good import *
from free_good import *
from logging_good import *
from coex_good import *
from Numeric import *

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

def BigglesPlot(device, file, legends, model=None, initial_text="", title=""):
	import biggles
	p=biggles.FramedPlot()
	#p(initial_text)
	#p("set data style linespoints")
	p.title=title
	p.xlabel=r'$t$'
	p.ylabel='Value'
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


def GnuPlot(self, device, file=None, legends=None, initial_text=""):
	import Gnuplot
	gp=Gnuplot.Gnuplot(debug=0)
	print device
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

	

def make_scen (name):
	g=globals()
	d={}
	l=len(name)
	for n in g.keys():
		if n[:l]==name:
			d[n]=g[n]
	return ModelParameter(d)
	
def test():
	scen=make_scen("biomass")
	scen.time=arange(51)
	BigglesPlot("postscript","biomass.eps", scen)
	scen=make_scen("free")
	scen.time=arange(51)
	BigglesPlot("postscript","free.eps", scen)
	scen=make_scen("logging")
	scen.time=arange(51)
	BigglesPlot("postscript","logging.eps", scen)
	scen=make_scen("spelper")
	scen.time=arange(51)
	BigglesPlot("postscript","spelper.eps", scen)
	scen=make_scen("coex")
	scen.time=arange(51)
	print scen
	BigglesPlot("postscript","coex.eps", scen)
	
if __name__=="__main__":
	test()