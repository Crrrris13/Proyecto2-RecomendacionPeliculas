from __future__ import annotations
from dataclasses import dataclass


@dataclass
class Rating:
    usuario_id:  str
    pelicula_id: str
    puntaje:     int          # 1-5
    fecha:       str | None = None

    def to_dict(self) -> dict:
        return {
            "usuario_id":  self.usuario_id,
            "pelicula_id": self.pelicula_id,
            "puntaje":     self.puntaje,
            "fecha":       self.fecha,
        }
