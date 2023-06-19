import osmnx as ox
from typing import Tuple, List
from networkx import MultiDiGraph


class Planner:

    def shortest_path(self, graph: MultiDiGraph, start_node: int, end_node: int) -> List:
        """Get the shortest path between two nodes in a graph.

        Args:
            graph (MultiDiGraph): Instance of an osmnx graph.
            start_node (int): Unique ID of the start node within the graph.
            end_node (int): Unique ID of the end node within the graph.

        Returns:
            List: [xxx, yyy, zzz] A sequence of nodes that form the shortest path.
        """        

        return ox.shortest_path(graph, start_node, end_node)

    # import random
    # from Graph import Graph
    # import math
    #coordinates are (lat, lon)

    # def circuit_gen_k(self, graph: MultiDiGraph, start_node: int, max_length):
    #     variance = 0.9
    #     direction = random.randint(-180,180)/360
    #     difference_lon = math.cos(direction)* max_length * variance / 111000
    #     difference_lat = math.sin(direction)* max_length * variance / 111000
    #     end_node = ox.nearest_nodes(graph, (int(graph.nodes[start_node].data["lat"]) + int(difference_lat), int(graph.nodes[start_node].data["lon"]) + int(difference_lon))
    #     #Graph.closest_node(graph,(graph.))
    #     first_path = ox.shortest_path(graph, start_node, end_node)