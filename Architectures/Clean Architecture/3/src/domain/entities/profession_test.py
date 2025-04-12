from domain.entities.profession import Profession


def test_profession_creation(fixture_profession_developer):
  profession = Profession(
    profession_id=fixture_profession_developer['profesion_id'],
    name=fixture_profession_developer['name'],
    description=fixture_profession_developer['description']
  )
  assert profession.name == fixture_profession_developer['name']
  