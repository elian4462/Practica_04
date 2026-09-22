"""Gestor de Tareas - Módulo Principal"""

from .core import GestorTareas, Tarea, Prioridad, EstadoTarea
from .storage import RepositorioJSON

__all__ = ["GestorTareas", "Tarea", "Prioridad", "EstadoTarea", "RepositorioJSON"]
__version__ = "1.0.0"
