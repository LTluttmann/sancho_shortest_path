from graph_class import Graph
from definition_functions import *
import time

from collections import defaultdict


def build_graph():
    """
    Define the network for the example in this function
    :return: graph containing the data of the specified example
    """
    # Nodes of the example
    g = Graph()
    parking_times = [[0, 12], [18, 30], [35, 45], [64, 75], [35, 50], [64, 75], [0, float('inf')], [0, float('inf')]]
    for i in range(1, 9):
        g.add_node(i, parking_times[i - 1])

    # Arcs of the example
    g.add_edge(1, 2, 10, [10, 15])
    g.add_edge(1, 3, 20, [10, 25])
    g.add_edge(1, 5, 25, [15, 25])
    g.add_edge(2, 4, 35, [28, 35])
    g.add_edge(2, 6, 35, [26, 34])
    g.add_edge(2, 7, 30, [32, 60])
    g.add_edge(3, 2, 15, [35, 50])
    g.add_edge(3, 4, 20, [43, 50])
    g.add_edge(4, 7, 30, [70, 99])
    g.add_edge(5, 2, 20, [30, 80])
    g.add_edge(5, 6, 25, [48, 55])
    g.add_edge(6, 7, 10, [72, 80])
    g.add_edge(7, 8, 0, [0, 0])

    return g


def new_main():
    g = build_graph()
    earliest_feasible_arrival_times = dict()
    sink = min(g.nodes)
    terminal = max(g.nodes)
    opt_is = dict()
    parking = defaultdict(list)
    arcs_from_sink = [jk[1] for jk in g.edges if jk[0] == sink]
    print("initialize the arcs from the sink")
    for k in arcs_from_sink:
        earliest_feasible_arrival_times[sink, k] = 0
    for k in g.nodes.difference({sink}):
        print("The iteration over k is currently at: ", k)
        arcs_to_k = [jk[0] for jk in g.edges if jk[1] == k]
        print("The following nodes move into {}: {}".format(k, arcs_to_k))
        for j in arcs_to_k:
            earliest_feasible_arrival_times, opt_is, parking = \
                calc_min_earliest_arrival_time(g, j, k, earliest_feasible_arrival_times, opt_is, parking)

    return earliest_feasible_arrival_times, opt_is, parking

def main():
    g = build_graph()
    earliest_feasible_arrival_times = dict()
    sink = min(g.nodes)
    terminal = max(g.nodes)
    opt_is = dict()
    parking = defaultdict(list)
    for k in range(sink, terminal + 2):
        print("The iteration over k is currently at: ", k)
        # initialize all arcs moving from the sink
        if k == 1:
            arcs_from_sink = [jk[1] for jk in g.edges if jk[0] == k]
            for l in arcs_from_sink:
                earliest_feasible_arrival_times[k, l] = 0
        else:
            arcs_to_k = [jk[0] for jk in g.edges if jk[1] == k]
            print("The following nodes move into {}: {}".format(k, arcs_to_k))
            for j in arcs_to_k:
                print("The iteration over j is currently at: ", j)
                if j == 1:
                    # we have initialized all arcs from the sink already
                    continue
                pot_earliest_feasible_arrival_times = []
                arcs_to_j = [ij[0] for ij in g.edges if ij[1] == j]
                print("The following nodes move into {}: {}".format(j, arcs_to_j))
                for i in arcs_to_j:
                    f_ij = earliest_feasible_arrival_times[i, j]
                    print("f({}, {}) is: {}".format(i, j, f_ij))
                    p_i = check_for_feasibility(g, i, j, f_ij, opt_is, earliest_feasible_arrival_times, parking)
                    f_ij = earliest_feasible_arrival_times[i, j]
                    print("p_{}:".format(i), p_i)
                    t_ij = g.distance[i, j]
                    parking[i, j] = p_i
                    print("current earliest_feasible_arrival_times: ", earliest_feasible_arrival_times)
                    print("current parking times: ", parking)
                    if p_i is not False and type(p_i) == int:
                        print("f_{}; p_{}; t_{}: ".format((i, j), i, (i, j)), f_ij, "; ", p_i, "; ", t_ij)
                        pot_earliest_feasible_arrival_times.append(f_ij + p_i + t_ij)
                    else:
                        pot_earliest_feasible_arrival_times.append(float('inf'))
                    print("pot_earliest_feasible_arrival_times", pot_earliest_feasible_arrival_times)
                earliest_feasible_arrival_times[j, k] = min(pot_earliest_feasible_arrival_times)
                print("best i", pot_earliest_feasible_arrival_times.index(min(pot_earliest_feasible_arrival_times)))
                opt_is[j, k] = arcs_to_j[
                    pot_earliest_feasible_arrival_times.index(min(pot_earliest_feasible_arrival_times))]
            # tour.append((j,k))
    return earliest_feasible_arrival_times, opt_is, parking


if __name__ == "__main__":
    start = time.time()
    #earliest_feasible_arrival_times, opt_is, parking = main()
    earliest_feasible_arrival_times, opt_is, parking = new_main()
    print("Finished. Runtime was: {}".format(time.time() - start))