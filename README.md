# ꓘamerka 2.0 aka FIST (Flickr, Instagram, Shodan, Twitter)
*Build interactive map of cameras, printers, tweets and photos.* 

The script creates a map of cameras, printers, tweets and photos based on your coordinates. Everything is clearly presented in form of interactive map with icons and popups.

Detailed write-up
https://medium.com/@woj_ciech/hunting-with-%EA%93%98amerka-2-0-aka-fist-flickr-instagram-shodan-twitter-ca363f12562a

Previous version https://medium.com/@woj_ciech/%EA%93%98amerka-build-interactive-map-of-cameras-from-shodan-a0267849ec0a

# Requirements
- Written with :heartpulse: in Python 2
- Shodan + paid subscription 
- Geopy  
- Foilum  
- Colorama
- InstagramAPI (https://github.com/LevPasha/Instagram-API-python) - Credentials instead of api keys
- Twitter
- flickrapi
- Branca

```pip install -r requirements.txt```
   
**Put your API keys in lines 85-99**

To use Instagram module, you have to add additional method to InstagramAPI.py file.
```
def geosearchLocation(self, lat, lon):
        return self.SendRequest('location_search/?latitude=' + str(lat)+'&longitude='+str(lon)+'&rank_token=' + self.rank_token)
```

More details here --> https://github.com/LevPasha/Instagram-API-python/pull/492/commits/ed74ee45fb3e3abe6df7f767d3353de6fd897401

https://github.com/LevPasha/Instagram-API-python/pull/492
		

# Usage
```
root@kali:~/# python kamerka.py -h
Fail to import moviepy. Need only for Video upload.
usage: kamerka.py [-h] [--lat LAT] [--lon LON] [--radius RADIUS] [--dark]
             [--twitter] [--camera] [--flickr] [--instagram] [--printer]

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
medium.com/@woj_ciech github.com/woj-ciech

python kamerka.py -h
Example: python kamerka.py --lat 37.235 --lon 115.811111 --dark --twitter --camera --printer

optional arguments:
  -h, --help       show this help message and exit
  --radius RADIUS  Radius in km (Default 3)
  --dark           Dark Theme
  --twitter        Twitter module
  --camera         Camera module
  --flickr         Flickr module
  --instagram      Instagram module
  --printer        Printer module

Required arguments:
  --lat LAT        Latitude
  --lon LON        Longitude

```   

```
root@kali:~/#python kamerka.py --lat 37.8368723 --lon -122.2645793 --camera --flickr --instagram --twitter --printer
```

![](https://i.imgur.com/OXFMYhc.png)

Dark mode
![](https://i.imgur.com/sdCkcfa.png)


# Other
Do not test on devices you don't own.


Thanks to [@xrxz](https://github.com/xrxz) - you were right with coordinates

[@42B](https://github.com/42B) and [@paoloo](https://github.com/paoloo)
