-- Create temp table for base app metadata
CREATE TEMP TABLE temp_app (
  app_abbreviation TEXT,
  app_description TEXT
);

-- Update this for different applications
INSERT INTO
  temp_app (app_abbreviation, app_description)
VALUES
  ('APT', 'Apportionment');

-- Create temp table for environment-specific entries
CREATE TEMP TABLE temp_envs (env_code TEXT, client_id TEXT);

-- Update this for different environments
INSERT INTO
  temp_envs (env_code, client_id)
VALUES
  ('DEV', '${client_id_dev_apt_oidc_client}'),
  ('TEST', '${client_id_test_apt_oidc_client}'),
  ('PROD', '${client_id_prod_apt_oidc_client}');

-- Create combined app+env view
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

-- Insert into fam_application and create inserted_apps from RETURNING result
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

-- Insert access admin roles into FAM app
INSERT INTO
  app_fam.fam_role (
    role_name,
    role_purpose,
    application_id,
    role_type_code,
    create_user,
    create_date
  )
SELECT
  t.app_abbreviation || '_' || t.env_code || '_ACCESS_ADMIN',
  'Provides the privilege to assign or unassign all roles for ' || t.app_abbreviation || ' (' || t.env_code || ')',
  (
    SELECT
      application_id
    FROM
      app_fam.fam_application
    WHERE
      application_name = 'FAM'
  ),
  'C',
  CURRENT_USER,
  CURRENT_DATE
FROM
  temp_combined_apps t;

-- Define shared roles
WITH role_definitions AS (
  SELECT
    *
  FROM
    (
      VALUES
        ('VIEW', 'View only access to application', 'C'),
        ('UPDATE', 'Write access to application', 'C'),
        (
          'REPORT',
          'Download and generate batch APT reports',
          'C'
        ),
        (
          'USER',
          'Provides the POPULATE_FORM action access to the user',
          'C'
        ),
        (
          'WEB_REPORTS',
          'POPULATE_FORM access for web reports service',
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
