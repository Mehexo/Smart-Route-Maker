from flask import Blueprint, render_template, request
from .SmartRouteMaker.Facades import SmartRouteMakerFacade as srm
# import srtm

core = Blueprint('core', __name__,
    static_folder='Static',
    static_url_path='/Core/Static',
    template_folder='Templates')

@core.route('/')
def index():
    return render_template('home.html')

@core.route('/handle_routing', methods=['POST'])
def handle_routing():
    srmf = srm.SmartRouteMakerFacade()
    # start = srmf.normalize_coordinates(request.form['start_point'])

    start_coordinates = request.form["start_point"]
    wanted_distance = int(request.form["distance"])
    graph, start_node = srmf.setup(start_coordinates, wanted_distance)
  
    
    
    wanted_height = 100
    # wanted_height = int(request.form["height"])
    # # wanted_incline = int(request.form["inlcine"])
    # # wanted_surface = int(request.form["surface"])
    # # elevation_data = srtm.main.get_data()
    
    print(start_node)
    route = srmf.plan_kcircuit(graph = graph,
                               start_node = start_node,
                               max_length = wanted_distance,
                               max_height = wanted_height,
                               i_points= 5,
                               iter = 5)
    
    
    

    # route = srmf.plan_route(start, end, options={"analyze": True, "surface_dist": True})
    # route = srmf.plan_kcircuit(start, options={"analyze": True, "surface_dist": True})
    return render_template('result.html', 
        surfaces=route['surface_dist'],
        surfaceDistLegenda=route['surface_dist_legenda'],
        surfaceDistVisualisation=route['surface_dist_visualisation'],
        path_length=route['path_length'],
        path_height = route['path_height'],
        max_incline = route['max_incline'],
        surface_percentage = route['surface_percentage'],
        routeVisualisation=route['simple_polylines'],
        line_graph = route['line_graph']

    )