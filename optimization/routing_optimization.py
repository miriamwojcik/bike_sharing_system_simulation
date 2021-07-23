# Returns the order of locations to be visited
# based on the https://developers.google.com/optimization/routing/cvrp

from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp


class Optimization:
    def __init__(self, distance_matrix, demands, vehicles_no, vehicles_capacity):
        self.distance_matrix = distance_matrix
        self.optimum_order = []
        self.depot = 0
        self.demands = demands
        self.vehicles_no = vehicles_no
        self.vehicle_capacities = vehicles_capacity
        self.data = {}


    def create_data_model(self):
        """Stores the data for the problem."""

        self.data['distance_matrix'] = self.distance_matrix
        self.data['demands'] = self.demands
        self.data['vehicle_capacities'] = self.vehicle_capacities
        self.data['num_vehicles'] = self.vehicles_no
        self.data['depot'] = self.depot
        return self.data

    # A function to get textual route data
    def print_solution(self, data, manager, routing, solution):
        """Prints solution on console."""
        total_distance = 0
        total_load = 0
        for vehicle_id in range(self.data['num_vehicles']):
            index = routing.Start(vehicle_id)
            plan_output = 'Route for vehicle {}:\n'.format(vehicle_id)
            route_distance = 0
            route_load = 0
            while not routing.IsEnd(index):
                node_index = manager.IndexToNode(index)
                self.optimum_order.append(node_index)
                route_load += self.data['demands'][node_index]
                plan_output += ' {0} Load({1}) -> '.format(node_index, route_load)
                previous_index = index
                index = solution.Value(routing.NextVar(index))
                route_distance += routing.GetArcCostForVehicle(
                    previous_index, index, vehicle_id)
            self.optimum_order.append(0)
            plan_output += ' {0} Load({1})\n'.format(manager.IndexToNode(index),
                                                     route_load)
            plan_output += 'Distance of the route: {}m\n'.format(route_distance)
            plan_output += 'Load of the route: {}\n'.format(route_load)
            #print(plan_output)
            total_distance += route_distance
            total_load += route_load


    def get_optimized_order(self):
        #create data model
        self.data = self.create_data_model()

        # Create the routing index manager.
        manager = pywrapcp.RoutingIndexManager(len(self.data['distance_matrix']),
                                           self.data['num_vehicles'], self.data['depot'])
        routing = pywrapcp.RoutingModel(manager)


            # Create and register a transit callback.
        def distance_callback(from_index, to_index):
            """Returns the distance between the two nodes."""
            # Convert from routing variable Index to distance matrix NodeIndex.
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return self.data['distance_matrix'][from_node][to_node]

        transit_callback_index = routing.RegisterTransitCallback(distance_callback)

        # Define cost of each arc.
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        # Add Capacity constraint.
        def demand_callback(from_index):
            """Returns the demand of the node."""
            # Convert from routing variable Index to demands NodeIndex.
            from_node = manager.IndexToNode(from_index)
            return self.data['demands'][from_node]

        demand_callback_index = routing.RegisterUnaryTransitCallback(
            demand_callback)
        routing.AddDimensionWithVehicleCapacity(
            demand_callback_index,
            0,  # null capacity slack
            self.data['vehicle_capacities'],  # vehicle maximum capacities
            True,  # start cumul to zero
            'Capacity')

        #Set heuristics
        # More on search strategies supported: https://developers.google.com/optimization/routing/routing_options#local_search_options
        # Default guided local search. According to documentation:  this is generally the most efficient metaheuristic for vehicle routing.
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PARALLEL_CHEAPEST_INSERTION)

        # Solve the problem.
        solution = routing.SolveWithParameters(search_parameters)
        # Print solution on console.
        if solution:
            print('Optimum Route Found')
            self.print_solution(self.data, manager, routing, solution)
        else:
            print('Failed to find a route')
        return self.optimum_order

