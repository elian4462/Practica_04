"""Interfaz de línea de comandos (CLI) para el Gestor de Tareas."""

import argparse
import sys
from .core import GestorTareas
from .storage import RepositorioJSON


def construir_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="gestor-tareas",
        description="CLI para la administración y seguimiento de tareas.",
    )
    parser.add_argument("--db", type=str, default="tareas.json", help="Ruta del archivo JSON de persistencia")
    subparsers = parser.add_subparsers(dest="comando", help="Comando a ejecutar")

    # Comando: crear
    p_crear = subparsers.add_parser("crear", help="Crea una nueva tarea")
    p_crear.add_argument("titulo", type=str, help="Título de la tarea")
    p_crear.add_argument("--desc", type=str, default="", help="Descripción detallada")
    p_crear.add_argument("--prioridad", type=str, default="media", choices=["baja", "media", "alta", "critica"], help="Prioridad")
    p_crear.add_argument("--etiquetas", nargs="*", default=[], help="Etiquetas asociadas")

    # Comando: listar
    p_listar = subparsers.add_parser("listar", help="Lista las tareas existentes")
    p_listar.add_argument("--estado", type=str, default=None, choices=["pendiente", "en_progreso", "completada", "cancelada"], help="Filtrar por estado")
    p_listar.add_argument("--prioridad", type=str, default=None, choices=["baja", "media", "alta", "critica"], help="Filtrar por prioridad")
    p_listar.add_argument("--etiqueta", type=str, default=None, help="Filtrar por etiqueta")

    # Comando: completar
    p_comp = subparsers.add_parser("completar", help="Marca una tarea como completada")
    p_comp.add_argument("id", type=int, help="ID de la tarea")

    # Comando: eliminar
    p_elim = subparsers.add_parser("eliminar", help="Elimina una tarea por su ID")
    p_elim.add_argument("id", type=int, help="ID de la tarea")

    # Comando: resumen
    subparsers.add_parser("resumen", help="Muestra estadísticas de las tareas")

    return parser


def ejecutar_cli(args=None, ruta_db="tareas.json") -> int:
    parser = construir_parser()
    opciones = parser.parse_args(args)

    if not opciones.comando:
        parser.print_help()
        return 1

    db_a_usar = opciones.db if opciones.db != "tareas.json" else ruta_db
    repo = RepositorioJSON(ruta_archivo=db_a_usar)
    gestor = GestorTareas(repositorio=repo)

    try:
        if opciones.comando == "crear":
            t = gestor.crear_tarea(
                titulo=opciones.titulo,
                descripcion=opciones.desc,
                prioridad=opciones.prioridad,
                etiquetas=opciones.etiquetas,
            )
            print(f"[OK] Tarea creada con ID: {t.id} - '{t.titulo}' (Prioridad: {t.prioridad.value})")
            return 0

        elif opciones.comando == "listar":
            tareas = gestor.listar_tareas(
                estado=opciones.estado,
                prioridad=opciones.prioridad,
                etiqueta=opciones.etiqueta,
            )
            if not tareas:
                print("No se encontraron tareas con los filtros especificados.")
            else:
                for t in tareas:
                    etqs = f" [{' ,'.join(t.etiquetas)}]" if t.etiquetas else ""
                    print(f"[{t.id}] [{t.estado.value.upper()}] ({t.prioridad.value.upper()}) {t.titulo}{etqs}")
            return 0

        elif opciones.comando == "completar":
            t = gestor.actualizar_estado(opciones.id, "completada")
            print(f"[OK] Tarea ID {t.id} completada exitosamente.")
            return 0

        elif opciones.comando == "eliminar":
            gestor.eliminar_tarea(opciones.id)
            print(f"[OK] Tarea ID {opciones.id} eliminada.")
            return 0

        elif opciones.comando == "resumen":
            stats = gestor.resumen_estadisticas()
            print(f"Total tareas: {stats['total']}")
            print(f"Completadas: {stats['completadas_pct']}%")
            return 0

    except Exception as err:
        print(f"[ERROR] {err}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(ejecutar_cli())
