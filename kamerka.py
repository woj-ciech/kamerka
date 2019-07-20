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
from twitter import *
import flickrapi
import branca
from InstagramAPI import InstagramAPI
import google_streetview.api
import random
import requests
import json
from elasticsearch import Elasticsearch



desc = "              o#######o\n\
            o###########o\n\
            o#############o\n\
            #################\n\
            ######  \########o\n\
           #;^ _^,/---\#####!\n\
           ,` /^_ .-~^~-.__\#\n\
          /    ^\/,,@@@,, ;|\n\
         |      \!!@@@@@!! ^,\n\
        #.    .\; \'9@@@P\'   ^,\n\
        ###./^ ----,_^^      /@-._\n\
                      ^--._,o@@@@@@\n\
                         ^;@@@@@@@@@\n\
                           ^-;@@@@\n\
ꓘamerka 2.0 (FIST) - Build interactive map of cameras, tweets and photos\n\
medium.com/@woj-ciech github.com/woj_ciech\n\n\
python kamerka.py -h\n\
Example: python kamerka.py --lat \"37.235 --lon 115.811111\" --dark --twitter --camera --printer\n\"" \
       "python kamerka.py --country RU"

parser = argparse.ArgumentParser(
    description=desc, formatter_class=RawTextHelpFormatter)

#https://github.com/paoloo and https://github.com/42B
group = parser.add_argument_group("Required arguments") #https://github.com/woj-ciech/kamerka/pull/13


group.add_argument("--lat", help="Latitude",  default=0.0, type=float)
group.add_argument("--lon", help="Longitude", default=0.0, type=float)
parser.add_argument("--radius", help="Radius in km (Default 3)", default="3")
#group1.add_argument("--address", help="Address")
parser.add_argument("--dark", help="Dark Theme", action='store_true')
parser.add_argument("--twitter", help="Twitter module", action='store_true')
parser.add_argument("--camera", help="Camera module", action='store_true')
parser.add_argument("--flickr", help="Flickr module", action='store_true')
parser.add_argument("--instagram", help="Instagram module", action='store_true')
parser.add_argument("--printer", help="Printer module", action='store_true')
parser.add_argument("--country", help="Find Industrial Control Systems for country. Short code for country: US,IL,RU", default="")
parser.add_argument("--rtsp", help="Real Time Streaming Protocol module",action="store_true")
parser.add_argument("--mqtt", help="Message Queuing Telemetry Transport module", action="store_true")
parser.add_argument("--open", help="Show only open devices", action="store_true")
parser.add_argument('--first', help='First page', default=None, type=int)
parser.add_argument('--last', help='Last page', default=None, type=int)
parser.add_argument("--recursive", help="Recusrive mode", action="store_true")
parser.add_argument("--elasticsearch", help="Save to ElasticSearch (works only with recursive) mode", action="store_true")
parser.add_argument("--host", help="Elasticsearch host", default="localhost")
parser.add_argument("--port", help="Elasticsearch port", default="9200")


###Initialize arguments
args = parser.parse_args()
dark = args.dark
twitter = args.twitter
camera = args.camera
flickr = args.flickr
instagram = args.instagram
printer = args.printer
radius = args.radius
lat = args.lat
lon = args.lon
country = args.country
rtsp = args.rtsp
open = args.open
first = args.first
last = args.last
recursive=args.recursive
mqtt = args.mqtt
elasticsearch = args.elasticsearch
port = args.port
host = args.host

if first and last is None:
    print("Correct pages")
    sys.exit()
elif last and first is None:
    print('Correct pages')
    sys.exit()
elif first is None and last is None:
    print("Choose pages to search")
    sys.exit()
elif first > last:
    print('Correct pages')
    sys.exit()
else:
    last = last + 1

coordinates = ""

#Thanks to https://github.com/xrxz
if not country:
    if args.lat != 0.0 and args.lon != 0.0:
        coordinates = str(args.lat) + "," + str(args.lon)
    else:
        print(desc)
        print(Fore.RED + "Correct your coordinates" + Fore.RESET)
        sys.exit()

