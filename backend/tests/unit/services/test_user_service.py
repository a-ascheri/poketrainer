import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone
from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.services.user_service import (
    get_password_hash,
    verify_password,
    _assert_unique_username_email,
    create_user,
    create_admin_user,
    ensure_initial_admin,
    list_users,
    get_user_by_id,
    update_user,
    soft_delete_user,
    change_password,
    authenticate_user,
    ADMIN_ROLE,
    TRAINER_ROLE,
    DEFAULT_ADMIN_PERMISSIONS,
)
from src.models.user import User
from src.schemas.user import UserCreate, AdminCreate, ChangePasswordInput, UserUpdate


class TestPasswordHashing:
    """Tests para funciones de hashing"""
    
    def test_get_password_hash(self):
        """Genera hash de contraseña"""
        hash_result = get_password_hash("mypassword")
        assert hash_result is not None
        assert hash_result != "mypassword"
        assert hash_result.startswith("$2b$")  # bcrypt format
    
    def test_verify_password_correct(self):
        """Verifica contraseña correcta"""
        hash_result = get_password_hash("mypassword")
        assert verify_password("mypassword", hash_result) is True
    
    def test_verify_password_incorrect(self):
        """Verifica contraseña incorrecta"""
        hash_result = get_password_hash("mypassword")
        assert verify_password("wrong", hash_result) is False


class TestAssertUniqueUsernameEmail:
    """Tests para _assert_unique_username_email"""
    
    def test_assert_unique_success(self, db_session):
        """Usuario nuevo - no hay conflicto"""
        # No debería lanzar excepción
        _assert_unique_username_email(db_session, "newuser", "new@email.com")
    
    def test_assert_unique_username_conflict(self, db_session):
        """Username ya existe - lanza 400"""
        # Crear usuario existente
        existing = User(
            username="existing",
            email="existing@email.com",
            hashed_password="hash",
            role=TRAINER_ROLE,
            permissions=[],
            is_active=True,
        )
        db_session.add(existing)
        db_session.commit()
        
        with pytest.raises(HTTPException) as exc_info:
            _assert_unique_username_email(db_session, "existing", "new@email.com")
        
        assert exc_info.value.status_code == 400
        assert "already registered" in str(exc_info.value.detail)
    
    def test_assert_unique_email_conflict(self, db_session):
        """Email ya existe - lanza 400"""
        existing = User(
            username="existing",
            email="existing@email.com",
            hashed_password="hash",
            role=TRAINER_ROLE,
            permissions=[],
            is_active=True,
        )
        db_session.add(existing)
        db_session.commit()
        
        with pytest.raises(HTTPException) as exc_info:
            _assert_unique_username_email(db_session, "newuser", "existing@email.com")
        
        assert exc_info.value.status_code == 400
    
    def test_assert_unique_skip_id(self, db_session):
        """Actualización - permite mismo username/email si es el mismo usuario"""
        user = User(
            username="testuser",
            email="test@email.com",
            hashed_password="hash",
            role=TRAINER_ROLE,
            permissions=[],
            is_active=True,
        )
        db_session.add(user)
        db_session.commit()
        
        # No debería lanzar excepción porque skip_id es el mismo usuario
        _assert_unique_username_email(db_session, "testuser", "test@email.com", skip_id=user.id)


