"""This module is responsible for creating a new profession"""

from typing import Dict
from interactor.dtos.create_profession_dtos import (
    CreateProfessionInputDto,
    CreateProfessionOutputDto,
)
from interactor.interfaces.presenters.create_profession_presenter import (
    CreateProfessionPresenterInterface,
)
from interactor.interfaces.repositories.profession_repository import (
    PsofessionPepositoryInterface,
)


class CreateProfessionUseCase:
    """This class is responsible for creatin a new profession"""

    def __init__(
        self,
        presenter: CreateProfessionPresenterInterface,
        repository: PsofessionPepositoryInterface,
    ):
        self.presenter = presenter
        self.repository = repository

    def execute(self, input_dto: CreateProfessionInputDto) -> Dict:
        """This metho is responsible for creating a new profession.
        :param input_dto: the input data transfer object
        :type input_dto: CreateProfessionInputDto
        :return: Dict
        """

        profession = self.repository.create(input_dto.name, input_dto.description)
        output_dto = CreateProfessionOutputDto(profession)
        return self.presenter.present(output_dto)
