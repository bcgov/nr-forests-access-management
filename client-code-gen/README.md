# FAM API Client Code Generation for Frontend with "typescript-axios"

This folder contains a mini npm project for generating FAM API client from OpenAPI(Swagger) spec. The genereated client (library) can be utilized for frontend with typescript/axio framework to make api call to FAM backend endpoints.

Client library regeneration is needed when endpints contract has changed.

## Package/Tool choice
This is using the popular [OpenAPI Generator/openapi-generator-cli](https://openapi-generator.tech/docs/installation) for generation.

There are two ways to generate the client code in this package.
1. Generate with openapitook docker image.
2. Generate with openapi-generator-cli.
>> However, second option requires java installed in the environment.There is also a javascript package "[openapi-typescript-codegen](https://www.npmjs.com/package/openapi-typescript-codegen)" that can generate the client without the need of 'Java' and the generated client is quite good and clean. However, Fam frontend uses custom "Axios" instance http client and this tool currently does not support configuring custom 'Axios' instance (it can only use global axios) so does not look like a good fit. The tool probably will support custom axio instance in the future. We can come back later for this tool later when the feature is available.

To run this client generation (using 'openapi-generator-cli'), you need following environments:

Environment
* NPM/Node.js
* JRE/JDK (Requires java install) for <ins>option 2</ins>.

The generated client can be used both as:
* Javascript (ES6 supported)
* Typedscript

## Client Generation

The generation utilizes [OpenAPI Generator Cli with "typescript-axios" as the client](https://openapi-generator.tech/docs/generators/typescript-axios).

The *package.json* contains simple scripts to run.
Two things are required to generate the client code:
* The FAM backend OpenAPI spec (.json or .yaml): Default to 'local' file <mark>[some-api-component]-openapi.json</mark>.
* Generator options: This is currently using a file <mark>api.json</mark> to include options.

Update OpenAPI Spec:
```
* Start backend server and navigate to OpenAPI spec at your browser, for example (locally) "http://localhost:8000/openapi.json".

* Copy the json content and update it to the "[some-api-component]-openapi.json" file at root directory.
```

To generate, build and compile the typescript sources to javascript use:
```
With Docker (example: for `admin-management-api`):
>> npm run dockergen-admin-management-api-bash

or for Windows(CMD/Powershell), use script
>>(npm run dockergen-admin-management-api-win)

With CLI:
>> npm install --ignore-scripts
>> npm run gen-admin-management-api
```

The generated client is located at "./gen/[xyz]-api" directory specified by the "-o" option at the script.

After api client code is generated:
```
>> update `axios` version in generated package to be consistent with "frontend" axios version.
- This is important. During generation, this version could be changed by generation script. See note below.
```

Note:
```
Depending on the Axios version used at frontend, please be aware different axios versions used between in generatred code and frontend dependency will cause integration headache, even if it is a patch version change.
Currently for openapi-generator with `typescript-axios`, there is no option available to spcify which `axios` version to use. If there is a need to upgrade frontend axios to higher version, then the generated code will also need to use the same version of axios. Use `npm ls axios` to check dependency tree after installation if not sure.

```

```
In some cases, it would be good idea to delete "/gen/[xyz]-api" directory before running script to regenerate new api client code to avoid leaving unnecessary files from last version generated code.
If you encounter folder permission during npm install or during generation, can issue command to temporarily change `gen` folder and files permission with `chmod -R 777`.
```
### Special Care on openapi.json Spec
* Current openapi(Swagger) spec produced from FastAPI is having issue. Specifically for the "Path" parameter of two endpoints: `"/{application_id}/fam_roles"` and `"/{application_id}/user_role_assignment"`. The path parameter in the produced spec isn't correctly typed (it has "any" type). This, however, only happens on these two endpoints and not on the endpoint that has the same signature `(@router.delete("/{user_role_xref_id}",))`
* We suspect FastAPI version (after we bump up verson to 0.100.0) might be related to this issue. However, we can not downgrade to lower than 0.90.0 and up to today's(2023/10/17) version 0.103.0 does not resolve to correct schema.
* Temporary solution is to add `"type":"integer",` into the corresponding `schema` section of the produced openapi.json manually.
* This is not a desirable behaviour but a temporary solution. So in the future, please verify again with higher FastAPI version and investigate further it further to see if it is fixed.

## How to Use/Integrate with Generated Client/Lib
The generated api client code (under /gen directory) can be used in frontend (located `frontend` folder under project root) as one of its dependencies/libs.

* In frontend package.json, add this dependency:
  ```
  For example:
  "fam-admin-mgmt-api": "file:../client-code-gen/gen/admin-management-api"
  ```

* Before runing `npm ci --ignore-scripts` or `npm install --ignore-scripts` for fronend dependencies, run:
  ```
  cd ../client-code-gen/gen/admin-management-api
  npm install

  cd ../../frontend
  npm ci --ignore-scripts

  If it is the first time.
  This will install fam-admin-mgmt-api for the frontend.
  ```


* After `fam-admin-mgmt-api` is installed from "/gen/admin-management-api", The generated api services and models can be imported, example:
  ```
  import {
    FAMSomeApi1,
    FAMSomeApi2
  } from 'fam-admin-mgmt-api';

  If there is a new api module, just added it in the import.
  ```

* Configure(supply) api services to use the axios instance (if not using global axios), example:
  ```
    // Using api client.
       this.applicationsApi = new FAMSomeApi1(undefined, '', httpInstance) // Note, Axios is strange, second parameter needs empty string, not null.
  ```

## References:
* [OpenAPI Generator](https://openapi-generator.tech/docs/installation)
* [OpenAPI Generator CLI](https://www.npmjs.com/package/@openapitools/openapi-generator-cli)
* [Use Swagger to generate API client in Frontend](https://medium.com/@suraj.kc/use-swagger-to-generate-api-client-in-frontend-60b7d65abf31)