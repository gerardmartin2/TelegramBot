import osmnx as ox
import sklearn
import pickle
import networkx as nx
import csv
import urllib.request
from staticmap import StaticMap, CircleMarker, Line

PLACE = 'Barcelona,Catalonia'


def download_graph(PLACE):
    """ Given a place, creates a graph of the site.

    Parameters:
    ----------
    PLACE: Name of the city and the comunity the graph of which is wanted.

    Returns:
    ----------
    graph: The graph of the given location
    """

    graph = ox.graph_from_place(PLACE, network_type='drive', simplify=True)
    graph = ox.utils_graph.get_digraph(graph, weight='length')
    return graph


def save_graph(graph, GRAPH_FILENAME):
    """ Given an osmnx multidigraph and the name of a file, saves the
    graph to file.

    Parameters:
    ----------
    graph: osmnx multidigraph
    GRAPH_FILENAME: name of the file where the graph is going to be stored

    Returns:
    ----------
    Nothing. Only saves the graph.
    """

    with open(GRAPH_FILENAME, 'wb') as file:
        pickle.dump(graph, file)
        file.close()


def load_graph(GRAPH_FILENAME):
    """ Given the name of a file, load its content in the variable graph.

    Parameters:
    ----------
    GRAPH_FILENAME: name of the file where the osmnx graph is stored

    Returns:
    ----------
    graph: osmnx multidigraph that was in the file.
    """

    with open(GRAPH_FILENAME, 'rb') as file:
        graph = pickle.load(file)
    return graph


def exists_graph(GRAPH_FILENAME):
    """Given the name of a file, determines if it exists.

    Parameters:
    ----------
    GRAPH_FILENAME: name of the file which is wanted to acces.

    Returns:
    ----------
    True if the file is found and False otherwise.
    """

    try:
        f = open(GRAPH_FILENAME)
    except:
        return False
    return True


def plot_graph(PLACE):
    """Given a place, plots a map of the site.

    Parameters:
    ----------
    PLACE: The name of the place from wich we want to get the map.

    Returns:
    ----------
    Osmnx function that shows the map of the indicated place.
    """

    return ox.plot_graph(ox.graph_from_place(PLACE, network_type='drive', simplify=True))


def download_highways(HIGHWAYS_URL):
    """Given a file url, read it and download its content, storing it
    in a dictionary.

    Parameters:
    ----------
    HIGHWAYS_URL: Url from a csv exel file that provides information about
    Barcelona's highways.

    Returns:
    ----------
    hw: Dictionary with way identification numbers as keys and the coordinates
    of each the points of each street as values.
    """

    # Read the file in csv format
    with urllib.request.urlopen(HIGHWAYS_URL) as response:
        lines = [l.decode('utf-8') for l in response.readlines()]
        reader = csv.reader(lines, delimiter=',', quotechar='"')
    next(reader)
    points = []
    tram_id = []
    hw = {}
    # For every line in the file
    for line in reader:
        # Add to hw the way id as a key and the list of coordinates
        # of the points in the way as the value
        way_id, description, coordinates = line
        hw[int(way_id)] = list(map(float, coordinates.split(',')))
    return hw


def plot_highways(highways, name, SIZE):
    """Given a dictionary that stores the coordinates of the points that
    form each way, a file name and a size, stores a map of that size in a
    file with the indicated name.

    Parameters:
    ----------
    highways: Dictionary with the identification number of each way as keys
    and the coordinates of the points that forms it as values.
    name: The name of the file where the map is going to be stored.
    SIZE: The size that the map is going to have.

    Returns:
    ----------
    Nothing. Plots a map on a given file.
    """

    mapa_bcn = StaticMap(600, 600)
    # For every way in highways
    for way in highways:
        row = highways[way]
        for i in range(0, len(row), 2):
            if (i == 0):
                marker = CircleMarker((row[i], row[i+1]), 'yellow', 3)
                mapa_bcn.add_marker(marker)
            elif (i == len(row) - 2):
                marker = CircleMarker((row[i], row[i+1]), 'blue', 3)
                mapa_bcn.add_marker(marker)
            if (i < len(row) - 3):
                coordinates = [[row[i], row[i+1]], [row[i+2], row[i+3]]]
                line_outline = Line(coordinates, 'red', 2)
                line = Line(coordinates, 'black', 3)
                mapa_bcn.add_line(line_outline)
                mapa_bcn.add_line(line)
    image = mapa_bcn.render()
    image.save(name)


