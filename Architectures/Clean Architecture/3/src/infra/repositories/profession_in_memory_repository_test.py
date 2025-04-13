

from domain.entities.profession import Profession
from infra.repositories.profession_in_memory_repository import ProfessionInMemoryRepository


def test_profession_in_memory_repository(fixture_profession_developer):
    repository = ProfessionInMemoryRepository()
    profession = repository.create(
        name=fixture_profession_developer['name'],
        description=fixture_profession_developer['description'],
    )
    response = repository.get(profession.profession_id)
    assert response.name == fixture_profession_developer['name']
    assert response.description == fixture_profession_developer['description']
    
    new_profession = Profession(
        profession_id=profession.profession_id,
        name='new name',
        description='new description',
    )
    response_update = repository.update(new_profession)
    assert response_update.name == 'new name'
    assert response_update.description == 'new description'