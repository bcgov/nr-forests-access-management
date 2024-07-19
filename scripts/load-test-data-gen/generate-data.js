
/*
Design: this script generates a 1-year realistic volume of data under a fake test application
(which allows for easier cleanup and regeneration). See https://apps.nrs.gov.bc.ca/int/confluence/display/FSAST1/Load+Testing for details

Record Counts
Application: 1

Users: 10,500
Concrete Roles: 5100 (based on a pool of 1000+ forest clients)
Role Assignments: 10,200

*/

const createUser = 'loadtest';

const minId = 1000;
const appId = minId;

const users = [];
const roles = [];
const clientNumbers = [];


function generateDeletes() {
    console.log(`
DELETE FROM app_fam.fam_user_role_xref where user_role_xref_id between 1000 and 99999;
DELETE FROM app_fam.fam_user_role_xref urx where urx.role_id in (select role_id from app_fam.fam_role where application_id = ${appId});
DELETE FROM app_fam.fam_role where application_id = ${appId};
DELETE FROM app_fam.fam_forest_client where client_number_id between 1000 and 99999;

DELETE FROM app_fam.fam_application_admin where application_id = ${appId};
DELETE FROM app_fam.fam_access_control_privilege acp where acp.role_id in (select role_id from app_fam.fam_role where application_id = ${appId});

DELETE FROM app_fam.fam_application where application_id = ${appId};
DELETE FROM app_fam.fam_user where user_id between 1000 and 99999;
    `);
}

function generateSequenceUpdates() {
    console.log(`
ALTER SEQUENCE app_fam.fam_user_role_xref_user_role_xref_id_seq RESTART WITH 100000;
ALTER SEQUENCE app_fam.fam_role_role_id_seq RESTART WITH 100000;
ALTER SEQUENCE app_fam.fam_forest_client_client_number_id_seq RESTART WITH 100000;
ALTER SEQUENCE app_fam.fam_application_application_id_seq RESTART WITH 100000;
ALTER SEQUENCE app_fam.fam_user_user_id_seq RESTART WITH 100000;
        `);
}

function generateApplication() {
    console.log(`INSERT INTO app_fam.fam_application (application_id, application_name, application_description, app_environment, create_user)
    VALUES (${appId}, 'LOAD_TEST', 'Fake application for load testing with realistic data volumes', 'TEST', '${createUser}' );
    `)
}

function generateForestClients() {
    console.log(`INSERT INTO app_fam.fam_forest_client (client_number_id, forest_client_number, create_user) OVERRIDING SYSTEM VALUE VALUES`);

    var clientNumberId = minId;

    const forestClientCount = 1000;
    for (var i = 0; i < forestClientCount; i++) {
        prefix = ',';
        if (i == 0) {
            prefix = '';
        }
        clientNumber = `9999${clientNumberId}`;
        console.log(`${prefix}(${clientNumberId}, '${clientNumber}', '${createUser}')`);
        clientNumbers.push(clientNumber);
        clientNumberId++;
    }

    console.log(`;`);
}

function generateRoles() {
    console.log(`INSERT INTO app_fam.fam_role (role_id, role_name, role_purpose, application_id, parent_role_id, role_type_code, create_user) OVERRIDING SYSTEM VALUE VALUES`);

    var roleId = minId;

    var abstractRoleNames = []
    var abstractRoleIds = []
    const totalRoles = 5100;
    const abstractRoleCount = (totalRoles / clientNumbers.length);

    for (var i = 0; i < abstractRoleCount; i++) {
        prefix = ',';
        if (i == 0) {
            prefix = '';
        }
        var abstractRoleName = `LOAD_TESTER_${i}`
        console.log(`${prefix}( ${roleId}, '${abstractRoleName}', 'Fake abstract role for load testing', ${appId}, null, 'A', '${createUser}')`);
        abstractRoleNames.push(abstractRoleName);
        abstractRoleIds.push(roleId);
        roleId++;
    }

    for (var r = 0; r < abstractRoleNames.length; r++) {
        for (var i = 0; i < clientNumbers.length; i++) {
            var clientNumber = clientNumbers[i];
            console.log(`,( ${roleId}, '${abstractRoleNames[r]}_${clientNumber}', 'Fake concrete role for load testing', ${appId}, ${abstractRoleIds[r]},'C', '${createUser}')`);
            roles.push(roleId);
            roleId++;
        }
    }

    console.log(`;`);
}

function generateUsers() {
    console.log(`INSERT INTO app_fam.fam_user (user_id, user_guid, cognito_user_id, user_name, user_type_code, business_guid, create_user) OVERRIDING SYSTEM VALUE VALUES`);

    var userId = minId;

    const userCount = 10500;
    for (var i = 0; i < userCount; i++) {
        prefix = ',';
        if (i == 0) {
            prefix = ' ';
        }
        // User GUID must be exactly 32 characters
        var userPrefix = userId.toString().padStart(5,"0")
        var userGuid = `${userPrefix}ABCD1234ABCD1234ABCD1234ABC`
        // User name must be max 20 characters
        var userName = `FAKE_LOAD_TEST_${userPrefix}`

        console.log(`${prefix}( ${userId}, '${userGuid}', 'test-idir_${userId}_load_test', '${userName}', 'I', '${userId}ABCD1234ABCD', '${createUser}')`);
        users.push(userId);
        userId++;
    }

    console.log(`;`);

}

function generateAssignments() {

    console.log(`INSERT INTO app_fam.fam_user_role_xref (user_role_xref_id, user_id, role_id, create_user) OVERRIDING SYSTEM VALUE VALUES`);

    var xrefId = minId;

    const assignmentsCount = 10200;
    for (var i = 0; i < assignmentsCount; i++) {
        prefix = ',';
        if (i == 0) {
            prefix = '';
        }
        var userId = users[i % users.length];
        var roleId = roles[i % roles.length];
        console.log(`${prefix}( ${xrefId}, '${userId}', '${roleId}', '${createUser}')`);
        xrefId++;
    }

    console.log(`;`);

}

function generateAppAdmins() {

    var admins = [ 'BVANDEGR', 'IANLIU', 'CMENG', 'OLIBERCH'];

    for (var i = 0; i < admins.length; i++) {
        console.log(`INSERT INTO app_fam.fam_application_admin (user_id, application_id, create_user) values ( (SELECT user_id FROM app_fam.fam_user WHERE user_name = '${admins[i]}' and user_type_code = 'I'), ${appId}, '${createUser}');`);
    }

}

generateDeletes();
generateUsers();
generateApplication();
generateForestClients();
generateRoles();
generateAssignments();
generateAppAdmins();
generateSequenceUpdates();
