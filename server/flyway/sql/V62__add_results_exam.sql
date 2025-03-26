-- Drop and create temp table for base app metadata
DROP TABLE IF EXISTS temp_app;

CREATE TEMP TABLE temp_app (
    app_abbreviation TEXT,
    app_description TEXT
);

-- Insert base app metadata
INSERT INTO
    temp_app (app_abbreviation, app_description)
VALUES
    ('RESULTS_EXAM', 'Results Exam');

-- Drop and create temp table for environment-specific entries
DROP TABLE IF EXISTS temp_envs;

CREATE TEMP TABLE temp_envs (env_code TEXT, client_id TEXT);

-- Insert environment-specific client IDs
INSERT INTO
    temp_envs (env_code, client_id)
VALUES
    (
        'DEV',
        '${client_id_dev_results_exam_oidc_client}'
    ),
    (
        'TEST',
        '${client_id_test_results_exam_oidc_client}'
    ),
    (
        'PROD',
        '${client_id_prod_results_exam_oidc_client}'
    );

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
