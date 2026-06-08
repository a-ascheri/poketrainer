from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.routes.auth_dependencies import require_admin
from src.routes.prefixes import ADMIN_TRAINER_PREFIX
from src.schemas.trainer import TrainerCreate, TrainerRead, TrainerUpdate
from src.services.trainer_service import create_trainer as create_trainer_service
from src.services.trainer_service import delete_trainer as delete_trainer_service
from src.services.trainer_service import list_trainers as list_trainers_service
from src.services.trainer_service import update_trainer as update_trainer_service

from ..database.database import get_db

router = APIRouter(prefix=ADMIN_TRAINER_PREFIX, tags=["Admin"])


@router.post("/", response_model=TrainerRead)
def create_trainer(
    trainer: TrainerCreate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    """
    Crea un nuevo entrenador en el sistema.

    Args:
        trainer (TrainerCreate): Datos del entrenador a crear.
        db (Session): Sesión de base de datos.
        admin: Dependencia para requerir permisos de administrador.

    Returns:
        TrainerRead: Entrenador creado.
    """
    return create_trainer_service(trainer, db)


@router.get("/", response_model=list[TrainerRead])
def list_trainers(db: Session = Depends(get_db), admin=Depends(require_admin)):
    """
    Lista todos los entrenadores registrados en el sistema.

    Args:
        db (Session): Sesión de base de datos.
        admin: Dependencia para requerir permisos de administrador.

    Returns:
        list[TrainerRead]: Lista de entrenadores.
    """
    return list_trainers_service(db)


@router.put("/{trainer_id}", response_model=TrainerRead)
def update_trainer(
    trainer_id: int,
    trainer_update: TrainerUpdate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    """
    Actualiza los datos de un entrenador existente.

    Args:
        trainer_id (int): ID del entrenador a actualizar.
        trainer_update (TrainerUpdate): Datos nuevos del entrenador.
        db (Session): Sesión de base de datos.
        admin: Dependencia para requerir permisos de administrador.

    Returns:
        TrainerRead: Entrenador actualizado.
    """
    return update_trainer_service(trainer_id, trainer_update, db)


@router.delete("/{trainer_id}")
def delete_trainer(
    trainer_id: int, db: Session = Depends(get_db), admin=Depends(require_admin)
):
    """
    Elimina un entrenador del sistema.

    Args:
        trainer_id (int): ID del entrenador a eliminar.
        db (Session): Sesión de base de datos.
        admin: Dependencia para requerir permisos de administrador.

    Returns:
        TrainerRead: Entrenador eliminado.
    """
    return delete_trainer_service(trainer_id, db)
