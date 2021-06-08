# Documentation of the REST API

- adopted from https://gist.github.com/azagniotov/a4b16faf0febd12efbc6c3d7370383a6

<details>
<summary><code>GET</code><code><b>/streamdecks</b></code> returns all stream decks</summary>


##### Parameters

None
</details>

<details>
<summary><code>GET</code><code><b>/streamdecks/{id}</b></code> get stream deck by its id</summary>


#####  URL Parameters

> | name              |  type     | data type      | description                         |
> |-------------------|-----------|----------------|-------------------------------------|
> | `id`              |  required | int            | The specific stream deck id         |


</details>

<details>
<summary><code>GET</code><code><b>/streamdecks/{id}/folders</b></code> get folders of stream deck</summary>


##### URL Parameters

> | name              |  type     | data type      | description                         |
> |-------------------|-----------|----------------|-------------------------------------|
> | `id`              |  required | int            | The specific stream deck id         |


</details>

<details>
<summary><code>GET</code><code><b>/streamdecks/{id}/folders/{folder_id}</b></code> get folder of stream deck by its folder id</summary>


##### URL Parameters

> | name              |  type     | data type      | description                         |
> |-------------------|-----------|----------------|-------------------------------------|
> | `id`              |  required | int            | The specific stream deck id         |
> | `folder_id`       |  required | int            | The specific folder id              |


</details>

<details>
<summary><code>GET</code><code><b>/key/{id}</b></code> get stream deck key by its id</summary>


##### URL Parameters

> | name              |  type     | data type      | description                         |
> |-------------------|-----------|----------------|-------------------------------------|
> | `id`              |  required | int            | The specific key id                 |


</details>

<details>
<summary><code>GET</code><code><b>/key/{id}/command/{command_id}</b></code> get command of a stream deck key by its id</summary>


##### URL Parameters

> | name              |  type     | data type      | description                         |
> |-------------------|-----------|----------------|-------------------------------------|
> | `id`              |  required | int            | The specific key id                 |
> | `command_id`      |  required | int            | The specific command id             |

</details>

<details>
<summary><code>PUT</code><code><b>/key/{id}/image_upload</b></code> upload image to stream deck key</summary>


##### URL Parameters

> | name              |  type     | data type      | description                         |
> |-------------------|-----------|----------------|-------------------------------------|
> | `id`              |  required | int            | The specific key id                 |

##### Data Parameters

> | name              |  type     | data type      | description                         |
> |-------------------|-----------|----------------|-------------------------------------|
> | `image_source`    |  required | request.data   | the image itself                    |
</details>

<details>
<summary><code>PUT</code><code><b>/key/{id}/command</b></code> add command to stream deck key</summary>


##### URL Parameters

> | name              |  type     | data type      | description                         |
> |-------------------|-----------|----------------|-------------------------------------|
> | `id`              |  required | int            | The specific key id                 |

##### Data Parameters

> | name              |  type     | data type      | description                         |
> |-------------------|-----------|----------------|-------------------------------------|
> | `name`            |  required | string         | name of the command                 |
> | `command_string`  |  required | string         | to be executed command string       |
> | `active_directory`|  optional | string         | directory path where the command should be executed                 |
> | `command_type`    |  optional | string         | type of command (default shell)     |
> | `time_value`      |  optional | int            | value required for timer and intervall shell function     |
> | `hotkeys`         |  optional | json array         | required for hotkey commands; array of keyboard keys                 |
</details>

<details>
<summary><code>PUT</code><code><b>/key/{id}/folder</b></code>creates a new folder reachable through a stream deck key</summary>


##### URL Parameters

> | name              |  type     | data type      | description                         |
> |-------------------|-----------|----------------|-------------------------------------|
> | `id`              |  required | int            | The specific key id                 |

##### Data Parameters

> | name              |  type     | data type      | description                         |
> |-------------------|-----------|----------------|-------------------------------------|
> | `name`            |  required | string         | folder name                         |
</details>

<details>
<summary><code>PATCH</code><code><b>/streamdecks/{id}</b></code> change name and/or brightness of stream deck</summary>


##### URL Parameters

> | name              |  type     | data type      | description                         |
> |-------------------|-----------|----------------|-------------------------------------|
> | `id`              |  required | int            | The specific stream deck id                 |

##### Data Parameters

> | name              |  type     | data type      | description                         |
> |-------------------|-----------|----------------|-------------------------------------|
> | `name`            |  optional | string         |  name of the stream deck            |
> | `brightness`      |  optional | int            |  brightness value (0-100)           |
</details>

<details>
<summary><code>PATCH</code><code><b>/key/{id}</b></code> change the text of the stream deck key</summary>


##### URL Parameters

> | name              |  type     | data type      | description                         |
> |-------------------|-----------|----------------|-------------------------------------|
> | `id`              |  required | int            | The specific stream deck key id     |

##### Data Parameters

> | name              |  type     | data type      | description                         |
> |-------------------|-----------|----------------|-------------------------------------|
> | `text`            |  required | string         |  text of stream deck key            |
</details>

<details>
<summary><code>PATCH</code><code><b>/key/{id}/command/{command_id}</b></code> add command to stream deck key</summary>


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
</details>

<details>
<summary><code>DELETE</code><code><b>/key/{id}/command/{command_id}</b></code> deletes command of stream deck key</summary>


##### URL Parameters

> | name              |  type     | data type      | description                         |
> |-------------------|-----------|----------------|-------------------------------------|
> | `id`              |  required | int            | The specific stream deck key id     |
> | `command_id`      |  required | int            | The specific command id             |
</details>

<details>
<summary><code>DELETE</code><code><b>/key/{id}/folder</b></code> deletes the folder where this stream deck key leads to</summary>


##### URL Parameters

> | name              |  type     | data type      | description                         |
> |-------------------|-----------|----------------|-------------------------------------|
> | `id`              |  required | int            | The specific stream deck key id     |
</details>