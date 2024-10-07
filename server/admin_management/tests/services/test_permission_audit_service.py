import copy
import logging
from http import HTTPStatus
from typing import List

import pytest
from api.app.constants import (ERROR_CODE_UNKNOWN_STATE,
                               PrivilegeChangeTypeEnum,
                               PrivilegeDetailsPermissionTypeEnum,
                               PrivilegeDetailsScopeTypeEnum, UserType)
from api.app.integration.forest_client_integration import \
    ForestClientIntegrationService
from api.app.models.model import (FamAccessControlPrivilege, FamApplication,
                                  FamForestClient, FamPrivilegeChangeAudit,
                                  FamRole, FamUser)
from api.app.schemas.schemas import (FamAccessControlPrivilegeCreateResponse,
                                     FamAccessControlPrivilegeGetResponse,
                                     FamApplicationBase, FamForestClientBase,
                                     FamRoleBase, FamRoleWithClientDto,
                                     FamUserInfoDto, FamUserTypeDto, Requester)
from api.app.services.permission_audit_service import PermissionAuditService
from fastapi import HTTPException
from mock import patch
from sqlalchemy.orm import Session
from tests.constants import (MOCK_FIND_CLIENT_00001011_RETURN,
                             TEST_APPLICATION_ID_FOM_DEV, TEST_USER_GUID_BCEID,
                             TEST_USER_NAME_BCEID)

LOGGER = logging.getLogger(__name__)

def test_store_delegated_admin_audit_history_granted_role_no_scope(
	db_pg_session: Session,
	permission_audit_service: PermissionAuditService,
	setup_new_user,
	new_idir_requester,
	mocker
):
	"""
	Test service saving delegated admin permission granted history on role change with no scope.
	"""
	# setup performer and change_target_user
	performer: Requester = new_idir_requester
	change_target_user: FamUser = setup_new_user(
		UserType.BCEID,
		TEST_USER_NAME_BCEID,
		TEST_USER_GUID_BCEID
	)
	mock_delegated_admin_permission_granted_list = [copy.copy(sample_delegated_admin_permission_granted_no_scope_details)]
	delegated_admin_privliege_granted_details_fn_spy = mocker.spy(PermissionAuditService, 'to_delegated_admin_privliege_granted_details')
	change_performer_user_details_fn_spy = mocker.spy(PermissionAuditService, 'to_change_performer_user_details')

	# test the service: granting delegagted admin user role with no scope.
	permission_audit_service.store_delegated_admin_permissions_granted_audit_history(
		performer, change_target_user, mock_delegated_admin_permission_granted_list
	)

	# find the audit record and verify
	audit_record = db_pg_session.query(FamPrivilegeChangeAudit).filter(
		FamPrivilegeChangeAudit.application_id == mock_delegated_admin_permission_granted_list[0].detail.role.application.application_id,
		FamPrivilegeChangeAudit.change_performer_user_id == performer.user_id,
		FamPrivilegeChangeAudit.change_target_user_id == change_target_user.user_id
	).one()
	assert audit_record is not None
	assert change_performer_user_details_fn_spy.call_count == 1
	assert delegated_admin_privliege_granted_details_fn_spy.call_count == 1
	assert audit_record.privilege_change_type_code == PrivilegeChangeTypeEnum.GRANT
	assert audit_record.change_target_user_id == change_target_user.user_id
	verify_change_performer_user(audit_record, performer)
	verify_delegated_admin_user_granted_privilege_details(audit_record, mock_delegated_admin_permission_granted_list)


