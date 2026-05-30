from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class User:
    id:                str
    nombre:            str
    edad:              int
    generos_favoritos: list[str] = field(default_factory=list)

    @classmethod
    def from_record(cls, record: dict) -> "User":
        return cls(
            id                = record.get("id", ""),
            nombre            = record.get("nombre", ""),
            edad              = record.get("edad", 0),
            generos_favoritos = record.get("generos_favoritos", []),
        )

    def to_dict(self) -> dict:
        return {
            "id":                self.id,
            "nombre":            self.nombre,
            "edad":              self.edad,
            "generos_favoritos": self.generos_favoritos,
        }
