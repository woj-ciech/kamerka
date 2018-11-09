# ꓘamerka
*Build interactive map of cameras from Shodan.*  
Based on your address or coordinates, script creates map of Shodan cameras in neighborhood.
https://medium.com/@woj_ciech/%EA%93%98amerka-build-interactive-map-of-cameras-from-shodan-a0267849ec0a
# Requirements
- Shodan  
- Geopy  
- Foilum  
- Colorama  

```pip install -r requirements.txt```   
**Change API_KEY in line 14**
# Restrictions
It can be used only with paid Shodan plan.
Build with Python 2
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
Do not test device that you don't own.
