
CREATE USER ${auth_lambda_db_user} WITH NOSUPERUSER NOCREATEDB NOCREATEROLE PASSWORD '${auth_lambda_db_password}';

GRANT USAGE ON SCHEMA app_fam TO ${auth_lambda_db_user};

GRANT SELECT, UPDATE, DELETE, INSERT ON ALL TABLES IN SCHEMA app_fam TO ${auth_lambda_db_user};
