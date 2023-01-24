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

The *package.json* contains simple scripts "gen-api-docker" and "gen-api" to run.
Two things are required to generate the client code:
* The FAM backend OpenAPI spec (.json or .yaml): Default to 'local' file <mark>openapi.json</mark>.
* Generator options: This is currently using a file <mark>api.json</mark> to include options.

Update OpenAPI Spec:
```
* Start backend server and navigate to OpenAPI spec at your browser, for example (locally) "http://localhost:8000/openapi.json".

* Copy the json content and update it to the "openapi.json" file at root directory.
```

To generate, build and compile the typescript sources to javascript use:
```
With Docker:
>> npm run dockergen-api-bash
or for Windows(CMD/Powershell), use script >>(npm run dockergen-api-win)

With CLI:
>> npm install
>> npm run gen-api

The generated client is located at "./gen" directory specified by the "-o" option at the script.
```

Note:

```
Depending on the Axios version used at frontend, please be aware different axios versions used between in generatred code and frontend dependency will cause integration headache, even if it is a patch version change. So if in the future there is a need to upgrade frontend to higher version Vue, then it would probably mean it needs to bump up the OpenAPI generator (either from cli or docker) version for client code compatibility reason. Use `npm ls axios` to check dependency tree after installation if not sure.
```

```
In some cases, it would be good idea to delete "/gen" directory before running script to regenerate new api client code to avoid leaving unnecessary files from last version generated code.
```

## How to Use/Integrate with Generated Client/Lib
The generated api client code (under /gen directory) can be used in frontend (located `frontend` folder under project root) as one of its dependencies/libs (currently named it as 'fam-api').

* In frontend package.json, add this dependency:
  ```
  For example:
  "fam-api": "file:../client-code-gen/gen"
  ```

* Before runing `npm ci` or `npm install` for fronend dependencies, run:
  ```
  cd ../client-code-gen/gen
  npm install

  cd ../../frontend
  npm ci

  If it is the first time.
  This will install fam-api for the frontend.
  ```


* After `fam-api` is installed from "/gen", The generated api services and models can be imported, example:
  ```
  import {
    FAMApplicationsApi,
    FAMRolesApi,
    FAMUserRoleAssignmentApi,
    FAMUsersApi
  } from 'fam-api';

  If there is a new api module, just added it in the import.
  ```

* Configure(supply) api services to use the axios instance (if not using global axios), example:
  ```
    // Instanciation for generated 'fam-api' client.
       this.applicationsApi = new FAMApplicationsApi(undefined, '', httpInstance) // Note, Axios is strange, second parameter needs empty string, not null.
  ```

## References:
* [OpenAPI Generator](https://openapi-generator.tech/docs/installation)
* [OpenAPI Generator CLI](https://www.npmjs.com/package/@openapitools/openapi-generator-cli)
* [Use Swagger to generate API client in Frontend](https://medium.com/@suraj.kc/use-swagger-to-generate-api-client-in-frontend-60b7d65abf31)