def download_congestions(CONGESTIONS_URL):
    """Given a file url, reads its content and stores it in a list.

    Parameters:
    ----------
    CONGESTIONS_URL: Url of the online file where the data about highways'
    congestion is.

    Returns:
    ----------
    congestion: List with the way id number and its current congestion.
    """

    with urllib.request.urlopen(CONGESTIONS_URL) as response:
        lines = [l.decode('utf-8') for l in response.readlines()]
        reader = csv.reader(lines, delimiter='#', quotechar='"')
    congestion = []
    for line in reader:
        congestion.append((int(line[0]), int(line[2])))
    return congestion


def plot_congestions(highways, congestions, name, SIZE):
    """Given a dictionary and a list with information about ways' congestions
    and points, plots a map of the city showing congestions information using
    colors. It loads the map of size SIZExSIZE in the specified file.

    Parameters:
    ----------
    highways: Dictionary with the identification numbers of each way as keys
    and the coordinates of the points that form it as values.
    congestions: List with the way id number and its current congestion.
    name: The name of the file where the map is going to be stored.
    SIZE: The size that tha map is going to have.

    Returns:
    ----------
    Nothing. Only plots the map in the given file.
    """

    mapa_bcn = StaticMap(600, 600)
    for tram in congestions:
        density = tram[1]
        color = {0: 'white', 1: 'green', 2: 'yellow', 3: 'purple', 4: 'orange', 5: 'red', 6: 'black'}
        row = highways[tram[0]]
        for i in range(0, len(row)-3, 2):
            coordinates = [[row[i], row[i+1]], [row[i+2], row[i+3]]]
            line = Line(coordinates, color[density], 3)
            mapa_bcn.add_line(line)
    image = mapa_bcn.render()
    image.save(name)


def congestion_time(density, usual_time):
    """Given the density of a highway and the time you would spent traversing
    it without traffic, calculates aproximately the extra time that traffic
    will add to the travel time.

    Parameters:
    ----------
    density: Congestion of the street given by a number between 0 and 6.
    0 means no data, whereas numbers between 1 to 5 indicate traffic levels,
    being 1 the lowest congestion level and 5 the biggest.
    Number 6 indicates a blocked street.
    usual_time: Time that takes to cross the way in average driving at the
    maximum allowed speed.

    Returns:
    ----------
    Double indicating the extra time added by traffic to the route.
    """

    if density == 0:
        return usual_time
    elif density == 1:
        return 0
    elif density == 2:
        return usual_time / 4
    elif density == 3:
        return 3*usual_time/4
    elif density == 4:
        return 3*usual_time/2
    elif density == 5:
        return 3*usual_time


def add_itime(graph, nodes, density):
    """Given a graph, a list of nodes that form a highway and the congestion
    of that highway, calculates the itime of the path and imputes it to every
    edge on it.

    Parameters:
    ----------
    graph: The graph with edges with the average itime.
    nodes: List of nodes that allow to access the edges of the path.
    density: Level of congestion of the highway.

    Returns:
    ----------
    Nothing. Modifies the attribute itme of the edges in the graph.
    """
    # For every node in the path
    for i in range(0, len(nodes)-1):
        way_length = 0
        # Get the distance in m and the speed in km/h
        way_lenght = graph[nodes[i]][nodes[i+1]]['length']
        way_speed_limit = graph[nodes[i]][nodes[i+1]]['maxspeed']
        # Convert the speed into m/s
        way_speed_limit = float(10*way_speed_limit/36)
        # Get the time that takes to cross the street without traffic
        usual_time = float(way_lenght / way_speed_limit)
        # Add the congestion time
        itime = usual_time + congestion_time(density, usual_time)
        graph[nodes[i]][nodes[i+1]]['itime'] = itime


