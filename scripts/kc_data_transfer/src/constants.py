import os
import dotenv
import sys
import logging

"""
used to load the env files.  Expects either environment variables to be
populated.  If they have not been populated then will try to load them from
a .env file in this directory

:raises EnvironmentError: _description_
"""

LOGGER = logging.getLogger(__name__)



# populate the env vars from an .env file if it exists
localEnvPath = os.path.join(os.path.dirname(__file__), '..', '.env')

#localEnvPath = os.path.join(os.getcwd(), '..', '.env')
LOGGER.debug(f"envPath: {localEnvPath}")

if os.path.exists(localEnvPath):
    LOGGER.debug(f"loading dot env {localEnvPath}...")
    dotenv.load_dotenv(localEnvPath)
else:
    LOGGER.warning("no .env file was found")

# env vars that should be populated for script to run
ENV_VARS = ['KC_HOST', 'KC_CLIENTID', 'KC_REALM', 'KC_SECRET',
            'KC_FOM_CLIENTID']
# KC_SA_CLIENTID

module = sys.modules[__name__]

# verify that the env vars that we want to be populated have been populated
envsNotSet = []
for env in ENV_VARS:
    if env not in os.environ:
        envsNotSet.append(env)
    else:
        # transfer env vars to module properties
        setattr(module, env, os.environ[env])

if envsNotSet:
    msg = 'The script expects the following environment variables to ' + \
          f'be set {envsNotSet}'
    raise EnvironmentError(msg)


FOM_CLIENT_ID = 'fom'