def test_connection(host, port):
    es = Elasticsearch(host=host, port=port)
    if not es.ping():
        print(Fore.RED+"Connection to Elasticsearch failed"+Fore.RESET)
        sys.exit()
    else:
        print (Fore.GREEN+"Succesfully connected to ElasticSearch"+Fore.RESET)


if not recursive and elasticsearch:
    print(Fore.RED + "Output to Elasticsearch works only with recursive mode" + Fore.RESET)
    sys.exit()
elif elasticsearch and recursive:
    test_connection(host,port)
    elastic = True


###API keys and credentials
#Shodan
SHODAN_API_KEY = ''

#Instagram
INSTAGRAM_USER = ""
INSTAGRAM_PASSWORD = ""

#Flickr
FLICKR_API_KEY = ''
FLICKR_SECRET_API_KEY = ""

#Twitter
TWITTER_ACCESS_TOKEN = ""
TWITTER_ACCESS_TOKEN_SECRET = ""
TWITTER_CONSUMER_KEY = ""
TWITTER_CONSUMER_SECRET = ""

#Google Street View
GOOGLE_STREET_VIEW_API_KEY = ""

#Change map theme
tile = "OpenStreetMap"
if dark:
    tile = "CartoDB dark_matter"

#Initialize Folium map
folium_map = folium.Map(location=[lat, lon],
                            zoom_start=2,
                            tiles=tile)
marker = folium.CircleMarker(location=[lat, lon])
marker.add_to(folium_map)
marker_cluster = MarkerCluster().add_to(folium_map)

#Instagram authentication and request
# noinspection PyShadowingNames
ics_queries = ["port:502,102,47808,44818,5094 country:",
"port:1911,4911 product:niagara country:",
"port:20000 source address country:",
'product:"general electric" country:',
"port:20547,1962 PLC country:",
"product:mitsubishi country:",
"port:9600 response code country:",
'port:789 product:"Red Lion Controls" country:',
"port:2404 asdu address country:",
"port:2455 operating system country:"]


def save_elastic(index, doc_type, body):
    es = Elasticsearch(host=host, port=port)
    # es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
    ids = []
    print (Fore.GREEN + "Saving output to Elasticsearch"+Fore.RESET)

    for i in body['data']:
        if 'ssl' in i:
            del i['ssl']['cert']['serial']

    # try:
    #
    #     if resp['hits']['hits']:
    #         for i in resp['hits']['hits']:
    #             int_id = int(i['_id'])
    #             ids.append(int_id)
    #         last_id = max(ids)
    #     else:
    #         last_id = 0

    resp = es.search(index=index)
    try:
        es.index(index=index, doc_type=doc_type, id=resp['hits']['total']+1, body=body)
    except Exception as e:
        print(Fore.RED + str(e) + Fore.RESET)

    # except Exception as e:
    #     try:
    #         print('chuj')
    #         es.index(index=index, doc_type=doc_type, id=1, body=body)
    #     except Exception as e:
    #         print(e.args)

def g_streetview(lat, lon, key):
    # Define parameters for street view api
    coo = str(lat) + "," + str(lon)
    params = [{
        'size': '640x640',  # max 640x640 pixels
        'location': coo,
        'key': key,
        'radius': '50'
    }]

    try:
        # Create a results object
        results = google_streetview.api.results(params)

        if results.metadata[0]['status'] == "ZERO_RESULTS":
            return False
        else:
            print(Fore.GREEN + "Found Street View photo for " + coo + Fore.RESET)
            return results
    except Exception as e:
        print("Error with Google Street View")
        print(e.args)
        return False

def get_host_info(ip):
    req = requests.get("https://api.shodan.io/shodan/host/"+ip+"?key="+SHODAN_API_KEY)
    req_json = json.loads(req.text)

    # with open(ip, 'w') as outfile:
    #     json.dump(req_json, outfile) ### IF you need to dump information for each host for statistics uncomment this line
    # it will create file named as IP with json data from Shodan


    results = {}

    if elastic:
        save_elastic('kamerka', 'kamerka', req_json)

    try:
        results['ports'] = req_json['ports']
        results['hostnames'] = req_json['hostnames']
    except:
        results['ports'] = []
        results['hostnames'] = []

    return results


