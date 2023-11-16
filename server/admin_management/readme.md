# Using Virtual Environment

If you have multiple python projects locally and you want to isolate your FAM developments, you can use a virtual environment.

```
cd server/admin_management
python3 -m venv venv
. ./venv/bin/activate
pip install -r requirements.txt
```

# Create or update the necessary environment variables

In general, if there is a setting change in local-dev.env, run below to have correct environments setup.

Note: This is no longer necessary if running through Docker or running tests through VS Code testrunner, as they both reference the .env file at startup.

```
cd server/admin_management
set -o allexport; source local-dev.env; set +o allexport
```