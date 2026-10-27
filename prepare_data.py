from pathlib import Path
import xml.etree.ElementTree as ET
import math,json,requests,io,concurrent.futures
from PIL import Image
session=requests.Session()
session.trust_env=False

ROOT=Path(__file__).parent; OUT=ROOT/'dist'; (OUT/'vendor').mkdir(exist_ok=True)
tree=ET.parse(r'D:\轨迹\武功山反穿.kml')
ns={'k':'http://www.opengis.net/kml/2.2','gx':'http://www.google.com/kml/ext/2.2'}
pts=[list(map(float,e.text.split())) for e in tree.findall('.//gx:coord',ns)]
assert len(pts)>100
def distance(a,b):
    x1,y1,x2,y2=map(math.radians,[a[0],a[1],b[0],b[1]])
    return 6371000*2*math.asin(min(1,math.sqrt(math.sin((y2-y1)/2)**2+math.cos(y1)*math.cos(y2)*math.sin((x2-x1)/2)**2)))
d=[0]
for a,b in zip(pts,pts[1:]): d.append(d[-1]+distance(a,b))
west=min(p[0] for p in pts)-.035; east=max(p[0] for p in pts)+.035
south=min(p[1] for p in pts)-.035; north=max(p[1] for p in pts)+.035
z=12
def tile(lon,lat):
    return (lon+180)/360*2**z,(1-math.asinh(math.tan(math.radians(lat)))/math.pi)/2*2**z
xa,ya=tile(west,north); xb,yb=tile(east,south)
tiles={}
def fetch(t):
    x,y=t; url=f'https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png'
    r=session.get(url,timeout=45);r.raise_for_status()
    return t,Image.open(io.BytesIO(r.content)).convert('RGB')
keys=[(x,y) for y in range(int(ya),int(yb)+1) for x in range(int(xa),int(xb)+1)]
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
    for k,im in pool.map(fetch,keys): tiles[k]=im
def elev(lon,lat):
    x,y=tile(lon,lat);r,g,b=tiles[(int(x),int(y))].getpixel((min(255,int(x%1*256)),min(255,int(y%1*256))))
    return round(r*256+g+b/256-32768,1)
n=257
heights=[elev(west+(east-west)*x/(n-1),north-(north-south)*y/(n-1)) for y in range(n) for x in range(n)]
terrain={'n':n,'bounds':[west,south,east,north],'heights':heights,'source':'Mapzen / AWS Terrain Tiles (SRTM)','zoom':z}
(OUT/'terrain.json').write_text(json.dumps(terrain,separators=(',',':')),encoding='utf-8')
landmarks=[]
for pm in tree.findall('.//k:Placemark',ns):
    e=pm.find('k:Point/k:coordinates',ns); name=pm.find('k:name',ns)
    if e is not None and name is not None: landmarks.append({'name':name.text,'coord':list(map(float,e.text.split(',')))})
route={'name':'武功山反穿','points':pts,'distances':d,'length':round(d[-1]),'maxAltitude':round(max(p[2] for p in pts)),'minAltitude':round(min(p[2] for p in pts)),'landmarks':landmarks,'source':'本地 武功山反穿.kml · 两步路导出','author':'微风同好'}
(OUT/'route.json').write_text(json.dumps(route,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
assets={
'vendor/three.module.js':'https://cdn.jsdelivr.net/npm/three@0.170.0/build/three.module.js',
'vendor/OrbitControls.js':'https://cdn.jsdelivr.net/npm/three@0.170.0/examples/jsm/controls/OrbitControls.js',
'vendor/THREE-LICENSE.txt':'https://cdn.jsdelivr.net/npm/three@0.170.0/LICENSE',
'earth.jpg':'https://raw.githubusercontent.com/mrdoob/three.js/dev/examples/textures/planets/earth_atmos_2048.jpg'}
def asset(pair):
    name,url=pair;r=session.get(url,timeout=60);r.raise_for_status();(OUT/name).write_bytes(r.content);return name
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool: print(list(pool.map(asset,assets.items())))
print(json.dumps({'points':len(pts),'km':d[-1]/1000,'bounds':terrain['bounds'],'elevation':[min(heights),max(heights)],'landmarks':landmarks},ensure_ascii=False))
