from pathlib import Path
import json,math,io,time,requests,concurrent.futures
from PIL import Image
ROOT=Path(__file__).parent;OUT=ROOT/'dist';CACHE=ROOT/'checks'/'dem-cache';CACHE.mkdir(parents=True,exist_ok=True)
SOURCE='https://paper.xinmin.cn/html/xmzk/2025-11-17/56/42043.html'
# Representative viewing regions, never route geometries or trailheads.
rows=[
('motuo','墨脱','西藏 · 林芝','MEDOG','派墨古道区域','雪山 / 深谷 / 森林',[95.02,29.43],[94.8,29.2,95.3,29.65],'雪山与峡谷相接，地形沿山谷层层下降。','https://www.columbiasports.cn/campaign/gonglue/motuo.pdf'),
('kailash','冈仁波齐','西藏 · 阿里','MOUNT KAILASH','转山线','雪峰 / 高原',[81.3125,31.06667],[81.20,30.93,81.43,31.19],'围绕冈底斯山中的雪峰，观察高原谷地与山脊。','https://zh.wikipedia.org/wiki/冈仁波齐峰'),
('tiger','虎跳峡','云南 · 迪庆','TIGER LEAPING GORGE','高路线','峡谷 / 雪山',[100.13,27.22],[100.04,27.14,100.23,27.31],'金沙江切开群山，峡谷两侧山体相向而立。','https://tubudili.com/en/tiger-leaping-gorge-high-trail/'),
('yubeng','雨崩','云南 · 迪庆','YUBENG','雨崩徒步','雪山 / 森林',[98.79,28.40],[98.69,28.31,98.89,28.50],'在梅里雪山东麓，辨认村落周围的山谷起伏。','https://tubudili.com/zh/yubeng-shenpu-oneway/'),
('taihang','南太行','河南 · 新乡','SOUTH TAIHANG','南太行徒步','崖壁 / 峡谷',[113.62,35.74],[113.48,35.60,113.78,35.86],'山地与平原在这里交会，沟壑勾勒出太行的轮廓。','https://www.earthol.com/view-10277.html'),
('changchuanbi','长穿毕','四川 · 阿坝','CHANGPING TO BIPENG','长坪沟—毕棚沟','山谷 / 垭口 / 雪峰',[102.86,31.14],[102.75,30.99,103.01,31.29],'长坪沟与毕棚沟之间，山谷被高高的山脊分隔。','https://en-gb.topographic-map.com/map-hswnmt/长坪沟/'),
('gongga','贡嘎','四川 · 甘孜','GONGGA MOUNTAINS','贡嘎大环线','雪峰 / 冰川 / 峡谷',[101.87889,29.59521],[101.66,29.40,102.04,29.84],'横断山脉的高差，在密集的山峰和谷地间展开。','https://www.fnrrc.com/ziranbaohuqujianjie/9804.html'),
('kalajun','喀拉峻','新疆 · 伊犁','KALAJUN','草原徒步','草原 / 河谷',[82.15,43.0765],[81.99,42.96,82.31,43.20],'由天山向河谷延伸的山坡，承接开阔草原。','https://www.bbkz.com/forum/map.php?discover=&gid=14483&gtype=spot'),
('wusun','乌孙古道','新疆 · 伊犁 / 阿克苏','WUSUN ANCIENT TRAIL','天山穿越','雪岭 / 湖泊 / 山谷',[82.385,42.58],[82.10,42.35,82.55,42.95],'以天堂湖附近为中心，查看天山南北的山地格局。','https://zh.wikipedia.org/wiki/乌孙古道'),
('tengger','腾格里','内蒙古 · 阿拉善','TENGGER DESERT','五湖连穿','沙漠 / 湖盆',[105.30,38.50],[105.12,38.32,105.48,38.68],'沙海与湖盆交错，地形起伏比高山更加平缓。','https://zh.wikipedia.org/wiki/腾格里沙漠')]
catalog=[{'id':'wugong','name':'武功山','region':'江西 · 萍乡 / 宜春 / 吉安','english':'WUGONG MOUNTAINS','variant':'反穿线','tags':'高山草甸 / 山脊穿越','center':[114.19,27.49],'description':'将连绵的草甸收进眼底，把脚步留在山脊线上。','trackStatus':'verified','routeUrl':'route.json','terrainUrl':'terrain.json','sourceUrl':'https://www.2bulu.com/','geoSourceUrl':'https://www.2bulu.com/','scope':'导入轨迹周边','isTopTen':False}]
def tile(lon,lat,z):return (lon+180)/360*2**z,(1-math.asinh(math.tan(math.radians(lat)))/math.pi)/2*2**z
def download(key):
 z,x,y=key;f=CACHE/f'{z}-{x}-{y}.png'
 if not f.exists():
  s=requests.Session();s.trust_env=False
  for attempt in range(3):
   try:
    r=s.get(f'https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png',timeout=25);r.raise_for_status();Image.open(io.BytesIO(r.content)).verify();f.write_bytes(r.content);break
   except Exception:
    if attempt==2:raise
    time.sleep(1)
 return key,Image.open(f).convert('RGB')
def build(row):
 ident,name,region,english,variant,tags,center,bounds,description,geoSource=row
 w,s,e,n=bounds;z=11;xa,ya=tile(w,n,z);xb,yb=tile(e,s,z)
 keys=[(z,x,y) for y in range(int(ya),int(yb)+1) for x in range(int(xa),int(xb)+1)]
 with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:tiles=dict(pool.map(download,keys))
 def height(lon,lat):
  x,y=tile(lon,lat,z);r,g,b=tiles[(z,int(x),int(y))].getpixel((min(255,int(x%1*256)),min(255,int(y%1*256))))
  return round(r*256+g+b/256-32768,1)
 size=193;heights=[height(w+(e-w)*x/(size-1),n-(n-s)*y/(size-1)) for y in range(size) for x in range(size)]
 folder=OUT/'terrains';folder.mkdir(exist_ok=True)
 (folder/f'{ident}.json').write_text(json.dumps({'n':size,'bounds':bounds,'heights':heights,'source':'Mapzen / AWS Terrain Tiles','zoom':z,'accessed':'2026-10-27'},separators=(',',':')),encoding='utf-8')
 record={'id':ident,'name':name,'region':region,'english':english,'variant':variant,'tags':tags,'center':center,'description':description,'trackStatus':'pending','routeUrl':None,'terrainUrl':f'terrains/{ident}.json','sourceUrl':SOURCE,'geoSourceUrl':geoSource,'scope':'代表区域地形，非完整线路范围','isTopTen':True}
 catalog.append(record);print(f'{ident}: {len(keys)} tiles, {min(heights)}..{max(heights)} m',flush=True)
for row in rows:build(row)
(OUT/'catalog.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2),encoding='utf-8')
print('Catalog: 11 entries / 1 verified track / 10 pending',flush=True)
