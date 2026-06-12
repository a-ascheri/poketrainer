from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.database.database import get_db
from src.routes.auth_dependencies import require_admin
from src.routes.prefixes import ADMIN_PREFIX
from src.schemas.user import AdminCreate, UserRead, UserUpdate
from src.services.user_service import (create_admin_user, get_user_by_id,
                                       list_users, soft_delete_user,
                                       update_user)

router = APIRouter(prefix=ADMIN_PREFIX, tags=["Admin"])


@router.get(
    "/users",
    response_model=list[UserRead],
)
def admin_list_users(
    include_deleted: bool = Query(False),
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    """
    Lista todos los usuarios del sistema para gestión administrativa.

    Args:
        include_deleted (bool): Si es True, incluye usuarios eliminados lógicamente.
        db (Session): Sesión de base de datos.
        admin: Dependencia para requerir permisos de administrador.

    Returns:
        list[UserRead]: Lista de usuarios.
    """
    return list_users(db, include_deleted=include_deleted)


@router.get(
    "/users/{user_id}",
    response_model=UserRead,
)
def admin_get_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    """
    Obtiene el detalle de un usuario específico, incluso si está inactivo.

    Args:
        user_id (int): ID del usuario a consultar.
        db (Session): Sesión de base de datos.
        admin: Dependencia para requerir permisos de administrador.

    Returns:
        UserRead: Detalle del usuario.
    """
    return get_user_by_id(user_id, db, include_deleted=True)


@router.put(
    "/users/{user_id}",
    response_model=UserRead,
)
def admin_update_user(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    """
    Actualiza los datos de un usuario existente.

    Args:
        user_id (int): ID del usuario a actualizar.
        payload (UserUpdate): Datos nuevos del usuario.
        db (Session): Sesión de base de datos.
        admin: Dependencia para requerir permisos de administrador.

    Returns:
        UserRead: Usuario actualizado.
    """
    return update_user(user_id, payload, db)


@router.delete(
    "/users/{user_id}",
)
def admin_delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    """
    Realiza un borrado lógico (soft delete) de un usuario.

    Args:
        user_id (int): ID del usuario a desactivar.
        db (Session): Sesión de base de datos.
        admin: Dependencia para requerir permisos de administrador.

    Returns:
        UserRead: Usuario desactivado.
    """
    return soft_delete_user(user_id, db)


@router.post("/internal/admins", response_model=UserRead, include_in_schema=False)
def create_admin(
    payload: AdminCreate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    """
    Crea un usuario administrador para bootstrap interno.

    Args:
        payload (AdminCreate): Datos del admin a crear.
        db (Session): Sesion de base de datos.
        admin: Dependencia para requerir permisos de administrador.

    Returns:
        UserRead: Admin creado.
    """
    return create_admin_user(payload, db)
