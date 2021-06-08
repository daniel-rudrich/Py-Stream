import requests
files = {'image_source': open(
    '/home/daniel/Projekt/python-elgato-streamdeck/src/Assets/' /
    'RGB_color_space_animated_view.gif', 'rb')}
r = requests.put('http://127.0.0.1:8000/key/17/image_upload',
                 data={}, files=files)
print(r.status_code)
