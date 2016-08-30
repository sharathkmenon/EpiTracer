import networkx as nx

# Computes ripple centrality for every node in network G
# ripple centrality(n) = closeness centrality(n) * fraction of nodes reachable from n
# Input : G, a networkx DiGraph
# Output : ripple_centrality, a dictionary
#	   key -> node
#	   value -> ripple centrality of this node
def compute_ripple_centrality(G):
	closeness_centr = nx.closeness_centrality(G, distance = True)
	shortest_path_costs = nx.all_pairs_dijkstra_path_length(G)
	reachable = {} # key -> node, value -> no. of nodes reachable from that node
	for n in G.nodes():
		reachable[n] = len(shortest_path_costs[n].keys())

	num_nodes = float(len(G.nodes()))
	ripple_centrality = {}
	for node in G.nodes():
		ripple_centrality[node] = closeness_centr[node] * (reachable[node]/num_nodes)
	return ripple_centrality
