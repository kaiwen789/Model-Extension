import re, copy, sys, os
from collections import defaultdict

def runMarkovCluster(out_dir,ext_edges,base_model,coef):
	
	ext_model = buildExtGraph(ext_edges,base_model)
	clusteringAlgo(out_dir,ext_model,coef)
	res = getGroupedExt(out_dir+'markov_cluster',ext_edges)

	return res

# Construct the graph for the extension edges and the original model
def buildExtGraph(ext_edges,base_model=dict()):
	
	ext_model = copy.deepcopy(base_model)

	for edge in ext_edges:
		if edge[1] in ext_model:
			ext_model[edge[1]].add(edge[0])
		else:
			ext_model[edge[1]] = {edge[0]}

	return ext_model



# Run MCL
def clusteringAlgo(out_dir,ext_model,coef):
	
	cluster_file = out_dir + 'markov_cluster'
	abc_model = out_dir + 'abc_model'
	output_stream = open(abc_model, 'w')
	for tgt in sorted(ext_model):
		for reg in sorted(ext_model[tgt]):
			if tgt==reg: continue
			output_stream.write(reg+' '+tgt+'\n')
	output_stream.close()
	# print('mcl '+abc_model.replace(' ','\ ')+' --abc -I '+str(coef)+' -V all -o '+cluster_file.replace(' ','\ '))
	os.system('mcl '+abc_model.replace(' ','\ ')+' --abc -I '+str(coef)+' -V all -o '+cluster_file.replace(' ','\ '))


# Generate list of extensions
def getGroupedExt(cluster_file,ext_edges):

	group_num = 1
	get_group = dict()
	get_ext = defaultdict(list)
	res = list()

	with open(cluster_file) as f:
		for idx, line in enumerate(f,start=1):
			for ele in re.findall('\S+',line.strip()):
				get_group[ele] = idx

	for edge in ext_edges:
		g1 = get_group[edge[0]] if edge[0] in get_group else sys.maxsize
		g2 = get_group[edge[1]] if edge[1] in get_group else sys.maxsize
		group = min(g1, g2)
		if group==sys.maxsize: continue
		get_ext[group] += [list(edge)]

	for key in sorted(get_ext):
		if not get_ext[key]: continue
		res.append([group_num]+get_ext[key])
		group_num += 1

	return res