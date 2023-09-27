import networkx as nx
import gpxpy
import gpxpy.gpx
from itertools import combinations

def shortest(G):
    odd_degree_nodes = [node for node, degree in G.degree() if degree % 2 == 1]

# Step 5: Make Graph Eulerian
        # Calculate the pairwise distance between all odd-degree nodes
    odd_node_pairs = list(combinations(odd_degree_nodes, 2))
    pair_distances = [(pair, nx.shortest_path_length(G, pair[0], pair[1], weight='length')) for pair in odd_node_pairs]

        #Sort pairs by distance
    pair_distances.sort(key=lambda x: x[1])

        # Add edges to the graph to make it Eulerian
    while odd_degree_nodes:
            # Start with the odd-degree node with the smallest distance pair
        node = odd_degree_nodes[0]
        min_distance = float('inf')
        min_pair = None

        for pair, distance in pair_distances:
            if node in pair:
                if distance < min_distance:
                    min_distance = distance
                    min_pair = pair

            # Add edge to the graph
        path = nx.shortest_path(G, min_pair[0], min_pair[1], weight='length')
        for i in range(len(path) - 1):
            G.add_edge(path[i], path[i + 1], length=min_distance)

        # Remove nodes from odd_degree_nodes list
        odd_degree_nodes.remove(min_pair[0])
        odd_degree_nodes.remove(min_pair[1])

        # Remove pairs that include these nodes from pair_distances list
        pair_distances = [(pair, dist) for pair, dist in pair_distances if pair[0] not in min_pair and pair[1] not in min_pair]


    eulerian_circuit = list(nx.eulerian_circuit(G))
        
    return eulerian_circuit


def gpx_file(G, eulerian_circuit):
# Initialize a new GPX object
    gpx = gpxpy.gpx.GPX()

    # Create a GPX track
    gpx_track = gpxpy.gpx.GPXTrack()
    gpx.tracks.append(gpx_track)

    # Create a GPX segment
    gpx_segment = gpxpy.gpx.GPXTrackSegment()
    gpx_track.segments.append(gpx_segment)

    n = 10  # Number of points to interpolate along each edge

    # Add points to the GPX segment, with interpolation
    for u, v in eulerian_circuit:
        x_u, y_u = G.nodes[u]['x'], G.nodes[u]['y']
        x_v, y_v = G.nodes[v]['x'], G.nodes[v]['y']
    
        # Interpolate n points along the edge
        for i in range(n + 1):
            x_i = x_u + (i / n) * (x_v - x_u)
            y_i = y_u + (i / n) * (y_v - y_u)
            gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(y_i, x_i))

    # Serialize to XML (GPX format)
    gpx_xml = gpx.to_xml()

    # Write to file
    

    return gpx_xml
    