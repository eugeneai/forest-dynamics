import pygraphviz as pgv
import sys

G=pgv.AGraph()
G.add_node('a')
G.add_edge('b','c')
print G
G.graph_attr['label']='A Graph'
G.node_attr['shape']='circle'
G.edge_attr['color']='blue'
s=G.string()
print s
G.write(sys.stdout)
G.layout(prog='dot')
print G.layout()


#import pdb; pdb.set_trace()

s=G.draw(None, format='plain')
print s

G.draw("a.ico", format='ico')
G.draw("a.bmp", format='bmp')

print len(s)
#print s

quit()
