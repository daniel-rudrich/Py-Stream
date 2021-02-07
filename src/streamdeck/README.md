# REST API 

## API calls with inputs

**GET /streamdecks** returns all streamdecks

**GET /streamdecks/<int:id>** returns the specific streamdeck
**PATCH /streamdecks/<int:id> (name=_string_), brightness=_int_** Change name and/or brightness of streamdeck 

**GET /streamdecks/<int:id>/folders** returns all folders of streamdeck

**GET /streamdecks/<int:id>/folders/<int:folder_id>** return folder of streamdeck

**GET /key/<int:id>** returns streamdeck key
**PATCH /key/<int:id> (text=_string_)** change text/title of key

**PUT /key/<int:id>/image_upload -> needs file for *image_source* in request.data** change image of streamdeck key

**PUT /key/<int:id>/command name=_string_, command_string=_string_(, value=_string_)** add command to streamdeck key

**GET /key/<int:id>/command/<int:command_id>** returns command of streamdeck key
**PATCH /key/<int:id>/command/<int:command_id> (name =_string_), (command_string=_string_), (value=_string_)** change command of streamdeck key
**DELETE /key/<int:id>/command/<int:command_id>** deletes command of streamdeck key

**PUT /key/<int:id>/folder name=_string_** creates new folder. Clicking the streamdeck key will change the streamdeck layout to this folder
**DELETE /key/<int:id>/folder** deletes the folder where this streamdeck key leads to