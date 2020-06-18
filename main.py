from graph_class import Graph
from definition_functions import *
import time
from definition_functions import Solver

from collections import defaultdict


def build_graph():
    """
    Define the network for the example in this function. Note that an additional "artifical"
    node has to be specified at the very end of the network, where no restrictions in terms of
    parking exist.
    :return: graph containing the data of the specified example
    """
    # Nodes of the example
    g = Graph()
    parking_times = [[0, float('inf')], [18, 30], [35, 45], [66, 75], [35, 50], [64, 75], [0, float('inf')], [0, float('inf')]]
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
    # edge from true terminal node to artifical node
    g.add_edge(7, 8, 0, [0, 0])

    return g


def main():
    g = build_graph()
    sol = Solver(g)
    earliest_feasible_arrival_times = dict()
    source = min(g.nodes)
    terminal = max(g.nodes)
    optimal_predecessors = dict()
    optimal_parking = defaultdict(list)
    arcs_from_source = [jk[1] for jk in g.edges if jk[0] == source]
    print("initialize the arcs from the source")
    for k in arcs_from_source:
        sol.earliest_feasible_arrival_times[source, k].append(0)
    for k in g.nodes.difference({source}):
        print("The iteration over k is currently at: ", k)
        arcs_to_k = [jk[0] for jk in g.edges if jk[1] == k]
        print("The following nodes move into {}: {}".format(k, arcs_to_k))
        for j in arcs_to_k:
            #earliest_feasible_arrival_times, optimal_predecessors, optimal_parking = \
            #    calc_min_earliest_arrival_time(g, j, k, earliest_feasible_arrival_times, optimal_predecessors, optimal_parking)
            sol.calc_min_earliest_arrival_time(j, k)
    # return earliest_feasible_arrival_times, optimal_predecessors, optimal_parking
    return sol

if __name__ == "__main__":
    start = time.time()
    #earliest_feasible_arrival_times, opt_is, parking = main()
    solution = main()
    print("Finished. Runtime was: {} \n".format(time.time() - start))
    print("""The result looks as follows: \n
          The earliest feasible arrival times are: {} \n
          The optimal predecessor nodes per node are: {} \n
          And the optimal parking durations at node i for an
          arc (j,k) are as follows: {}""".format(solution.earliest_feasible_arrival_times,
                                                 solution.opt_is, solution.parking))