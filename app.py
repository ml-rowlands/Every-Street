from itertools import combinations
import geopandas as gpd
import gpxpy
import gpxpy.gpx
import matplotlib.pyplot as plt
import networkx as nx
import osmnx as ox
import pandas as pd
import streamlit as st
from shapely.geometry import MultiPolygon, Polygon
import warnings

from utils import *

NETWORK_TYPE = 'all'
MILES_CONVERSION = 1609

@st.cache
def fetch_graph(option, **kwargs):
    if option == 'Bounding Box':
        return ox.graph_from_bbox(**kwargs, network_type=NETWORK_TYPE)
    elif option == 'City/State':
        return ox.graph_from_place(f"{kwargs['city']},{kwargs['state']}", network_type=NETWORK_TYPE).to_undirected()
    elif option == 'Point and Radius':
        return ox.graph_from_point((kwargs['lat'], kwargs['long']), dist=kwargs['rad'], network_type=NETWORK_TYPE).to_undirected()

def main():
    
    warnings.filterwarnings('ignore')
    
    st.title('Run Your City Optimal Path')
    
    st.markdown(
        'Inspired by [Ricky Gates](https://www.everysinglestreet.com/why), I wanted to come up with a way to download a gpx file for the places I run. \
        This app [works](https://github.com/ml-rowlands) by solving the [Chinese Postman Problem](https://en.wikipedia.org/wiki/Chinese_postman_problem) on a graph created from OSM data. \
        It should work with both roads and trails, so a network of running or bike trails should be solvable as well.\
        Try to limit the size of the geographical area for suitable performance  '
    )
    
    
    if 'gpx_xml' not in st.session_state:
        st.session_state.gpx_xml = None
        
    if 'min_lat' not in st.session_state:
        st.session_state.min_lat = None
    
    if 'max_lat' not in st.session_state:
        st.session_state.max_lat = None
    
    if 'min_lon' not in st.session_state:
        st.session_state.min_lon = None
        
    if 'max_lon' not in st.session_state:
        st.session_state.max_lon = None
        
    if 'lat' not in st.session_state:
        st.session_state.lat = None
    
    if 'lon' not in st.session_state:
        st.session_state.lon = None
    
    if 'rad' not in st.session_state:
        st.session_state.rad = None

    
    # 1. User Input for Location
    with st.sidebar:
        option = st.selectbox("Select Input Type", ["City/State", "Point and Radius", "Bounding Box"])
    
        if option == "Bounding Box":
            st.subheader("Enter Bounding Box Coordinates")
            st.session_state.min_lat = float(st.text_input("Minimum Latitude", "40.7128"))
            st.session_state.min_lon = float(st.text_input("Minimum Longitude", "-74.0060"))
            st.session_state.max_lat = float(st.text_input("Maximum Latitude", "40.7129"))
            st.session_state.max_lon = float(st.text_input("Maximum Longitude", "-74.0059"))

            if st.button("Submit Bounding Box"):
                st.write(f"You submitted the bounding box from ({st.session_state.min_lat}, {st.session_state.min_lon}) to ({st.session_state.max_lat}, {st.session_state.max_lon})")

        elif option == "City/State":
            st.subheader("Enter City and State")
            st.session_state.city = st.text_input("City", "Big Timber")
            st.session_state.state = st.text_input("State", "MT")

        if st.button("Submit City/State"):
            st.write(f"You submitted the location: {st.session_state.city}, {st.session_state.state}")
    
        elif option == 'Point and Radius':
            st.subheader('Enter a Coordinate Pair, and Radius in Meters')
            st.session_state.lat = float(st.text_input('Latitude', '40.7128'))
            st.session_state.lon = float(st.text_input('Longitude', '-74.060'))
            st.session_state.rad = float(st.text_input('Radius', '100'))
        
            if st.button('Submit Point and Radius'):
                st.write(f"You submitted the point ({st.session_state.lat}, {st.session_state.lon}) and a radius of {st.session_state.rad}")
    
    if st.button("Find Optimal Path"):
        fetch_params = {'min_lat': st.session_state.min_lat, 'min_lon': st.session_state.min_lon, 'max_lat': st.session_state.max_lat, 'max_lon': st.session_state.max_lon, 'city': st.session_state.city, 'state': st.session_state.state, 'lat': st.session_state.lat, 'lon': st.session_state.lon, 'rad': st.session_state.rad}
        G = fetch_graph(option, **fetch_params)
        G = ox.distance.add_edge_lengths(G)
        
        fig, ax = ox.plot.plot_graph(G, show=False, close=False, edge_color='#777777', node_color='blue')
        st.pyplot(fig)
        
        eulerian_circuit = shortest(G)
        total_length = sum(G[u][v][0]['length'] for u, v in eulerian_circuit) / MILES_CONVERSION
        st.write(f"Total length of the Eulerian circuit: {total_length} miles")
        
        gpx_xml = gpx_file(G, eulerian_circuit)
        st.session_state.gpx_xml = gpx_xml
        st.download_button("Download GPX file", gpx_xml, file_name="eulerian_circuit.gpx", mime="application/gpx+xml")
        
    # Footer
    st.markdown("---")
    st.markdown("Made with :heart: by Michael Rowlands")

if __name__ == "__main__":
    main()