
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


def calc_min_earliest_arrival_time(g, j, k, earliest_feasible_arrival_times,
                                   opt_is, parking):
    # earliest_feasible_arrival_times = earliest_feasible_arrival_times.copy()
    # opt_is = opt_is.copy()
    # parking = parking.copy()
    if j == 1:
        # we have initialized all arcs from the sink already
        return earliest_feasible_arrival_times, opt_is, parking

    pot_earliest_feasible_arrival_times = []
    arcs_to_j = [ij[0] for ij in g.edges if ij[1] == j]
    print("The following nodes move into {}: {}".format(j, arcs_to_j))
    inter_parking = []
    for i in arcs_to_j:
        f_ij = earliest_feasible_arrival_times[i, j]
        print("f({}, {}) is: {}".format(i, j, f_ij))
        p_i = check_for_feasibility(g, i, j, f_ij, opt_is, earliest_feasible_arrival_times, parking)
        f_ij = earliest_feasible_arrival_times[i, j]
        print("p_{}:".format(i), p_i)
        t_ij = g.distance[i, j]
        # parking[i, j] = p_i
        inter_parking.append(p_i)
        print("current earliest_feasible_arrival_times: ", earliest_feasible_arrival_times)
        print("current parking times: ", parking)
        if p_i is not False and type(p_i) == int:
            print("f_{}; p_{}; t_{}: ".format((i, j), i, (i, j)), f_ij, "; ", p_i, "; ", t_ij)
            pot_earliest_feasible_arrival_times.append(f_ij + p_i + t_ij)
        else:
            pot_earliest_feasible_arrival_times.append(float('inf'))
        print("pot_earliest_feasible_arrival_times", pot_earliest_feasible_arrival_times)
    earliest_feasible_arrival_times[j, k] = min(pot_earliest_feasible_arrival_times)
    parking[j, k] = inter_parking[pot_earliest_feasible_arrival_times.index(min(pot_earliest_feasible_arrival_times))]
    print("best i", pot_earliest_feasible_arrival_times.index(min(pot_earliest_feasible_arrival_times)))
    opt_is[j, k] = arcs_to_j[
        pot_earliest_feasible_arrival_times.index(min(pot_earliest_feasible_arrival_times))]

    return earliest_feasible_arrival_times, opt_is, parking


def do_recursion(g, i, j, earliest_feasible_at, opt_is, earliest_feasible_arrival_times, parking):
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
    print("so lets do the recursion")
    alpha_i = g.f_park_t[i][0]
    beta_i = g.f_park_t[i][1]

    # specify time window for traveling the arc
    gamma_ij = g.f_dep_t[(i, j)][0]
    delta_ij = g.f_dep_t[(i, j)][1]

    previous_arcs = get_route_for_arc((i, j), opt_is)
    print(previous_arcs)
    if len(previous_arcs) == 0:
        return float('inf')
    else:
        # this time is missing on node j in order to be able to park or directly move to k
        time_gap = min([alpha_i - earliest_feasible_at, gamma_ij - earliest_feasible_at])
        if time_gap < 0:
            time_gap = max([alpha_i - earliest_feasible_at, gamma_ij - earliest_feasible_at])
        print("time_gap", time_gap)

        curr_prev_arc = previous_arcs[-1]
        print(curr_prev_arc)
        f_i1_i2 = earliest_feasible_arrival_times[curr_prev_arc]
        new_p_i = check_for_feasibility(g, *curr_prev_arc, f_i1_i2, opt_is, earliest_feasible_arrival_times,
                                        parking, add_park_time=time_gap)
        if not new_p_i == float('inf'):
            new_earliest_feasible_at = f_i1_i2 + new_p_i + g.distance[curr_prev_arc]
            print("new f({}): ".format((i, j)), new_earliest_feasible_at, "new_p{}: ".format(i), new_p_i)
            earliest_feasible_arrival_times[i, j] = new_earliest_feasible_at
            # parking[curr_prev_arc] = new_p_i
            parking[i, j] = new_p_i
        else:
            new_earliest_feasible_at = earliest_feasible_at
        return check_for_feasibility(g, i, j, new_earliest_feasible_at, opt_is,
                                     earliest_feasible_arrival_times, parking)


def check_for_feasibility(g, i, j, earliest_feasible_at, opt_is, earliest_feasible_arrival_times,
                          parking, add_park_time=None):
    print("Check feasibility for usage of arc ({}) for earliest feasible time {}".format((i, j), earliest_feasible_at))
    if earliest_feasible_at == float('inf'):
        print("Infeasible solution found. Recalculate the best path for node {} proceeding to {}".format(i,j))
        earliest_feasible_arrival_times, opt_is, parking = \
            calc_min_earliest_arrival_time(g, i, j, earliest_feasible_arrival_times, opt_is, parking)
        latest_arc = get_route_for_arc((i, j), opt_is)
        if len(latest_arc) == 0:
            return False
        else:
            return parking[i, j]

    # specify time window for parking
    alpha_i = g.f_park_t[i][0]
    beta_i = g.f_park_t[i][1]

    # specify time window for traveling the arc
    gamma_ij = g.f_dep_t[(i, j)][0]
    delta_ij = g.f_dep_t[(i, j)][1]

    # check first equation:
    if alpha_i <= delta_ij:
        # pass
        max_p_i = min(beta_i - earliest_feasible_at, delta_ij - earliest_feasible_at)
        p_i = []
        for feas_p_i in range(max_p_i + 1):
            if (alpha_i <= earliest_feasible_at <= beta_i) and (
                    gamma_ij <= earliest_feasible_at + feas_p_i <= delta_ij):
                p_i.append(feas_p_i)
        print("feasible parking times at {} when moving to {}: {}".format(i, j, p_i))
        if len(p_i) > 0:
            print("1st cond satisfied")
            if add_park_time:
                print("additional parking time at node {} is needed: ".format(i), add_park_time)
                new_p_i = p_i[0] + add_park_time
                print("This sums up to: ", new_p_i)
                if new_p_i < max_p_i:
                    print('which is still a feasible solution. Proceed with p_{} = {}'.format(i, new_p_i))
                    return new_p_i
                else:
                    print("which is not a feasible solution. ")
                    # So when we move here we set f(2,7) to infinity, but what we really want to do is set
                    # f(1,2) to infinit and with this new insight calculate a new f(2,7): How can we proceed here?
                    earliest_feasible_arrival_times[i,j] = float('inf')
                    return float('inf')
            else:
                print("Proceed with least possible parking time :", p_i[0])
                return p_i[0]

    # check second equation
    if (beta_i - earliest_feasible_at <= 0) and (gamma_ij <= earliest_feasible_at <= delta_ij):
        print("2nd cond satisfied")
        p_i = 0
        return p_i
    # check third equation
    elif (earliest_feasible_at < gamma_ij <= alpha_i) or (
            earliest_feasible_at < alpha_i < gamma_ij < beta_i) or (
            earliest_feasible_at < beta_i < gamma_ij):
        a = do_recursion(g, i, j, earliest_feasible_at, opt_is, earliest_feasible_arrival_times, parking)
        print("recursion is done, result is: ", a)
        return a

    # check fourth equation
    elif gamma_ij < earliest_feasible_at < alpha_i <= delta_ij:
        print("4th cond satisfied")
        p_i = 0
        return [p_i]

    # check fifth equation
    elif delta_ij < earliest_feasible_at:
        print("5th cond satisfied")
        return [float('inf')]

    else:
        print(Warning("Some cases are not considered in feasibility check"))