def instagram_query(lat, lon):
    print("----------------" + Fore.MAGENTA + "Instagram" + Fore.RESET + "----------------")
    dict_to_return = {}
    limit = 4

    #Authentication
    instagram_api = InstagramAPI(INSTAGRAM_USER, INSTAGRAM_PASSWORD)
    instagram_api.login()
    if instagram_api.LastJson['status'] == "fail":
        print(Fore.RED + instagram_api.LastJson['message'] + Fore.RESET)
        return False

    #Get coordinates - https://github.com/LevPasha/Instagram-API-python/pull/492/commits/ed74ee45fb3e3abe6df7f767d3353de6fd897401
    try:
        instagram_api.geosearchLocation(lat, lon)
    except AttributeError:
        print(Fore.RED +  "Add additional method to Instagram library" + Fore.RESET)
        sys.exit()

    #Get places near given coordinates
    places_results = instagram_api.LastJson
    print("Found " + Fore.GREEN + str(len(places_results['venues'])) + Fore.RESET + ' venue(s)')
    print("Checking " + str(limit + 1) + " newest results of each venue")

    #for each place
    for venue in places_results['venues']:
        help = 0
        #Get photos for location based on ID
        instagram_api.getLocationFeed(venue['external_id'])
        coordinates = []
        coordinates.append(float(venue['lat']))
        coordinates.append(float(venue['lng']))
        info = instagram_api.LastJson
        print("Found " + Fore.GREEN + str(len(info['items'])) + Fore.RESET + " photos in " + Fore.GREEN + venue['address'] + Fore.RESET)
        for j in info['items']:
            if help > limit:
                break
            try:
                #dict = {url_to_photo : [lat,lon]}
                dict_to_return.update({j['image_versions2']['candidates'][0]['url'] : coordinates})
            except:
                pass

            help = help + 1

    return dict_to_return

#Shodan module
def shodan_query(query, device,page):
    print("----------------" + Fore.LIGHTRED_EX + 'Shodan ' + device  + Fore.RESET + "----------------")
    try:
        api = shodan.Shodan(SHODAN_API_KEY)
        result = api.search(query, page)
    except shodan.APIError as e:
        print(Fore.RED + e.value + Fore.RESET)
        return False

    ics_results = {'matches':[]}

    if len(result['matches']) > 0:
        print('Found ' + str(len(result['matches'])) + " results")

        if device == "ics":
            for match in result['matches']:
                if "tags" in match:
                    if 'ics' in match['tags']:
                        print("IP: " + Fore.GREEN + match['ip_str'] + Fore.RESET)
                        print("Coordinates: " + Fore.BLUE + str(match['location']['latitude']) + "," + Fore.BLUE + str(
                            match['location']['longitude']) + Fore.RESET)
                        ics_results['matches'].append(match)

            return ics_results

        else:
            for match in result['matches']:

                print("IP: " + Fore.GREEN + match['ip_str'] + Fore.RESET)
                print("Coordinates: " + Fore.BLUE + str(match['location']['latitude']) + "," + Fore.BLUE + str(
                    match['location']['longitude']) + Fore.RESET)

            return result
    else:
        print("Nothing was found")
        return False


#Flickr module
def flickr_query(lat, lon):
    flickr = flickrapi.FlickrAPI(FLICKR_API_KEY, FLICKR_SECRET_API_KEY)
    try:
        photo_list = flickr.photos.search(api_key=FLICKR_API_KEY, lat=lat, lon=lon, accuracy=16, format='parsed-json',per_page=100, extras='url_l,geo', has_geo=1 ,sort='newest')
    except Exception as e:
        print(Fore.RED +  e.args + Fore.RESET)
        return False

    print("----------------" + Fore.LIGHTYELLOW_EX + "Flickr" + Fore.RESET + "----------------")
    print("Found " + Fore.GREEN + photo_list['photos']['total'] + Fore.RESET + " result(s)")
    for photo in photo_list['photos']['photo']:
        try:
            print(Fore.LIGHTYELLOW_EX + photo['title'] + Fore.RESET + " in " + Fore.LIGHTYELLOW_EX + photo[
                        'latitude'] + Fore.RESET + ',' + Fore.LIGHTYELLOW_EX + photo['longitude'] + Fore.RESET)
        except TypeError:
            pass

    return photo_list['photos']['photo']