def test_store_delegated_admin_audit_history_nosaving_when_no_success_permission_granted(
	db_pg_session: Session,
	permission_audit_service: PermissionAuditService,
	setup_new_user,
	new_idir_requester
):
	"""
	Test service saving delegated admin permission granted history but no success granted permission
	return from execution. Should have no audit record saved.
	"""
	performer: Requester = new_idir_requester
	change_target_user: FamUser = setup_new_user(
		UserType.BCEID,
		TEST_USER_NAME_BCEID,
		TEST_USER_GUID_BCEID
	)
	mock_delegated_admin_permission_granted_list = [copy.copy(sample_delegated_admin_permission_granted_no_scope_details)]
	# setup all responses to no success
	for item in mock_delegated_admin_permission_granted_list:
		item.status_code = HTTPStatus.CONFLICT

	# test the service: granting delegated admin user role with no scope.
	permission_audit_service.store_delegated_admin_permissions_granted_audit_history(
		performer, change_target_user, mock_delegated_admin_permission_granted_list
	)

	# find the audit record and verify
	audit_record = db_pg_session.query(FamPrivilegeChangeAudit).filter(
		FamPrivilegeChangeAudit.application_id == mock_delegated_admin_permission_granted_list[0].detail.role.application.application_id,
		FamPrivilegeChangeAudit.change_performer_user_id == performer.user_id,
		FamPrivilegeChangeAudit.change_target_user_id == change_target_user.user_id
	).one_or_none()
	assert audit_record is None


def test_store_delegated_admin_audit_history_granted_role_with_client_scopes(
	db_pg_session: Session,
	permission_audit_service: PermissionAuditService,
	setup_new_user,
	new_idir_requester,
	mocker
):
	"""
	Test service saving delegated admin permission granted history
	on role change with 'CLIENT' scopes.
	"""
	performer: Requester = new_idir_requester
	change_target_user: FamUser = setup_new_user(
		UserType.BCEID,
		TEST_USER_NAME_BCEID,
		TEST_USER_GUID_BCEID
	)
	mock_delegated_admin_permission_granted_list = [copy.copy(sample_delegated_admin_permission_granted_with_scope_details)]
	delegated_admin_privliege_granted_details_fn_spy = mocker.spy(PermissionAuditService, 'to_delegated_admin_privliege_granted_details')
	change_performer_user_details_fn_spy = mocker.spy(PermissionAuditService, 'to_change_performer_user_details')

	# test the service: granting delegated admin role with scopes.
	permission_audit_service.store_delegated_admin_permissions_granted_audit_history(
		performer, change_target_user, mock_delegated_admin_permission_granted_list
	)

	# find the audit record and verify
	audit_records = db_pg_session.query(FamPrivilegeChangeAudit).filter(
		FamPrivilegeChangeAudit.application_id == mock_delegated_admin_permission_granted_list[0].detail.role.application.application_id,
		FamPrivilegeChangeAudit.change_performer_user_id == performer.user_id,
		FamPrivilegeChangeAudit.change_target_user_id == change_target_user.user_id
	).all()

	assert len(audit_records) == len(mock_delegated_admin_permission_granted_list)
	assert change_performer_user_details_fn_spy.call_count == 1
	assert delegated_admin_privliege_granted_details_fn_spy.call_count == 1
	for record in audit_records:
		assert record.privilege_change_type_code == PrivilegeChangeTypeEnum.GRANT
		assert record.change_target_user_id == change_target_user.user_id
		verify_change_performer_user(record, performer)
		verify_delegated_admin_user_granted_privilege_details(record, mock_delegated_admin_permission_granted_list)


def test_store_delegated_admin_audit_history_revoke_role_no_scopes(
	db_pg_session: Session,
	permission_audit_service: PermissionAuditService,
	setup_new_user,
	new_idir_requester,
	mocker
):
	"""
	Test service saving delegated admin permission revoked history
	on role change with no scope.
	"""
	performer: Requester = new_idir_requester
	change_target_user: FamUser = setup_new_user(
		UserType.BCEID,
		TEST_USER_NAME_BCEID,
		TEST_USER_GUID_BCEID
	)
	mock_delete_record = copy.copy(sameple_delegated_admin_role_with_no_client_revoked_record)
	mock_delete_record.user = change_target_user
	delegated_admin_privliege_revoked_details_fn_spy = mocker.spy(PermissionAuditService, 'to_delegated_admin_privliege_revoked_details')
	change_performer_user_details_fn_spy = mocker.spy(PermissionAuditService, 'to_change_performer_user_details')

	# test the service: revoke delegated admin role with no scope.
	permission_audit_service.store_delegated_admin_permissions_revoked_audit_history(performer, mock_delete_record)

	# find the audit record and verify
	audit_record = db_pg_session.query(FamPrivilegeChangeAudit).filter(
		FamPrivilegeChangeAudit.application_id == mock_delete_record.role.application.application_id,
		FamPrivilegeChangeAudit.change_performer_user_id == performer.user_id,
		FamPrivilegeChangeAudit.change_target_user_id == change_target_user.user_id
	).one()
	assert audit_record is not None
	assert delegated_admin_privliege_revoked_details_fn_spy.call_count == 1
	assert change_performer_user_details_fn_spy.call_count == 1
	assert audit_record.privilege_change_type_code == PrivilegeChangeTypeEnum.REVOKE
	assert audit_record.change_target_user_id == change_target_user.user_id
	verify_change_performer_user(audit_record, performer)
	verify_delegated_admin_revoked_privilege_details(audit_record, mock_delete_record)


