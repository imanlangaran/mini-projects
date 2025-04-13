from domain.entities.profession import Profession


def test_profession_creation(fixture_profession_developer):
    profession = Profession(
        profession_id=fixture_profession_developer["profesion_id"],
        name=fixture_profession_developer["name"],
        description=fixture_profession_developer["description"],
    )
    assert profession.name == fixture_profession_developer["name"]
    assert profession.description == fixture_profession_developer["description"]


def test_profession_from_dict(fixture_profession_developer):
    profession = Profession.from_dict(fixture_profession_developer)
    assert profession.name == fixture_profession_developer["name"]
    assert profession.description == fixture_profession_developer["description"]


def test_profession_to_dict(fixture_profession_developer):
    profession = Profession.from_dict(fixture_profession_developer)
    assert profession.to_dict() == fixture_profession_developer


def test_profession_comparison(fixture_profession_developer):
    profession1 = Profession.from_dict(fixture_profession_developer)
    profession2 = Profession.from_dict(fixture_profession_developer)
    assert profession1 == profession2