#Twitter module
def twitter_query(coordinates):
    print("----------------" + Fore.BLUE + "Twitter" + Fore.RESET + "----------------")
    twitter = Twitter(auth=OAuth(TWITTER_ACCESS_TOKEN,
                                 TWITTER_ACCESS_TOKEN_SECRET,
                                 TWITTER_CONSUMER_KEY,
                                 TWITTER_CONSUMER_SECRET))

    data = {}

    result_count = 0
    num_pages = 10
    pages = 0
    last_id = None
    while pages < num_pages:
        try:
            query = twitter.search.tweets(q="*", geocode=coordinates+','+radius+"km", count=100,
                                          include_entities=True,max_id = last_id, result_type='mixed')
            pages += 1
            print(str(pages) + " page")
            for result in query["statuses"]:
                if result["geo"] and 'media' in result['entities']:
                    data.update(
                        {str(result['entities']['media'][0]['media_url_https']): result['coordinates']['coordinates']})
                    result_count += 1
                    print("Found photo: " + Fore.BLUE + str(result['coordinates']['coordinates'][0]) + Fore.RESET + ','+ Fore.BLUE + str(result['coordinates']['coordinates'][1]) + Fore.RESET)
                if result['geo'] and 'media' not in result['entities']:
                    data.update({result['text'].encode('ascii','ignore'):result['coordinates']['coordinates']})
                    result_count += 1
                    print("Found tweet: " + Fore.BLUE + str(result['coordinates']['coordinates'][0]) + Fore.RESET + ','+ Fore.BLUE +str(result['coordinates']['coordinates'][1]) + Fore.RESET)
                last_id = result["id"]
        except TwitterHTTPError as e:
            print(e.args)
            return False

    print("Found tweets: " + str(result_count))

    return data

