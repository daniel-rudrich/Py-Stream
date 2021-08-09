---
layout: page
title: Rest Api
permalink: /installation/restapi
parent: Usage
nav_order: 2
---

# Documentation of the REST API

- adopted from https://gist.github.com/azagniotov/a4b16faf0febd12efbc6c3d7370383a6

------------------------------------------------------------------------------------------

#### Listing stream decks, stream deck keys, folders and commands as json string

<details>

<summary markdown="span">
<code>GET</code><code><b>/api/streamdecks</b></code> returns all stream decks
</summary>

##### Parameters

None

##### Responses

> | http code     | content-type                      | response                                                            |
> |---------------|-----------------------------------|---------------------------------------------------------------------|
> | `200`         | `application/json`                | json string                                                         |

##### Example cURL

> ```javascript
>  curl -X GET -H "Content-Type: application/json" http://localhost:8000/api/streamdecks
> ```
</details>


<details>
<summary markdown="span"><code>GET</code><code><b>/api/streamdecks/{id}</b></code> get stream deck by its id</summary>


#####  URL Parameters

> | name              |  type     | data type      | description                         |
> |-------------------|-----------|----------------|-------------------------------------|
> | `id`              |  required | int            | The specific stream deck id         |

##### Responses

> | http code     | content-type                      | response                                                            |
> |---------------|-----------------------------------|---------------------------------------------------------------------|
> | `200`         | `application/json`                | json string                                                         |
> | `404`         | `text/html; charset=utf-8`        | `Stream deck with id {id} not found`                                |

##### Example cURL

> ```javascript
>  curl -X GET -H "Content-Type: application/json" http://localhost:8000/api/streamdecks/1
> ```

</details>

<details>
<summary markdown="span"><code>GET</code><code><b>/api/streamdecks/{id}/folders</b></code> get folders of stream deck</summary>


##### URL Parameters

> | name              |  type     | data type      | description                         |
> |-------------------|-----------|----------------|-------------------------------------|
> | `id`              |  required | int            | The specific stream deck id         |

##### Responses

> | http code     | content-type                      | response                                                            |
> |---------------|-----------------------------------|---------------------------------------------------------------------|
> | `200`         | `application/json`                | json string                                                         |
> | `404`         | `text/html; charset=utf-8`        | `Stream deck with id {id} not found`                                |

##### Example cURL

> ```javascript
>  curl -X GET -H "Content-Type: application/json" http://localhost:8000/api/streamdecks/1/folders
> ```

</details>

<details>
<summary markdown="span"><code>GET</code><code><b>/api/streamdecks/{id}/folders/{folder_id}</b></code> get folder of stream deck by its folder id</summary>


##### URL Parameters

> | name              |  type     | data type      | description                         |
> |-------------------|-----------|----------------|-------------------------------------|
> | `id`              |  required | int            | The specific stream deck id         |
> | `folder_id`       |  required | int            | The specific folder id              |

##### Responses

> | http code     | content-type                      | response                                                            |
> |---------------|-----------------------------------|---------------------------------------------------------------------|
> | `200`         | `application/json`                | json string                                                         |
> | `404`         | `text/html; charset=utf-8`        | `Stream deck with id {id} not found`                                |
> | `404`         | `text/html; charset=utf-8`        | `Folder with id {folder_id} not found`                              |

##### Example cURL

> ```javascript
>  curl -X GET -H "Content-Type: application/json" http://localhost:8000/api/streamdecks/1/folders/1
> ```

</details>

<details>
<summary markdown="span"><code>GET</code><code><b>/api/key/{id}</b></code> get stream deck key by its id</summary>


##### URL Parameters

> | name              |  type     | data type      | description                         |
> |-------------------|-----------|----------------|-------------------------------------|
> | `id`              |  required | int            | The specific key id                 |

##### Responses

> | http code     | content-type                      | response                                                            |
> |---------------|-----------------------------------|---------------------------------------------------------------------|
> | `200`         | `application/json`                | json string                                                         |
> | `404`         | `text/html; charset=utf-8`        | `Stream deck key with id {id} not found`                                |

