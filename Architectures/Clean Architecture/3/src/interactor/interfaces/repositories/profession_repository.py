""" this module contains the intedface for the ProfessionRepository """

from abc import abstractmethod

from src.domain.entities.profession import Profession
from src.domain.value_objects import ProfessionId


class ProfessionRepositoryInterface:
  """ this class is the interface fot the profesionRepositoty """
  
  @abstractmethod
  def get(self, profession_id: ProfessionId) -> Profession:
    """ this method gets a profession by its id 
    :param profession_id: ProfessionId
    :return: Profession
    """
    
  @abstractmethod
  def create(self , name: str, description: str)-> Profession:
    """  Create a Profession 
    :param name: Profession Name
    :param description : Profession Description
    :return: Profession
    """
    
  @abstractmethod
  def update(self, profession: Profession)-> Profession:
    """ update a Profession 
    :param profession: Profession
    :return: Profession
    """
    