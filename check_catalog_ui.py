from playwright.sync_api import sync_playwright
from pathlib import Path
import json
root=Path(__file__).parent;out=root/'checks';out.mkdir(exist_ok=True)
catalog=json.loads((root/'dist/catalog.json').read_text(encoding='utf-8'))
with sync_playwright() as p:
 browser=p.chromium.launch(channel='msedge',headless=True,timeout=20000)
 page=browser.new_page(viewport={'width':1440,'height':960},device_scale_factor=1)
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto('http://127.0.0.1:8768',wait_until='networkidle')
 page.wait_for_selector('body[data-ready="true"]')
 assert page.locator('.catalog-card').count()==11
 assert page.locator('.globe-dot').count()==11
 page.evaluate("localStorage.setItem('shoushanlu:wugong','1')")
 page.reload(wait_until='networkidle');page.wait_for_selector('body[data-ready="true"]')
 assert page.locator('#count').inner_text()=='1'
 page.click('#topFilter');assert page.locator('.catalog-card').count()==10
 page.fill('#search','新疆');assert page.locator('.catalog-card').count()==2
 page.fill('#search','不存在的山');assert page.locator('#empty').is_visible()
 page.fill('#search','');page.click('#allFilter')
 for r in catalog:
  page.locator('[data-route="'+r['id']+'"] button').count() # selector remains harmless for body attribute
  page.locator('button.catalog-card[data-route="'+r['id']+'"]').click()
  page.wait_for_selector('body[data-ready="true"][data-route="'+r['id']+'"]')
  assert page.locator('#detailName').inner_text()==r['name']
  if r['trackStatus']=='pending':
   assert page.locator('#pendingPanel').is_visible()
   assert not page.locator('#profilePanel').is_visible()
   assert page.evaluate('window.__atlas.routePoints')==0
   assert page.evaluate('window.__atlas.routeKm') is None
   assert page.locator('#distance').inner_text()=='待补'
  else:
   assert page.locator('#profilePanel').is_visible()
   page.click('#play');page.wait_for_timeout(350);page.click('#play')
   assert page.evaluate('window.__atlas.progress')>0
  print('checked',r['id'],flush=True)
  if r['id']=='gongga':page.screenshot(path=str(out/'catalog-gongga.png'))
 page.click('#save');assert page.locator('#count').inner_text()=='2'
 page.reload(wait_until='networkidle');page.wait_for_selector('body[data-ready="true"]')
 assert page.evaluate('window.__atlas.routeId')=='tengger'
 assert page.locator('#count').inner_text()=='2'
 page.click('#collection');assert page.locator('.catalog-card').count()==2
 page.click('#save');assert page.locator('.catalog-card').count()==1
 page.click('#explore')
 # Last selection must win even when resources complete out of order.
 page.evaluate("Promise.all([window.__atlas.selectRoute('motuo','terrain'),window.__atlas.selectRoute('wugong','terrain'),window.__atlas.selectRoute('kailash','terrain')])")
 assert page.evaluate('window.__atlas.routeId')=='kailash'
 assert page.locator('#detailName').inner_text()=='冈仁波齐'
 assert page.locator('#pendingPanel').is_visible()
 page.click('#globeBtn');page.screenshot(path=str(out/'catalog-globe.png'))
 page.set_viewport_size({'width':390,'height':844})
 page.locator('button.catalog-card[data-route="gongga"]').click()
 page.wait_for_selector('body[data-ready="true"][data-route="gongga"]')
 assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
 page.screenshot(path=str(out/'catalog-mobile.png'),full_page=True)
 assert not errors,errors
 print(json.dumps({'passed':True,'routes':len(catalog),'errors':errors,'checks':['all terrains','honest pending state','search','filters','collection migration','independent collection','persistence','last selection wins','mobile']},ensure_ascii=False))
 browser.close()
