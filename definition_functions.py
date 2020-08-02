from collections import defaultdict

class Solver:
    def __init__(self, g):
        self.g = g
        self.earliest_feasible_arrival_times = defaultdict(list)
        self.opt_is = dict()
        self.parking = defaultdict(list)
        self.blacklist = defaultdict(list)
        self.recalculate = []

    @staticmethod
    def get_route_for_arc(arc: tuple, optimal_i: dict):
        """
        This function returns all arcs used in order to arrive at a given arc for a specified solution set
        :param arc: The arc for which preceeding arcs shall be determined
        :param optimal_i: The current solution found by the algorithm, i.e. for all f(i,j) the optimal
        preceeding node.
        :return: Set of arcs preceeding the arc specified in the functions arguments
        """
        check_route_for = arc
        route = list()
        i = check_route_for[0]
        j = check_route_for[1]
        try:
            while True:
                curr_arc = (i, j)
                i = optimal_i[curr_arc]
                j = curr_arc[0]
                route.append((i, j))
                if i == 1:
                    break
            return [i for i in reversed(route)]
        # Direct links from source nodes have no optimal predecessor, hence they don´t appear in the solution
        # set. Therefore, when keys are not found in the dictionary, and empty list will be returned
        except KeyError:
            return []

    def calc_min_earliest_arrival_time(self, j, k):
        if j == 1:
            # we have initialized all arcs from the source already
            return

        pot_earliest_feasible_arrival_times = []
        inter_parking = []
        arcs_to_j = [ij[0] for ij in self.g.edges if ij[1] == j]
        print("The following nodes move into {}: {}".format(j, arcs_to_j))
        for i in arcs_to_j:
            if (i, j) in self.blacklist[j, k]:
                print("Arc ({},{}) is blacklisted for route containing current arc ({},{})".format(i, j, j, k))
                pot_earliest_feasible_arrival_times.append(float('inf'))
                inter_parking.append(float('inf'))
            else:
                print("f({}, {}) is: {}".format(i, j, self.earliest_feasible_arrival_times[i, j][-1]))
                p_i = self.check_for_feasibility(i, j)
                t_ij = self.g.distance[i, j]
                inter_parking.append(p_i)
                if p_i is not False and type(p_i) == int:
                    print("f({},{}): {}; p_{}: {}; t_{}{}: {}".format(i, j,
                                                                      self.earliest_feasible_arrival_times[i, j][-1],
                                                                      i, p_i, i, j, t_ij))
                    pot_earliest_feasible_arrival_times.append(self.earliest_feasible_arrival_times[i, j][-1] + p_i + t_ij)
                # if the backtracking founds that an arc doen't yield a feasible solution, it returns False
                else:
                    pot_earliest_feasible_arrival_times.append(float('inf'))
            print("pot_earliest_feasible_arrival_times: ", pot_earliest_feasible_arrival_times)
        min_arrival_time_index = pot_earliest_feasible_arrival_times.index(min(pot_earliest_feasible_arrival_times))
        self.earliest_feasible_arrival_times[j, k].append(pot_earliest_feasible_arrival_times[min_arrival_time_index])
        self.parking[j, k].append(inter_parking[min_arrival_time_index])
        self.opt_is[j, k] = arcs_to_j[min_arrival_time_index]
        print("optimal i for ({},{}): {}".format(j, k, self.opt_is[j, k]))

    def do_recursion(self, i, j, earliest_feasible_at, time_gap=None):
        """
        Recursion for identifying a parking time p_i when in succeeding links f(j,k) a situation occurs,
        where condition (equation) 3 from the paper is met, i.e. a node is visited before the parking
        is allowed as well as before the transition to node k is possible. In this case, parking time
        in preceeding nodes has to be increased. This works in a backtracking manner, i.e. if parking
        cannot increased in preceeding node i because parking is not allowed there yet but transition
        to the next node j is, then the preceeding node for i is checked. If at no preceeding node
        parking is possible, then the solution set will be omitted (set to infinity)
        :param i:
        :param j:
        :param earliest_feasible_at:
        :param opt_is:
        :param earliest_feasible_arrival_times:
        :return:
        """
        if earliest_feasible_at == float('inf'):
            return float('inf')
        # specify time window for parking
        print("so lets do the backtracking")
        alpha_i = self.g.f_park_t[i][0]

        # specify time window for traveling the arc
        gamma_ij = self.g.f_dep_t[(i, j)][0]

        previous_arcs = self.get_route_for_arc((i, j), self.opt_is)
        print("The arcs preceeding arc ({},{}) are: {}".format(i, j, previous_arcs))
        all_blacklisted = all([x in self.blacklist[i, j] for x in previous_arcs])
        if len(previous_arcs) == 0 or all_blacklisted:
            return float('inf')
        else:
            # this time is missing on node j in order to be able to park or directly move to k.
            # The time that is missing must be greater (or equal to zero), hence this condition is applied here.
            # Generally, the least time needed to make a solution feasible is seeked
            if not time_gap:
                time_missing = [alpha_i - earliest_feasible_at, gamma_ij - earliest_feasible_at]
                time_gap = min([x for x in time_missing if x >= 0])
                if time_gap == alpha_i - earliest_feasible_at:
                    print("{} time periods are missing to be able to park at the node".format(time_gap))
                else:
                    print("{}time periods are missing to be able to move along the route ahead".format(time_gap))
            curr_prev_arc = previous_arcs[-1]
            # for curr_prev_arc in reversed(previous_arcs):
            print(curr_prev_arc)
            f_i1_i2 = self.earliest_feasible_arrival_times[curr_prev_arc][-1]
            new_p_i = self.add_parking_to_predecessor(*curr_prev_arc, add_park_time=time_gap, successors=(i, j))
            # check_for_feasibility returns infinity if parking cannot be extended by the amount of time
            # specified in time_gap at node i1. If that is not the case, the solution is feasible and the
            # algorithm may proceed with the new parking time at the node i1.
            if not new_p_i == float('inf'):
                new_earliest_feasible_at = f_i1_i2 + new_p_i + self.g.distance[curr_prev_arc]
                print("new f({}): ".format((i, j)), new_earliest_feasible_at, "new p_{}: ".format(i), new_p_i)
                self.earliest_feasible_arrival_times[i, j].append(new_earliest_feasible_at)
                self.parking[i, j].append(new_p_i)
                return self.check_for_feasibility(i, j)
            # else, the backtracking needs to proceed further to see if the time at pr
            else:
                # put the arc for this specific route on the blacklist so it wont be used anymore
                self.blacklist[i, j].append(curr_prev_arc)
                print("Infeasible solution found. Recalculate the best path for node {} proceeding to {}".format(i, j))
                self.calc_min_earliest_arrival_time(i, j)
                return self.check_for_feasibility(i, j)

    def get_time_windows(self, i, j):
        # specify time window for parking
        alpha_i = self.g.f_park_t[i][0]
        beta_i = self.g.f_park_t[i][1]

        # specify time window for traveling the arc
        gamma_ij = self.g.f_dep_t[(i, j)][0]
        delta_ij = self.g.f_dep_t[(i, j)][1]

        return alpha_i, beta_i, gamma_ij, delta_ij

    def add_parking_to_predecessor(self, i, j, add_park_time, successors):
        earliest_feasible_at = self.earliest_feasible_arrival_times[i, j][-1]

        alpha_i, beta_i, gamma_ij, delta_ij = self.get_time_windows(i, j)

        max_p_i = min(beta_i - earliest_feasible_at, delta_ij - earliest_feasible_at)
        if add_park_time:
            print("additional parking time at node {} is needed: ".format(i), add_park_time)
            # if we run this function in backtracking mode, where at preceeding nodes the parking time has to be
            # extended, the needed additional time is added to the parking time found in the previous solution
            # parking time at the corresponding node.
            new_p_i = self.parking[successors][-1] + add_park_time
            print("This sums up to: ", new_p_i)
            if new_p_i <= max_p_i:
                print('which is still a feasible solution. Proceed with p_{} = {}'.format(i, new_p_i))
                return new_p_i
            else:
                print("which is not a feasible solution. ")
                # if the parking time with the additional time exceeds the time window where parking is allowed, we
                # arrived again at an infeasible solution, hence the backtracking will proceed to the next predecessor,
                # until a solution is found or no more predecessors exist (which is the case for the source node).
                # The parking time at the next predecessor must match the parking time at the node found in the
                # previous solution plus the additional parking time.
                print("Another round of recusion will be tried. The parking at the next node needs to be increased \n "
                      "by add_park_time: {} + current paarking: {}".format(add_park_time, self.parking[successors][-1]))
                return self.do_recursion(i, j, earliest_feasible_at, new_p_i)

    def check_for_feasibility(self, i, j):
        earliest_feasible_at = self.earliest_feasible_arrival_times[i, j][-1]
        print("Check feasibility for usage of arc ({}) for earliest feasible time {}".format((i, j),
                                                                                             earliest_feasible_at))
        if earliest_feasible_at == float('inf'):
            return float('inf')

        # get time window for parking and for traveling the arc
        alpha_i, beta_i, gamma_ij, delta_ij = self.get_time_windows(i, j)

        # check first equation:
        # in the first equation of the paper, parking is considered to be possible. Hence, inside the following
        # for loop, the feasible parking times are determined. If the resulting set is empty, the algorithm proceeds
        # to the next condition. To determine if a parking time is feasible, the conditions in the first equation
        # of the paper are checked.
        max_p_i = min(beta_i - earliest_feasible_at, delta_ij - earliest_feasible_at)
        feasible_p_i = []
        for pot_p_i in range(max_p_i + 1):
            # here, eq. (1) is checked.
            if (alpha_i <= earliest_feasible_at <= beta_i) and (gamma_ij <= earliest_feasible_at + pot_p_i <= delta_ij):
                feasible_p_i.append(pot_p_i)
        print("feasible parking times at {} when moving to {}: {}".format(i, j, feasible_p_i))
        if len(feasible_p_i) > 0:
            print("1st cond satisfied")
            # in here, use greedy methodology and choose the smallest feasible parking time. If this leeds
            # to an infeasible solution in later stages, the backtracking will try to increase the parking time.
            p_i = feasible_p_i[0]

        # check second equation
        elif (beta_i - earliest_feasible_at <= 0) and (gamma_ij <= earliest_feasible_at <= delta_ij):
            print("2nd cond satisfied")
            p_i = 0

        # check third equation
        # note: in comparison to the paper by Sancho, this condition has been changed, as the original
        # set of conditions did not cover all cases. Here, it is checked WHETHER
        # 1.) we arrive to early at a node, so that the route ahead is blocked and parking is not possible yet OR
        # 2.) parking is not possible, as beta is smaller than gamma, and we arrive to early to directly take the route ahead.
        # If this condition is satisfied, the backtracking is done to check whether longer parking at predecessor nodes
        # makes the current route feasible.
        elif (earliest_feasible_at < alpha_i and earliest_feasible_at < gamma_ij) or (
                earliest_feasible_at < gamma_ij and beta_i < gamma_ij):
            print("3rd condition satisfied")
            p_i = self.do_recursion(i, j, earliest_feasible_at)
            print("recursion is done, result is: ", p_i)

        # check fourth equation
        elif (gamma_ij < earliest_feasible_at < alpha_i <= delta_ij) or (
                gamma_ij < earliest_feasible_at < delta_ij <= alpha_i):
            print("4th cond satisfied")
            p_i = 0

        # check fifth equation
        elif delta_ij < earliest_feasible_at:
            print("5th cond satisfied")
            p_i = float('inf')

        # raise an error if a case satisfies no condition
        else:
            raise AssertionError("Some cases are not considered in feasibility check")

        return p_i