class TestCreateUser:
    """Tests para create_user - cubre líneas 35-39, 118"""
    
    def test_create_user_success(self, db_session):
        """Crear usuario trainer exitosamente"""
        user_data = UserCreate(
            username="trainer1",
            email="trainer1@pokemon.com",
            password="password123"
        )
        
        result = create_user(user_data, db_session)
        
        assert result is not None
        assert result.username == "trainer1"
        assert result.email == "trainer1@pokemon.com"
        assert result.role == TRAINER_ROLE
        assert result.permissions == []
        assert result.force_password_change is False
        assert result.starter_pokemon_selected is False
        assert result.is_active is True
        assert result.deleted_at is None
        
        # Verificar que la contraseña está hasheada
        assert result.hashed_password != "password123"
        assert verify_password("password123", result.hashed_password) is True
    
    def test_create_user_duplicate_username(self, db_session):
        """Username duplicado - lanza 400"""
        user_data1 = UserCreate(
            username="trainer1",
            email="trainer1@pokemon.com",
            password="password123"
        )
        create_user(user_data1, db_session)
        
        user_data2 = UserCreate(
            username="trainer1",
            email="trainer2@pokemon.com",
            password="password456"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            create_user(user_data2, db_session)
        
        assert exc_info.value.status_code == 400
    
    def test_create_user_duplicate_email(self, db_session):
        """Email duplicado - lanza 400"""
        user_data1 = UserCreate(
            username="trainer1",
            email="shared@pokemon.com",
            password="password123"
        )
        create_user(user_data1, db_session)
        
        user_data2 = UserCreate(
            username="trainer2",
            email="shared@pokemon.com",
            password="password456"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            create_user(user_data2, db_session)
        
        assert exc_info.value.status_code == 400


class TestCreateAdminUser:
    """Tests para create_admin_user - cubre líneas 123-141, 154"""
    
    def test_create_admin_user_with_default_permissions(self, db_session):
        """Crear admin con permisos por defecto"""
        admin_data = AdminCreate(
            username="admin1",
            email="admin1@pokemon.com",
            password="adminpass"
        )
        
        result = create_admin_user(admin_data, db_session)
        
        assert result is not None
        assert result.username == "admin1"
        assert result.role == ADMIN_ROLE
        assert result.permissions == DEFAULT_ADMIN_PERMISSIONS
        assert result.force_password_change is True
        assert result.starter_pokemon_selected is True
        assert result.is_active is True
    
    def test_create_admin_user_with_custom_permissions(self, db_session):
        """Crear admin con permisos personalizados"""
        admin_data = AdminCreate(
            username="admin2",
            email="admin2@pokemon.com",
            password="adminpass",
            permissions=["manage_users", "manage_pokemon"]
        )
        
        result = create_admin_user(admin_data, db_session)
        
        assert result.permissions == ["manage_users", "manage_pokemon"]
    
    def test_create_admin_user_duplicate(self, db_session):
        """Admin duplicado - lanza 400"""
        admin_data1 = AdminCreate(
            username="admin1",
            email="admin1@pokemon.com",
            password="pass"
        )
        create_admin_user(admin_data1, db_session)
        
        admin_data2 = AdminCreate(
            username="admin1",
            email="admin2@pokemon.com",
            password="pass"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            create_admin_user(admin_data2, db_session)
        
        assert exc_info.value.status_code == 400


class TestEnsureInitialAdmin:
    """Tests para ensure_initial_admin"""
    
    def test_ensure_initial_admin_creates(self, db_session):
        """Crear admin inicial si no existe"""
        result = ensure_initial_admin(db_session)
        
        assert result is not None
        assert result.username == "originadmin"
        assert result.email == "originadmin@poketrainer.com"
        assert result.role == ADMIN_ROLE
        assert result.permissions == DEFAULT_ADMIN_PERMISSIONS
        assert result.force_password_change is True
    
    def test_ensure_initial_admin_exists(self, db_session):
        """Admin inicial ya existe - retorna existente"""
        # Primera llamada crea
        first = ensure_initial_admin(db_session)
        
        # Segunda llamada retorna el mismo
        second = ensure_initial_admin(db_session)
        
        assert first.id == second.id


class TestListUsers:
    """Tests para list_users - cubre líneas 175, 178"""
    
    def test_list_users_only_active(self, db_session):
        """Listar solo usuarios activos (no eliminados)"""
        # Crear usuarios activos
        user1 = User(username="active1", email="active1@test.com", hashed_password="hash", role=TRAINER_ROLE, permissions=[], is_active=True)
        user2 = User(username="active2", email="active2@test.com", hashed_password="hash", role=TRAINER_ROLE, permissions=[], is_active=True)
        db_session.add_all([user1, user2])
        
        # Crear usuario eliminado
        deleted = User(username="deleted", email="deleted@test.com", hashed_password="hash", role=TRAINER_ROLE, permissions=[], is_active=False, deleted_at=datetime.now(timezone.utc))
        db_session.add(deleted)
        db_session.commit()
        
        result = list_users(db_session, include_deleted=False)
        
        assert len(result) == 2
        assert all(u.deleted_at is None for u in result)
    
    def test_list_users_include_deleted(self, db_session):
        """Listar usuarios incluyendo eliminados"""
        user = User(username="user", email="user@test.com", hashed_password="hash", role=TRAINER_ROLE, permissions=[], is_active=True)
        deleted = User(username="deleted", email="deleted@test.com", hashed_password="hash", role=TRAINER_ROLE, permissions=[], is_active=False, deleted_at=datetime.now(timezone.utc))
        db_session.add_all([user, deleted])
        db_session.commit()
        
        result = list_users(db_session, include_deleted=True)
        
        assert len(result) == 2


class TestGetUserById:
    """Tests para get_user_by_id"""
    
    def test_get_user_by_id_success(self, db_session):
        """Obtener usuario por ID"""
        user = User(username="user1", email="user1@test.com", hashed_password="hash", role=TRAINER_ROLE, permissions=[], is_active=True)
        db_session.add(user)
        db_session.commit()
        
        result = get_user_by_id(user.id, db_session)
        
        assert result.id == user.id
        assert result.username == "user1"
    
    def test_get_user_by_id_not_found(self, db_session):
        """Usuario no existe - lanza 404"""
        with pytest.raises(HTTPException) as exc_info:
            get_user_by_id(999, db_session)
        
        assert exc_info.value.status_code == 404
    
    def test_get_user_by_id_deleted_excluded(self, db_session):
        """Usuario eliminado no se encuentra por defecto"""
        deleted = User(username="deleted", email="deleted@test.com", hashed_password="hash", role=TRAINER_ROLE, permissions=[], is_active=False, deleted_at=datetime.now(timezone.utc))
        db_session.add(deleted)
        db_session.commit()

        with pytest.raises(HTTPException) as exc_info:
            get_user_by_id(deleted.id, db_session, include_deleted=False)
        
        assert exc_info.value.status_code == 404
    
    def test_get_user_by_id_deleted_included(self, db_session):
        """Usuario eliminado se encuentra si include_deleted=True"""
        deleted = User(username="deleted", email="deleted@test.com", hashed_password="hash", role=TRAINER_ROLE, permissions=[], is_active=False, deleted_at=datetime.now(timezone.utc))
        db_session.add(deleted)
        db_session.commit()
        
        result = get_user_by_id(deleted.id, db_session, include_deleted=True)
        
        assert result.id == deleted.id


class TestUpdateUser:
    """Tests para update_user"""
    
    def test_update_user_is_active(self, db_session):
        """Actualizar solo el campo is_active - cubre línea 137"""
        user = User(
            username="activeuser",
            email="active@test.com",
            hashed_password=get_password_hash("pass"),
            role=TRAINER_ROLE,
            permissions=[],
            is_active=True
        )
        db_session.add(user)
        db_session.commit()
        
        # Actualizar is_active a False
        update_data = UserUpdate(is_active=False)
        result = update_user(user.id, update_data, db_session)
        
        assert result.is_active is False
        
        # Actualizar is_active a True nuevamente
        update_data2 = UserUpdate(is_active=True)
        result2 = update_user(user.id, update_data2, db_session)
        
        assert result2.is_active is True

    def test_update_user_username(self, db_session):
        """Actualizar solo username"""
        user = User(username="oldname", email="user@test.com", hashed_password="hash", role=TRAINER_ROLE, permissions=[], is_active=True)
        db_session.add(user)
        db_session.commit()
        
        update_data = UserUpdate(username="newname")
        result = update_user(user.id, update_data, db_session)
        
        assert result.username == "newname"
        assert result.email == "user@test.com"
    
    def test_update_user_email(self, db_session):
        """Actualizar solo email"""
        user = User(username="user1", email="old@test.com", hashed_password="hash", role=TRAINER_ROLE, permissions=[], is_active=True)
        db_session.add(user)
        db_session.commit()
        
        update_data = UserUpdate(email="new@test.com")
        result = update_user(user.id, update_data, db_session)
        
        assert result.email == "new@test.com"
    
    def test_update_user_password(self, db_session):
        """Actualizar contraseña - force_password_change se setea a False"""
        user = User(username="user1", email="user@test.com", hashed_password=get_password_hash("oldpass"), role=TRAINER_ROLE, permissions=[], is_active=True, force_password_change=True)
        db_session.add(user)
        db_session.commit()
        
        update_data = UserUpdate(password="newpass")
        result = update_user(user.id, update_data, db_session)
        
        assert verify_password("newpass", result.hashed_password) is True
        assert result.force_password_change is False
    
    def test_update_user_conflict(self, db_session):
        """Actualizar a username que ya existe - lanza 400"""
        user1 = User(username="user1", email="user1@test.com", hashed_password="hash", role=TRAINER_ROLE, permissions=[], is_active=True)
        user2 = User(username="user2", email="user2@test.com", hashed_password="hash", role=TRAINER_ROLE, permissions=[], is_active=True)
        db_session.add_all([user1, user2])
        db_session.commit()
        
        update_data = UserUpdate(username="user2")
        
        with pytest.raises(HTTPException) as exc_info:
            update_user(user1.id, update_data, db_session)
        
        assert exc_info.value.status_code == 400


class TestSoftDeleteUser:
    """Tests para soft_delete_user"""
    
    def test_soft_delete_user(self, db_session):
        """Soft delete usuario"""
        user = User(username="todelete", email="delete@test.com", hashed_password="hash", role=TRAINER_ROLE, permissions=[], is_active=True)
        db_session.add(user)
        db_session.commit()
        
        result = soft_delete_user(user.id, db_session)
        
        assert result["detail"] == "User soft deleted"
        
        # Verificar que se actualizó
        deleted_user = db_session.query(User).filter(User.id == user.id).first()
        assert deleted_user.is_active is False
        assert deleted_user.deleted_at is not None


class TestChangePassword:
    """Tests para change_password"""
    
    def test_change_password_success(self, db_session):
        """Cambiar contraseña exitosamente"""
        user = User(
            username="user1",
            email="user@test.com",
            hashed_password=get_password_hash("oldpass"),
            role=TRAINER_ROLE,
            permissions=[],
            is_active=True,
            force_password_change=True
        )
        db_session.add(user)
        db_session.commit()
        
        change_data = ChangePasswordInput(
            current_password="oldpass",
            new_password="newpass123"
        )
        
        result = change_password(user, change_data, db_session)
        
        assert result["detail"] == "Password updated"
        assert verify_password("newpass123", user.hashed_password) is True
        assert user.force_password_change is False
    
    def test_change_password_invalid_current(self, db_session):
        """Contraseña actual incorrecta - lanza 400"""
        user = User(
            username="user1",
            email="user@test.com",
            hashed_password=get_password_hash("correctpass"),
            role=TRAINER_ROLE,
            permissions=[],
            is_active=True
        )
        db_session.add(user)
        db_session.commit()
        
        change_data = ChangePasswordInput(
            current_password="wrongpass",
            new_password="newpass123"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            change_password(user, change_data, db_session)
        
        assert exc_info.value.status_code == 400
        assert "Invalid current password" in str(exc_info.value.detail)


class TestAuthenticateUser:
    """Tests para authenticate_user"""
    
    def test_authenticate_user_success(self, db_session):
        """Autenticación exitosa"""
        user = User(
            username="trainer1",
            email="trainer1@test.com",
            hashed_password=get_password_hash("password123"),
            role=TRAINER_ROLE,
            permissions=[],
            is_active=True,
            deleted_at=None
        )
        db_session.add(user)
        db_session.commit()
        
        result = authenticate_user("trainer1", "password123", db_session)
        
        assert result is not None
        assert result.username == "trainer1"
    
    def test_authenticate_user_not_found(self, db_session):
        """Usuario no existe - lanza 400"""
        with pytest.raises(HTTPException) as exc_info:
            authenticate_user("nonexistent", "pass", db_session)
        
        assert exc_info.value.status_code == 400
        assert "Usuario no encontrado" in str(exc_info.value.detail)
    
    def test_authenticate_user_wrong_password(self, db_session):
        """Contraseña incorrecta - lanza 400"""
        user = User(
            username="trainer1",
            email="trainer1@test.com",
            hashed_password=get_password_hash("correctpass"),
            role=TRAINER_ROLE,
            permissions=[],
            is_active=True,
            deleted_at=None
        )
        db_session.add(user)
        db_session.commit()
        
        with pytest.raises(HTTPException) as exc_info:
            authenticate_user("trainer1", "wrongpass", db_session)
        
        assert exc_info.value.status_code == 400
        assert "Contraseña incorrecta" in str(exc_info.value.detail)
    
    def test_authenticate_user_inactive(self, db_session):
        """Usuario inactivo - no se autentica"""
        user = User(
            username="inactive",
            email="inactive@test.com",
            hashed_password=get_password_hash("pass"),
            role=TRAINER_ROLE,
            permissions=[],
            is_active=False,
            deleted_at=None
        )
        db_session.add(user)
        db_session.commit()
        
        with pytest.raises(HTTPException) as exc_info:
            authenticate_user("inactive", "pass", db_session)
        
        assert exc_info.value.status_code == 400
        assert "Usuario no encontrado" in str(exc_info.value.detail)


# Fixture para db_session
@pytest.fixture
def db_session():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from src.database.database import Base
    
    engine = create_engine("sqlite:///:memory:")
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()