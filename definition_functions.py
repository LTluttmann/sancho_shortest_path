
class Solver:
    def __init__(self, g):
        self.g = g
        self.earliest_feasible_arrival_times = dict()
        self.opt_is = dict()
        self.parking = dict()

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
        # Direct links from sink nodes have no optimal predecessor, hence they don´t appear in the solution
        # set. Therefore, when keys are not found in the dictionary, and empty list will be returned
        except KeyError:
            return []

    def calc_min_earliest_arrival_time(self, j, k):
        # earliest_feasible_arrival_times = earliest_feasible_arrival_times.copy()
        if j == 1:
            # we have initialized all arcs from the sink already
            return

        pot_earliest_feasible_arrival_times = []
        inter_parking = []
        arcs_to_j = [ij[0] for ij in self.g.edges if ij[1] == j]
        print("The following nodes move into {}: {}".format(j, arcs_to_j))
        for i in arcs_to_j:
            f_ij = self.earliest_feasible_arrival_times[i, j]
            print("f({}, {}) is: {}".format(i, j, f_ij))
            if f_ij == float('inf'):
                pot_earliest_feasible_arrival_times.append(float('inf'))
            else:
                p_i = self.check_for_feasibility(i, j, f_ij)
                t_ij = self.g.distance[i, j]
                inter_parking.append(p_i)
                if p_i is not False and type(p_i) == int:
                    print("f({},{}): {}; p_{}: {}; t_{}{}: {}".format(i, j, f_ij, i, p_i, i, j, t_ij))
                    pot_earliest_feasible_arrival_times.append(self.earliest_feasible_arrival_times[i, j] + p_i + t_ij)
                # if the backtracking founds that an arc doen't yield a feasible solution, it returns False
                else:
                    pot_earliest_feasible_arrival_times.append(float('inf'))
            print("pot_earliest_feasible_arrival_times: ", pot_earliest_feasible_arrival_times)
        min_arrival_time_index = pot_earliest_feasible_arrival_times.index(min(pot_earliest_feasible_arrival_times))
        self.earliest_feasible_arrival_times[j, k] = pot_earliest_feasible_arrival_times[min_arrival_time_index]
        self.parking[j, k] = inter_parking[min_arrival_time_index]
        self.opt_is[j, k] = arcs_to_j[min_arrival_time_index]
        print("optimal i for ({},{}): {}".format(j, k, self.opt_is[j, k]))

    def do_recursion(self, i, j, earliest_feasible_at):
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
        # specify time window for parking
        print("so lets do the backtracking")
        alpha_i = self.g.f_park_t[i][0]

        # specify time window for traveling the arc
        gamma_ij = self.g.f_dep_t[(i, j)][0]

        previous_arcs = self.get_route_for_arc((i, j), self.opt_is)
        print("The arcs preceeding arc ({},{}) are: {}".format(i, j, previous_arcs))
        if len(previous_arcs) == 0:
            return float('inf')
        else:
            # this time is missing on node j in order to be able to park or directly move to k.
            # The time that is missing must be greater (or equal to zero), hence this condition is applied here.
            # Generally, the least time needed to make a solution feasible is seeked
            time_missing = [alpha_i - earliest_feasible_at, gamma_ij - earliest_feasible_at]
            time_gap = min([x for x in time_missing if x >= 0])
            curr_prev_arc = previous_arcs[-1]
            # for curr_prev_arc in reversed(previous_arcs):
            print(curr_prev_arc)
            f_i1_i2 = self.earliest_feasible_arrival_times[curr_prev_arc]
            new_p_i = self.check_for_feasibility(*curr_prev_arc, f_i1_i2, add_park_time=time_gap)
            # check_for_feasibility returns infinity if parking cannot be extended at node i1
            if not new_p_i == float('inf'):
                new_earliest_feasible_at = f_i1_i2 + new_p_i + self.g.distance[curr_prev_arc]
                print("new f({}): ".format((i, j)), new_earliest_feasible_at, "new p_{}: ".format(i), new_p_i)
                self.earliest_feasible_arrival_times[i, j] = new_earliest_feasible_at
                self.parking[i, j] = new_p_i
                return self.check_for_feasibility(i, j, new_earliest_feasible_at)
            elif new_p_i == float('inf') and curr_prev_arc == previous_arcs[0]:
                var_curr_arc = self.earliest_feasible_arrival_times[curr_prev_arc]
                self.earliest_feasible_arrival_times[curr_prev_arc] = float('inf')
                print("Infeasible solution found. Recalculate the best path for node {} proceeding to {}".format(i, j))
                self.calc_min_earliest_arrival_time(i, j)
                self.earliest_feasible_arrival_times[curr_prev_arc] = var_curr_arc
                latest_arc = self.get_route_for_arc((i, j), self.opt_is)
                if len(latest_arc) == 0:
                    return False
                else:
                    return self.parking[i, j]
            else:
                pass

    def get_time_windows(self, i, j):
        # specify time window for parking
        alpha_i = self.g.f_park_t[i][0]
        beta_i = self.g.f_park_t[i][1]

        # specify time window for traveling the arc
        gamma_ij = self.g.f_dep_t[(i, j)][0]
        delta_ij = self.g.f_dep_t[(i, j)][1]

        return alpha_i, beta_i, gamma_ij, delta_ij

    def check_for_feasibility(self, i, j, earliest_feasible_at, add_park_time=None):
        print("Check feasibility for usage of arc ({}) for earliest feasible time {}".format((i, j),
                                                                                             earliest_feasible_at))
        if earliest_feasible_at == float('inf'):
            return False

        if add_park_time:
            pass
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
            if (alpha_i <= earliest_feasible_at <= beta_i) and (gamma_ij <= earliest_feasible_at + pot_p_i <= delta_ij):
                feasible_p_i.append(pot_p_i)
        print("feasible parking times at {} when moving to {}: {}".format(i, j, feasible_p_i))
        if len(feasible_p_i) > 0:
            print("1st cond satisfied")
            # in here, use greedy methodology and choose the smallest feasible parking time. If this leeds
            # to an infeasible solution, the backtracking will try to increase the parking time.
            p_i = feasible_p_i[0]
            if add_park_time:
                print("additional parking time at node {} is needed: ".format(i), add_park_time)
                # if we run this function in backtracking mode, where at preceeding nodes the parking
                # time has to be extended, the needed additional time is added to the minimum possible
                # parking time at the corresponding node.
                new_p_i = p_i + add_park_time
                print("This sums up to: ", new_p_i)
                if new_p_i <= max_p_i:
                    print('which is still a feasible solution. Proceed with p_{} = {}'.format(i, new_p_i))
                    p_i = new_p_i
                else:
                    print("which is not a feasible solution. ")
                    # earliest_feasible_arrival_times[i, j] = float('inf')
                    p_i = self.do_recursion(i, j, earliest_feasible_at)

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
        elif (
                earliest_feasible_at < alpha_i and earliest_feasible_at < gamma_ij
        ) or (
                earliest_feasible_at < gamma_ij and beta_i < gamma_ij
        ):
            print("3rd condition satisfied")
            p_i = self.do_recursion(i, j, earliest_feasible_at)
            print("recursion is done, result is: ", p_i)

        # check fourth equation
        elif (
                gamma_ij < earliest_feasible_at < alpha_i <= delta_ij
        ) or (
                gamma_ij < earliest_feasible_at < delta_ij <= alpha_i
        ):
            print("4th cond satisfied")
            p_i = 0

        # check fifth equation
        elif delta_ij < earliest_feasible_at:
            print("5th cond satisfied")
            p_i = float('inf')

        # raise an error if a case satisfies no condition
        else:
            print(Warning("Some cases are not considered in feasibility check"))
            raise AssertionError()

        return p_i




















