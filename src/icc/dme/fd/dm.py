import DModel
def DMConnect(item, to, value):
	edge=DModel.NewItem()
	edge.another=to
	edge.value=value
	edge.initValue=value

	edge.next=item.another
	item.another=edge

	return edge

def DMItem(value, next=None, connect_to=None, intens=0.0):
	node=DModel.NewItem()
	node.value=value
	node.initValue=value
	node.next=next
	if connect_to is None:
		return node
	DMConnect(node, connect_to, intens)
	return node
