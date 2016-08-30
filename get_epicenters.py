import condition_specific_han as csh
import ripple_centrality as rc
import sys
import operator
import networkx as nx

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

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
        ranks = [] # list of tuples (node, rank)
        ranked_values = set() # values for which a rank has been assigned
        for val in sorted_values:
                if val[1] not in ranked_values: # if this value has not been assigned a rank
                        ranked_values.add(val[1])
                        for node in inv_values[val[1]]: # these are the nodes with the same value
                                ranks.append((node, rank))
                        rank += 1
        return ranks



############################################### Error checking of inputs ###############################################
num_args = len(sys.argv)
# Must have 4 or 5 arguments
if num_args < 4 or num_args > 5:
	print "Usage: python2.7", sys.argv[0], "control_network disease_network compute_cshan?(True/False) percentile_threshold(If True)"
	sys.exit(1)

# 3rd argument must be True or False
if sys.argv[3] != "True" and sys.argv[3] != "False":
	print "Need a \'True\' or \'False\' answer"
	sys.exit(1)

# If 3rd argument is True, 4th argument must be a number
if sys.argv[3] == "True":
	if not is_number(sys.argv[4]):
		print "Need a numeric percentile threshold"
		sys.exit(1)


################################################ Main program ##########################################################
# Read graph control
print "Reading graph control"
fh = open(sys.argv[1], 'r')
G_control = nx.read_weighted_edgelist(fh, nodetype = str, create_using = nx.DiGraph())
fh.close()

# Read graph disease
print "Reading graph disease"
fh = open(sys.argv[2], 'r')
G_disease = nx.read_weighted_edgelist(fh, nodetype = str, create_using = nx.DiGraph())
fh.close()

# Compute condition-specific highest activity networks if necessary
compute_cshan = sys.argv[3] == "True"
if compute_cshan:
	print "Computing condition-specific highest activity networks"
	percentile_threshold = float(sys.argv[4])
	G_control, G_disease = csh.condition_specific_han(G_control, G_disease, percentile_threshold)

	# Write condition-specific highest activity networks into files
	nx.write_weighted_edgelist(G_control, "control_cshan.txt", delimiter = "\t")
	nx.write_weighted_edgelist(G_disease, "disease_cshan.txt", delimiter = "\t")

# Compute ripple centrality for disease-specific highest activity network
print "Computing ripple centrality"
ripple_centrality_disease = rc.compute_ripple_centrality(G_disease)
ripple_centrality_disease_ranks = rank_dict_rev_val(ripple_centrality_disease, 1)

# Split nodes into disease-specific and common
# Write output in two different files
# Assign ranks as per order in new files
print "Ranking and splitting nodes into disease-specific and common"
disease_specific_nodes = set(G_disease.nodes()) - set(G_control.nodes())
disease_specific_rank = 0
disease_specific_prev_rank = 0
common_rank = 0
common_prev_rank = 0
with open("disease_specific_ranks.txt", 'w') as f_disease:
	with open("common_ranks.txt", 'w') as f_common:
		f_disease.write( "Node" + "\t" + "Ripple_centrality_rank" + "\n" )
		f_common.write( "Node" + "\t" + "Ripple_centrality_rank" + "\n" )

		for tup in ripple_centrality_disease_ranks:
			if tup[0] in disease_specific_nodes:
				if tup[1] != disease_specific_prev_rank:
					disease_specific_rank += 1
				f_disease.write( tup[0] + "\t" + str(disease_specific_rank) + "\n" )
				disease_specific_prev_rank = tup[1]
			else:
				if tup[1] != common_prev_rank:
                                        common_rank += 1
                                f_common.write( tup[0] + "\t" + str(common_rank) + "\n" )
                                common_prev_rank = tup[1]