##### Example cURL

> ```javascript
>  curl -X GET -H "Content-Type: application/json" http://localhost:8000/api/key/1
> ```

</details>

<details>
<summary markdown="span"><code>GET</code><code><b>/api/key/{id}/command/{command_id}</b></code> get command of a stream deck key by its id</summary>


##### URL Parameters

> | name              |  type     | data type      | description                         |
> |-------------------|-----------|----------------|-------------------------------------|
> | `id`              |  required | int            | The specific key id                 |
> | `command_id`      |  required | int            | The specific command id             |

##### Responses

> | http code     | content-type                      | response                                                            |
> |---------------|-----------------------------------|---------------------------------------------------------------------|
> | `200`         | `application/json`                | json string                                                         |
> | `404`         | `text/html; charset=utf-8`        | `Stream deck key with id {id} not found`                            |
> | `404`         | `text/html; charset=utf-8`        | `Command with id {id} not found under this stream deck key`         |

##### Example cURL

> ```javascript
>  curl -X GET -H "Content-Type: application/json" http://localhost:8000/api/key/1/command/1
> ```

</details>

-------------------------------------------------------------------------------------------

#### Uploading images or creating folders and commands

<details>
<summary markdown="span"><code>PUT</code><code><b>/api/key/{id}/image_upload</b></code> upload image to stream deck key</summary>


##### URL Parameters

> | name              |  type     | data type      | description                         |
> |-------------------|-----------|----------------|-------------------------------------|
> | `id`              |  required | int            | The specific key id                 |

##### Data Parameters

> | name              |  type     | data type      | description                         |
> |-------------------|-----------|----------------|-------------------------------------|
> | `image_source`    |  required | request.data   | the image itself                    |

##### Responses

> | http code     | content-type                      | response                                                            |
> |---------------|-----------------------------------|---------------------------------------------------------------------|
> | `200`         | `text/html; charset=utf-8`        | `Image uploaded successfully`                                       |
> | `404`         | `text/html; charset=utf-8`        | `Stream deck key with id {id} not found`                            |

##### Example cURL

> ```javascript
>  curl -X PUT -F "image_source=@/path/to/image.png" http://localhost:8000/api/key/1/image_upload 
> ```
</details>

<details>
<summary markdown="span"><code>PUT</code><code><b>/api/key/{id}/command</b></code> add command to stream deck key</summary>


##### URL Parameters

> | name              |  type     | data type      | description                         |
> |-------------------|-----------|----------------|-------------------------------------|
> | `id`              |  required | int            | The specific key id                 |

##### Data Parameters

> | name              |  type     | data type      | description                         |
> |-------------------|-----------|----------------|-------------------------------------|
> | `name`            |  required | string         | name of the command                 |
> | `command_string`  |  optional | string         | to be executed command string       |
> | `active_directory`|  optional | string         | directory path where the command should be executed                 |
> | `command_type`    |  optional | string         | type of command (default shell)     |
> | `time_value`      |  optional | int            | value required for timer and intervall shell function     |
> | `hotkeys`         |  optional | json array     | required for hotkey commands; array of keyboard keys                 |

##### Responses

> | http code     | content-type                      | response                                                            |
> |---------------|-----------------------------------|---------------------------------------------------------------------|
> | `200`         | `application/json`                | None                                                                |
> | `400`         | `text/html; charset=utf-8`        | `Command type not valid`                                            |
> | `404`         | `text/html; charset=utf-8`        | `Stream deck key with id {id} not found`                            |

##### Example cURLs

> ```javascript
>  curl -X PUT -H "Content-Type: application/json" -d "{ "name":"echo", "command_string":"echo new", "command_type":"shell"}" http://localhost:8000/api/key/1/command
>  curl -X PUT -H "Content-Type: application/json" -d "{ "name":"stopwatch", "command_type":"stopwatch"}" http://localhost:8000/api/key/2/command
>  curl -X PUT -H "Content-Type: application/json" -d "{ "name":"timer", "command_type":"timer", "time_value":"60"}" http://localhost:8000/api/key/3/command
>  curl -X PUT -H "Content-Type: application/json" -d "{ "name":"strg+f", "command_type":"hotkey", "hotkeys":[{"key1": {"key":"Control", "location":1}}, {"key2": {"key":"f", "location":0}}]}" http://localhost:8000/api/key/4/command
> ```
</details>

