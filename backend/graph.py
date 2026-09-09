import networkx as nx

def build_track_network():
    G = nx.Graph()
    G.add_edge("S1", "S2", weight=15)
    G.add_edge("S2", "S3", weight=20)
    return G
