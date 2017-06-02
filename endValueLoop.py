import os, re
import openpyxl
import multiprocessing
import extension_util as eu
import pkg.Simulator.simulator as sim
from joblib import Parallel, delayed
from collections import defaultdict



def runEndValueLoop(init_model,extensions,logf,outPath,**kwargs):

	simLen = kwargs["simLen"] if "simLen" in kwargs else 10000
	simRun = kwargs["simRun"] if "simRun" in kwargs else 10

	curr_model = outPath + "final.xlsx"
	os.system("cp "+init_model+" "+curr_model)

	golden = get_golden(curr_model)
	model = sim.Manager(curr_model)
	model.run_simulation('ra',simRun,simLen,outPath+"trace.txt",outMode=3)
	prev_diff, curr_diff = float('inf'), get_diff(outPath+"trace.txt",golden,simRun)


	logf.write("Inital difference between golden and current model: " + str(curr_diff) + "\n\n")
	print("Inital difference between golden and current model: " + str(curr_diff))

	ignore, diff_trend = set(), [curr_diff]
	while curr_diff < prev_diff and len(extensions) > len(ignore):
		prev_diff = curr_diff
		
		gen = (ext for ext in extensions if ext[0] not in ignore)
		num_cores = multiprocessing.cpu_count()
		Parallel(n_jobs=num_cores,verbose=50)(delayed(eu.extend_unit)\
			(curr_model,ext,ignore,simRun,simLen,outPath) \
			for ext in gen)

		gen = (ext for ext in extensions if ext[0] not in ignore)
		ext_to_diff = dict()
		for ext in gen:
			trace = outPath+"~temp_trace_"+str(ext[0])+".txt"
			ext_to_diff[ext[0]] = get_diff(trace,golden,simRun)
		
		min_idx = min(ext_to_diff, key=ext_to_diff.get)
		if ext_to_diff[min_idx] < prev_diff:
			curr_diff = ext_to_diff[min_idx]
			diff_trend += [curr_diff]
			ignore.add(min_idx)
			ext_model = outPath + "~temp_final_" + str(min_idx) + ".xlsx"
			os.system("cp "+ext_model+" "+curr_model)
			# os.system("rm ~temp_*")

			print("Extend the model using extension group "+str(min_idx)+".")
			logf.write("Extend the model using extension group "+str(min_idx)+". Difference is "+str(curr_diff))
			logf.write("\nEdges are: \n")
			for ele in extensions[min_idx-1][1:]:
				logf.write(str(ele))
			logf.write('\n\n')

	print("Diff Trend: ",diff_trend)
	logf.write('Diff Trend: ')
	logf.write(' -> '.join([str(ele) for ele in diff_trend]))


# Read in the baseline model, return a dictionary for the golden result
def get_golden(mdl):

	wb = openpyxl.load_workbook(mdl)
	ws = wb.active
	golden = dict()
	for rows in ws.iter_rows():
		if rows[0].value is None or rows[0].value.lower()=="variable name" \
			or len(rows)<7 or rows[6].value is None: continue
		golden[rows[0].value] = float(rows[6].value)
	return golden


# Parse the trace file and return the total difference
def get_diff(trace,golden,simRun):

	total_diff = 0
	with open(trace) as f:
		f.readline()
		for line in f:
			line = line.strip()
			s = re.split(' ', line)

			if s[0] in golden:
				total_diff += abs(golden[s[0]] - float(int(s[-1]) / simRun))

	return total_diff
