from playwright.sync_api import sync_playwright
from pathlib import Path
import json
out=Path(__file__).parent/'checks';out.mkdir(exist_ok=True)
with sync_playwright() as p:
    browser=p.chromium.launch(channel='msedge',headless=True,timeout=20000,args=['--enable-webgl','--ignore-gpu-blocklist'])
    page=browser.new_page(viewport={'width':1440,'height':960},device_scale_factor=1)
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto('http://127.0.0.1:8768',wait_until='networkidle')
    page.wait_for_selector('body[data-ready="true"]',timeout=20000)
    page.screenshot(path=str(out/'globe.png'))
    page.click('#enter');page.wait_for_timeout(1700)
    assert page.evaluate('window.__atlas.mode')=='terrain'
    page.screenshot(path=str(out/'terrain.png'))
    page.click('#play');page.wait_for_timeout(1500);page.click('#play')
    assert page.evaluate('window.__atlas.progress')>0
    page.locator('#progress').fill('650');page.locator('#progress').dispatch_event('input')
    assert abs(page.evaluate('window.__atlas.progress')-.65)<.001
    page.click('#save');assert page.locator('#count').inner_text()=='1'
    page.reload(wait_until='networkidle');page.wait_for_selector('body[data-ready="true"]')
    assert page.locator('#count').inner_text()=='1'
    page.click('#save');page.click('#collection');assert page.locator('#empty').is_visible()
    page.click('#explore');assert page.locator('#routeCard').is_visible()
    page.set_viewport_size({'width':390,'height':844});page.click('#terrainBtn');page.wait_for_timeout(500)
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    page.screenshot(path=str(out/'mobile.png'),full_page=True)
    assert not errors,errors
    print(json.dumps({'ok':True,'errors':errors,'checks':['globe','terrain','playback','scrub','collection persistence','empty collection','mobile width'],'data':page.evaluate('({...window.__atlas})')},ensure_ascii=False))
    browser.close()
