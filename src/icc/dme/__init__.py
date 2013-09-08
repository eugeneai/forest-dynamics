import DModel
def DMConnect(item, to, value):
	answer=DModel.NewItem()
	answer.next=item.another
	item.another=answer
	answer.another=to
	answer.value=value
	answer.initValue=value
	return answer

def DMItem(value, next=None, connect_to=None, intens=0.0):
	answer=DModel.NewItem()
	answer.value=value
	answer.initValue=value
	answer.next=next
	if connect_to is None:
		return answer
	DMConnect(answer, connect_to, intens)
	return answer
	

