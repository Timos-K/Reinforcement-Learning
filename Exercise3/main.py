#!/usr/bin/env python3
# encoding utf-8


from Environment import HFOEnv
import torch
import torch.multiprocessing as mp
from Networks import ValueNetwork
from Worker import train,hard_copy
import argparse
from SharedAdam import SharedAdam
import copy

parser = argparse.ArgumentParser(description='PyTorch MNIST Example')
parser.add_argument('--epochs', type=int, default=10, metavar='N',
                    help='number of epochs to train (default: 10)')
parser.add_argument('--lr', type=float, default=0.01, metavar='LR',
                    help='learning rate (default: 0.01)')
parser.add_argument('--momentum', type=float, default=0.5, metavar='M',
                    help='SGD momentum (default: 0.5)')
parser.add_argument('--seed', type=int, default=1, metavar='S',
                    help='random seed (default: 1)')
parser.add_argument('--log-interval', type=int, default=10, metavar='N',
                    help='how many batches to wait before logging training status')
parser.add_argument('--num_processes', type=int, default=8, metavar='N',
                    help='how many training processes to use (default: 2)')
parser.add_argument('--cuda', action='store_true', default=False,
                    help='enables CUDA training')


# Use this script to handle arguments and 
# initialize important components of your experiment.
# These might include important parameters for your experiment,
# your models, torch's multiprocessing methods, etc.

if __name__ == "__main__" :

	# Example on how to initialize global locks for processes
	# and counters.

	numOpponents = 1
	args = parser.parse_args()	
	counter = mp.Value('i', 0)
	lock = mp.Lock()
	device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

	# Initialize shared network

    
	# max_grads = 1.0
	# batch_size = 128
	# gamma = 0.999
	# copy_freq = 2000

	# val_network = ValueNetwork(inputDims=15,layerDims=64,outputDims=4)
	

	# target_value_network.apply(target_value_network.init_weights)
	val_network = ValueNetwork(15,[16,16,4],4)
	val_network.share_memory()

	target_value_network = ValueNetwork(15,[16,16,4],4)
	target_value_network.share_memory()

	hard_copy(val_network,target_value_network)


	# Shared optimizer ->  Share the gradients between the processes. Lazy allocation so gradients are not shared here
	optimizer = SharedAdam(params=val_network.parameters())
	optimizer.share_memory()
	timesteps_per_process = 2*(10**6) // args.num_processes

	processes = []
	for idx in range(0, args.num_processes):
			trainingArgs = (idx, val_network, target_value_network, optimizer, lock, counter,timesteps_per_process)
			p = mp.Process(target=train, args=trainingArgs)
			p.start()
			processes.append(p)
	for p in processes:
			p.join()
