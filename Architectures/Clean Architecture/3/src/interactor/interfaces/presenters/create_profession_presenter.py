"""Module for the CreateProfessionPresenterInterface"""

from abc import ABC, abstractmethod
from typing import Dict

from src.interactor.dtos.create_profession_dtos import CreateProfessionOutputDto


class CreateProfessionPresenterInterface(ABC):
    """Class for the inteface of the ProfessionPresenter"""

    @abstractmethod
    def present(self, output_dto: CreateProfessionOutputDto) -> Dict:
        """Present the Profession"""
