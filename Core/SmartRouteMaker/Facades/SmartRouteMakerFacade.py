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
import matplotlib.pyplot as plt
import io
import base64


class SmartRouteMakerFacade():

    def __init__(self) -> None:
        """Initialize the facade.
        """        

        self.analyzer = Analyzer.Analyzer()
        self.visualizer = Visualizer.Visualizer()
        self.graph = Graph.Graph()
        self.planner = Planner.Planner()

    def setup(self,start_point, distance):
        
        start_coordinates = self.normalize_coordinates(start_point)
        graph = self.graph.full_geometry_point_graph(start_coordinates, radius= .5*distance, type="bike")
                
    
        Y,X = start_coordinates
        start_node = ox.nearest_nodes(graph, X, Y) 
        return graph, start_node


        
    def get_graph(self, start_coordinates: str, radius:int = 10000, route_type:str ="bike"):
        start = self.normalize_coordinates(start_coordinates)
        graph = self.graph.full_geometry_point_graph(start,
                                                     radius=0.5 * radius,
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
            print("12")
        else:
            route_analysis = None
            print("13")
        
        if "surface_dist" in options and options['surface_dist']:
            print("14")
            surface_dist = self.analyzer.get_path_surface_distribution(route_analysis)
            surface_dist_visualisation = self.visualizer.build_surface_dist_visualisation(route_analysis, graph)

            surface_dist_legenda = {}

            for type in surface_dist:
                surface_dist_legenda[type] = (self.visualizer.get_surface_color(type))
        else:
            print("15")
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

    
    def get_loss(self,route_dist, kms_target, height = 0, height_target = 0, wegdekverhard = 0, wegdeknietverhard = 0, wegdek_target = None, printb = False):
        length_loss = abs(route_dist*1000 / kms_target - 1)
        height_loss = abs(height / height_target - 1)

        if wegdek_target == None:
            wegdek_loss = 0
        else:
            if wegdek_target > 0.5:
                wegdek_loss = abs(wegdekverhard / route_dist -1)
            else:
                wegdek_loss = abs(wegdeknietverhard / route_dist-1)  
        loss = (float(length_loss) + float(height_loss) + float(wegdek_loss))/3 # + height, surface,
        if printb == True:
            donothing = 0
            #   print(f"distance from target: {length_loss}")
            #   print(f"height from target: {height_loss}")
        return float(loss) ,length_loss, height_loss, wegdek_loss 


    def calculate_height(self,graph, route, elevation_data):
        route_elevations = []
        for row in route:
            elevation = elevation_data.get_elevation(graph.nodes[row]["y"],graph.nodes[row]['x'])
            # print(elevation)
            route_elevations.append(elevation)
        # print(route_elevations)
        d_plus_out = 0
        for i, val in enumerate(route_elevations[1:]):
            if val > route_elevations[i]:
                d_plus_out += val - route_elevations[i]
            # print(f'{i+1} - prec_elev: {route_elevations[i]}, elev: {val}, d+: {d_plus_out}')
        return route_elevations, d_plus_out




    def plan_kcircuit(self, graph: MultiDiGraph, start_node: int, max_length:int = 10000, i_points: int = 5, max_height:int= 150, max_incline:int = 5,max_surface:int = None, iter:int = 30) -> dict:
        
        elevation_data = srtm.main.get_data()
        variance = 1.2
        change = 500 #meters
        loss = float("inf")
        route_not_found = False
        lengte_verhard = 0
        lengte_onverhard = 0
        points_data= dict()
        points =[]
        elevation_data = srtm.get_data()
        verhard = ["asphalt",
                    "paved",
                    "concrete",
                    "Concrete:lanes",
                    "Concrete:plates",
                    "paving",
                    "cobblestone",
                    "unhewn_cobblestone",
                    "metal",
                    "stepping_stones",
                    "compacted",
                    "rock"
                    ]
        onverhard = ["sett",
                    "grass",
                    "wood",
                    "unpaved",
                    "fine_gravel",
                    "gravel",
                    "earth",
                    "ground",
                    "dirt",
                    "soil",
                    "mud",
                    "sand",
            ]

        #cirkel opzetten (randomizer voor middelpunt)
        angle = np.linspace(0, 2*np.pi, 360) 
        direction = angle[random.randint(0,359)]
        
        opposite_direction = (direction + np.pi) % (2 * np.pi)
        # opposite_degree = np.degrees(opposite_direction)
        radius = max_length / math.pi / 2
        difference_lon = math.cos(direction)* radius * variance / 111000
        difference_lat = math.sin(direction)* radius * variance / 111000
        x=float(graph.nodes[start_node]["x"]) + float(difference_lon)
        y=float(graph.nodes[start_node]["y"]) + float(difference_lat)
        center = ox.nearest_nodes(graph, x , y)


        
        
        
    
       
        
        #punten verdelen in i gelijken stukken
        circle_dpoints = i_points
        
        angle = np.linspace(0, 2*np.pi, circle_dpoints) 
        for i in angle:
            degree = opposite_direction + i
            
            difference_lon = math.cos(degree)* radius * variance / 111000
            difference_lat = math.sin(degree)* radius * variance / 111000
            y = float(graph.nodes[center]["y"]) + float(difference_lat)
            x = float(graph.nodes[center]["x"]) + float(difference_lon)
            cirkel_node = ox.nearest_nodes(graph, x, y)
            points_data[cirkel_node]=graph.nodes[cirkel_node]
            points.append(cirkel_node)
        
        #make sure that you go past your starting location
        points[0] = start_node


        
        
        for i in range(0,iter):
            cyclus_temp = []
            cyclus_length_temp = 0
            seperate_paths =[]
            if i > 0:
                distances = []
                new_points =[]
                for p in points:
                    angle = np.linspace(0, 2*np.pi, 4) 
                    
                    direction = random.choice(angle)
                    degree = np.degrees(direction)
                    difference_lon = math.cos(degree)* (change / 111000)
                    difference_lat = math.sin(degree)* (change / 111000)
                    y = float(graph.nodes[p]["y"]) + float(difference_lat)
                    x = float(graph.nodes[p]["x"]) + float(difference_lon)

                    if p == 0 or p =="0": #something happens here that i don't know how to fix
                        continue
                    new_cirkel_node = ox.nearest_nodes(graph, x, y)
                    new_points.append(new_cirkel_node)
                points = new_points
                
            
            
            for waypoint_start in range(0,len(points)-1):
                # print(f"start: {waypoint_start}")
                waypoint_end = waypoint_start+1
                #not needed because the last point is always the first because you go full circle
                if waypoint_end >= len(points):
                    waypoint_end = 0
                if points[waypoint_end] == 0 or points[waypoint_end] == "0": #some BULLSHIT happens here that i don't know how to fix
                    continue
                #merge the subsections
                segm = self.planner.shortest_path(graph,points[waypoint_start],points[waypoint_end])
                if segm == None:
                    route_not_found = True
                    continue
                
                for m in segm:
                    
                    cyclus_temp.append(m)
                seperate_paths.append(segm)
                cyclus_length_temp += self.analyzer.shortest_path_length(graph,points[waypoint_start],points[waypoint_end])
            if route_not_found == True:
                route_not_found = False
                continue
                
            for path in seperate_paths:
                
                route_analysis = self.analyzer.get_path_attributes(graph, path)
                surface_dist = self.analyzer.get_path_surface_distribution(route_analysis)
                for surfice in surface_dist:
                    if surfice in verhard:
                        lengte_verhard+= surface_dist[surfice]
                    elif surfice in onverhard:
                        lengte_onverhard += surface_dist[surfice]


            print(f"interatie: {i}")
            print(f"oude loss: {loss}")
            elevations, height_route = self.calculate_height(graph, cyclus_temp, elevation_data)
            new_loss,length_loss, height_loss, wegdek_loss = self.get_loss(route_dist = cyclus_length_temp, 
                                kms_target = max_length, 
                                height = height_route, 
                                height_target = max_height,
                                wegdekverhard= lengte_verhard,
                                wegdeknietverhard= lengte_onverhard,
                                wegdek_target= max_surface,
                                printb=True)
            print(f"nieuwe loss: {new_loss}")
            if loss > new_loss: 
                loss = new_loss
                cyclus = cyclus_temp
                cyclus_length = cyclus_length_temp
                cyclus_height = height_route
                segments_path = seperate_paths
                final_verhard = lengte_verhard
                final_onverhard = lengte_onverhard
                

        
        
        path = cyclus
        #get data for graph        
        cum_length = [0]
        cum_length_temp = 0
        for i, way in enumerate(path):
            j = i+1
            if j>= len(path):
                break
            cum_length_temp += self.analyzer.shortest_path_length(graph,path[i],path[j])
            cum_length.append(cum_length_temp)

        elevations, height_route = self.calculate_height(graph, path, elevation_data)


        

        # Create a plot
        plt.plot(cum_length, elevations)
        plt.xlabel('afstand in km')
        plt.ylabel('hoogte in meters')
        plt.title('relief')

        # Save the plot to a BytesIO object
        img_buf = io.BytesIO()
        plt.savefig(img_buf, format='png')
        img_buf.seek(0)

        # Encode the image to base64 for HTML display
        img_base64 = base64.b64encode(img_buf.read()).decode('utf-8')

        # Close the plot to free up resources
        plt.close()



















        #calculate max incline
        incline = []
        dx = []
        for i, way in enumerate(path):
            j = i+1
            if j>= len(path):
                j = 0
            if path[i] == path[j]:
                delta_x = 000.1
            #delta y /delta x
            else:
                delta_x = self.analyzer.shortest_path_length(graph,path[i],path[j])
            dx.append(delta_x)
            if delta_x == 0:
                incline.append(0)
            else:
                incline.append((elevations[j]- elevations[i]) / (delta_x*1000))
        
        max_incline = max(incline)
        
        #clean the path for visualisation
        path = [cyclus[0]]
        for i in range(1, len(cyclus)):
            if cyclus[i] != cyclus[i-1]:
                path.append(cyclus[i])
        
        #route visualization
        route_analysis = self.analyzer.get_path_attributes(graph, path)
     
        surface_dist = self.analyzer.get_path_surface_distribution(route_analysis)
        surface_dist_visualisation = self.visualizer.build_surface_dist_visualisation(route_analysis, graph)

        surface_dist_legenda = {}

        for type in surface_dist:
            surface_dist_legenda[type] = (self.visualizer.get_surface_color(type))

        
        simple_polylines = self.visualizer.extract_polylines_from_folium_map(graph, path, invert=False)
        

        output = {
            "start_node": start_node,
            "end_node": start_node,
            "path": cyclus,
            "path_length": cyclus_length,
            "path_height": cyclus_height,
            "max_incline": max_incline*100,
            "route_analysis": route_analysis,
            "surface_percentage": (final_verhard/cyclus_length)*100,
            "surface_dist": surface_dist,
            "surface_dist_visualisation": surface_dist_visualisation,
            "surface_dist_legenda": surface_dist_legenda,
            "simple_polylines": simple_polylines,
            "line_graph": img_base64
        }

        return output
    
    def euclidian_distance_nodes(self, graph, node1, node2):
        x1 = graph._node[node1]["x"]
        y1 = graph._node[node1]["y"]
        x2 = graph._node[node2]["x"]
        y2 = graph._node[node2]["y"]
        distance = ((x2-x1)**2+(y2-y1)**2)**0.5
        return distance

   