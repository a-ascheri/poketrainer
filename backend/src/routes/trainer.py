from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.routes.user import require_admin
from src.schemas.trainer import TrainerCreate, TrainerRead, TrainerUpdate
from src.services.trainer_service import (create_trainer, delete_trainer,
                                          list_trainers, update_trainer)

from ..database.database import get_db

router = APIRouter(tags=["Trainer"])


@router.post("/trainers/", response_model=TrainerRead)
def create_trainer_route(
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
    return create_trainer(trainer, db)


@router.get("/trainers/", response_model=list[TrainerRead])
def list_trainers_route(db: Session = Depends(get_db), admin=Depends(require_admin)):
    """
    Lista todos los entrenadores registrados en el sistema.

    Args:
        db (Session): Sesión de base de datos.
        admin: Dependencia para requerir permisos de administrador.

    Returns:
        list[TrainerRead]: Lista de entrenadores.
    """
    return list_trainers(db)


@router.put("/trainers/{trainer_id}", response_model=TrainerRead)
def update_trainer_route(
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
    return update_trainer(trainer_id, trainer_update, db)


@router.delete("/trainers/{trainer_id}")
def delete_trainer_route(
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
    return delete_trainer(trainer_id, db)
