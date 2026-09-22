"""Lógica de negocio y modelos para el Gestor de Tareas."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any


class Prioridad(str, Enum):
    BAJA = "baja"
    MEDIA = "media"
    ALTA = "alta"
    CRITICA = "critica"


class EstadoTarea(str, Enum):
    PENDIENTE = "pendiente"
    EN_PROGRESO = "en_progreso"
    COMPLETADA = "completada"
    CANCELADA = "cancelada"


@dataclass
class Tarea:
    id: int
    titulo: str
    descripcion: str = ""
    prioridad: Prioridad = Prioridad.MEDIA
    estado: EstadoTarea = EstadoTarea.PENDIENTE
    creada_en: str = field(default_factory=lambda: datetime.now().isoformat())
    etiquetas: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "titulo": self.titulo,
            "descripcion": self.descripcion,
            "prioridad": self.prioridad.value if isinstance(self.prioridad, Prioridad) else self.prioridad,
            "estado": self.estado.value if isinstance(self.estado, EstadoTarea) else self.estado,
            "creada_en": self.creada_en,
            "etiquetas": self.etiquetas,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Tarea":
        prioridad_val = data.get("prioridad", "media")
        try:
            prioridad = Prioridad(prioridad_val.lower())
        except (ValueError, AttributeError):
            prioridad = Prioridad.MEDIA

        estado_val = data.get("estado", "pendiente")
        try:
            estado = EstadoTarea(estado_val.lower())
        except (ValueError, AttributeError):
            estado = EstadoTarea.PENDIENTE

        return cls(
            id=int(data["id"]),
            titulo=str(data["titulo"]),
            descripcion=str(data.get("descripcion", "")),
            prioridad=prioridad,
            estado=estado,
            creada_en=str(data.get("creada_en", datetime.now().isoformat())),
            etiquetas=list(data.get("etiquetas", [])),
        )


class GestorTareas:
    """Gestor principal de tareas con validación y reglas de negocio."""

    def __init__(self, repositorio=None):
        self.repositorio = repositorio
        self._tareas: Dict[int, Tarea] = {}
        self._siguiente_id = 1
        if self.repositorio:
            self._cargar()

    def _cargar(self):
        datos = self.repositorio.cargar()
        self._tareas = {t.id: t for t in datos}
        if self._tareas:
            self._siguiente_id = max(self._tareas.keys()) + 1

    def _guardar(self):
        if self.repositorio:
            self.repositorio.guardar(list(self._tareas.values()))

    def crear_tarea(
        self,
        titulo: str,
        descripcion: str = "",
        prioridad: str = "media",
        etiquetas: Optional[List[str]] = None,
    ) -> Tarea:
        """Crea una nueva tarea validando título, longitud y prioridad."""
        if not titulo or not titulo.strip():
            raise ValueError("El título de la tarea no puede estar vacío.")

        titulo_limpio = titulo.strip()
        if len(titulo_limpio) > 100:
            raise ValueError("El título no puede exceder los 100 caracteres.")

        try:
            p_enum = Prioridad(prioridad.lower())
        except (ValueError, AttributeError):
            raise ValueError(f"Prioridad inválida: '{prioridad}'. Opciones válidas: baja, media, alta, critica.")

        tarea = Tarea(
            id=self._siguiente_id,
            titulo=titulo_limpio,
            descripcion=descripcion.strip() if descripcion else "",
            prioridad=p_enum,
            estado=EstadoTarea.PENDIENTE,
            etiquetas=etiquetas or [],
        )
        self._tareas[self._siguiente_id] = tarea
        self._siguiente_id += 1
        self._guardar()
        return tarea

    def obtener_tarea(self, tarea_id: int) -> Optional[Tarea]:
        """Obtiene una tarea por su ID."""
        if tarea_id <= 0:
            raise ValueError("El ID de la tarea debe ser un entero positivo.")
        return self._tareas.get(tarea_id)

    def listar_tareas(
        self,
        estado: Optional[str] = None,
        prioridad: Optional[str] = None,
        etiqueta: Optional[str] = None,
    ) -> List[Tarea]:
        """Lista tareas aplicando filtros opcionales."""
        resultado = list(self._tareas.values())

        if estado:
            try:
                e_enum = EstadoTarea(estado.lower())
                resultado = [t for t in resultado if t.estado == e_enum]
            except ValueError:
                raise ValueError(f"Estado de filtro inválido: '{estado}'.")

        if prioridad:
            try:
                p_enum = Prioridad(prioridad.lower())
                resultado = [t for t in resultado if t.prioridad == p_enum]
            except ValueError:
                raise ValueError(f"Prioridad de filtro inválida: '{prioridad}'.")

        if etiqueta:
            resultado = [t for t in resultado if etiqueta.lower() in [e.lower() for e in t.etiquetas]]

        return resultado

    def actualizar_estado(self, tarea_id: int, nuevo_estado: str) -> Tarea:
        """Actualiza el estado de una tarea existente."""
        tarea = self.obtener_tarea(tarea_id)
        if not tarea:
            raise KeyError(f"No existe ninguna tarea con ID {tarea_id}.")

        try:
            e_enum = EstadoTarea(nuevo_estado.lower())
        except (ValueError, AttributeError):
            raise ValueError(f"Estado inválido: '{nuevo_estado}'. Opciones: pendiente, en_progreso, completada, cancelada.")

        tarea.estado = e_enum
        self._guardar()
        return tarea

    def eliminar_tarea(self, tarea_id: int) -> bool:
        """Elimina una tarea por su ID."""
        if tarea_id not in self._tareas:
            raise KeyError(f"No se encontró la tarea con ID {tarea_id}.")
        del self._tareas[tarea_id]
        self._guardar()
        return True

    def resumen_estadisticas(self) -> Dict[str, Any]:
        """Calcula el resumen de tareas por estado y prioridad."""
        total = len(self._tareas)
        por_estado = {e.value: 0 for e in EstadoTarea}
        por_prioridad = {p.value: 0 for p in Prioridad}

        for t in self._tareas.values():
            por_estado[t.estado.value] += 1
            por_prioridad[t.prioridad.value] += 1

        return {
            "total": total,
            "por_estado": por_estado,
            "por_prioridad": por_prioridad,
            "completadas_pct": round((por_estado["completada"] / total * 100), 1) if total > 0 else 0.0,
        }
