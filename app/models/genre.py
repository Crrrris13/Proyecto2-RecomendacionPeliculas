from dataclasses import dataclass

@dataclass
class Genre:
    nombre: str

    def to_dict(self) -> dict:
        return {"nombre": self.nombre}