def draw_map(results, service, lat=None, lon=None):
    repeats = []
    coordinates = []
    first_coordinates_measure = (lat, lon)

    if service == "mqtt":
        mqtt_open_icon = "https://www.iconsdb.com/icons/preview/green/network-xxl.png"
        mqtt_closed_icon = "https://www.iconsdb.com/icons/preview/red/network-xxl.png"
        if results:
            all_ips = []

            for counter, device in enumerate(results['matches']):
                ip = device['ip_str']

                coordinates.append(device['location']['latitude'])
                coordinates.append(device['location']['longitude'])

                popup_text = ip + "<br><a href=https://shodan.io/host/" + ip + ">Lookup on Shodan</a>" + " <br> <a href=https://bgp.he.net/ip/" + ip + "#_whois> Check ownership </a><br>"

                if "Connection Code: 0" in device['data']:
                    topics = device['data'].replace("MQTT Connection Code: 0", "")
                    topics = topics.replace("Topics:","").strip()
                    topics_list = topics.split()
                    if len(topics_list) < 15:
                        popup_text = popup_text + "Topics: <br>"+ topics.replace("\n","<br>")
                    else:
                        popup_text = popup_text + "Too many topics, please check manually on Shodan"


                if recursive:
                    if ip not in all_ips:

                        print("Checking " + ip)
                        details = get_host_info(ip)
                        str1 = ','.join(details['hostnames'])
                        popup_text = popup_text + "<br> Hostnames: " + str1 + "<br> "
                        str2 = ','.join(str(e) for e in details['ports'])
                        popup_text = popup_text + "Ports: " + str2
                        all_ips.append(ip)

                popup = folium.Popup(popup_text, max_width=2137)

                #Check if device returns 200 OK, i.e. if it's open
                if "Connection Code: 0" not in device['data']:
                    shodan_icon = folium.features.CustomIcon(mqtt_closed_icon, icon_size=(35, 35))  # bug
                else:
                    shodan_icon = folium.features.CustomIcon(mqtt_open_icon, icon_size=(35, 35))  # bug

                #if there is more than one device with the same coordinates, add it to cluster
                if coordinates in repeats:
                    folium.Marker([device['location']['latitude'], device['location']['longitude']], icon=shodan_icon,
                                  popup=popup).add_to(marker_cluster)
                else:
                    folium.Marker([device['location']['latitude'], device['location']['longitude']], icon=shodan_icon,
                                  popup=popup,
                                  ).add_to(folium_map)

                repeats.append(coordinates)  # make list of lists of coordinates


    if service == "printer":
        closed_printer_icon = "https://www.iconsdb.com/icons/preview/red/printer-xxl.png"
        open_printer_icon = "https://www.iconsdb.com/icons/preview/green/printer-xxl.png"

        if results:
            all_ips = []

            for counter, printer in enumerate(results['matches']):
                ip = printer['ip_str']
                product = printer['product']

                coordinates.append(printer['location']['latitude'])
                coordinates.append(printer['location']['longitude'])

                popup_text = ip + "<br>" + product + "<br><a href=https://shodan.io/host/" + ip + ">Lookup on Shodan</a>" + " <br> <a href=https://bgp.he.net/ip/" + ip + "#_whois> Check ownership </a><br>"

                if recursive:
                    if ip not in all_ips:

                        print("Checking " + ip)
                        details = get_host_info(ip)
                        str1 = ','.join(details['hostnames'])
                        popup_text = popup_text + "<br> Hostnames: " + str1 + "<br> "
                        str2 = ','.join(str(e) for e in details['ports'])
                        popup_text = popup_text + "Ports: " + str2
                        all_ips.append(ip)

                popup = folium.Popup(popup_text, max_width=2137)

                #Check if device returns 200 OK, i.e. if it's open
                if "200 OK" not in printer['data']:
                    shodan_icon = folium.features.CustomIcon(closed_printer_icon, icon_size=(35, 35))  # bug
                else:
                    shodan_icon = folium.features.CustomIcon(open_printer_icon, icon_size=(35, 35))  # bug

                #if there is more than one device with the same coordinates, add it to cluster
                if coordinates in repeats:
                    folium.Marker([printer['location']['latitude'], printer['location']['longitude']], icon=shodan_icon,
                                  popup=popup).add_to(marker_cluster)
                else:
                    folium.Marker([printer['location']['latitude'], printer['location']['longitude']], icon=shodan_icon,
                                  popup=popup,
                                  ).add_to(folium_map)

                repeats.append(coordinates)  # make list of lists of coordinates

    if service == 'camera':
        closed_camera_icon = "https://www.iconsdb.com/icons/preview/red/security-camera-xxl.png"
        open_camera_icon = "https://www.iconsdb.com/icons/preview/green/security-camera-3-xxl.png"

        if results:
            all_ips = []
            for counter, camera in enumerate(results['matches']):
                ip = camera['ip_str']
                product = camera['product']

                coordinates.append(camera['location']['latitude'])
                coordinates.append(camera['location']['longitude'])

                # make marker red

                coordinates_measure = (camera['location']['latitude'], camera['location']['longitude'])
                distance_compare = distance.distance(first_coordinates_measure, coordinates_measure).m
                unit = "m"
                if distance_compare > 1000.0:
                    distance_compare = distance_compare / 1000
                    unit = "km"

                popup_text = ip + "<br>" + product + "<br>" + str(distance_compare)[0:5] + "" + unit + " from target" + "<br><a href=https://shodan.io/host/" + ip + ">Lookup on Shodan</a>" + " <br> <a href=https://bgp.he.net/ip/" + ip + "#_whois> Check ownership </a><br>"
                #check if camera has screenshot
                has_screenshot = 0
                if 'opts' in camera:
                    has_screenshot = 1
                    eocoded = camera['opts']['screenshot']['data']
                    html = '<img style="width:100%; height:100%;" src="data:image/jpeg;base64,{}">'.format(eocoded)
                    popup_text = popup_text + html

                if recursive:
                    if ip not in all_ips:
                        print("Checking " + ip)
                        details = get_host_info(ip)
                        str1 = ','.join(details['hostnames'])
                        popup_text = popup_text + "<br> Hostnames: " + str1 + "<br> "
                        str2 = ','.join(str(e) for e in details['ports'])
                        popup_text = popup_text + "Ports: " + str2
                        all_ips.append(ip)

                popup = folium.Popup(html=popup_text, max_width=2137)


                if "200 OK" not in camera['data']:
                    shodan_icon = folium.features.CustomIcon(closed_camera_icon, icon_size=(35, 35))  # bug
                else:
                    shodan_icon = folium.features.CustomIcon(open_camera_icon, icon_size=(35, 35))  # bug

                #Check if coordinates are repetitives and if camera has screenshot
                if coordinates in repeats and has_screenshot ==1:
                        folium.Marker([camera['location']['latitude'], camera['location']['longitude']], icon=shodan_icon, popup=popup).add_to(marker_cluster)
                elif coordinates in repeats and has_screenshot ==0:
                        folium.Marker([camera['location']['latitude'], camera['location']['longitude']],icon=shodan_icon,
                                  popup=popup,
                                  ).add_to(marker_cluster)
                elif coordinates not in repeats and has_screenshot ==1:
                    folium.Marker([camera['location']['latitude'], camera['location']['longitude']], icon=shodan_icon, popup=popup,
                                  ).add_to(folium_map)
                else:
                    folium.Marker([camera['location']['latitude'], camera['location']['longitude']], icon=shodan_icon, popup=popup).add_to(folium_map)

                    repeats.append(coordinates)  # make list of lists of coordinates

    if service == 'rtsp':
        closed_rtsp_icon = "https://www.iconsdb.com/icons/preview/red/security-camera-5-xxl.png"
        open_rtsp_icon = "https://www.iconsdb.com/icons/preview/green/security-camera-5-xxl.png"

        if results:
            all_ips = []

            for counter, camera in enumerate(results['matches']):
                ip = camera['ip_str']
                # product = camera['product']

                coordinates.append(camera['location']['latitude'])
                coordinates.append(camera['location']['longitude'])
                # make marker red

                coordinates_measure = (camera['location']['latitude'], camera['location']['longitude'])
                distance_compare = distance.distance(first_coordinates_measure, coordinates_measure).m
                unit = "m"
                if distance_compare > 1000.0:
                    distance_compare = distance_compare / 1000
                    unit = "km"

                popup_text = ip + "<br>" + str(distance_compare)[
                                                              0:5] + "" + unit + " from target" + "<br><a href=https://shodan.io/host/" + ip + ">Lookup on Shodan</a>" + " <br> <a href=https://bgp.he.net/ip/" + ip + "#_whois> Check ownership </a><br>"
                if recursive:
                    print("Checking " + ip)
                    details = get_host_info(ip)
                    str1 = ','.join(details['hostnames'])
                    popup_text = popup_text + "<br> Hostnames: " + str1 + "<br> "
                    str2 = ','.join(str(e) for e in details['ports'])
                    popup_text = popup_text + "Ports: " + str2
                    all_ips.append(ip)

                popup = folium.Popup(html=popup_text, max_width=2137)

                if "200 OK" not in camera['data']:
                    shodan_icon = folium.features.CustomIcon(closed_rtsp_icon, icon_size=(35, 35))  # bug
                else:
                    shodan_icon = folium.features.CustomIcon(open_rtsp_icon, icon_size=(35, 35))  # bug

                if coordinates in repeats:
                    folium.Marker([camera['location']['latitude'], camera['location']['longitude']], icon=shodan_icon,
                                  popup=popup).add_to(marker_cluster)
                else:
                    folium.Marker([camera['location']['latitude'], camera['location']['longitude']], icon=shodan_icon,
                                  popup=popup,
                                  ).add_to(folium_map)

                repeats.append(coordinates)

    if service == 'instagram':
        insta_icon = "http://icons-for-free.com/free-icons/png/512/2329265.png"
        for photo, coordinates in results.items():
            icon = folium.features.CustomIcon(insta_icon, icon_size=(35, 35))  # bug
            html = '<img style="width:100%; height:100%;" src="{}">'.format(str(photo))
            popup = folium.Popup(branca.element.IFrame(html=html, width=420, height=320), max_width=2137)
            if coordinates in repeats:
                folium.Marker([coordinates[0], coordinates[1]], icon=icon,
                              popup=popup).add_to(marker_cluster)
            else:
                folium.Marker([coordinates[0], coordinates[1]], icon=icon,
                              popup=popup).add_to(folium_map)

            repeats.append(coordinates)

    if service == 'flickr':
        flickr_icon = "http://www.myiconfinder.com/uploads/iconsets/f425a318030877cc09cb7832bea3e2c8.png"
        for flickr_photo in results:
            icon = folium.features.CustomIcon(flickr_icon, icon_size=(35, 35))


            str_coordinates = str(flickr_photo['latitude']) + ',' + str(flickr_photo['longitude'])
            lat =  float(flickr_photo['latitude'])
            long =  float(flickr_photo['longitude'])
            try:
                html = '<img style="width:100%; height:100%;" src="{}">'.format(flickr_photo['url_l'])
            except KeyError:
                html = ''

            popup = folium.Popup(branca.element.IFrame(html=html, width=420, height=320), max_width=2137)

            if coordinates in repeats:
                folium.Marker([lat, int], icon=icon,
                              popup=popup).add_to(marker_cluster)
            else:
                folium.Marker([lat, int], icon=icon,
                              popup=popup).add_to(folium_map)

            repeats.append(str_coordinates)


    if service == 'twitter':
        twitter_icon = "https://cdn2.iconfinder.com/data/icons/metro-uinvert-dock/256/Twitter_NEW.png"
        help = 0
        for photo, coords in results.items():
            icon = folium.features.CustomIcon(twitter_icon, icon_size=(35, 35))  # bug
            if coords in repeats:
                if photo.startswith("https://"):
                    twitter_icon_green = "https://www.iconsdb.com/icons/preview/green/twitter-xxl.png"

                    icon = folium.features.CustomIcon(twitter_icon_green, icon_size=(35, 35))  # bug
                    html = '<img style="width:100%; height:100%;" src="{}">'.format(photo)
                    popup = folium.Popup(branca.element.IFrame(html=html, width=420, height=320), max_width=2137)

                    folium.Marker([coords[1], coords[0]], icon=icon,
                                  popup=popup).add_to(marker_cluster)
                else:
                    test = folium.Html(photo, script=False)
                    popup = folium.Popup(test, max_width=2650)

                    folium.Marker([coords[1], coords[0]], icon=icon,
                                  popup=popup).add_to(marker_cluster)
            else:
                if photo.startswith("https://"):
                    twitter_icon_green = "https://www.iconsdb.com/icons/preview/green/twitter-xxl.png"

                    icon = folium.features.CustomIcon(twitter_icon_green, icon_size=(35, 35))  # bug
                    html = '<img style="width:100%; height:100%;" src="{}">'.format(photo)
                    popup = folium.Popup(branca.element.IFrame(html=html, width=420, height=320), max_width=2137)

                    folium.Marker([coords[1], coords[0]], icon=icon,
                                  popup=popup).add_to(folium_map)
                else:
                    test = folium.Html(photo, script=False)
                    popup = folium.Popup(test, max_width=2650)
                    folium.Marker([coords[1], coords[0]], icon=icon,popup=popup).add_to(folium_map)

            repeats.append(coords)
            help = help + 1

    if service == "ics":
        color = "%06x" % random.randint(0, 0xFFFFFF)
        factory_icon = "https://www.iconsdb.com/icons/download/color/"+color+"/factory-128.png"
        unique_coordinates_ics = []

        for counter, printer in enumerate(results['matches']):
            coordinates = []
            ip = printer['ip_str']
            port = printer['port']
            ports_html = ""

            coordinates.append(printer['location']['latitude'])
            coordinates.append(printer['location']['longitude'])

            additional_ports = get_host_info(ip)
            additional_ports_without_default = []

            if additional_ports:
                        for i in additional_ports:
                            if i != port:
                                additional_ports_without_default.append(i)

            if len(additional_ports_without_default) > 0:
                for i in additional_ports_without_default:
                    ports_html = ports_html + ip + ":" + str(i) + "<br>"

            streetview = g_streetview(str(printer['location']['latitude']), str(printer['location']['longitude']), GOOGLE_STREET_VIEW_API_KEY)

            if streetview:
                html = '<img style="width:100%; height:100%;" src="' + streetview.links[0] + '">'
            else:
                html = ""

            try:
                product = printer['product']
                org = printer['org']
                version = printer['version']
                popup_text = "<b>" + product + " " + version + "</b> <br>" + org + "<br>" + ip + ":" + str(
                    port) + "<br>" + ports_html + "<a href=http://maps.google.com/maps?q=&layer=c&cbll="+str(printer['location']['latitude'])+","+str(printer['location']['longitude']) +"> Go for a walk</a>" + "<br><a href=https://shodan.io/host/"+ip +">Shodan details</a>" + html

            except:
                popup_text = ip + ":" + str(
                    port) + "<br>"  + ports_html + "<a href=http://maps.google.com/maps?q=&layer=c&cbll="+str(printer['location']['latitude'])+","+str(printer['location']['longitude']) +"> Go for a walk</a>" + "<br><a href=https://shodan.io/host/"+ip +">Shodan details</a>" + html

            if "img" in html:
                popup = folium.Popup(branca.element.IFrame(html=popup_text, width=450, height=500), max_width=2137)
            else:
                popup = folium.Popup(popup_text, max_width=2137)


            shodan_icon = folium.features.CustomIcon(factory_icon, icon_size=(35, 35))  # bug

            #if there is more than one device with the same coordinates, add it to cluster
            if coordinates in repeats:
                folium.Marker([printer['location']['latitude'], printer['location']['longitude']], icon=shodan_icon,
                              popup=popup).add_to(marker_cluster)
            else:
                folium.Marker([printer['location']['latitude'], printer['location']['longitude']], icon=shodan_icon,
                              popup=popup,
                              ).add_to(folium_map)

            repeats.append(coordinates)
            # make list of lists of coordinates

        for i in repeats:
            if i not in unique_coordinates_ics:
                unique_coordinates_ics.append(i)


        return unique_coordinates_ics

