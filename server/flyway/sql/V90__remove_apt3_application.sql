
--- Warning, delete Migration: APT3 Application Cleanup/Remove

-- =====================================================
-- 1. STRICT SAFETY CHECKS
--    * on APT3-specific data counts (EXACT)
--    * generic safeguard on related tables (MAX 30). Data range is known and verified in all environments before this migration.
-- =====================================================

DO $$
DECLARE
    v_app_count INT;
    v_role_count INT;
    v_client_count INT;

    -- other tables (upper limit controlled by variable)
    v_user_role_xref_count INT;
    v_access_priv_count INT;
    v_admin_count INT;
    v_audit_count INT;

    v_max_other INT := 30;

BEGIN
    -- Check fam_application (expected EXACT 3, one each env: DEV/TEST/PROD)
    SELECT COUNT(*) INTO v_app_count
    FROM app_fam.fam_application
    WHERE application_name LIKE 'APT3_%';

    IF v_app_count != 3 THEN
        RAISE EXCEPTION
        'ABORT: Expected exactly 3 applications, found %', v_app_count;
    END IF;

    -- Check fam_role (expected EXACT 6, two per env: DEV/TEST/PROD)
    SELECT COUNT(*) INTO v_role_count
    FROM app_fam.fam_role
    WHERE application_id IN (
        SELECT application_id
        FROM app_fam.fam_application
        WHERE application_name LIKE 'APT3_%'
    );

    IF v_role_count != 6 THEN
        RAISE EXCEPTION
        'ABORT: Expected exactly 6 roles, found %', v_role_count;
    END IF;

    -- Check fam_application_client (expected EXACT 3, one per env: DEV/TEST/PROD)
    SELECT COUNT(*) INTO v_client_count
    FROM app_fam.fam_application_client
    WHERE application_id IN (
        SELECT application_id
        FROM app_fam.fam_application
        WHERE application_name LIKE 'APT3_%'
    );

    IF v_client_count != 3 THEN
        RAISE EXCEPTION
        'ABORT: Expected exactly 3 application_client rows, found %', v_client_count;
    END IF;

    -- ==========================
    -- UPPER LIMIT CHECKS (≤ v_max_other) - rate limit checks to prevent mass delete.
    -- ==========================

    -- user_role_xref
    SELECT COUNT(*) INTO v_user_role_xref_count
    FROM app_fam.fam_user_role_xref
    WHERE role_id IN (
        SELECT role_id FROM app_fam.fam_role
        WHERE application_id IN (
            SELECT application_id
            FROM app_fam.fam_application
            WHERE application_name LIKE 'APT3_%'
        )
    );

    IF v_user_role_xref_count > v_max_other THEN
        RAISE EXCEPTION
        'ABORT: fam_user_role_xref exceeds limit (%). Found %',
        v_max_other, v_user_role_xref_count;
    END IF;

    -- access_control_privilege
    SELECT COUNT(*) INTO v_access_priv_count
    FROM app_fam.fam_access_control_privilege
    WHERE role_id IN (
        SELECT role_id FROM app_fam.fam_role
        WHERE application_id IN (
            SELECT application_id
            FROM app_fam.fam_application
            WHERE application_name LIKE 'APT3_%'
        )
    );

    IF v_access_priv_count > v_max_other THEN
        RAISE EXCEPTION
        'ABORT: fam_access_control_privilege exceeds limit (%). Found %',
        v_max_other, v_access_priv_count;
    END IF;

    -- application_admin
    SELECT COUNT(*) INTO v_admin_count
    FROM app_fam.fam_application_admin
    WHERE application_id IN (
        SELECT application_id
        FROM app_fam.fam_application
        WHERE application_name LIKE 'APT3_%'
    );

    IF v_admin_count > v_max_other THEN
        RAISE EXCEPTION
        'ABORT: fam_application_admin exceeds limit (%). Found %',
        v_max_other, v_admin_count;
    END IF;

    -- privilege_change_audit
    SELECT COUNT(*) INTO v_audit_count
    FROM app_fam.fam_privilege_change_audit
    WHERE application_id IN (
        SELECT application_id
        FROM app_fam.fam_application
        WHERE application_name LIKE 'APT3_%'
    );

    IF v_audit_count > v_max_other THEN
        RAISE EXCEPTION
        'ABORT: fam_privilege_change_audit exceeds limit (%). Found %',
        v_max_other, v_audit_count;
    END IF;

    -- ==========================
    -- LOG SUMMARY
    -- ==========================

    RAISE NOTICE 'Safety checks passed: app=% role=% app_client=%',
        v_app_count, v_role_count, v_client_count;

    RAISE NOTICE 'Other counts: user_role=% access_priv=% app_admin=% audit=% (limit=%)',
        v_user_role_xref_count, v_access_priv_count, v_admin_count, v_audit_count, v_max_other;

