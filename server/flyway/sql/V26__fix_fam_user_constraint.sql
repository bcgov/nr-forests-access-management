
WITH duplicate AS (
    SELECT u.user_type_code, upper(u.user_name) AS upper_name
    FROM app_fam.fam_user u
    GROUP BY u.user_type_code, upper(u.user_name)
    HAVING count(1) > 1
),
delete_candidates AS (
    SELECT * FROM app_fam.fam_user u JOIN duplicate
    ON u.user_type_code = duplicate.user_type_code
    AND upper(u.user_name) = duplicate.upper_name
    WHERE u.user_guid IS NOT NULL
)
DELETE FROM app_fam.fam_user u WHERE u.user_id IN (SELECT user_id FROM delete_candidates);


ALTER TABLE app_fam.fam_user DROP CONSTRAINT fam_usr_uk;

CREATE UNIQUE INDEX fam_usr_uk ON app_fam.fam_user(user_type_code, lower(user_name));