# Only for local development. You can debug this file and have the server
# running in debug mode. Not packaged for production.

import uvicorn

import api.app.main as main

uvicorn.run(main.app, host="127.0.0.1", port=8000, log_level="info")