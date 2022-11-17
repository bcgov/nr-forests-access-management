import env from "./env.json" assert { type: "json" }; // type: "json" is needed or browser will not allow import json.

window.localStorage.setItem('env_data', JSON.stringify(env))

window.localStorage.setItem('fam_environment_display_name', 'dev') // TODO, add this to env.json tf generation script.

