# Task is to find the network induced by the highest activity paths
# Because of the formulation of node and edge weights,
# this translates to all the shortest paths whose weight < percentile threshold
# Also the path has to have no. of hops >= 2
import networkx as nx
import sys
import numpy as np

# Given a graph and a list of nodes comprising a path
# Return sum of weights of edges in the path
def get_path_cost(G, path):
	path_cost = 0.0
	for i in range(len(path) - 1): # Add edges in this path to edge set
		path_cost += G[path[i]][path[i+1]]['weight']
	return path_cost

# Input: Weighted network, Percentile threshold
# Return: Highest activity paths
def highest_activity_paths(input_network, percentile):
	path_length_thresh = 2

	#print "Calculating shortest paths..."
	shortest_paths = nx.all_pairs_dijkstra_path(input_network)

	#print "Extracting paths with length >=",path_length_thresh,"and corresponding costs into an array..."
	# list of tuples (cost, path)
	# path is a list of nodes
	cost_paths = []
	for src, dest_paths in shortest_paths.items():
		for dest, path in dest_paths.items():
			if (len(path) - 1) >= path_length_thresh:
				cost_paths.append((get_path_cost(input_network, path), path))
	costs = [tup[0] for tup in cost_paths] # this is necessary for the percentile computation
	#print "Got ", len(cost_paths), " shortest paths"

	#print "Sorting paths based on costs..."
	cost_paths_sorted = sorted(cost_paths)

	network_path_cost_thresh = np.percentile(costs, percentile)

	# Get highest activity paths
	highestActivityPaths_network = set()
	for tup in cost_paths_sorted:
		if tup[0] < network_path_cost_thresh:
			highestActivityPaths_network.add(tuple(tup[1]))
		else:
			break
	#print "Got ", len(highestActivityPaths_network), " highest activity paths in network"
	return highestActivityPaths_network