def test_store_delegated_admin_audit_history_revoke_role_with_client_scopes(
	mock_forest_client_integration_service: ForestClientIntegrationService,
	permission_audit_service: PermissionAuditService,
	db_pg_session: Session,
	setup_new_user,
	new_idir_requester,
	mocker
):
	"""
	Test service saving delegated admin permission revoked history
	on role change with 'CLIENT' scope.
	"""
	performer = new_idir_requester
	change_target_user: FamUser = setup_new_user(
		UserType.BCEID,
		TEST_USER_NAME_BCEID,
		TEST_USER_GUID_BCEID
	)
	mock_delete_record = copy.copy(sameple_delegated_admin_role_with_client_revoked_record)
	mock_delete_record.user_id = change_target_user.user_id
	mock_delete_record.user = change_target_user
	mock_forest_client_number = "00001011"
	mock_delete_record.role.client_number.forest_client_number = mock_forest_client_number
	mock_delete_record.role.role_name = f"FOM_SUBMITTER_{mock_forest_client_number}"
	mock_forest_client_integration_service.find_by_client_number.return_value = MOCK_FIND_CLIENT_00001011_RETURN

	enduser_privliege_revoked_details_fn_spy = mocker.spy(PermissionAuditService, 'to_delegated_admin_privliege_revoked_details')
	change_performer_user_details_fn_spy = mocker.spy(PermissionAuditService, 'to_change_performer_user_details')
	forest_client_integration_fn_spy = mocker.spy(ForestClientIntegrationService, 'find_by_client_number')

	# test the service: revoking end user role with scopes.
	permission_audit_service.store_delegated_admin_permissions_revoked_audit_history(performer, mock_delete_record)

	# find the audit record and verify
	audit_record = db_pg_session.query(FamPrivilegeChangeAudit).filter(
		FamPrivilegeChangeAudit.application_id == mock_delete_record.role.application.application_id,
		FamPrivilegeChangeAudit.change_performer_user_id == performer.user_id,
		FamPrivilegeChangeAudit.change_target_user_id == change_target_user.user_id
	).one()
	assert audit_record is not None
	assert enduser_privliege_revoked_details_fn_spy.call_count == 1
	assert change_performer_user_details_fn_spy.call_count == 1
	assert forest_client_integration_fn_spy.call_count == 1
	assert audit_record.privilege_change_type_code == PrivilegeChangeTypeEnum.REVOKE
	assert audit_record.change_target_user_id == change_target_user.user_id
	verify_change_performer_user(audit_record, performer)
	verify_delegated_admin_revoked_privilege_details(audit_record, mock_delete_record)


