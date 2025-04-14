"""module for ProfessionInMemoryRepository"""

import copy
from typing import Dict
import uuid
from src.domain.entities.profession import Profession
from src.domain.value_objects import ProfessionId
from src.interactor.interfaces.repositories.profession_repository import (
    ProfessionRepositoryInterface,
)


class ProfessionInMemoryRepository(ProfessionRepositoryInterface):
    """InMemory Repository for Profession"""

    def __init__(self) -> None:
        self._data: Dict[ProfessionId, Profession] = {}

    def get(self, profession_id: ProfessionId) -> Profession:
        """get a profession by id
        :param profession_id: ProfessionId
        :retutn: Profession
        """
        return copy.deepcopy(self._data[profession_id])

    def creaate(self, name: str, desription: str) -> Profession:
        profession = Profession(
            profession_id=uuid.uuid4(), name=name, description=desription
        )
        self._data[profession.profession_id] = copy.deepcopy(profession)
        return copy.deepcopy(self._data[profession.profession_id])

    def update(self, profession: Profession) -> Profession:
        self._data[profession.profession_id] = copy.deepcopy(profession)
        return copy.deepcopy(self._data[profession.profession_id])
