# FAM API Client Code Generation for Frontend with "typescript-axios"

This folder contains a mini npm project for generating FAM API client from OpenAPI(Swagger) spec. The genereated client (library) can be utilized for frontend with typescript/axio framework to make api call to FAM backend endpoints.

Client library regeneration is needed when endpints contract has changed.

## Package/Tool choice
This is using the popular [OpenAPI Generator/openapi-generator-cli](https://openapi-generator.tech/docs/installation) for generation.
However, it requires java installed in the environment.
There is also a javascript package "[openapi-typescript-codegen](https://www.npmjs.com/package/openapi-typescript-codegen)" that can generate the client without the need of 'Java' and the generated client is quite good and clean. However, Fam frontend uses custom "Axios" instance http client and this tool currently does not support configuring custom 'Axios' instance (it can only use global axios) so does not look like a good fit. The tool probably will support custom axio instance in the future. We can come back later for this tool later when the feature is available.

To run this client generation (using 'openapi-generator-cli'), you need following environments:

Environment
* NPM/Node.js
* JRE/JDK (Requires java install)

The generated client can be used both as:
* Javascript (ES6 supported)
* Typedscript

## Client Generation

The generation utilizes [OpenAPI Generator Cli with "typescript-axios" as the client](https://openapi-generator.tech/docs/generators/typescript-axios).

The *package.json* contains a simple script "gen-api" to run.
Two things are required to generate the client code:
* The fam backend OpenAPI spec (.json or .yaml): Default to 'local' file <mark>openapi.json</mark>.
* Generator options: This is currently using a file <mark>api.json</mark> to include options.

Update OpenAPI Spec:
```
* Start backend server and navigate to OpenAPI spec at your browser, for example (locally) "http://localhost:8000/openapi.json".

* Copy the json content and update it to the "openapi.json" file at root directory.
```

To generate, build and compile the typescript sources to javascript use:
```
npm install
npm run gen-api

The generated client is located at "./gen" directory specified by the "-o" option at the script.
```

## <mark>TODO</mark>: How to Use/Integrate with Generated Client/Lib


## References:
* [OpenAPI Generator](https://openapi-generator.tech/docs/installation)
* [OpenAPI Generator CLI](https://www.npmjs.com/package/@openapitools/openapi-generator-cli)
* [Use Swagger to generate API client in Frontend](https://medium.com/@suraj.kc/use-swagger-to-generate-api-client-in-frontend-60b7d65abf31)