def build_igraph(graph, highways, congestions):
    """Given a graph and the information about highways and its congestions,
    imputs to every edge a  new attribute called itime.
    Itime would aproximately simulate the time it would take to go through
    a street taking into account its traffic level, the maximum speed allowed
    and its lenght.
    For streets that not have traffic information, we would suppose an average
    congestion of level 2.

    Paramaters:
    ----------
    graph: Osmnx graph of Barcelona.
    highways: Dictionary containing information about the coordinates of the
    points that form each way.
    congestions: List that contains the way identifier, as well as the
    current level of traffic.

    Returns:
    ----------
    graph: Modified version of the original graph with a new attribute itime
    set in most edges.
    """

    # Travel through all edges and imput them the average itime attribute
    # supposing traffic level 2
    for edge in graph.edges(data=True):
        try:
            edge[2]['itime'] =  edge[2]['length'] / (10 * float(edge[2]['maxspeed']) / 36)
            edge[2]['itime'] = edge[2]['itime'] + congestion_time(2, edge[2]['itime'])
        except:
            pass
    # For every street with traffic information, modifie the itime in order
    # to be precise
    for way in congestions:
        density = way[1]
        way_id = way[0]
        coord = highways[way_id]
        for i in range(0, len(coord)-3, 2):
            # Get the neareest nodes to the coordinates of the points
            origin_node = ox.distance.nearest_nodes(graph, coord[i], coord[i+1])
            destination_node = ox.distance.nearest_nodes(graph, coord[i+2], coord[i+3])
            try:
                # Get the nodes that have to be visited to go from the origin
                # to the destination
                nodes = nx.shortest_path(graph, origin_node, destination_node, weight='length')
                # Modify the itimes of the edges between these nodes taking
                # into account the real congestion of these way.
                add_itime(graph, nodes, density)
            except:
                # Nodes are not connected
                pass
    return graph


def get_shortest_path_with_itimes(igraph, origin_lat, origin_lon, destination="Sagrada Família"):
    """Given the intelligent version of the graph, the coordinates of the
    origin point and the name of the destination, determines the shortest
    path between these two points.

    Parameters:
    ----------
    igraph: Intelligent version of the graph with edges that have the itime
    attribute.
    origin_lat: Latitude of the origin point.
    origin_lon: Longitude of the origin point.
    destination: String with the name of the destination.

    Returns:
    ----------
    route: List of nodes. The edges between them create the shortest path
    taking into account traffic congestion.
    """

    # Add more information about the destination to ensure getting the proper
    # coordinates
    destination = destination + ",Barcelona,Catalonia"
    # Get the coordinates of the destination
    dest_lat, dest_lon = ox.geocode(destination)
    # Search the nearest nodes to the origin and destination points
    # in the osmnx graph
    orig = ox.distance.nearest_nodes(igraph, origin_lon, origin_lat)
    dest = ox.distance.nearest_nodes(igraph, dest_lon, dest_lat)
    # Create the shortest path between the points
    route = nx.shortest_path(igraph, orig, dest, weight='itime')
    return route


def plot_path(igraph, ipath, SIZE):
    """Given a graph, a size and a path, plots the map of that size with a
    drawn path into a file. This path is the shortest one from the between the
    first and the last point in the ipath.

    Parameters:
    ----------
    igraph: Intelligent version of the graph with edges that have the itime
    attribute.
    ipath: List of nodes that form the shortest possible path between two
    points taking into account the traffic.
    SIZE: The size that the map will have.

    Returns:
    ----------
    The image of the map as well as storing it in the file 'mapa.png'.
    """

    m = StaticMap(SIZE, SIZE)
    # Mark the origin and the destination nodes.
    nix = igraph.nodes[ipath[0]]['x']
    niy = igraph.nodes[ipath[0]]['y']
    ndx = igraph.nodes[ipath[len(ipath)-1]]['x']
    ndy = igraph.nodes[ipath[len(ipath)-1]]['y']
    s_marker = CircleMarker((nix, niy), 'red', 8)
    e_marker = CircleMarker((ndx, ndy), 'red', 8)
    m.add_marker(s_marker)
    m.add_marker(e_marker)
    # Store the first node coordinates
    ni = [nix, niy]
    # For each node in ipath
    for i in range(len(ipath)-1):
        # Store the following node
        nfx = igraph.nodes[ipath[i+1]]['x']
        nfy = igraph.nodes[ipath[i+1]]['y']
        nf = [nfx, nfy]
        # Store the coordinates of both connected nodes
        coordinates = [ni, nf]
        # Plot a line simulating the edge between them
        line = Line(coordinates, 'blue', 5)
        m.add_line(line)
        # Repeat the process for the next node
        ni = nf
    # Create and save the image in a file
    image = m.render()
    image.save('mapa.png')
    return image