if lat and lon:
    print(desc)
    try:
        geolocator = Nominatim(user_agent="Kamerka")
        location = geolocator.reverse(coordinates, language='en')
        print(Fore.GREEN + location.address + Fore.RESET)
    except:
        print(Fore.RED +  "No address was found for your coordinates" + Fore.RED)
        # sys.exit()

    string_printers = "geo:" + coordinates + "," + radius + " device:printer"
    string_cameras = "geo:" + coordinates + "," + radius + " device:webcam"
    string_rtsp = "geo:" + coordinates + ","+radius+ " port:554"
    string_mqtt = "geo:"+coordinates+","+radius+ " product:mqtt"


    if open:
        string_rtsp = string_rtsp + " 200 ok"
        string_cameras = string_cameras + " 200 ok"
        string_printers = string_printers + " 200 ok"
        string_mqtt = string_mqtt + " 0"

    if twitter:
        twitter_results = twitter_query(coordinates)
        if twitter_results:
            draw_map(twitter_results, 'twitter',lat, lon )

    if flickr:
        flickr_results = flickr_query(lat, lon)
        if flickr_results:
            draw_map(flickr_results, 'flickr',lat, lon, )

    if camera:
        for page in range(first, last):
            cameras_results = shodan_query(string_cameras, 'camera',page)
            if cameras_results:
                draw_map(cameras_results, "camera",lat, lon )

    if printer:
        for page in range(first, last):
            printers_results = shodan_query(string_printers, 'printer',page)
            if printers_results:
                draw_map(printers_results, 'printer',lat, lon)

    if instagram:
        insta_results = instagram_query(lat, lon)
        if insta_results:
            draw_map(insta_results, 'instagram', lat, lon)

    if rtsp:
        for page in range(first, last):
            rtsp_results = shodan_query(string_rtsp, "rtsp",page)
            if rtsp_results:
                draw_map(rtsp_results,"rtsp",lat,lon)

    if mqtt:
        for page in range(first, last):
            mqtt_results = shodan_query(string_mqtt, "mqtt", page)
            if mqtt_results:
                draw_map(mqtt_results,'mqtt',page)

    print("Saving map as " + str(coordinates) + '.html')
    folium_map.save(str(coordinates) + ".html")

    sys.exit()


if country:
    for ics_query in ics_queries:
        shodan_ics_results = shodan_query(ics_query+country, "ics")
        if shodan_ics_results:
            ics_coordinates = draw_map(shodan_ics_results, "ics")

    print("Saving map as " + country + '.html')
    folium_map.save(country + ".html")

    sys.exit()


else:
    print(desc)
    sys.exit()
