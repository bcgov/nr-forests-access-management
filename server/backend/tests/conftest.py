import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

pytest_plugins = [
    "tests.fixtures.fixtures_crud_application",
    "tests.fixtures.fixtures_router_application",
    "tests.fixtures.fixtures_crud_user",
    "tests.fixtures.fixtures_router_user",
    "tests.fixtures.fixtures_crud_role",
    "tests.fixtures.fixtures_crud_user_role_assignment",
    "tests.fixtures.fixtures_crud_forestclient"
]
