from src.services.pokemon_service import _calculate_battle_stats, _experience_to_level


def test_experience_to_level_growth():
    assert _experience_to_level(0) == 1
    assert _experience_to_level(1000) >= 10
    assert _experience_to_level(1000000) <= 100


def test_calculate_stats_returns_required_fields():
    stats = _calculate_battle_stats(
        {
            "hp": 45,
            "attack": 49,
            "defense": 49,
            "special-attack": 65,
            "special-defense": 65,
            "speed": 45,
        },
        10,
    )

    assert set(stats.keys()) == {
        "max_hp",
        "attack",
        "defense",
        "sp_attack",
        "sp_defense",
        "speed",
    }
    assert stats["max_hp"] > 0
