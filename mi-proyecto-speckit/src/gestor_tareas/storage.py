"""Persistencia en archivo JSON para las tareas."""

import json
from pathlib import Path
from typing import List
from .core import Tarea


class RepositorioJSON:
    """Maneja el almacenamiento y recuperación de tareas en formato JSON."""

    def __init__(self, ruta_archivo: str = "tareas.json"):
        self.ruta = Path(ruta_archivo)

    def cargar(self) -> List[Tarea]:
        if not self.ruta.exists():
            return []
        try:
            contenido = self.ruta.read_text(encoding="utf-8")
            if not contenido.strip():
                return []
            datos = json.loads(contenido)
            return [Tarea.from_dict(item) for item in datos]
        except (json.JSONDecodeError, KeyError, ValueError):
            return []

    def guardar(self, tareas: List[Tarea]) -> None:
        self.ruta.parent.mkdir(parents=True, exist_ok=True)
        datos = [t.to_dict() for t in tareas]
        self.ruta.write_text(json.dumps(datos, indent=2, ensure_ascii=False), encoding="utf-8")
