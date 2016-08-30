import sys
import networkx as nx
import highest_activity_paths as hap

def get_edges_in_paths(paths, G):
        edges_in_paths = set()
        for path in paths:
                for i in range(len(path) - 1):
                        edges_in_paths.add((path[i], path[i+1], G[path[i]][path[i+1]]['weight']))
        return list(edges_in_paths)



##########################################################################
def condition_specific_han(G_control, G_disease, percentile_threshold):
	highestActivityPaths_control = hap.highest_activity_paths(G_control, percentile_threshold)
	highestActivityPaths_disease = hap.highest_activity_paths(G_disease, percentile_threshold)

	control_specific_hap = highestActivityPaths_control - highestActivityPaths_disease
	#print "No. of paths unique to control = ", len(control_specific_hap)
	control_specific_hap_edges = get_edges_in_paths(control_specific_hap, G_control)
	control_specific_han = nx.DiGraph()
	control_specific_han.add_weighted_edges_from(control_specific_hap_edges)

	disease_specific_hap = highestActivityPaths_disease - highestActivityPaths_control
	#print "No. of paths unique to disease = ", len(disease_specific_hap)
	disease_specific_hap_edges = get_edges_in_paths(disease_specific_hap, G_disease)
	disease_specific_han = nx.DiGraph()
	disease_specific_han.add_weighted_edges_from(disease_specific_hap_edges)

	return control_specific_han, disease_specific_han
