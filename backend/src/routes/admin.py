from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.database.database import get_db
from src.routes.user import require_admin
from src.schemas.user import UserRead, UserUpdate
from src.services.user_service import get_user_by_id, list_users, soft_delete_user, update_user

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get(
    "/users",
    response_model=list[UserRead],
    summary="Listar usuarios",
    description="Devuelve usuarios del sistema para gestión administrativa.",
)
def admin_list_users(
    include_deleted: bool = Query(False),
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    return list_users(db, include_deleted=include_deleted)


@router.get(
    "/users/{user_id}",
    response_model=UserRead,
    summary="Detalle de usuario",
    description="Obtiene detalle de un usuario específico, incluso si está inactivo.",
)
def admin_get_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    return get_user_by_id(user_id, db, include_deleted=True)


@router.put(
    "/users/{user_id}",
    response_model=UserRead,
    summary="Editar usuario",
    description="Actualiza datos de cuenta y estado activo/inactivo.",
)
def admin_update_user(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    return update_user(user_id, payload, db)


@router.delete(
    "/users/{user_id}",
    summary="Soft delete de usuario",
    description="Desactiva usuario y marca deleted_at sin borrado físico.",
)
def admin_delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    return soft_delete_user(user_id, db)
