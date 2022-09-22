<!--
 Copyright 2022 Indoc Research
 
 Licensed under the EUPL, Version 1.2 or – as soon they
 will be approved by the European Commission - subsequent
 versions of the EUPL (the "Licence");
 You may not use this work except in compliance with the
 Licence.
 You may obtain a copy of the Licence at:
 
 https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12
 
 Unless required by applicable law or agreed to in
 writing, software distributed under the Licence is
 distributed on an "AS IS" basis,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
 express or implied.
 See the Licence for the specific language governing
 permissions and limitations under the Licence.
 
-->

# Metadata Service

using Apache Atlas as metadata store to proxy the authorization

The service will running at `<host>:5064`

## Installation

follow the step below to setup the service

### Clone

- Clone this repo to machine using `https://git.indocresearch.org/platform/service_metadata.git`

### Setup:

> To run the service as dev mode

```
python3 -m pip install -r requirements.txt
python3 app.py
```

> To run the service as production in docker and gunicorn

```
docker build . -t metadata/latest
docker run metadata/latest -d
```

> To add new entity in atlas run the curl in the `type.txt` it will add two more entity in atlas:

 - nfs_file
 - nfs_file_processed

## Features:

the service uses the swagger to make the api documents: see the detailed [doc](localhost:6064/v1/api-doc)

### Entity Related API:

 - Add entity to atlas

 - Query entity by the input payload

 - Get entiy by the guid

### Audit Related API:

 - Get audit of entity by guid