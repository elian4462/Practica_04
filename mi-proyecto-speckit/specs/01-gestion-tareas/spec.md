# Especificación del Sistema: Gestor de Tareas

## Resumen
Sistema modular para la creación, consulta, actualización de estado, eliminación y generación de estadísticas de tareas personales y de equipo, con persistencia en JSON y CLI ejecutable.

## Functional Requirements
- **FR-001**: El sistema debe permitir la creación de tareas con título, descripción opcional, nivel de prioridad (`baja`, `media`, `alta`, `critica`) y etiquetas asociadas.
- **FR-002**: El sistema debe listar tareas existentes permitiendo filtrado por `estado`, `prioridad` o `etiqueta`.
- **FR-003**: El sistema debe permitir actualizar el estado de una tarea (`pendiente`, `en_progreso`, `completada`, `cancelada`).
- **FR-004**: El sistema debe permitir eliminar tareas existentes mediante su identificador numérico único.
- **FR-005**: El sistema debe generar un resumen estadístico del total de tareas, desglose por estado y porcentaje de tareas completadas.

## Acceptance Scenarios
- **Scenario 1: Creación exitosa de tarea básica**
  - **Given**: Un gestor de tareas vacío.
  - **When**: Se crea una tarea con título "Comprar insumos", descripción "Insumos de oficina" y prioridad "alta".
  - **Then**: La tarea se almacena con ID asignado incrementalmente (>=1), estado inicial "pendiente" y creada_en con timestamp ISO.

- **Scenario 2: Transición de estado a completada**
  - **Given**: Una tarea existente con ID 1 en estado "pendiente".
  - **When**: Se invoca la actualización de estado a "completada".
  - **Then**: El estado cambia a "completada" y se persiste correctamente.

- **Scenario 3: Filtrado de tareas por prioridad**
  - **Given**: 3 tareas registradas: Tarea 1 (prioridad "baja"), Tarea 2 (prioridad "alta"), Tarea 3 (prioridad "alta").
  - **When**: Se listan las tareas con filtro prioridad "alta".
  - **Then**: El resultado contiene exactamente 2 tareas (Tarea 2 y Tarea 3).

- **Scenario 4: Interfaz CLI en memoria e integración entre CLI y GestorTareas**
  - **Given**: Una base de datos temporal con tareas.
  - **When**: La función `ejecutar_cli` es invocada con argumentos `["crear", "Presentar demo", "--prioridad", "critica"]`.
  - **Then**: El código de salida retornado es 0 y la tarea es creada.

- **Scenario 5: Ejecución CLI de punta a punta (End-to-End)**
  - **Given**: La CLI ejecutada como subproceso `python -m gestor_tareas.cli`.
  - **When**: Se ejecuta `python -m gestor_tareas.cli listar`.
  - **Then**: El subproceso termina con código de retorno 0 y produce la salida esperada en stdout.

## Edge Cases
- **Edge Case 1: Título vacío o con solo espacios en blanco**
  - La creación debe fallar arrojando `ValueError` indicando que el título no puede estar vacío.
- **Edge Case 2: Título excede la longitud máxima (100 caracteres)**
  - La creación debe fallar arrojando `ValueError`.
- **Edge Case 3: Prioridad no reconocida**
  - Se debe rechazar arrojando `ValueError` listando las opciones válidas.
- **Edge Case 4: Identificador numérico no positivo (<= 0)**
  - La consulta o modificación debe arrojar `ValueError`.
- **Edge Case 5: Identificador inexistente al eliminar o actualizar**
  - La operación debe arrojar `KeyError`.

## Clarifications
- **Clarification 1 (FR-006)**: Si el repositorio de persistencia no encuentra el archivo JSON al iniciar, debe inicializarse silenciosamente como una lista vacía sin producir excepciones no controladas.
- **Clarification 2**: El cálculo de porcentaje de tareas completadas debe retornar `0.0` si no existen tareas registradas para evitar divisiones por cero.
