# This program extracts the influence zone around a given node
# If more than one input node is given, a separate influence zone is extracted for each
# All nodes upstream_limit hops upstream, and downstream_limit hops downstream are
# considered to be part of the influence zone

# In each influence zone, we highlight the nodes which are up/down-regulated
# For these nodes we give the path between the node of interest and the up/down-regulated node
# The fold-change cutoff for considering a node as up/down-regulated is a user input


import networkx as nx
import csv
import sys
import numpy as np

def get_downstream_nodes(G, noi, down_limit):
	down_tree = nx.single_source_dijkstra_path(G, noi, weight = 'None', cutoff = down_limit)
	return down_tree

def get_upstream_nodes(G, noi, up_limit):
	Grev = G.reverse(copy = True) # reverse all edge directions
	up_tree = nx.single_source_dijkstra_path(Grev, noi, weight = 'None', cutoff = up_limit)
	return up_tree

def examine_nodes(nodes, fc, fc_limit):
	deg = {}
	for node in nodes.keys():
		node_fc = float(fc[node])
		if node_fc > fc_limit or (1/node_fc) > fc_limit:
			print node, " has fc ", fc[node]
			deg[node] = node_fc
	return deg

def which_network(noi, disease_specific_nodes, control_specific_nodes, common_nodes):
        if noi in disease_specific_nodes:
                return "unique to perturbed CSHAN"
        elif noi in control_specific_nodes:
                return "unique to control CSHAN"
        elif noi in common_nodes:
                return "common to both CSHANs"
        else:
                return "not in any CSHAN"

# direction is "upstream" or "donwstream"
# returns number of nodes with significant fold change
def examine_nodes_print_table(noi, nodes, direction, fc, disease_specific_nodes, control_specific_nodes, common_nodes, fc_limit, outfile):
	num_sign_fc = 0
	with open(outfile, 'a') as f:
		for node, path in nodes.items():
        	        node_fc = float(fc[node])
			num_hops = len(path) - 1
                	if node_fc > fc_limit or (1/node_fc) > fc_limit:
				num_sign_fc += 1
				f.write( "\t".join([node, direction, str(num_hops), fc[node], which_network(node, disease_specific_nodes, control_specific_nodes, common_nodes)]) + "\t" )
				for index in range(1, num_hops):
					node_fc = float(fc[path[index]])
					significant_fc = node_fc > fc_limit or (1/node_fc) > fc_limit
					f.write( "\t".join([path[index], fc[path[index]], str(significant_fc), which_network(path[index], disease_specific_nodes, control_specific_nodes, common_nodes)]) + "\t" )
				f.write( "\n" )
	return num_sign_fc

def print_influence_zone(G, node_wts, fc, noi, downstream, upstream):
	nodes = set(downstream).union(set(upstream))
	inf_zone = G.subgraph(nodes)
	nx.write_weighted_edgelist(inf_zone, noi+'_inf_zone.txt')
	with open(noi+'_inf_zone_nodes.txt', 'wb') as f:
		f.write( "\t".join(["node", "weight", "fold_change"]) + "\n" )
		for node in nodes:
			f.write( "\t".join([node, node_wts[node], fc[node]]) + "\n" )

################## Main #################
if len(sys.argv) != 10:
        print "argv[1] = network from which to extract influence zone"
	print "argv[2] = nodes around which to extract influence zone (file)"
	print "argv[3] = node weights (file)"
	print "argv[4] = fold change (file)"
	print "argv[5] = control-specific highest activity network"
	print "argv[6] = disease-specific highest activity network"
	print "argv[7] = upstream limit"
	print "argv[8] = downstream limit"
	print "argv[9] = fold change limit"
        sys.exit(1)

# Read input network
print "Reading network"
fh = open(sys.argv[1], 'r')
G = nx.read_weighted_edgelist(fh, nodetype = str, create_using = nx.DiGraph())
fh.close()

# noi stands for node of interest
# We will be extracting the influence zone for each of these nodes
print "Reading nodes of interest"
with open(sys.argv[2]) as f:
        noi_list = f.read().splitlines()

# Read node weight information
print "Reading node weights"
reader = csv.reader(open(sys.argv[3], 'rb'), delimiter = '\t')
node_wts = dict(reader) # node_wts has the form { 'gene' : 'weight' }

# Reading fold change information
print "Reading fold change"
reader = csv.reader(open(sys.argv[4], 'rb'), delimiter = '\t')
fc = dict(reader) # fc has the form {'gene' : 'fc'}

# Read control-specific highest activity network
print "Reading control-specific highest activity network"
fh = open(sys.argv[5], 'r')
G_control_specific_han = nx.read_weighted_edgelist(fh, nodetype = str, create_using = nx.DiGraph())
fh.close()

# Read disease-specific highest activity network
print "Reading disease-specific highest activity network"
fh = open(sys.argv[6], 'r')
G_disease_specific_han = nx.read_weighted_edgelist(fh, nodetype = str, create_using = nx.DiGraph())
fh.close()

up_limit = int(sys.argv[7])
down_limit = int(sys.argv[8])
fc_limit = float(sys.argv[9])

# Get nodes unique to disease, control
# Also get common nodes
common_nodes = set(G_control_specific_han.nodes()).intersection(set(G_disease_specific_han.nodes()))
disease_specific_nodes = set(G_disease_specific_han.nodes()) - common_nodes
control_specific_nodes = set(G_control_specific_han.nodes()) - common_nodes

# creating the output file. After this we will append to it
outfile = "influence_zone_table.txt"
summaryFile = "summary.txt"
with open(outfile, 'w') as f:
	f.write( "\t".join(["node", "direction", "num_hops", "fold_change", "which_network"]) + "\t" )
	for index in range(1, max(up_limit, down_limit)):
		f.write( "\t".join(["intermediate_node_"+str(index), "fold_change", "significant_fc?", "which_network"]) + "\t" )
	f.write( "\n" )
with open(summaryFile, 'w') as f:
	f.write( "Summary output" + "\n\n" )

for noi in noi_list:
	print "working with ", noi

	with open(outfile, 'a') as f:
		f.write( "\t".join([noi, "input_node", "0", fc[noi], which_network(noi, disease_specific_nodes, control_specific_nodes, common_nodes)]) + "\n" )
	downstream = get_downstream_nodes(G, noi, down_limit)
	num_sign_fc = examine_nodes_print_table(noi, downstream, "down_"+noi, fc, disease_specific_nodes, control_specific_nodes, common_nodes, fc_limit, outfile)
	with open(summaryFile, 'a') as f:
		f.write( "nodes <= " + str(down_limit) + " hops downstream from " + noi + "\n" )
		f.write( str(num_sign_fc) + " out of " + str(len(downstream.keys())) + " nodes have significant fold change" + "\n" )

	upstream = get_upstream_nodes(G, noi, up_limit)
	num_sign_fc = examine_nodes_print_table(noi, upstream, "up_"+noi, fc, disease_specific_nodes, control_specific_nodes, common_nodes, fc_limit, outfile)
	with open(summaryFile, 'a') as f:
		f.write( "nodes <= " + str(up_limit) + " hops upstream from " + noi + "\n" )
		f.write( str(num_sign_fc) + " out of " + str(len(upstream.keys())) + " nodes have significant fold change" + "\n" )
		f.write( "\n" )

	print_influence_zone(G, node_wts, fc, noi, downstream.keys(), upstream.keys())
