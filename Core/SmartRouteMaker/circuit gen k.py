import random
from Graph import Graph
#from Facades.SmartRouteMakerFacade import SmartRouteMakerFacade as srm
import math
import pandas
import osmnx as ox
from networkx import MultiDiGraph
import json
from turtle import st
from typing import Tuple
from Planner import Planner
import numpy as np
from Analyzer import Analyzer
import timeit




# self.analyzer = Analyzer.Analyzer()
# self.visualizer = Visualizer.Visualizer()
# self.graph = Graph.Graph()
# self.planner = Planner.Planner()

# "need to be deleted and implemented in huidige code"
def normalize_coordinates(coordinates: str, delimiter: str = ",") -> Tuple:
        """Converts a front-end inputted coordinate string into a tuple of two floats.

        Args:
            coordinates (str): String of two delimited coordinates
            delimiter (str, optional): The delimiter. Defaults to ",".

        Returns:
            Tuple: (x.xx, y.yy) tuple of normalized coordinates.
        """

        return tuple([float(coordinate.strip()) for coordinate in coordinates.split(delimiter)])  


    
#     # coordinates are (lat, lon)

def circuit_gen_k(graph: MultiDiGraph, start_node: int, max_length:int, i_points: int):
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
    print(points)

    #make route
    planner = Planner()
    analyzer = Analyzer()
    loss = float("inf")
    for i in range(0,5):

        
        cyclus_temp = []
        cyclus_length_temp = 0
        for i in range(0,len(points)-1):
            j= i+1
            #not needed because the last point is always the first because you go full circle
            if j >= len(points):
                j = 0
            #merge the subsections
            for m in planner.shortest_path(graph,points[i],points[j]):
                cyclus_temp.append(m)
            cyclus_length_temp += analyzer.shortest_path_length(graph,points[i],points[j])
        if len(cyclus_temp) != len(set(cyclus_temp)):
            duplicates = []
            for i, item in enumerate(cyclus_temp):
                if cyclus_temp.count(item) > 1 and item not in duplicates:
                    duplicates.append(item)       
            for item in duplicates:
                indices = []
                for i,x in enumerate(cyclus_temp):
                    if x == item:
                        indices.append(i)
                if indices !=  []:
                    min_index = min(indices)
                    max_index = max(indices)
                    del cyclus_temp[min_index+1:max_index]
            for dupe in duplicates:
                if dupe in cyclus_temp:
                    closest_node = ox.distance.nearest_nodes(graph, dupe, points)
                    points.insert(i,points.index(closest_node))
                    points.remove(closest_node)
            cyclus_length_temp = 0
            for i in range(0,len(points)-1):
                j= i+1
                if j >= len(points):
                    j = 0
                cyclus_length_temp += analyzer.shortest_path_length(graph,points[i],points[j])

        new_loss = get_loss(cyclus_length_temp, max_length)
        if loss <= new_loss:   
            loss = new_loss
            cyclus = cyclus_temp
            cyclus_length = cyclus_length_temp
        
        change = 500

        if i > 0:
            for i in points:
                angle = np.linspace(0, 2*np.pi, circle_dpoints) 
                
                degree = random.choice(angle)
                difference_lon = math.cos(degree)* change / 111000
                difference_lat = math.sin(degree)* change / 111000
                y = float(graph.nodes[center]["y"]) + float(difference_lat)
                x = float(graph.nodes[center]["x"]) + float(difference_lon)
                cirkel_node = ox.nearest_nodes(graph, x, y)
                closest_node = ox.distance.nearest_nodes(graph, cirkel_node, points)
                points.insert(i,points.index(closest_node))
                points.remove(closest_node)





    return cyclus, cyclus_length
    # return list(set(cyclus))#, cyclus_length
    # for i in range(len(0,points)):


    #     start_node = graph.closest_node(graph, start_coordinates)
    #     end_node = graph.closest_node(graph, end_coordinates)

    #     path = planner.shortest_path(graph, start_node, end_node)
    #     start_node = ox.nearest_nodes(graph)   
    #     planner.shortest_path(graph, start_node= start_node)
        






    #Graph.closest_node(graph,(graph.))
    #first_path = ox.shortest_path(graph, start_node, end_node)
def delete_nodes_between_duplicates(lst):
    duplicates = []
    for i, item in enumerate(lst):
        if lst.count(item) > 1 and item not in duplicates:
            duplicates.append(item)

    for item in duplicates:
        indices = [i for i, x in enumerate(lst) if x == item]
        min_index = min(indices)
        max_index = max(indices)
        del lst[min_index+1:max_index]

    return lst

    # Example usage
    



def get_loss(route_dist, kms_target, height, height_target):
    
  dist_delta = abs(kms_target - route_dist)
  loss_dist = dist_delta

  loss = loss_dist # + height, inlcine,
  return loss     

if __name__ == "__main__" :
    #k is afstand in meter van route
    k = 5000
    start_point =str(50.880848676808334)+","+str( 5.960501432418824)
    graph_class = Graph()
    
    print(start_point)
    start_coordinates = normalize_coordinates(start_point)
    graph = Graph.full_geometry_point_graph(graph_class, start_coordinates, radius= 5000) 


    print(graph)
    X,Y = start_coordinates
    start_node = ox.nearest_nodes(graph, X, Y) 
    
    k_values = [3,4,5,6,7,8,9,10]
    kilometers = [5000,10000,15000,20000,25000,30000,35000,40000]
    # for i in range(0,len(kilometers)):
    #     for j in range(0,len(k_values)):
    #         start_time = timeit.default_timer()
    #         path =  circuit_gen_k(graph, start_node, kilometers[i],k_values[j])
    #         end_time = timeit.default_timer()
    #         print("kilometers = ", kilometers[i],"\naantal punten op cirkel = ", k_values[j],"\nExecution time : ", end_time -start_time)
     

    # pause = input("pause")
    start = timeit.timeit()
    path, length =  circuit_gen_k(graph, start_node, k, 5)
    end = timeit.timeit()
    print("time elapsed: ", end - start)
    # path, length =circuit_gen_k(graph, start_node, k, 4)
    print("path =", end = " ")
    print(path)
    print("lengte = " , length)
    print("finished")
    # print("length =", end = " ")
    # print(length)
    
    
    
