"""Module for the CreateProfessionPresenter"""

from typing import Dict
from interactor.dtos.create_profession_dtos import CreateProfessionOutputDto
from interactor.interfaces.presenters.create_profession_presenter import (
    CreateProfessionPresenterInterface,
)


class CreateProfessionPresenter(CreateProfessionPresenterInterface):
    """Class for the CreateProfessionPresenter"""

    def present(self, output_dto: CreateProfessionOutputDto) -> Dict:
        """Present the CreateProfession
        :param output_dto: CreateProfessionOutputDto
        :return: Dict"""
        return {
            "profession_id": output_dto.profession.profession_id,
            "name": output_dto.profession.name,
            "description": output_dto.profession.description,
        }
