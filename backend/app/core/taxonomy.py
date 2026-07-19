from enum import Enum

class JobArea(str, Enum):
    TI_SOFTWARE = "TI_SOFTWARE"
    DADOS = "DADOS"
    DESIGN = "DESIGN"
    MARKETING = "MARKETING"
    NEGOCIOS = "NEGOCIOS"
    RH = "RH"
    FINANCAS = "FINANCAS"
    ENGENHARIA_OUTRAS = "ENGENHARIA_OUTRAS"
    DIREITO = "DIREITO"
    OUTROS = "OUTROS"

class JobModality(str, Enum):
    REMOTE = "REMOTE"
    HYBRID = "HYBRID"
    ONSITE = "ONSITE"

class JobStatus(str, Enum):
    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"

class SourceStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    ERROR = "ERROR"
