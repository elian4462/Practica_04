"""Test End-to-End (E2E) con proceso completo vía subprocess.

Escenario 5: Valida la ejecución del programa completo como lo haría un usuario real desde la terminal.
"""

import subprocess
import sys
from pathlib import Path


def test_e2e_flujo_completo_usuario(tmp_path):
    db_path = str(tmp_path / "e2e_tareas.json")
    env = {"PYTHONPATH": "src"}

    # 1. Crear tarea vía CLI subprocess
    cmd_crear = [
        sys.executable, "-m", "gestor_tareas.cli",
        "--db", db_path,
        "crear", "Tarea E2E Usuario Real", "--prioridad", "alta", "--etiquetas", "e2e", "qa"
    ]
    res_crear = subprocess.run(cmd_crear, capture_output=True, text=True, env=env)
    assert res_crear.returncode == 0
    assert "[OK] Tarea creada con ID: 1" in res_crear.stdout

    # 2. Listar tareas vía CLI subprocess
    cmd_listar = [sys.executable, "-m", "gestor_tareas.cli", "--db", db_path, "listar"]
    res_listar = subprocess.run(cmd_listar, capture_output=True, text=True, env=env)
    assert res_listar.returncode == 0
    assert "Tarea E2E Usuario Real" in res_listar.stdout
    assert "ALTA" in res_listar.stdout

    # 3. Completar tarea vía CLI subprocess
    cmd_comp = [sys.executable, "-m", "gestor_tareas.cli", "--db", db_path, "completar", "1"]
    res_comp = subprocess.run(cmd_comp, capture_output=True, text=True, env=env)
    assert res_comp.returncode == 0
    assert "completada exitosamente" in res_comp.stdout

    # 4. Consultar resumen estadístico vía CLI subprocess
    cmd_resumen = [sys.executable, "-m", "gestor_tareas.cli", "--db", db_path, "resumen"]
    res_resumen = subprocess.run(cmd_resumen, capture_output=True, text=True, env=env)
    assert res_resumen.returncode == 0
    assert "Total tareas: 1" in res_resumen.stdout
    assert "Completadas: 100.0%" in res_resumen.stdout
