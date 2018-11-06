#!/usr/bin/env python
# -*- coding: utf-8 -*-

import folium
import shodan
from folium.plugins import MarkerCluster
import argparse
from geopy.geocoders import Nominatim
from colorama import Fore
import sys
from geopy import distance
from argparse import RawTextHelpFormatter

API_KEY = 'CHANGE_ME'

desc = """              o#######o
            o###########o
            o#############o
            #################
            ######  \########o
           #;^ _^,/---\#####!
           ,` /^_ .-~^~-.__\#
          /    ^\/,,@@@,, ;|
         |      \!!@@@@@!! ^,
        #.    .\; \'9@@@P\'   ^,
        ###./^ ----,_^^      /@-._
                      ^--._,o@@@@@@
                         ^;@@@@@@@@@
                           ^-;@@@@
    ꓘamemrka - Build interactive map of cameras from Shodan
    medium.com/@woj-ciech github.com/woj_ciech\n
    Example: kamerka.py --address "FSB, Russia"
             kamerka.py --coordinates "37.235,-115.811111" --dark"""

parser = argparse.ArgumentParser(
    description=desc, formatter_class=RawTextHelpFormatter)

parser.add_argument("--coordinates", help="Coordinates",
                    default="")
parser.add_argument("--radius", help="Radius in km (Default 3)", default="3")
parser.add_argument("--address", help="Address")
parser.add_argument("--dark", help="Dark Theme", action='store_true')

args = parser.parse_args()
dark = args.dark
coordinates = args.coordinates
address = args.address

radius = args.radius

def shodan_query(query):
    api = shodan.Shodan(API_KEY)

    try:
        result = api.search(query)
    except shodan.APIError as e:
        print e.message
        sys.exit()

    if len(result['matches']) > 0:
        print 'Found ' + str(len(result['matches'])) + " results"
    else:
        print "Nothing was found"
        sys.exit()

    return result


def draw_map(results, first_coordinates, filename):
    tile = "OpenStreetMap"
    if dark:
        tile = "CartoDB dark_matter"

    repeats = []

    folium_map = folium.Map(location=[first_coordinates[0], first_coordinates[1]],
                            zoom_start=13,
                            tiles=tile)
    marker = folium.CircleMarker(location=[first_coordinates[0], first_coordinates[1]])
    marker.add_to(folium_map)
    marker_cluster = MarkerCluster().add_to(folium_map)
    coordinates = []
    first_coordinates_measure = (first_coordinates[0], first_coordinates[1])

    for counter, camera in enumerate(results['matches']):
        ip = camera['ip_str']
        product = camera['product']

        coordinates.append(camera['location']['latitude'])
        coordinates.append(camera['location']['longitude'])

        # make marker red
        if "200 OK" not in camera['data']:
            color = "red"
        else:
            color = "green"

        print "IP: " + Fore.GREEN + ip + Fore.RESET
        print "Coordinates: " + Fore.BLUE + str(camera['location']['latitude']) + "," + Fore.BLUE + str(
            camera['location']['longitude']) + Fore.RESET
        print "-----------------------------------"
        coordinates_measure = (camera['location']['latitude'], camera['location']['longitude'])
        distance_compare = distance.distance(first_coordinates_measure, coordinates_measure).m
        unit = "m"
        if distance_compare > 1000.0:
            distance_compare = distance_compare / 1000
            unit = "km"

        if coordinates in repeats:
            folium.Marker([camera['location']['latitude'], camera['location']['longitude']], popup=ip + "<br>" + product + "<br>" + str(distance_compare)[0:5] + "" + unit + " from target",icon=folium.Icon(color=color)).add_to(marker_cluster)
        else:
            folium.Marker([camera['location']['latitude'], camera['location']['longitude']], popup=ip + "<br>" + product + "<br>" + str(distance_compare)[0:5] + unit + " from target",icon=folium.Icon(color=color)).add_to(folium_map)

        repeats.append(coordinates)  # make list of lists of coordinates
        coordinates = []

    print "Saving map as " + filename + '.html'
    folium_map.save(filename + ".html")


if coordinates:
    print desc
    geolocator = Nominatim(user_agent="Kamerka")
    try:
        location = geolocator.reverse(coordinates, language='en')
        if location.address is None:
            print "Nothing was found"
            sys.exit()
    except:
        print "No address was found"
        sys.exit()

    print location.address

    query_cameras = "geo:" + coordinates + "," + radius + " device:webcam"

    split_coordinates = coordinates.split(',')
    converted_coordinates = [float(i) for i in split_coordinates]
    cameras = shodan_query(query_cameras)
    draw_map(cameras, converted_coordinates, coordinates)
    sys.exit()
if address:
    print desc
    geolocator = Nominatim(user_agent="test")
    location = geolocator.geocode(address)
    try:
        print location.address
    except Exception as e:
        print "Nothing was found, correct your address"
        sys.exit()

    coordinates = [location.latitude, location.longitude]
    query_cameras = "geo:" + str(location.latitude) + "," + str(location.longitude) + "," + radius + " device:webcam"
    cameras = shodan_query(query_cameras)
    draw_map(cameras, coordinates, address)
