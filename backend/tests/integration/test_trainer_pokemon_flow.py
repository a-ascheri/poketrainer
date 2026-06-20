import pytest
from passlib.context import CryptContext

from src.models.user import User
from src.services import pokemon_service

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _auth_headers(token: str):
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(autouse=True)
def pokeapi_mock(monkeypatch):
    def fake_fetch_json(url: str):
        if "/pokemon/" in url:
            return {
                "id": 1,
                "name": "bulbasaur",
                "types": [{"type": {"name": "grass"}}],
                "abilities": [{"ability": {"name": "overgrow"}}],
                "stats": [
                    {"stat": {"name": "hp"}, "base_stat": 45},
                    {"stat": {"name": "attack"}, "base_stat": 49},
                    {"stat": {"name": "defense"}, "base_stat": 49},
                    {"stat": {"name": "special-attack"}, "base_stat": 65},
                    {"stat": {"name": "special-defense"}, "base_stat": 65},
                    {"stat": {"name": "speed"}, "base_stat": 45},
                ],
                "moves": [
                    {
                        "move": {"name": "tackle"},
                        "version_group_details": [
                            {
                                "move_learn_method": {"name": "level-up"},
                                "level_learned_at": 1,
                            }
                        ],
                    },
                    {
                        "move": {"name": "vine-whip"},
                        "version_group_details": [
                            {
                                "move_learn_method": {"name": "level-up"},
                                "level_learned_at": 7,
                            }
                        ],
                    },
                ],
                "species": {"url": "https://pokeapi.co/api/v2/pokemon-species/1/"},
            }

        if "pokemon-species" in url:
            return {
                "evolution_chain": {
                    "url": "https://pokeapi.co/api/v2/evolution-chain/1/"
                }
            }

        if "evolution-chain" in url:
            return {
                "chain": {
                    "species": {"name": "bulbasaur"},
                    "evolves_to": [
                        {
                            "species": {"name": "ivysaur"},
                            "evolves_to": [
                                {"species": {"name": "venusaur"}, "evolves_to": []}
                            ],
                        }
                    ],
                }
            }

        raise RuntimeError(f"Unexpected url in test: {url}")

    monkeypatch.setattr(pokemon_service, "_fetch_json", fake_fetch_json)


def test_starter_selection_and_gain_exp(client, db_session):
    # Crear usuario trainer directamente en la base de datos (solo para el test)
    hashed_password = pwd_context.hash("rock123")
    user = User(
        username="brock",
        email="brock@pokemon.com",
        hashed_password=hashed_password,
        role="trainer",
        is_active=True,
        force_password_change=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # Login con el usuario creado
    login_response = client.post(
        "/api/v1/user/login",
        data={"username": "brock", "password": "rock123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    options = client.get(
        "/api/v1/game/trainer/starter/options", headers=_auth_headers(token)
    )
    assert options.status_code == 200
    assert len(options.json()) == 3

    selected = client.post(
        "/api/v1/game/trainer/starter/select",
        json={"pokemon_name": "bulbasaur"},
        headers=_auth_headers(token),
    )
    assert selected.status_code == 200
    trainer_pokemon_id = selected.json()["id"]

    gained = client.post(
        f"/api/v1/game/trainer/pokemon/{trainer_pokemon_id}/gain-exp",
        json={"amount": 2000},
        headers=_auth_headers(token),
    )
    assert gained.status_code == 200
    assert gained.json()["current_level"] > 5

    stats = client.get(
        f"/api/v1/game/trainer/pokemon/{trainer_pokemon_id}/stats",
        headers=_auth_headers(token),
    )
    assert stats.status_code == 200
    assert stats.json()["max_hp"] >= stats.json()["current_hp"]

    moves = client.get(
        f"/api/v1/game/trainer/pokemon/{trainer_pokemon_id}/moves",
        headers=_auth_headers(token),
    )
    assert moves.status_code == 200
    assert len(moves.json()["known_moves"]) >= 1
    