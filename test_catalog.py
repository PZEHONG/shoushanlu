import json,unittest,math
from pathlib import Path
root=Path(__file__).parent/'dist'
class CatalogTest(unittest.TestCase):
 def test_all_regions_have_real_terrain_and_honest_tracks(self):
  cat=json.loads((root/'catalog.json').read_text(encoding='utf-8'))
  self.assertEqual(len(cat),11)
  self.assertEqual(len({r['id'] for r in cat}),11)
  for r in cat:
   t=json.loads((root/r['terrainUrl']).read_text(encoding='utf-8'))
   self.assertEqual(len(t['heights']),t['n']**2)
   self.assertTrue(all(math.isfinite(h) and -500<h<9000 for h in t['heights']))
   w,s,e,n=t['bounds'];self.assertTrue(w<r['center'][0]<e and s<r['center'][1]<n)
   self.assertTrue(r['sourceUrl'].startswith('https://'))
   if r['trackStatus']=='pending':self.assertIsNone(r['routeUrl'])
   else:
    route=json.loads((root/r['routeUrl']).read_text(encoding='utf-8'))
    self.assertGreater(len(route['points']),100)
    self.assertEqual(len(route['points']),len(route['distances']))
    self.assertTrue(all(a<=b for a,b in zip(route['distances'],route['distances'][1:])))
    self.assertTrue(all(w<=p[0]<=e and s<=p[1]<=n for p in route['points']))
if __name__=='__main__':unittest.main()
