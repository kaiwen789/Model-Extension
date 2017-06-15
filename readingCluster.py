import os, re
from collections import defaultdict

def runReadingCluster(out_dir,ext_info,coef):
	
	sorted_edge = sorted(ext_info)
	reading_edges, edge_idx = parse_reading_edges(sorted_edge,ext_info)
	clusteringAlgo(out_dir,reading_edges,coef)
	res = getGroupedExt(out_dir+'reading_cluster',sorted_edge)

	return res


def parse_reading_edges(sorted_edge,ext_info):

	reading_edges, reading_to_ext, edge_idx = defaultdict(int), defaultdict(list), dict()
	for idx, edge in enumerate(sorted_edge):
		edge_idx[edge] = idx
		for reading in re.split(' ',ext_info[edge][4]):
			for pre_id in reading_to_ext[reading]:
				reading_edges[(pre_id, idx)] += 1
			reading_to_ext[reading].append(idx)

	return reading_edges, edge_idx



def clusteringAlgo(out_dir,reading_edges,coef):

	cluster_file, abc_model = out_dir + "reading_cluster", out_dir + "reading_abc"
	output_stream = open(abc_model, 'w')
	for ext, affinity in reading_edges.items():
		output_stream.write(str(ext[0])+" "+str(ext[1])+" "+str(affinity)+"\n")
	output_stream.close()
	os.system('mcl '+abc_model.replace(' ','\ ')+' --abc -I '+str(coef)+' -V all -o '+cluster_file.replace(' ','\ '))


def getGroupedExt(cluster_file,sorted_edge):

	group_num = 1
	res = list()

	with open(cluster_file) as f:
		for idx, line in enumerate(f,start=1):
			curr = [idx]
			for edge_idx in re.findall('\S+',line.strip()):
				curr.append(list(sorted_edge[int(edge_idx)]))
			res.append(curr)

	return res
