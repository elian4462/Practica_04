"""Test de Integración EN MEMORIA (sin subprocess).

Prueba la interacción entre la interfaz CLI y el Gestor de Tareas directamente en memoria.
"""

from gestor_tareas.cli import ejecutar_cli
from gestor_tareas.core import GestorTareas
from gestor_tareas.storage import RepositorioJSON


def test_integracion_cli_crear_y_listar_en_memoria(tmp_path, capsys):
    """Escenario 4: CLI invocando la lógica de negocio y persistencia en memoria/archivo."""
    db_file = str(tmp_path / "test_cli_mem.json")

    # 1. Invocación CLI para crear tarea
    codigo_crear = ejecutar_cli(["crear", "Presentar demo", "--prioridad", "critica", "--desc", "Sprint review"], ruta_db=db_file)
    assert codigo_crear == 0
    captura = capsys.readouterr()
    assert "[OK] Tarea creada con ID: 1" in captura.out

    # 2. Invocación CLI para listar y verificar integración
    codigo_listar = ejecutar_cli(["listar", "--prioridad", "critica"], ruta_db=db_file)
    assert codigo_listar == 0
    captura_listar = capsys.readouterr()
    assert "Presentar demo" in captura_listar.out
    assert "CRITICA" in captura_listar.out

    # 3. Invocación CLI para completar
    codigo_comp = ejecutar_cli(["completar", "1"], ruta_db=db_file)
    assert codigo_comp == 0
    captura_comp = capsys.readouterr()
    assert "completada exitosamente" in captura_comp.out

    # 4. Verificación directa en el repositorio
    repo = RepositorioJSON(ruta_archivo=db_file)
    gestor = GestorTareas(repositorio=repo)
    tarea = gestor.obtener_tarea(1)
    assert tarea is not None
    assert tarea.estado.value == "completada"