#
#
#
#
#
# def get_route_for_arc(arc: tuple, optimal_i: dict):
#     """
#     This function returns all arcs used in order to arrive at a given arc for a specified solution set
#     :param arc: The arc for which preceeding arcs shall be determined
#     :param optimal_i: The current solution found by the algorithm, i.e. for all f(i,j) the optimal
#     preceeding node.
#     :return: Set of arcs preceeding the arc specified in the functions arguments
#     """
#     check_route_for = arc
#     route = list()
#     i = check_route_for[0]
#     j = check_route_for[1]
#     try:
#         while True:
#             curr_arc = (i, j)
#             i = optimal_i[curr_arc]
#             j = curr_arc[0]
#             route.append((i, j))
#             if i == 1:
#                 break
#         return [i for i in reversed(route)]
#     # Direct links from sink nodes have no optimal predecessor, hence they don´t appear in the solution
#     # set. Therefore, when keys are not found in the dictionary, and empty list will be returned
#     except KeyError:
#         return []
#
#
# def calc_min_earliest_arrival_time(g, j, k, earliest_feasible_arrival_times,
#                                    opt_is, parking):
#     #earliest_feasible_arrival_times = earliest_feasible_arrival_times.copy()
#     if j == 1:
#         # we have initialized all arcs from the sink already
#         return earliest_feasible_arrival_times, opt_is, parking
#
#     pot_earliest_feasible_arrival_times = []
#     arcs_to_j = [ij[0] for ij in g.edges if ij[1] == j]
#     print("The following nodes move into {}: {}".format(j, arcs_to_j))
#     inter_parking = []
#     for i in arcs_to_j:
#         f_ij = earliest_feasible_arrival_times[i, j]
#         print("f({}, {}) is: {}".format(i, j, f_ij))
#         if f_ij == float('inf'):
#             pot_earliest_feasible_arrival_times.append(float('inf'))
#         else:
#             p_i = check_for_feasibility(g, i, j, f_ij, opt_is, earliest_feasible_arrival_times, parking)
#             f_ij = earliest_feasible_arrival_times[i, j]
#             t_ij = g.distance[i, j]
#             inter_parking.append(p_i)
#             if p_i is not False and type(p_i) == int:
#                 print("f({},{}): {}; p_{}: {}; t_{}{}: {}".format(i, j, f_ij, i, p_i, i, j, t_ij))
#                 pot_earliest_feasible_arrival_times.append(f_ij + p_i + t_ij)
#             # if the backtracking founds that an arc doen't yield a feasible solution, it returns False
#             else:
#                 pot_earliest_feasible_arrival_times.append(float('inf'))
#         print("pot_earliest_feasible_arrival_times: ", pot_earliest_feasible_arrival_times)
#     min_arrival_time_index = pot_earliest_feasible_arrival_times.index(min(pot_earliest_feasible_arrival_times))
#     earliest_feasible_arrival_times[j, k] = pot_earliest_feasible_arrival_times[min_arrival_time_index]
#     parking[j, k] = inter_parking[min_arrival_time_index]
#     opt_is[j, k] = arcs_to_j[min_arrival_time_index]
#     print("optimal i for ({},{}): {}".format(j, k, opt_is[j, k]))
#
#     return earliest_feasible_arrival_times, opt_is, parking
#
#
# def do_recursion(g, i, j, earliest_feasible_at, opt_is, earliest_feasible_arrival_times, parking):
#     """
#     Recursion for identifying a parking time p_i when in succeeding links f(j,k) a situation occurs,
#     where condition (equation) 3 from the paper is met, i.e. a node is visited before the parking
#     is allowed as well as before the transition to node k is possible. In this case, parking time
#     in preceeding nodes has to be increased. This works in a backtracking manner, i.e. if parking
#     cannot increased in preceeding node i because parking is not allowed there yet but transition
#     to the next node j is, then the preceeding node for i is checked. If at no preceeding node
#     parking is possible, then the solution set will be omitted (set to infinity)
#     :param i:
#     :param j:
#     :param earliest_feasible_at:
#     :param opt_is:
#     :param earliest_feasible_arrival_times:
#     :return:
#     """
#     # specify time window for parking
#     print("so lets do the backtracking")
#     alpha_i = g.f_park_t[i][0]
#     beta_i = g.f_park_t[i][1]
#
#     # specify time window for traveling the arc
#     gamma_ij = g.f_dep_t[(i, j)][0]
#     delta_ij = g.f_dep_t[(i, j)][1]
#
#     previous_arcs = get_route_for_arc((i, j), opt_is)
#     print("The arcs preceeding arc ({},{}) are: {}".format(i, j, previous_arcs))
#     if len(previous_arcs) == 0:
#         return float('inf')
#     else:
#         # this time is missing on node j in order to be able to park or directly move to k.
#         # The time that is missing must be greater (or equal to zero), hence this condition is applied here.
#         # Generally, the least time needed to make a solution feasible is seeked
#         time_missing = [alpha_i - earliest_feasible_at, gamma_ij - earliest_feasible_at]
#         time_gap = min([x for x in time_missing if x >= 0])
#         print("time_gap", time_gap)
#         # it is tried to extend parking at a previous node. Here, the last element is accessed, however the
#         # recursion moves the route backwards by itself, so we also check for all other nodes in the system
#         # if parking cannot be extended at this particular node.
#         # curr_prev_arc = previous_arcs[-1]
#         # print(curr_prev_arc)
#         # f_i1_i2 = earliest_feasible_arrival_times[curr_prev_arc]
#         # new_p_i = check_for_feasibility(g, *curr_prev_arc, f_i1_i2, opt_is, earliest_feasible_arrival_times,
#         #                                 parking, add_park_time=time_gap)
#         # # check_for_feasibility returns infinity if parking cannot be extended at node i1
#         # if not new_p_i == float('inf'):
#         #     new_earliest_feasible_at = f_i1_i2 + new_p_i + g.distance[curr_prev_arc]
#         #     print("new f({}): ".format((i, j)), new_earliest_feasible_at, "new p_{}: ".format(i), new_p_i)
#         #     earliest_feasible_arrival_times[i, j] = new_earliest_feasible_at
#         #     parking[i, j] = new_p_i
#         # else:
#         #     #
#         #     new_earliest_feasible_at = earliest_feasible_at
#         # # here, the recursion happens by calling again # TOOODOO: check if i, j decrease in each stage.
#         # return check_for_feasibility(g, i, j, new_earliest_feasible_at, opt_is,
#         #                              earliest_feasible_arrival_times, parking)
#         for curr_prev_arc in reversed(previous_arcs):
#             print(curr_prev_arc)
#             f_i1_i2 = earliest_feasible_arrival_times[curr_prev_arc]
#             new_p_i = check_for_feasibility(g, *curr_prev_arc, f_i1_i2, opt_is, earliest_feasible_arrival_times,
#                                             parking, add_park_time=time_gap)
#             # check_for_feasibility returns infinity if parking cannot be extended at node i1
#             if not new_p_i == float('inf'):
#                 new_earliest_feasible_at = f_i1_i2 + new_p_i + g.distance[curr_prev_arc]
#                 print("new f({}): ".format((i, j)), new_earliest_feasible_at, "new p_{}: ".format(i), new_p_i)
#                 earliest_feasible_arrival_times[i, j] = new_earliest_feasible_at
#                 parking[i, j] = new_p_i
#                 return check_for_feasibility(g, i, j, new_earliest_feasible_at, opt_is,
#                                              earliest_feasible_arrival_times, parking)
#             elif new_p_i == float('inf') and curr_prev_arc == previous_arcs[0]:
#                 var_curr_arc = earliest_feasible_arrival_times[curr_prev_arc]
#                 earliest_feasible_arrival_times[curr_prev_arc] = float('inf')
#                 print("Infeasible solution found. Recalculate the best path for node {} proceeding to {}".format(i, j))
#                 earliest_feasible_arrival_times, opt_is, parking = \
#                     calc_min_earliest_arrival_time(g, i, j, earliest_feasible_arrival_times, opt_is, parking)
#                 earliest_feasible_arrival_times = var_curr_arc
#                 latest_arc = get_route_for_arc((i, j), opt_is)
#                 if len(latest_arc) == 0:
#                     return False, earliest_feasible_arrival_times
#                 else:
#                     return parking[i, j], earliest_feasible_arrival_times
#             else:
#                 pass
#
#
# def get_time_windows(g, i, j):
#     # specify time window for parking
#     alpha_i = g.f_park_t[i][0]
#     beta_i = g.f_park_t[i][1]
#
#     # specify time window for traveling the arc
#     gamma_ij = g.f_dep_t[(i, j)][0]
#     delta_ij = g.f_dep_t[(i, j)][1]
#
#     return alpha_i, beta_i, gamma_ij, delta_ij
#
#
# def check_for_feasibility(g, i, j, earliest_feasible_at, opt_is, earliest_feasible_arrival_times,
#                           parking, add_park_time=None):
#     print("Check feasibility for usage of arc ({}) for earliest feasible time {}".format((i, j), earliest_feasible_at))
#     if earliest_feasible_at == float('inf'):
#         return False
#     # get time window for parking and for traveling the arc
#     alpha_i, beta_i, gamma_ij, delta_ij = get_time_windows(g, i, j)
#
#     # check first equation:
#     # in the first equation of the paper, parking is considered to be possible. Hence, inside the following
#     # for loop, the feasible parking times are determined. If the resulting set is empty, the algorithm proceeds
#     # to the next condition. To determine if a parking time is feasible, the conditions in the first equation
#     # of the paper are checked.
#     max_p_i = min(beta_i - earliest_feasible_at, delta_ij - earliest_feasible_at)
#     feasible_p_i = []
#     for pot_p_i in range(max_p_i + 1):
#         if (alpha_i <= earliest_feasible_at <= beta_i) and (gamma_ij <= earliest_feasible_at + pot_p_i <= delta_ij):
#             feasible_p_i.append(pot_p_i)
#     print("feasible parking times at {} when moving to {}: {}".format(i, j, feasible_p_i))
#     if len(feasible_p_i) > 0:
#         print("1st cond satisfied")
#         # in here, use greedy methodology and choose the smallest feasible parking time. If this leeds
#         # to an infeasible solution, the backtracking will try to increase the parking time.
#         p_i = feasible_p_i[0]
#         if add_park_time:
#             print("additional parking time at node {} is needed: ".format(i), add_park_time)
#             # if we run this function in backtracking mode, where at preceeding nodes the parking
#             # time has to be extended, the needed additional time is added to the minimum possible
#             # parking time at the corresponding node.
#             new_p_i = p_i + add_park_time
#             print("This sums up to: ", new_p_i)
#             if new_p_i <= max_p_i:
#                 print('which is still a feasible solution. Proceed with p_{} = {}'.format(i, new_p_i))
#                 return new_p_i
#             else:
#                 print("which is not a feasible solution. ")
#                 # earliest_feasible_arrival_times[i, j] = float('inf')
#                 return float('inf')
#         else:
#             print("Proceed with least possible parking time :", p_i)
#             return p_i
#
#     # check second equation
#     elif (beta_i - earliest_feasible_at <= 0) and (gamma_ij <= earliest_feasible_at <= delta_ij):
#         print("2nd cond satisfied")
#         p_i = 0
#         return p_i
#
#     # check third equation
#     # note: in comparison to the paper by Sancho, this condition has been changed, as the original
#     # set of conditions did not cover all cases. Here, it is checked WHETHER
#     # 1.) we arrive to early at a node, so that the route ahead is blocked and parking is not possible yet OR
#     # 2.) parking is not possible, as beta is smaller than gamma, and we arrive to early to directly take the route ahead.
#     # If this condition is satisfied, the backtracking is done to check whether longer parking at predecessor nodes
#     # makes the current route feasible.
#     elif (
#             earliest_feasible_at < alpha_i and earliest_feasible_at < gamma_ij
#     ) or (
#             earliest_feasible_at < gamma_ij and beta_i < gamma_ij
#     ):
#         print("3rd condition satisfied")
#         p_i, earliest_feasible_arrival_times = do_recursion(g, i, j, earliest_feasible_at, opt_is, earliest_feasible_arrival_times, parking)
#         print("recursion is done, result is: ", p_i)
#         return p_i
#
#     # check fourth equation
#     elif (
#             gamma_ij < earliest_feasible_at < alpha_i <= delta_ij
#     ) or (
#             gamma_ij < earliest_feasible_at < delta_ij <= alpha_i
#     ):
#         print("4th cond satisfied")
#         p_i = 0
#         return p_i
#
#     # check fifth equation
#     elif delta_ij < earliest_feasible_at:
#         print("5th cond satisfied")
#         return float('inf')
#
#     # raise an error if a case satisfies no condition
#     else:
#         print(Warning("Some cases are not considered in feasibility check"))
#         raise AssertionError()
