from sqlalchemy.orm import Session
from api.app.models import FamUserRoleXrefModel, FamUserModel


def get_user_role_by_cognito_user_id_and_role_id(
    db: Session, cognito_user_id: str, role_id: int
) -> FamUserRoleXrefModel:
    user_role = (
        db.query(FamUserRoleXrefModel)
        .join(FamUserModel)
        .filter(
            FamUserModel.cognito_user_id == cognito_user_id,
            FamUserRoleXrefModel.role_id == role_id,
        )
        .one_or_none()
    )
    return user_role
