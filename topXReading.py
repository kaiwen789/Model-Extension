# The last five elements from Peter are 
# score,kindscore,matchlevel,epistemicvalue,file_numbers,number
import re
from queue import Queue
from copy import deepcopy
from collections import defaultdict

def runTopXReading(ext_info, topX, max_layer):

	if topX >= len(ext_info):
		return getAll(ext_info)

	num_to_ext, ext_to_num = getNumExt(ext_info)

	my_q, visited = Queue(), set(sorted(ext_info,key=lambda k: int(ext_info[k][0]),reverse=True)[:topX])
	for ext in visited:
		my_q.put((1,ext))
	while not my_q.empty():
		layer, ext = my_q.get()
		if layer >= max_layer: break
		print(ext, ext_to_num[ext])
		for num in ext_to_num[ext]:
			print(num, num_to_ext[num])
			for e in num_to_ext[num]:
				if e in visited: continue
				my_q.put((layer+1, e))
				visited.add(e)

	res = [0]
	for ext in visited:
		res.append(list(ext))

	return res


def getAll(ext_info):

	res = [0]
	for ext in ext_info:
		res.append(list(ext))
	return res

def getNumExt(ext_info):

	num_to_ext, ext_to_num = defaultdict(set), defaultdict(set)
	for ext, info in ext_info.items():
		for num in re.split(' ',info[4]):
			num_to_ext[int(num)].add(ext)
			ext_to_num[ext].add(int(num))

	return num_to_ext, ext_to_num

