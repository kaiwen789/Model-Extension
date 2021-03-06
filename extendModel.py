import pickle
import os, sys
import argparse
import pkg.Simulator.simulator as sim
from extension_util import extend_model
from endValueLoop import runEndValueLoop


def input_parsing():

	parser = argparse.ArgumentParser()
	requiredNamed = parser.add_argument_group('required input arguments')
	requiredNamed.add_argument("-m","--model",help="name of the model (under dataPath)", required=True)
	requiredNamed.add_argument("-ex","--experiment",help="name of the folder of the experiment (under dataPath)", required=True)
	parser.add_argument("-i", "--dataPath", help="relative path to the data", default="../data/")
	parser.add_argument("-eg","--extensionGroup",help="extension groups produced by buildExtension.py, default as \'grouped_ext\' (under dataPath)", default="grouped_ext")
	parser.add_argument("-me","--method", help="method to do model extension", choices=["endValueLoop","checkerLoop","simple"], default="endValueLoop")
	parser.add_argument("-l","--logFile", help="output folder for current experiment", default="logFile")
	parser.add_argument("-t","--topCluster", help="use only the top few clusters", default=0, type=int)
	additionalArg = parser.add_argument_group('additional argument for each method')
	additionalArg.add_argument("--simRun", help="(endValueLoop/checkerLoop) number of simulation experiment, default as 100", default=100, type=int)
	additionalArg.add_argument("--simLen", help="(endValueLoop/checkerLoop) step of simulation, default as 10000", default=10000, type=int)
	additionalArg.add_argument("--clusterNum", help="(simple) the index of the cluster to be extended, default as 1 (1-base)", default=1, type=int)
	args = parser.parse_args()

	assert os.path.isdir(args.dataPath), "dataPath \"" + args.dataPath + "\" is not a path"
	assert os.path.isdir(args.dataPath+args.experiment), "experiment path \"" + args.dataPath + args.experiment + "\" is not a path"
	assert os.path.exists(args.dataPath+args.model), "model \"" + args.dataPath+args.model + "\" does not exist"
	assert os.path.exists(args.dataPath+args.experiment+args.extensionGroup), "extension group \"" + args.extensionGroup + "\" does not exist"

	return args


def main():

	args = input_parsing()
	print(args)

	outPath = (args.dataPath + args.experiment).replace(' ','\ ')
	print(outPath)
	init_model = args.dataPath + args.model
	extensions = pickle.load(open(args.dataPath+args.experiment+args.extensionGroup,'rb'))
	if args.topCluster > 0: extensions = extensions[:min(args.topCluster,len(extensions))]
	logf = open(args.dataPath + args.experiment + args.logFile, 'w')

	if args.method == "endValueLoop":
		logf.write("Starting to extend model "+args.model+" \nwith "+args.extensionGroup+" using end value loop method...\n")
		print("Starting to extend model "+args.model+" \nwith "+args.extensionGroup+" using end value loop method...")
		runEndValueLoop(init_model,extensions,logf,outPath,simLen=args.simLen,simRun=args.simRun)

	elif args.method == "simple":
		assert len(extensions) >= args.clusterNum and args.clusterNum >= 1, "cluster number "+str(args.clusterNum)+" out of bound. Size of extensions is "+str(len(extensions))+"."
		logf.write("Extend the model "+args.model+" with cluster number "+str(args.clusterNum)+" in "+args.extensionGroup+"\n")
		logf.write("Extended edges are: \n")
		logf.write(str(extensions[args.clusterNum-1]))
		print("Extend the model "+args.model+" with cluster number "+str(args.clusterNum)+" in "+args.extensionGroup)
		print("Extended edges are: ")
		print(extensions[args.clusterNum-1])
		extend_model(init_model,extensions[args.clusterNum-1],outPath+"simpleFinal.xlsx")



if __name__ == '__main__':
	main()