
from sqlalchemy.orm import Session
from api.app.models import model as models


def get_user_role_by_cognito_user_id_and_role_id(
    db: Session, cognito_user_id: str, role_id: int
) -> models.FamUserRoleXref:
    user_role = (
        db.query(models.FamUserRoleXref)
        .join(models.FamUser)
        .filter(
            models.FamUser.cognito_user_id == cognito_user_id,
            models.FamUserRoleXref.role_id == role_id,
        )
        .one_or_none()
    )
    return user_role
