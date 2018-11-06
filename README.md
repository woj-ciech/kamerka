# ꓘamerka
*Build an interactive map of cameras from Shodan.*  
The script creates a map of Shodan cameras based on your address or coordinates.
https://medium.com/@woj_ciech/%EA%93%98amerka-build-interactive-map-of-cameras-from-shodan-a0267849ec0a
# Requirements
- Shodan  
- Geopy  
- Foilum  
- Colorama  

```pip -r install requirements```   
**Change API_KEY in line 14**
# Restrictions
It can be used only with a paid Shodan plan.
Build with Python 2.
# Usage
```
root@kali: kamerka.py --address "White House"

White House, 1600, Pennsylvania Avenue Northwest, Golden Triangle, Washington, D.C., 20500, USA
Found 81 results
IP: xxx.xxx.xxx.xxx
Coordinates: 38.xxx,-77.xxx
-----------------------------------
IP: xxx.xxx.xxx.xxx
Coordinates: 38.xxx,-77.xxx
-----------------------------------
IP: xxx.xxx.xxx.xxx
Coordinates: 38.xxx,-77.xxx
-----------------------------------
...
-----------------------------------
IP: xxx.xxx.xxx.xxx
Coordinates: 38.xxx,-77.xxx
-----------------------------------
Saving map as White House.html
```   

![](https://i.imgur.com/6SHjUdI.png)

```kamerka.py --coordinates "x.y,x.y" --dark --radius 4```
![](https://i.imgur.com/CQrsGMp.png)


# Other
Do not test on devices you don't own.
