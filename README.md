# ꓘamerka 2.0 aka FIST (Flickr, Instagram, Shodan, Twitter)
*Build interactive map of cameras, printers, tweets and photos.* 

The script creates a map of cameras, printers, tweets and photos based on your coordinates. Everything is clearly presented in form of interactive map with icons and popups.

Detailed write-up
https://medium.com/@woj_ciech/hunting-with-%EA%93%98amerka-2-0-aka-fist-flickr-instagram-shodan-twitter-ca363f12562a

Previous version https://medium.com/@woj_ciech/%EA%93%98amerka-build-interactive-map-of-cameras-from-shodan-a0267849ec0a

# v4 update
Added RTSP (Real-Time Streaming Protocol)
 ![](https://i.imgur.com/diuLuHd.jpg)
 
 MQTT (Message Queue Telemetry Transport).
![](https://i.imgur.com/LAscLR2.jpg)

Elasticsearch output
![](https://i.imgur.com/ZuHhbf4.jpg)

Additional:
- recursive mode (check each host for open ports and more information)
- "Check ownership" link on map which redirects to bgp.he.net for detailed information about IP
- "Lookup on Shodan" takes you to Shodan details about host

# v3 update
Visualize Industrial Control Systems of any country.  
Use *--country* flag and pass short code for your country.  
To use Street View add your API key in line 109


```
root@kali:~/# python kamerka.py --country PL
```

![](https://i.imgur.com/IYIcd22.jpg)

```
root@kali:~/# python kamerka.py --country CH
```

![](https://i.imgur.com/yq9yNpv.jpg)


# Requirements
- Written with :heartpulse: in Python 3
- Shodan + paid subscription 
- Geopy  
- Foilum  
- Colorama
- InstagramAPI (https://github.com/LevPasha/Instagram-API-python) - Credentials instead of api keys
- Twitter
- flickrapi
- Branca
- Google Street View API
- Elasticsearch

```pip install -r requirements.txt```
   
**Put your API keys in code**

To use Instagram module, you have to add additional method to InstagramAPI.py file.
```
def geosearchLocation(self, lat, lon):
        return self.SendRequest('location_search/?latitude=' + str(lat)+'&longitude='+str(lon)+'&rank_token=' + self.rank_token)
```

More details here --> https://github.com/LevPasha/Instagram-API-python/pull/492/commits/ed74ee45fb3e3abe6df7f767d3353de6fd897401

https://github.com/LevPasha/Instagram-API-python/pull/492
		

# Usage
```
(venv) root@kali:~/PycharmProjects/kamerka# python kamerka.py -h
usage: kamerka.py [-h] [--lat LAT] [--lon LON] [--radius RADIUS] [--dark]
                  [--twitter] [--camera] [--flickr] [--instagram] [--printer]
                  [--country COUNTRY] [--rtsp] [--mqtt] [--open]
                  [--first FIRST] [--last LAST] [--recursive]
                  [--elasticsearch] [--host HOST] [--port PORT]

              o#######o
            o###########o
            o#############o
            #################
            ######  \########o
           #;^ _^,/---\#####!
           ,` /^_ .-~^~-.__\#
          /    ^\/,,@@@,, ;|
         |      \!!@@@@@!! ^,
        #.    .\; '9@@@P'   ^,
        ###./^ ----,_^^      /@-._
                      ^--._,o@@@@@@
                         ^;@@@@@@@@@
                           ^-;@@@@
ꓘamerka 2.0 (FIST) - Build interactive map of cameras, tweets and photos
medium.com/@woj-ciech github.com/woj_ciech

python kamerka.py -h
Example: python kamerka.py --lat "37.235 --lon 115.811111" --dark --twitter --camera --printer
"python kamerka.py --country RU

optional arguments:
  -h, --help         show this help message and exit
  --radius RADIUS    Radius in km (Default 3)
  --dark             Dark Theme
  --twitter          Twitter module
  --camera           Camera module
  --flickr           Flickr module
  --instagram        Instagram module
  --printer          Printer module
  --country COUNTRY  Find Industrial Control Systems for country. Short code for country: US,IL,RU
  --rtsp             Real Time Streaming Protocol module
  --mqtt             Message Queuing Telemetry Transport module
  --open             Show only open devices
  --first FIRST      First page
  --last LAST        Last page
  --recursive        Recursive mode
  --elasticsearch    Save to ElasticSearch (works only with recursive) mode
  --host HOST        Elasticsearch host
  --port PORT        Elasticsearch port

Required arguments:
  --lat LAT          Latitude
  --lon LON          Longitude

```   

```
root@kali:~/#python kamerka.py --lat 37.8368723 --lon -122.2645793 --camera --flickr --instagram --twitter --printer --first 1 --last 1
```

![](https://i.imgur.com/OXFMYhc.png)

Dark mode
![](https://i.imgur.com/sdCkcfa.png)


# Other
Do not test on devices you don't own.


Thanks to [@xrxz](https://github.com/xrxz) - you were right with coordinates

[@42B](https://github.com/42B) and [@paoloo](https://github.com/paoloo)
