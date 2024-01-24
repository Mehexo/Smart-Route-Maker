import json
from turtle import st
from typing import Tuple
from networkx import MultiDiGraph


from ...SmartRouteMaker import Analyzer
from ...SmartRouteMaker import Visualizer
from ...SmartRouteMaker import Graph
from ...SmartRouteMaker import Planner

import random

#from Facades.SmartRouteMakerFacade import SmartRouteMakerFacade as srm
import math
import osmnx as ox
import numpy as np
import srtm


class SmartRouteMakerFacade():

    def __init__(self) -> None:
        """Initialize the facade.
        """        

        self.analyzer = Analyzer.Analyzer()
        self.visualizer = Visualizer.Visualizer()
        self.graph = Graph.Graph()
        self.planner = Planner.Planner()

    def get_graph(self, start_coordinates: str, radius:int = 10000, route_type:str ="bike"):
        start = self.normalize_coordinates(start_coordinates)
        graph = self.graph.full_geometry_point_graph(start,
                                                     radius=0.7 * radius,
                                                     type= route_type)
        return graph
    
    def get_start_node(self, graph, start_coordinates):
        start = self.normalize_coordinates(start_coordinates)
        X,Y = start
        start_node = ox.nearest_nodes(graph, X, Y) 
        return start_node


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






    def plan_kcircuit(self, graph: MultiDiGraph, start_node:int,  options: dict, max_length:int = 5000, max_height:int = 0, circle_dpoints:int =5, iter:int =5) -> dict:
        variance = 1.2 #vermenigvuldiging voor de cirkel
        loss = float("inf")
        change = 500 #meters
        elevation_data = srtm.main.get_data()

        # graph = self.graph.full_geometry_point_graph(start_coordinates)
        # start_node = self.graph.closest_node(graph, start_coordinates)
    
       
        angle = np.linspace(0, 2*np.pi, 360) 
        direction = angle[random.randint(0,359)]
        radius = max_length / math.pi /2
        difference_lon = math.cos(direction)* radius * variance / 111000
        difference_lat = math.sin(direction)* radius * variance / 111000
        x=float(graph.nodes[start_node]["x"]) + float(difference_lon)
        y=float(graph.nodes[start_node]["y"]) + float(difference_lat)
        center = ox.nearest_nodes(graph, x ,y )


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
        


        loss = float("inf")
        elevation_data = srtm.get_data()
        for i in range(0,iter):
            cyclus_temp = []
            cyclus_length_temp = 0
            if i > 0:
                distances = []
                new_points =[]
                for p in points:
                    angle = np.linspace(0, 2*np.pi, circle_dpoints) 
                    
                    degree = random.choice(angle)
                    difference_lon = math.cos(degree)* (change / 111000)
                    difference_lat = math.sin(degree)* (change / 111000)
                    y = float(graph.nodes[p]["y"]) + float(difference_lat)
                    x = float(graph.nodes[p]["x"]) + float(difference_lon)

                    if p == 0 or p =="0": #something happens here that i don't know how to fix
                        continue
                    new_cirkel_node = ox.nearest_nodes(graph, x, y)
                    new_points.append(new_cirkel_node)
                points = new_points
                print(points)
            
            
            for waypoint_start in range(0,len(points)-1):
                # print(f"start: {waypoint_start}")
                waypoint_end = waypoint_start+1
                #not needed because the last point is always the first because you go full circle
                if waypoint_end >= len(points):
                    waypoint_end = 0
                if points[waypoint_end] == 0 or points[waypoint_end] == "0": #some BULLSHIT happens here that i don't know how to fix
                    continue
                #merge the subsections
                for m in self.planner.shortest_path(graph,points[waypoint_start],points[waypoint_end]):
                    # print(f"node:{m}")
                    cyclus_temp.append(m)
                cyclus_length_temp += self.analyzer.shortest_path_length(graph,points[waypoint_start],points[waypoint_end])
            
            # if len(cyclus_temp) != len(set(cyclus_temp)):
            #     duplicates = []
            #     #find all duplicates
            #     for i, item in enumerate(cyclus_temp):
            #         if cyclus_temp.count(item) > 1 and item not in duplicates:
            #             duplicates.append(item)
            #     for p in points:
            #         #check of er naast ieder point duplicaten aan waardes zitten en verwijder deze todat je geen duplicaten meer tegenkomt
            #         p_index = cyclus_temp.index(p)
            #         check = True
            #         difference = 1
            #         to_delete = [] #list of indexen
                    
            #         deleted = False
            #         while check:
            #             if p == points[-1]:
            #                 check = False
                            
            #             else:
            #                 if cyclus_temp[p_index-difference]==cyclus_temp[p_index+difference]:
            #                     to_delete.append(p_index-difference)
            #                     to_delete.append(p_index+difference)
            #                     deleted = True
            #                 else:
            #                     check = False
            #                 difference += 1
            #         if deleted == True:
            #             del to_delete[-1]#zorgt ervoor dat het verbind stuk blijft
            #             to_delete.append(p_index)
                        


            #         for r in to_delete:
            #             del cyclus_temp[r]
            #     '''
            #     vervang een point door het dichtsbijzijnde duplicate punt dat nog steeds in de route zit.
            #     '''
            #     for p in points:
            #         if p == 0 or p == "0": #something happens here that i don't know how to fix
            #             continue
            #         distances = []
            #         if p not in cyclus_temp:
            #             continue
            #             #move p to fit on cyclus temp

            print(f"oude loss: {loss}")
            elevations, height_route = self.calculate_height(graph, cyclus_temp,elevation_data)
            new_loss = self.get_loss(route_dist = cyclus_length_temp, 
                                kms_target = max_length, 
                                height = height_route, 
                                height_target = max_height,
                                printb=True)
            print(f"nieuwe loss: {new_loss}")
            if loss > new_loss: 
                loss = new_loss
                cyclus = cyclus_temp
                cyclus_length = cyclus_length_temp
            
        print(cyclus)
        print(cyclus_length)    
        path = cyclus
        path_length = cyclus_length    
                
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
            "path_height": height_route,
            "route_analysis": route_analysis,
            "surface_dist": surface_dist,
            "surface_dist_visualisation": surface_dist_visualisation,
            "surface_dist_legenda": surface_dist_legenda,
            "simple_polylines": simple_polylines
        }

        return output
    
    def euclidian_distance_nodes(self, graph, node1, node2):
        x1 = graph._node[node1]["x"]
        y1 = graph._node[node1]["y"]
        x2 = graph._node[node2]["x"]
        y2 = graph._node[node2]["y"]
        distance = ((x2-x1)**2+(y2-y1)**2)**0.5
        return distance

    def calculate_height(self, graph, route, elevation_data):
        route_elevations = []
        for row in route:
            elevation = elevation_data.get_elevation(graph.nodes[row]["y"],graph.nodes[row]['x'])
            route_elevations.append(elevation)
        print(route_elevations)
        d_plus_out = 0
        for i, val in enumerate(route_elevations[1:]):
            if val > route_elevations[i]:
                d_plus_out += val - route_elevations[i]
            # print(f'{i+1} - prec_elev: {route_elevations[i]}, elev: {val}, d+: {d_plus_out}')
        return route_elevations, d_plus_out

    def get_loss(self, route_dist, kms_target, height = 0, height_target = 0, printb = False):
        
        dist_delta = abs(kms_target - route_dist*1000)
        loss_dist = dist_delta
        loss_height = abs(height - height_target)
        loss = (loss_dist ) + (loss_height *10) # + height, inlcine,
        if printb == True:
            print(f"distance from target: {loss_dist}")
            print(f"height from target: {loss_height}")
        return loss     
