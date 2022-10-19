import pytest
import os
import psycopg2

# @pytest.fixture(scope='session')
# def db_connection():
#     connection = psycopg2.connect(host=os.environ.get('PG_HOST', 'localhost'),
#                                   port=os.environ.get('PG_PORT', '5432'),
#                                   dbname=os.environ.get('PG_DATABASE', 'postgres'),
#                                   user=os.environ.get('PG_USER', 'fam_proxy_api'),
#                                   password=os.environ.get('PG_PASSWORD', 'test'),
#                                   sslmode='disable')
#     connection.autocommit = False  # With tests we don't need to clean up the data
#     function.db_connection = connection
#     function.testing = True

#     yield connection

#     connection.close()