<details>
<summary markdown="span"><code>PUT</code><code><b>/api/key/{id}/folder</b></code> creates a new folder reachable through a stream deck key</summary>


##### URL Parameters

> | name              |  type     | data type      | description                         |
> |-------------------|-----------|----------------|-------------------------------------|
> | `id`              |  required | int            | The specific key id                 |

##### Data Parameters

> | name              |  type     | data type      | description                         |
> |-------------------|-----------|----------------|-------------------------------------|
> | `name`            |  required | string         | folder name                         |

##### Responses

> | http code     | content-type                      | response                                                            |
> |---------------|-----------------------------------|---------------------------------------------------------------------|
> | `200`         | `application/json`                | None                                                                |
> | `403`         | `text/html; charset=utf-8`        | `This stream deck key already leads to a folder!`                   |
> | `404`         | `text/html; charset=utf-8`        | `Stream deck key with id {id} not found`                            |

##### Example cURL

> ```javascript
>  curl -X PUT -H "Content-Type: application/json" -d "{ "name":"work_folder"}" http://localhost:8000/api/key/1/folder
> ```
</details>

-------------------------------------------------------------------------------------------

#### Modifying stream decks, stream deck keys and commands

<details>
<summary markdown="span"><code>PATCH</code><code><b>/api/streamdecks/{id}</b></code> change name and/or brightness of stream deck</summary>


##### URL Parameters

> | name              |  type     | data type      | description                         |
> |-------------------|-----------|----------------|-------------------------------------|
> | `id`              |  required | int            | The specific stream deck id         |

##### Data Parameters

> | name              |  type     | data type      | description                         |
> |-------------------|-----------|----------------|-------------------------------------|
> | `name`            |  optional | string         |  name of the stream deck            |
> | `brightness`      |  optional | int            |  brightness value (0-100)           |

##### Responses

> | http code     | content-type                      | response                                                            |
> |---------------|-----------------------------------|---------------------------------------------------------------------|
> | `200`         | `application/json`                | `json string`                                                       |
> | `404`         | `text/html; charset=utf-8`        | `Stream deck with id {id} not found`                            |

##### Example cURL

> ```javascript
>  curl -X PUT -H "Content-Type: application/json" -d "{ "brightness":"100"}" http://localhost:8000/api/streandecks/1
> ```
</details>

<details>
<summary markdown="span"><code>PATCH</code><code><b>/api/key/{id}</b></code> change the text of the stream deck key</summary>


##### URL Parameters

> | name              |  type     | data type      | description                         |
> |-------------------|-----------|----------------|-------------------------------------|
> | `id`              |  required | int            | The specific stream deck key id     |

##### Data Parameters

> | name              |  type     | data type      | description                         |
> |-------------------|-----------|----------------|-------------------------------------|
> | `text`            |  required | string         |  text of stream deck key            |

##### Responses

> | http code     | content-type                      | response                                                            |
> |---------------|-----------------------------------|---------------------------------------------------------------------|
> | `200`         | `application/json`                | `json string`                                                       |
> | `404`         | `text/html; charset=utf-8`        | `Stream deck key with id {id} not found`                            |

##### Example cURL

> ```javascript
>  curl -X PUT -H "Content-Type: application/json" -d "{ "text":"test"}" http://localhost:8000/api/key/1
> ```

</details>

<details>
<summary markdown="span"><code>PATCH</code><code><b>/api/key/{id}/command/{command_id}</b></code> change command of stream deck key</summary>


##### URL Parameters

> | name              |  type     | data type      | description                         |
> |-------------------|-----------|----------------|-------------------------------------|
> | `id`              |  required | int            | The specific key id                 |
> | `command_id`      |  required | int            | The specific command id             |