def test_store_delegated_admin_audit_history_revoke_role_client_search_error(
	mock_forest_client_integration_service: ForestClientIntegrationService,
	db_pg_session: Session,
	setup_new_user,
	new_idir_requester,
	permission_audit_service: PermissionAuditService,
	mocker
):
	"""
	Test service saving user permission revoked history on role change with 'CLIENT' scope
	but with scenario that forest client number is not found (unknown reason) from
	FC integration external service. Exception should be raised and no audit record is saved.
	"""
	performer : Requester = new_idir_requester
	change_target_user: FamUser = setup_new_user(
		UserType.BCEID,
		TEST_USER_NAME_BCEID,
		TEST_USER_GUID_BCEID
	)
	mock_delete_record = copy.copy(sameple_delegated_admin_role_with_notfound_client_revoked_record)
	mock_forest_client_integration_service.find_by_client_number.return_value = [] # FC external service result not found.
	forest_client_integration_fn_spy = mocker.spy(ForestClientIntegrationService, 'find_by_client_number')

	with pytest.raises(HTTPException) as e:
		permission_audit_service.store_delegated_admin_permissions_revoked_audit_history(performer, mock_delete_record)

	assert str(e.value.detail.get("code")).find(ERROR_CODE_UNKNOWN_STATE) != -1
	error_msg = (
		"Revoke delegated admin permission encountered problem."
		+ f"Unknown forest client number {mock_delete_record.role.client_number.forest_client_number} for "
		+ f"scoped permission {mock_delete_record.role.role_name}."
	)
	assert str(e.value.detail.get("description")).find(error_msg) != -1
	assert forest_client_integration_fn_spy.call_count == 1
	# find the audit record and verify
	audit_record = db_pg_session.query(FamPrivilegeChangeAudit).filter(
		FamPrivilegeChangeAudit.application_id == mock_delete_record.role.application.application_id,
		FamPrivilegeChangeAudit.change_performer_user_id == performer.user_id,
		FamPrivilegeChangeAudit.change_target_user_id == change_target_user.user_id
	).one_or_none()
	assert audit_record is None


def verify_change_performer_user(audit_record: FamPrivilegeChangeAudit, performer: FamUser):
	audit_record.change_performer_user_id == performer.user_id
	change_performer_user_details_dict = audit_record.change_performer_user_details
	assert change_performer_user_details_dict["username"] == performer.user_name
	assert change_performer_user_details_dict["first_name"] == performer.first_name
	assert change_performer_user_details_dict["last_name"] == performer.last_name
	assert change_performer_user_details_dict["email"] == performer.email


def verify_delegated_admin_user_granted_privilege_details(
	audit_record: FamPrivilegeChangeAudit,
	mock_delegated_admin_permission_granted_list: List[FamAccessControlPrivilegeCreateResponse]
):
	audit_privilege_details_dict = audit_record.privilege_details
	assert audit_privilege_details_dict["permission_type"] == PrivilegeDetailsPermissionTypeEnum.DELEGATED_ADMIN
	assert len(audit_privilege_details_dict["roles"]) != 0
	audit_role = audit_privilege_details_dict["roles"][0] # FAM can grant 1 role at a time for now.
	granted_role = mock_delegated_admin_permission_granted_list[0].detail.role
	assert audit_role["role"] == granted_role.display_name
	audit_scopes = audit_role.get("scopes")
	if granted_role.client_number is None:
		# "scopes" attribute is not present  in json structure if the granted role has no scope.
		assert audit_scopes is None

	else:
		assert len(audit_scopes) == len(mock_delegated_admin_permission_granted_list)
		org_id_list = list(map(
			lambda item: item.detail.role.client_number.forest_client_number, mock_delegated_admin_permission_granted_list
		))
		for scope in audit_scopes:
			scope.get("scope_type") == PrivilegeDetailsScopeTypeEnum.CLIENT  # Current FAM supports 'CLIENT' type only, more in future.
			scope.get("client_id") in org_id_list


def verify_delegated_admin_revoked_privilege_details(
	audit_record: FamPrivilegeChangeAudit,
	mock_delete_record: FamAccessControlPrivilege
):
	audit_privilege_details_dict = audit_record.privilege_details
	assert audit_privilege_details_dict["permission_type"] == PrivilegeDetailsPermissionTypeEnum.DELEGATED_ADMIN
	assert len(audit_privilege_details_dict["roles"]) != 0
	audit_role = audit_privilege_details_dict["roles"][0] # FAM can revoke 1 role at a time for now.
	revoked_role = mock_delete_record.role
	assert audit_role["role"] == revoked_role.display_name
	audit_scopes = audit_role.get("scopes")
	if not revoked_role.client_number_id:
		# "scopes" attribute is not present if the revoked role has no scopes.
		assert audit_scopes is None

	else:
		assert len(audit_scopes) == 1  # Fam can revoke role with 1 org at a time.
		org_id = revoked_role.client_number_id
		scope = audit_scopes[0]
		scope.get("scope_type") == PrivilegeDetailsScopeTypeEnum.CLIENT  # Current FAM supports 'CLIENT' type only, more in future.
		scope.get("client_id") == org_id


