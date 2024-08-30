# Using Virtual Environment

If you have multiple python projects locally and you want to isolate your FAM developments, you can use a virtual environment.

```
cd server/admin_management
python3 -m venv venv
. ./venv/bin/activate
pip install -r requirements.txt
```

# Create or update the necessary environment variables

Find the env files template [here](https://github.com/bcgov/nr-forests-access-management/wiki/Local-Env-Vars-Template) and create them on your local machine.

If you want to run the service locally without using docker compose, you can export the env vars with the following script
```bash
cd server/admin_management
export $(cat local-dev.env | xargs)
```

## -------------- Windows Configuration ----------------------------------------

Before you follow the steps below, ensure you have Python installed or updated to the latest version. Install and start your Docker desktop for Windows.

```
  - ensure that the backend is running. See the readme in the backend folder on how to start/run the backend
  - cd server/admin_management
  - run this command in the same directory: python3 -m venv venv
  - activate the venv environment by running this bat file: .\venv\Scripts\activate
  - Ask one of the developers for the environment properties in the local-dev.env, and update the properties in local-dev-window.env.bat with them
  - To install the required packages run: pip install -r requirements.txt
  - In the same directory, enter(run) local-dev-window.env.bat
  - To run start the backend, run python serverstart.py
```