##### Data Parameters

> | name              |  type     | data type      | description                         |
> |-------------------|-----------|----------------|-------------------------------------|
> | `name`            |  optional | string         | name of the command                 |
> | `command_string`  |  optional | string         | to be executed command string       |
> | `active_directory`|  optional | string         | directory path where the command should be executed                 |
> | `command_type`    |  optional | string         | type of command (default shell)     |
> | `time_value`      |  optional | int            | value required for timer and intervall shell command function     |
> | `hotkeys`         |  optional | json array         | required for hotkey commands; array of keyboard keys                 |

##### Responses

> | http code     | content-type                      | response                                                            |
> |---------------|-----------------------------------|---------------------------------------------------------------------|
> | `200`         | `application/json`                | `json string`                                                       |
> | `404`         | `text/html; charset=utf-8`        | `Command with id {id} not found under this stream deck key`         |
> | `404`         | `text/html; charset=utf-8`        | `Stream deck key with id {id} not found`                            |

##### Example cURL

> ```javascript
>  curl -X PATCH -H "Content-Type: application/json" -d "{ "name":"changed_name"}" http://localhost:8000/api/key/1/command/1
> ```
</details>

-------------------------------------------------------------------------------------------

#### Deleting images, folders and commands

<details>
<summary markdown="span"><code>DELETE</code><code><b>/api/key/{id}</b></code> deletes image of stream deck key</summary>


##### URL Parameters

> | name              |  type     | data type      | description                         |
> |-------------------|-----------|----------------|-------------------------------------|
> | `id`              |  required | int            | The specific stream deck key id     |

##### Responses

> | http code     | content-type                      | response                                                            |
> |---------------|-----------------------------------|---------------------------------------------------------------------|
> | `204`         | `text/html; charset=utf-8`        | `Image deleted successfully`                                       |
> | `404`         | `text/html; charset=utf-8`        | `Stream deck key with id {id} not found`                            |

##### Example cURL

> ```javascript
>  curl -X DELETE http://localhost:8000/api/key/1
> ```
</details>
<details>
<summary markdown="span"><code>DELETE</code><code><b>/api/key/{id}/command/{command_id}</b></code> deletes command of stream deck key</summary>


##### URL Parameters

> | name              |  type     | data type      | description                         |
> |-------------------|-----------|----------------|-------------------------------------|
> | `id`              |  required | int            | The specific stream deck key id     |
> | `command_id`      |  required | int            | The specific command id             |

##### Responses

> | http code     | content-type                      | response                                                            |
> |---------------|-----------------------------------|---------------------------------------------------------------------|
> | `204`         | `text/html; charset=utf-8`        | `Command deleted successfully`                                       |
> | `400`         | `text/html; charset=utf-8`        | `Command type not valid`                                            |
> | `404`         | `text/html; charset=utf-8`        | `Command with id {id} not found under this stream deck key`         |
> | `404`         | `text/html; charset=utf-8`        | `Stream deck key with id {id} not found`                            |

##### Example cURL

> ```javascript
>  curl -X DELETE http://localhost:8000/api/key/1/command/1
> ```
</details>

<details>
<summary markdown="span"><code>DELETE</code><code><b>/api/key/{id}/folder</b></code> deletes the folder where this stream deck key leads to</summary>


##### URL Parameters

> | name              |  type     | data type      | description                         |
> |-------------------|-----------|----------------|-------------------------------------|
> | `id`              |  required | int            | The specific stream deck key id     |

##### Responses

> | http code     | content-type                      | response                                                            |
> |---------------|-----------------------------------|---------------------------------------------------------------------|
> | `200`         | `text/html; charset=utf-8`        | `folder deleted successfully`                                       |
> | `404`         | `text/html; charset=utf-8`        | `this stream deck key does not lead to a folder`                    |
> | `404`         | `text/html; charset=utf-8`        | `Stream deck key with id {id} not found`                            |

##### Example cURL

> ```javascript
>  curl -X DELETE http://localhost:8000/api/key/1/folder
> ```

</details>

-------------------------------------------------------------------------------------------