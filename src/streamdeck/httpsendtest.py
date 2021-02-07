import requests
files = {'image_source': open(
    '/home/daniel/IoTSec_Projekt/streamdeck/src/assets/Released.png', 'rb')}
r = requests.put('http://127.0.0.1:8000/key/12/image_upload',
                 data={}, files=files)
print(r.status_code)