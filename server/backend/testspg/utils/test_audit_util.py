from unittest.mock import MagicMock

from api.app.constants import UserType
from api.app.utils.audit_util import AuditEventLog


def mock_requester(user_guid="requester-guid", user_type_code=UserType.IDIR, user_name="requester_name"):
    requester = MagicMock()
    requester.user_guid = user_guid
    requester.user_type_code = user_type_code
    requester.user_name = user_name
    return requester


def mock_target_user(user_guid="requester-guid", user_type_code=UserType.IDIR):
    target_user = MagicMock()
    target_user.user_guid = user_guid
    target_user.user_type_code = user_type_code
    return target_user


def mock_assignment_result(user_name="requester_name", user_type_code=UserType.IDIR, has_detail=True):
    result = MagicMock()
    if not has_detail:
        result.detail = None
        return result
    result.detail.user.user_name = user_name
    result.detail.user.user_type_relation.user_type_code = user_type_code
    return result


def test_is_self_action_false_when_no_requesting_user():
    audit_event_log = AuditEventLog(requesting_user=None)
    assert audit_event_log.is_self_action() is False


def test_is_self_action_true_for_matching_target_user():
    requester = mock_requester()
    audit_event_log = AuditEventLog(
        requesting_user=requester,
        target_user=mock_target_user(user_guid=requester.user_guid, user_type_code=requester.user_type_code),
    )
    assert audit_event_log.is_self_action() is True


def test_is_self_action_false_for_different_target_user():
    requester = mock_requester()
    audit_event_log = AuditEventLog(
        requesting_user=requester,
        target_user=mock_target_user(user_guid="someone-else-guid", user_type_code=requester.user_type_code),
    )
    assert audit_event_log.is_self_action() is False


def test_is_self_action_true_when_requester_in_batch_assignment_results():
    requester = mock_requester()
    audit_event_log = AuditEventLog(
        requesting_user=requester,
        user_assignment_results=[
            mock_assignment_result(user_name="someone_else", user_type_code=requester.user_type_code),
            mock_assignment_result(user_name=requester.user_name, user_type_code=requester.user_type_code),
        ],
    )
    assert audit_event_log.is_self_action() is True


def test_is_self_action_false_when_requester_not_in_batch_assignment_results():
    requester = mock_requester()
    audit_event_log = AuditEventLog(
        requesting_user=requester,
        user_assignment_results=[
            mock_assignment_result(user_name="someone_else", user_type_code=requester.user_type_code),
            mock_assignment_result(has_detail=False),
        ],
    )
    assert audit_event_log.is_self_action() is False


def test_is_self_action_false_when_batch_assignment_results_empty():
    audit_event_log = AuditEventLog(
        requesting_user=mock_requester(),
        user_assignment_results=[],
    )
    assert audit_event_log.is_self_action() is False
