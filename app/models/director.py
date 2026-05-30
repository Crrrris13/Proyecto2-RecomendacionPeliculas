from dataclasses import dataclass

@dataclass
class Director:
    id:           str
    nombre:       str
    nacionalidad: str = "Desconocida"

    def to_dict(self) -> dict:
        return {"id": self.id, "nombre": self.nombre, "nacionalidad": self.nacionalidad}
