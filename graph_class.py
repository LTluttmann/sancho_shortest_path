from collections import defaultdict


class Graph:
    def __init__(self):
        self.nodes = set()
        self.edges = list()
        self.edges_out = defaultdict(list)
        self.edges_in = defaultdict(list)
        self.distance = dict()
        self.f_dep_t = dict()
        self.f_park_t = dict()

    def add_node(self, value, feasible_parking_time):
        self.nodes.add(value)
        self.f_park_t[value] = feasible_parking_time

    def add_edge(self, from_node, to_node, distance, feasible_dep_time):
        self.edges.append((from_node, to_node))
        self.edges_out[from_node].append(to_node)
        self.edges_in[to_node].append(from_node)
        self.distance[(from_node, to_node)] = distance
        self.f_dep_t[(from_node, to_node)] = feasible_dep_time
