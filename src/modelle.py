from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class User:
    username: str
    role: str

@dataclass
class Tool:
    id: str
    name: str
    status: str
    lagerplatz: str = ""
    extra_data: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Ruestwerkzeug:
    id: str
    name: str
    kasten: int
    lade: int
    fach: int
    bestand: int
    min_bestand: int = 0
