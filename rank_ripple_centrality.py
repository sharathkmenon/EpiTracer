import networkx as nx
import operator
import numpy as np
from math import log, ceil
from collections import Counter
import sys

def invert_dict(somedict):
	inverted_dict = {}
	for k, v in somedict.iteritems():
		inverted_dict.setdefault(v, []).append(k)
	return inverted_dict
	
# Rank a dictionary based on value
# Values are sorted in descending order
# Nodes with same value are given same rank
# Starting rank is given
def rank_dict_rev_val(somedict, rank):
	sorted_values = sorted(somedict.items(), key = operator.itemgetter(1), reverse = True)
	inv_values = invert_dict(somedict)
	# key -> node
	# value -> rank in terms of value
	ranks = {}
	ranked_values = set() # values for which a rank has been assigned
	for val in sorted_values:
		if val[1] not in ranked_values: # if this value has not been assigned a rank
			ranked_values.add(val[1])
			for node in inv_values[val[1]]: # these are the nodes with the same value
				ranks[node] = rank
			rank += 1
	return ranks



######################### Main #########################	
if len(sys.argv) != 3:
	print "argv[1] = CSHAN"
	print "argv[2] = output file"
	sys.exit(1)

print "Reading graph"
fh = open(sys.argv[1], 'r')
G = nx.read_weighted_edgelist(fh, nodetype = str, create_using = nx.DiGraph())
fh.close()
num_nodes = len(G.nodes())

print "Computing closeness centrality"
close_centr = nx.closeness_centrality(G, distance = True)
# key -> node
# value -> rank in terms of closeness centrality
close_centr_ranks = rank_dict_rev_val(close_centr, 1)

# No. of reachable nodes
print "Computing reachability"
shortest_path_costs = nx.all_pairs_dijkstra_path_length(G)
print "Done computing shortest paths"
# key -> node
# value -> no. of nodes reachable from the key node
reachable = {}
for n in G.nodes():
	reachable[n] = len(shortest_path_costs[n].values())
reachable_ranks = rank_dict_rev_val(reachable, 1)

# close_reach
# close_reach score = closeness centrality * fraction of reachable nodes
print "Computing close_reach score"
close_reach = {}
for node in G.nodes():
	close_reach[node] = close_centr[node] * (reachable[node]/float(num_nodes))
close_reach_ranks = rank_dict_rev_val(close_reach, 1)

with open(sys.argv[2], 'wb') as f:
	f.write( "node" + "\t" )
	f.write( "\t".join(["closeness_centr_rank", "closeness_centr_value"]) + "\t" )
	f.write( "\t".join(["reachability_rank", "reachability_value"]) + "\t" )
	f.write( "\t".join(["close_reach_rank", "close_reach_value"]) + "\t" )
	f.write( "\n" )
	for node in G.nodes():
		f.write( node + "\t" )
		f.write( "\t".join([str(close_centr_ranks[node]), str(close_centr[node])]) + "\t" )
		f.write( "\t".join([str(reachable_ranks[node]), str(reachable[node])]) + "\t" )
		f.write( "\t".join([str(close_reach_ranks[node]), str(close_reach[node])]) + "\t" )
		f.write( "\n" )