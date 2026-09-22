"""Tests Unitarios para el Gestor de Tareas basados en specs/*/spec.md"""

import pytest
from gestor_tareas.core import GestorTareas, Tarea, Prioridad, EstadoTarea
from gestor_tareas.storage import RepositorioJSON


class TestCreacionTareas:
    """Escenario 1 y Functional Requirement FR-001."""

    def test_creacion_tarea_exitosa(self):
        gestor = GestorTareas()
        tarea = gestor.crear_tarea(
            titulo="Comprar insumos",
            descripcion="Insumos de oficina",
            prioridad="alta",
            etiquetas=["oficina", "compras"]
        )
        assert tarea.id >= 1
        assert tarea.titulo == "Comprar insumos"
        assert tarea.descripcion == "Insumos de oficina"
        assert tarea.prioridad == Prioridad.ALTA
        assert tarea.estado == EstadoTarea.PENDIENTE
        assert "oficina" in tarea.etiquetas
        assert tarea.creada_en is not None

    def test_edge_case_titulo_vacio(self):
        """Edge Case 1: Título vacío arroja ValueError."""
        gestor = GestorTareas()
        with pytest.raises(ValueError, match="no puede estar vacío"):
            gestor.crear_tarea("   ")

    def test_edge_case_titulo_largo(self):
        """Edge Case 2: Título excede 100 caracteres."""
        gestor = GestorTareas()
        titulo_largo = "A" * 105
        with pytest.raises(ValueError, match="no puede exceder los 100 caracteres"):
            gestor.crear_tarea(titulo_largo)

    def test_edge_case_prioridad_invalida(self):
        """Edge Case 3: Prioridad no reconocida."""
        gestor = GestorTareas()
        with pytest.raises(ValueError, match="Prioridad inválida"):
            gestor.crear_tarea("Tarea de prueba", prioridad="super_urgente")


class TestActualizacionEstado:
    """Escenario 2 y Functional Requirement FR-003."""

    def test_actualizar_estado_completada(self):
        gestor = GestorTareas()
        t = gestor.crear_tarea("Documentar API", prioridad="media")
        actualizada = gestor.actualizar_estado(t.id, "completada")
        assert actualizada.estado == EstadoTarea.COMPLETADA

    def test_actualizar_estado_invalido(self):
        gestor = GestorTareas()
        t = gestor.crear_tarea("Revisar PR")
        with pytest.raises(ValueError, match="Estado inválido"):
            gestor.actualizar_estado(t.id, "estado_inexistente")

    def test_actualizar_id_no_existente(self):
        """Edge Case 5: ID inexistente."""
        gestor = GestorTareas()
        with pytest.raises(KeyError, match="No existe ninguna tarea con ID 999"):
            gestor.actualizar_estado(999, "completada")


class TestFiltradoYListado:
    """Escenario 3 y Functional Requirement FR-002."""

    def test_filtrado_por_prioridad(self):
        gestor = GestorTareas()
        gestor.crear_tarea("Tarea 1", prioridad="baja")
        t2 = gestor.crear_tarea("Tarea 2", prioridad="alta")
        t3 = gestor.crear_tarea("Tarea 3", prioridad="alta")

        filtradas = gestor.listar_tareas(prioridad="alta")
        assert len(filtradas) == 2
        assert all(t.prioridad == Prioridad.ALTA for t in filtradas)
        assert {t.id for t in filtradas} == {t2.id, t3.id}

    def test_filtrado_por_estado(self):
        gestor = GestorTareas()
        t1 = gestor.crear_tarea("Tarea 1")
        gestor.crear_tarea("Tarea 2")
        gestor.actualizar_estado(t1.id, "completada")

        pendientes = gestor.listar_tareas(estado="pendiente")
        completadas = gestor.listar_tareas(estado="completada")
        assert len(pendientes) == 1
        assert len(completadas) == 1

    def test_filtrado_por_etiqueta(self):
        gestor = GestorTareas()
        gestor.crear_tarea("Backend API", etiquetas=["python", "backend"])
        gestor.crear_tarea("Frontend UI", etiquetas=["react", "frontend"])

        py_tareas = gestor.listar_tareas(etiqueta="python")
        assert len(py_tareas) == 1
        assert py_tareas[0].titulo == "Backend API"


class TestEliminacionYEstadisticas:
    """Functional Requirements FR-004 y FR-005."""

    def test_eliminacion_tarea_exitosa(self):
        gestor = GestorTareas()
        t = gestor.crear_tarea("Tarea temporal")
        assert gestor.eliminar_tarea(t.id) is True
        assert gestor.obtener_tarea(t.id) is None

    def test_eliminacion_id_inexistente(self):
        gestor = GestorTareas()
        with pytest.raises(KeyError):
            gestor.eliminar_tarea(404)

    def test_resumen_estadisticas_calculo(self):
        gestor = GestorTareas()
        gestor.crear_tarea("T1", prioridad="alta")
        t2 = gestor.crear_tarea("T2", prioridad="media")
        gestor.actualizar_estado(t2.id, "completada")

        stats = gestor.resumen_estadisticas()
        assert stats["total"] == 2
        assert stats["por_estado"]["completada"] == 1
        assert stats["por_estado"]["pendiente"] == 1
        assert stats["completadas_pct"] == 50.0

    def test_clarification_stats_vacias(self):
        """Clarification 2: 0% sin división por cero cuando no hay tareas."""
        gestor = GestorTareas()
        stats = gestor.resumen_estadisticas()
        assert stats["total"] == 0
        assert stats["completadas_pct"] == 0.0


class TestStorageRepositorio:
    """Clarification 1 (FR-006) y persistencia."""

    def test_archivo_no_existente_retorna_vacio(self, tmp_path):
        repo = RepositorioJSON(ruta_archivo=str(tmp_path / "inexistente.json"))
        assert repo.cargar() == []

    def test_guardar_y_cargar_tareas(self, tmp_path):
        ruta = str(tmp_path / "tareas_test.json")
        repo = RepositorioJSON(ruta_archivo=ruta)
        gestor1 = GestorTareas(repositorio=repo)
        t = gestor1.crear_tarea("Persistir datos", prioridad="critica")

        gestor2 = GestorTareas(repositorio=repo)
        t_cargada = gestor2.obtener_tarea(t.id)
        assert t_cargada is not None
        assert t_cargada.titulo == "Persistir datos"
        assert t_cargada.prioridad == Prioridad.CRITICA
