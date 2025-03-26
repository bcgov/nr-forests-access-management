-- Drop and create temp table for base app metadata
DROP TABLE IF EXISTS temp_app;

CREATE TEMP TABLE temp_app (
  app_abbreviation TEXT,
  app_description TEXT
);

-- Update this for different applications
INSERT INTO
  temp_app (app_abbreviation, app_description)
VALUES
  ('APT', 'Apportionment');

-- Drop and create temp table for environment-specific entries
DROP TABLE IF EXISTS temp_envs;

CREATE TEMP TABLE temp_envs (env_code TEXT, client_id TEXT);

-- Update this for different environments
INSERT INTO
  temp_envs (env_code, client_id)
VALUES
  ('DEV', '${client_id_dev_apt_oidc_client}'),
  ('TEST', '${client_id_test_apt_oidc_client}'),
  ('PROD', '${client_id_prod_apt_oidc_client}');

-- Drop and create combined app+env view
DROP TABLE IF EXISTS temp_combined_apps;

CREATE TEMP TABLE temp_combined_apps AS
SELECT
  app.app_abbreviation,
  app.app_description,
  env.env_code,
  app.app_abbreviation || '_' || env.env_code AS application_name,
  app.app_description || ' (' || env.env_code || ')' AS application_description,
  env.client_id
FROM
  temp_app app
  CROSS JOIN temp_envs env;

-- Drop and create inserted_apps from RETURNING result
DROP TABLE IF EXISTS inserted_apps;

CREATE TEMP TABLE inserted_apps AS WITH ins AS (
  INSERT INTO
    app_fam.fam_application (
      application_name,
      application_description,
      app_environment,
      create_user,
      create_date
    )
  SELECT
    application_name,
    application_description,
    env_code,
    CURRENT_USER,
    CURRENT_DATE
  FROM
    temp_combined_apps RETURNING application_id,
    application_name,
    app_environment
)
SELECT
  *
FROM
  ins;

-- Define shared roles
WITH role_definitions AS (
  SELECT
    *
  FROM
    (
      VALUES
        (
          'VIEWER',
          'Users have view-only access to content.',
          'C'
        ),
        (
          'EDITOR',
          'Users can view and make edits to content.',
          'C'
        )
    ) AS r(role_name, role_purpose, role_type_code)
)
INSERT INTO
  -- Insert shared roles for all inserted apps
  app_fam.fam_role (
    role_name,
    role_purpose,
    application_id,
    role_type_code,
    create_user,
    create_date
  )
SELECT
  r.role_name,
  r.role_purpose,
  a.application_id,
  r.role_type_code,
  CURRENT_USER,
  CURRENT_DATE
FROM
  role_definitions r
  CROSS JOIN inserted_apps a;

-- Insert app client mappings
INSERT INTO
  app_fam.fam_application_client (
    cognito_client_id,
    application_id,
    create_user,
    create_date
  )
SELECT
  c.client_id,
  a.application_id,
  CURRENT_USER,
  CURRENT_DATE
FROM
  temp_combined_apps c
  JOIN inserted_apps a ON c.application_name = a.application_name;