END $$;

-- =====================================================
-- 2. START LOG
-- =====================================================

DO $$ BEGIN
    RAISE NOTICE '=== STARTING APT3 CLEANUP DELETE ===';
END $$;

-- =====================================================
-- 3. CHILD TABLES
-- =====================================================

-- user_role_xref
DO $$
DECLARE v_rows INT;
BEGIN
    DELETE FROM app_fam.fam_user_role_xref
    WHERE role_id IN (
        SELECT fr.role_id
        FROM app_fam.fam_role fr
        JOIN app_fam.fam_application fa
          ON fa.application_id = fr.application_id
        WHERE fa.application_name LIKE 'APT3_%'
    );

    GET DIAGNOSTICS v_rows = ROW_COUNT;
    RAISE NOTICE 'Deleted % rows from fam_user_role_xref', v_rows;
END $$;

-- access_control_privilege
DO $$
DECLARE v_rows INT;
BEGIN
    DELETE FROM app_fam.fam_access_control_privilege
    WHERE role_id IN (
        SELECT fr.role_id
        FROM app_fam.fam_role fr
        JOIN app_fam.fam_application fa
          ON fa.application_id = fr.application_id
        WHERE fa.application_name LIKE 'APT3_%'
    );

    GET DIAGNOSTICS v_rows = ROW_COUNT;
    RAISE NOTICE 'Deleted % rows from fam_access_control_privilege', v_rows;
END $$;

-- application_admin
DO $$
DECLARE v_rows INT;
BEGIN
    DELETE FROM app_fam.fam_application_admin
    WHERE application_id IN (
        SELECT application_id
        FROM app_fam.fam_application
        WHERE application_name LIKE 'APT3_%'
    );

    GET DIAGNOSTICS v_rows = ROW_COUNT;
    RAISE NOTICE 'Deleted % rows from fam_application_admin', v_rows;
END $$;

-- privilege_change_audit
DO $$
DECLARE v_rows INT;
BEGIN
    DELETE FROM app_fam.fam_privilege_change_audit
    WHERE application_id IN (
        SELECT application_id
        FROM app_fam.fam_application
        WHERE application_name LIKE 'APT3_%'
    );

    GET DIAGNOSTICS v_rows = ROW_COUNT;
    RAISE NOTICE 'Deleted % rows from fam_privilege_change_audit', v_rows;
END $$;

-- application_client
DO $$
DECLARE v_rows INT;
BEGIN
    DELETE FROM app_fam.fam_application_client
    WHERE application_id IN (
        SELECT application_id
        FROM app_fam.fam_application
        WHERE application_name LIKE 'APT3_%'
    );

    GET DIAGNOSTICS v_rows = ROW_COUNT;
    RAISE NOTICE 'Deleted % rows from fam_application_client', v_rows;
END $$;

-- =====================================================
-- 4. PARENT TABLES
-- =====================================================

-- roles
DO $$
DECLARE v_rows INT;
BEGIN
    DELETE FROM app_fam.fam_role
    WHERE application_id IN (
        SELECT application_id
        FROM app_fam.fam_application
        WHERE application_name LIKE 'APT3_%'
    );

    GET DIAGNOSTICS v_rows = ROW_COUNT;
    RAISE NOTICE 'Deleted % rows from fam_role', v_rows;
END $$;

-- applications (LAST)
DO $$
DECLARE v_rows INT;
BEGIN
    DELETE FROM app_fam.fam_application
    WHERE application_name LIKE 'APT3_%';

    GET DIAGNOSTICS v_rows = ROW_COUNT;
    RAISE NOTICE 'Deleted % rows from fam_application', v_rows;
END $$;

-- =====================================================
-- 5. FINAL LOG
-- =====================================================

DO $$ BEGIN
    RAISE NOTICE '=== APT3 CLEANUP DELETE COMPLETED ===';
END $$;
