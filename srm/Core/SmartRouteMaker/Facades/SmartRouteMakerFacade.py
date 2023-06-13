import json
from turtle import st
from typing import Tuple

from ...SmartRouteMaker import Analyzer
from ...SmartRouteMaker import Visualizer
from ...SmartRouteMaker import Graph
from ...SmartRouteMaker import Planner

import random

#from Facades.SmartRouteMakerFacade import SmartRouteMakerFacade as srm
import math
import osmnx as ox
import numpy as np

class SmartRouteMakerFacade():

    def __init__(self) -> None:
        """Initialize the facade.
        """        

        self.analyzer = Analyzer.Analyzer()
        self.visualizer = Visualizer.Visualizer()
        self.graph = Graph.Graph()
        self.planner = Planner.Planner()

    def plan_route(self, start_coordinates: tuple, end_coordinates: tuple, options: dict) -> dict:
        """Plan a route between two coordinates.

        Args:
            start_coordinates (tuple): Tuple of two coordinates that represent the start point.
            end_coordinates (tuple): Tuple of two coordinates that represent the end point.
            options (dict): Analysis options, see the documentation.

        Returns:
            dict: Route and analysis data.
        """        

        graph = self.graph.full_geometry_point_graph(start_coordinates)

        start_node = self.graph.closest_node(graph, start_coordinates)
        end_node = self.graph.closest_node(graph, end_coordinates)

        path = self.planner.shortest_path(graph, start_node, end_node)
        path_length = self.analyzer.shortest_path_length(graph, start_node, end_node)

        if "analyze" in options and options['analyze']:
            route_analysis = self.analyzer.get_path_attributes(graph, path)
        else:
            route_analysis = None
        
        if "surface_dist" in options and options['surface_dist']:
            surface_dist = self.analyzer.get_path_surface_distribution(route_analysis)
            surface_dist_visualisation = self.visualizer.build_surface_dist_visualisation(route_analysis, graph)

            surface_dist_legenda = {}

            for type in surface_dist:
                surface_dist_legenda[type] = (self.visualizer.get_surface_color(type))
        else:
            surface_dist = None
            surface_dist_visualisation = None
        
        simple_polylines = self.visualizer.extract_polylines_from_folium_map(graph, path, invert=False)

        output = {
            "start_node": start_node,
            "end_node": end_node,
            "path": path,
            "path_length": path_length,
            "route_analysis": route_analysis,
            "surface_dist": surface_dist,
            "surface_dist_visualisation": surface_dist_visualisation,
            "surface_dist_legenda": surface_dist_legenda,
            "simple_polylines": simple_polylines
        }

        return output

    def normalize_coordinates(self, coordinates: str, delimiter: str = ",") -> Tuple:
        """Converts a front-end inputted coordinate string into a tuple of two floats.

        Args:
            coordinates (str): String of two delimited coordinates
            delimiter (str, optional): The delimiter. Defaults to ",".

        Returns:
            Tuple: (x.xx, y.yy) tuple of normalized coordinates.
        """

        return tuple([float(coordinate.strip()) for coordinate in coordinates.split(delimiter)])  






    def plan_kcircuit(self, start_coordinates,  options: dict, max_length = 50000) -> dict:
        # max_length = 5000
        i_points = 10

        graph = self.graph.full_geometry_point_graph(start_coordinates)
        start_node = self.graph.closest_node(graph, start_coordinates)
    
        variance = 0.9
        angle = np.linspace(0, 2*np.pi, 360) 
        direction = angle[random.randint(0,359)]
        radius = max_length / math.pi /2
        difference_lon = math.cos(direction)* radius * variance / 111000
        difference_lat = math.sin(direction)* radius * variance / 111000
        x=float(graph.nodes[start_node]["x"]) + float(difference_lon)
        y=float(graph.nodes[start_node]["y"]) + float(difference_lat)
        center = ox.nearest_nodes(graph, x ,y )




        circle_dpoints = i_points
        points_data= dict()
        points =[]
        angle = np.linspace(0, 2*np.pi, circle_dpoints) 
        for i in angle:
            degree = i
            difference_lon = math.cos(degree)* radius / 111000
            difference_lat = math.sin(degree)* radius / 111000
            y = float(graph.nodes[center]["y"]) + float(difference_lat)
            x = float(graph.nodes[center]["x"]) + float(difference_lon)
            print("x = "+ str(x))
            print("y = " + str(y))
            cirkel_node = ox.nearest_nodes(graph, x, y)
            print(cirkel_node)
            points_data[cirkel_node]=graph.nodes[cirkel_node]
            points.append(cirkel_node)
        # print(points)
        # planner = Planner()
        # analyzer = Analyzer()
        cyclus = []
        cyclus_length = 0
        for i in range(0,len(points)-1):
            j= i+1
            #not needed because the last point is always the first because you go full circle
            if j >= len(points):
                j = 0
            #merge the subsections
            for m in self.planner.shortest_path(graph,points[i],points[j]):
                cyclus.append(m)
            cyclus.pop(-1)   
            # cyclus_length += analyzer.shortest_path_length(graph,points[i],points[j])

        # path = list(set(cyclus))#, cyclus_length
        path = cyclus
        path_length = 7        
                
        if "analyze" in options and options['analyze']:
            route_analysis = self.analyzer.get_path_attributes(graph, path)
        else:
            route_analysis = None
        
        if "surface_dist" in options and options['surface_dist']:
            surface_dist = self.analyzer.get_path_surface_distribution(route_analysis)
            surface_dist_visualisation = self.visualizer.build_surface_dist_visualisation(route_analysis, graph)

            surface_dist_legenda = {}

            for type in surface_dist:
                surface_dist_legenda[type] = (self.visualizer.get_surface_color(type))
        else:
            surface_dist = None
            surface_dist_visualisation = None
            surface_dist_legenda = None
        
        simple_polylines = self.visualizer.extract_polylines_from_folium_map(graph, path, invert=False)

        output = {
            "start_node": start_node,
            "end_node": start_node,
            "path": path,
            "path_length": path_length,
            "route_analysis": route_analysis,
            "surface_dist": surface_dist,
            "surface_dist_visualisation": surface_dist_visualisation,
            "surface_dist_legenda": surface_dist_legenda,
            "simple_polylines": simple_polylines
        }

        return output