from typing import Dict
from app.cli_memory.interfaces.cli_memory_controller_interface import (
    CliMemoryControllerInterface,
)
from interactor.dtos.create_profession_dtos import CreateProfessionOutputDto


class CreateProfessionController(CliMemoryControllerInterface):
    """Class for the CreateProfessionPresenter"""

    def present(self, output_dto: CreateProfessionOutputDto) -> Dict:
        """Present the CreateProfession
        :param output_dto: CreateProfessionOutputDto
        :return: dict
        """
        return {
            "profession_id": output_dto.profession.profession_id,
            "name": output_dto.profession.name,
            "description": output_dto.profession.description,
        }