# sample end user permission granted response - role with no scope
sample_delegated_admin_permission_granted_no_scope_details = FamAccessControlPrivilegeCreateResponse(
	**{'status_code': HTTPStatus.OK,
		'detail': FamAccessControlPrivilegeGetResponse(
		access_control_privilege_id=999, user_id=9, role_id=4,
		user=FamUserInfoDto(user_name='dadminuser', first_name='first', last_name='last', email='a@b.com',
			user_type_relation=FamUserTypeDto(user_type_code=UserType.BCEID, description='BCEID')),
		role=FamRoleWithClientDto(role_name='FOM_REVIEWER',
		application=FamApplicationBase(application_id=2, application_name='FOM_DEV', application_description='Forest Operations Map (DEV)'),
		role_id=999, display_name='Reviewer', role_purpose='Provides the privilege to review all FOMs in the system', client_number=None, parent_role=None)),
		'error_message': None
	}
 )

# sample delegated admin permission granted response - role with forest_client scope
sample_delegated_admin_permission_granted_with_scope_details = FamAccessControlPrivilegeCreateResponse(
	**{'status_code': HTTPStatus.OK,
		'detail': FamAccessControlPrivilegeGetResponse(
		access_control_privilege_id=888, user_id=9, role_id=127,
		user=FamUserInfoDto(user_name='dadminuser', first_name='first', last_name='last', email='a@b.com',
			user_type_relation=FamUserTypeDto(user_type_code=UserType.BCEID, description='BCEID')),
		role=FamRoleWithClientDto(role_name='FOM_SUBMITTER_00001012',
		application=FamApplicationBase(application_id=2, application_name='FOM_DEV', application_description='Forest Operations Map (DEV)'),
		role_id=127, display_name='Submitter', role_purpose='Provides the privilege to submit a FOM (on behalf of a specific forest client)',
		client_number=FamForestClientBase(client_name=None, forest_client_number="00001012", status=None),
		parent_role=FamRoleBase(role_name="FOM_SUBMITTER", role_type_code="A",
			application=FamApplicationBase(application_id=2, application_name='FOM_DEV', application_description='Forest Operations Map (DEV)')))),
		'error_message': None
	}
 )

sameple_delegated_admin_role_with_no_client_revoked_record = FamAccessControlPrivilege(**{
	"user_id": 111, "role_id": 999,
	"user": FamUser(**{"user_id": 111}),
	"role": FamRole(** {"display_name": "Reviewer",
		"application": FamApplication(** {"application_id": TEST_APPLICATION_ID_FOM_DEV})
	})
})

sameple_delegated_admin_role_with_client_revoked_record = FamAccessControlPrivilege(**{
	"user_id": 111, "role_id": 999,
	"user": FamUser(**{"user_id": 111}),
	"role": FamRole(**{"display_name": "Submitter", "role_name": "FOM_SUBMITTER_00001011",
		"application": FamApplication(** {"application_id": TEST_APPLICATION_ID_FOM_DEV, }),
		"client_number_id": 3, "client_number": FamForestClient(**{
			"forest_client_number": "00001011"
		})
   })
})

sameple_delegated_admin_role_with_notfound_client_revoked_record = FamAccessControlPrivilege(**{
	"user_id": 111, "role_id": 999,
	"user": FamUser(**{"user_id": 111}),
	"role": FamRole(**{"display_name": "Submitter", "role_name": "FOM_SUBMITTER_09090909",
		"application": FamApplication(** {"application_id": TEST_APPLICATION_ID_FOM_DEV, }),
		"client_number_id": 3, "client_number": FamForestClient(**{
			"forest_client_number": "09090909"
		})
   })
})

