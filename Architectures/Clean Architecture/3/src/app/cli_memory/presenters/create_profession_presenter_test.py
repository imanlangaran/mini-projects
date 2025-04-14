from app.cli_memory.presenters.create_profession_presenter import (
    CreateProfessionPresenter,
)
from domain.entities.profession import Profession
from interactor.dtos.create_profession_dtos import CreateProfessionOutputDto


def test_create_profession_presenter(fixture_profession_developer):
    profession = Profession(
        profession_id=fixture_profession_developer["profession_id"],
        name=fixture_profession_developer["name"],
        description=fixture_profession_developer["description"],
    )
    output_dto = CreateProfessionOutputDto(profession)
    presenter = CreateProfessionPresenter()
    assert presenter.present(output_dto) == {
        "profession_id": fixture_profession_developer["profession_id"],
        "name": fixture_profession_developer["name"],
        "description": fixture_profession_developer["description"],
    }