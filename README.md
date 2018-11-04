# ꓘamerka
*Build interactive map of cameras from Shodan.*  
Based on your address or coordinates, script creates map of Shodan cameras in neighborhood.
# Requirements
- Shodan  
- Geopy  
- Foilum  
- Colorama  

```pip -r install requirements```   
**Change API_KEY in line 14**

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
