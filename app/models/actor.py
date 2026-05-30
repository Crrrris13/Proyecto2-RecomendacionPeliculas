from dataclasses import dataclass

@dataclass
class Actor:
    id:           str
    nombre:       str
    nacionalidad: str = "Desconocida"

    def to_dict(self) -> dict:
        return {"id": self.id, "nombre": self.nombre, "nacionalidad": self.nacionalidad}
