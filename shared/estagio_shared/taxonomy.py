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
    PROGRAMA_ESTAGIO = "PROGRAMA_ESTAGIO"
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


class TrackingStatus(str, Enum):
    SAVED = "SAVED"
    APPLIED = "APPLIED"
    INTERVIEW = "INTERVIEW"
    OFFER = "OFFER"
    HIRED = "HIRED"
    REJECTED = "REJECTED"
