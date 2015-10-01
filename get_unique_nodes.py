import networkx as nx
import sys

if len(sys.argv) != 6:
	print "argv[1] = perturbed graph"
	print "argv[2] = control graph"
	print "argv[3] = nodes unique to perturbed (output file)"
	print "argv[4] = nodes unique to control (output file)"
	print "argv[5] = common nodes (output file)"
	sys.exit(1)

print "Reading perturbed graph"
fh = open(sys.argv[1], 'r')
perturbed = nx.read_weighted_edgelist(fh, nodetype = str, create_using = nx.DiGraph())
fh.close()

print "Reading control graph"
fh = open(sys.argv[2], 'r')
control = nx.read_weighted_edgelist(fh, nodetype = str, create_using = nx.DiGraph())
fh.close()

perturbed_nodes = set(perturbed.nodes())
control_nodes = set(control.nodes())
print "perturbed network has ", len(perturbed_nodes), " nodes"
print "control network has ", len(control_nodes), " nodes"

perturbed_only = perturbed_nodes - control_nodes
control_only = control_nodes - perturbed_nodes
common = perturbed_nodes.intersection(control_nodes)
print "No. of nodes unique to perturbed = ", len(perturbed_only)
print "No. of nodes unique to control = ", len(control_only)
print "No. of common nodes = ", len(common)

print "Writing to files"
with open(sys.argv[3], "wb") as f:
	for node in perturbed_only:
		f.write( node + "\n" )
with open(sys.argv[4], "wb") as f:
	for node in control_only:
		f.write( node + "\n" )
with open(sys.argv[5], "wb") as f:
	for node in common:
		f.write( node + "\n" )