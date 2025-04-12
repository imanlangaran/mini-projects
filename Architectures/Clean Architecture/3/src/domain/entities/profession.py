from dataclasses import asdict, dataclass
from domain.value_objects import ProfessionId

@dataclass
class Profession:
  """ definition of profession entity
  """
  profession_id: ProfessionId
  name: str
  description: str
  
  @classmethod
  def from_dict(cls, data):
    """ converts data from a dictionary
    """
    return cls(**data)
  
  def to_dict(self):
    """ convert data to dictionary
    """
    return asdict(self)
  