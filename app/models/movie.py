from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class Movie:
    id:       str
    titulo:   str
    anio:     int
    rating:   float
    generos:  list[str] = field(default_factory=list)
    actores:  list[str] = field(default_factory=list)
    director: str | None = None

    @classmethod
    def from_record(cls, record: dict) -> "Movie":
        """Construye un Movie desde el dict que retorna Neo4j."""
        return cls(
            id       = record.get("id", ""),
            titulo   = record.get("titulo", ""),
            anio     = record.get("anio", 0),
            rating   = record.get("rating", 0.0),
            generos  = record.get("generos", []),
            actores  = record.get("actores", []),
            director = record.get("director"),
        )

    def to_dict(self) -> dict:
        return {
            "id":       self.id,
            "titulo":   self.titulo,
            "anio":     self.anio,
            "rating":   self.rating,
            "generos":  self.generos,
            "actores":  self.actores,
            "director": self.director,
        }
