import env from "./env.json" assert { type: "json" }; // type: "json" is needed or browser will not allow import json.

window.localStorage.setItem('env_data', JSON.stringify(env))

