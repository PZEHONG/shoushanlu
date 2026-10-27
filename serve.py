from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
from pathlib import Path
SimpleHTTPRequestHandler.extensions_map.update({'.js':'text/javascript','.json':'application/json','.css':'text/css'})
print('Preview: http://127.0.0.1:8768',flush=True)
ThreadingHTTPServer(('127.0.0.1',8768),partial(SimpleHTTPRequestHandler,directory=str(Path(__file__).parent/'dist'))).serve_forever()
