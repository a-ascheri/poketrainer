from src.models.user import User


def _login(client, username: str, password: str):
    response = client.post(
        "/api/v1/user/login",
        data={"username": username, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    return response.json()


def _auth_headers(token: str):
    return {"Authorization": f"Bearer {token}"}


def test_initial_admin_must_change_password(client):
    login_payload = _login(client, "originadmin", "admin123")
    assert login_payload["role"] == "admin"
    assert login_payload["force_password_change"] is True

    denied = client.get(
        "/api/v1/admin/users", headers=_auth_headers(login_payload["access_token"])
    )
    assert denied.status_code == 403

    change_password = client.post(
        "/api/v1/user/change-password",
        json={"current_password": "admin123", "new_password": "NewAdmin123!"},
        headers=_auth_headers(login_payload["access_token"]),
    )
    assert change_password.status_code == 200

    relogin_payload = _login(client, "originadmin", "NewAdmin123!")
    assert relogin_payload["force_password_change"] is False

    visible_admin_api = client.get(
        "/api/v1/admin/users", headers=_auth_headers(relogin_payload["access_token"])
    )
    assert visible_admin_api.status_code == 200


def test_hidden_admin_creation_and_soft_delete(client, db_session):
    admin_login = _login(client, "originadmin", "NewAdmin123!")
    token = admin_login["access_token"]

    created_trainer = client.post(
        "/api/v1/user/register",
        json={
            "username": "misty",
            "email": "misty@pokemon.com",
            "password": "water123",
        },
    )
    assert created_trainer.status_code == 200
    trainer_id = created_trainer.json()["id"]

    created_admin = client.post(
        "/api/v1/admin/internal/admins",
        json={
            "username": "admin2",
            "email": "admin2@pokemon.com",
            "password": "admin2pass",
            "permissions": ["manage_users", "manage_admins"],
        },
        headers=_auth_headers(token),
    )
    assert created_admin.status_code == 200
    assert created_admin.json()["role"] == "admin"

    deleted = client.delete(
        f"/api/v1/admin/users/{trainer_id}", headers=_auth_headers(token)
    )
    assert deleted.status_code == 200

    soft_deleted = db_session.query(User).filter(User.id == trainer_id).first()
    assert soft_deleted is not None
    assert soft_deleted.is_active is False
    assert soft_deleted.deleted_at is not None
