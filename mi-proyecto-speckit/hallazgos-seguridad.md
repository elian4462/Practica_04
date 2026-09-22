# Auditoría de Seguridad — Gestor de Tareas

| Caso | Lo que se encontró | Corrección sugerida |
|---|---|---|
| 🔑 Secreto expuesto | Sin hallazgos (ninguna clave/API key quemada en código fuente) | Mantener uso exclusivo de variables de entorno mediante `.env` y `os.environ.get(...)` |
| 🧪 Validación de entradas | Sin hallazgos (validación exhaustiva de longitud, tipos y valores permitidos en `core.py` y `cli.py`) | Mantener sanitización con `.strip()` y límites de 100 caracteres por título |
| 🚪 Manejo de excepciones | Excepciones específicas capturadas (`KeyError`, `ValueError`, `json.JSONDecodeError`); captura controlada en CLI para retroalimentación | Mantener el no uso de bloques `except: pass` ciegos en la capa de negocio |

## Acciones de higiene aplicadas
- Se verificó la existencia del archivo `.env.example` con la plantilla de variables requeridas para el entorno.
- Se verificó que el archivo `.env` esté correctamente registrado en `.gitignore` y no se encuentre trackeado en el historial de Git (`git check-ignore` y `git ls-files` validados).
- Se confirmó que no existen credenciales reales ni tokens expuestos en los archivos fuente de `src/`.
