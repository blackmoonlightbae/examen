# Instituto Arandu — inscripcion a materias

Caso de estudio del **Taller IV · Desarrollo Personal** (Analisis de Sistemas, UCOM).

El sistema hace una sola cosa: decide si un estudiante puede inscribirse a una comision
en un periodo academico. Ocho reglas, ningun framework, ninguna base de datos. Es
deliberadamente pequeno para que quepa entero en la cabeza y se pueda verificar.

Las reglas del dominio estan en [`docs/reglas-del-dominio.md`](docs/reglas-del-dominio.md).
Ese documento es el contrato: si el codigo y el documento no coinciden, **manda el documento**.

## Como correrlo

### Opcion A — GitHub Codespaces (recomendada para la primera semana)

1. En la pagina del repositorio: boton verde **Code** -> pestana **Codespaces** ->
   **Create codespace on main**.
2. Esperar a que termine de construirse (2 a 4 minutos la primera vez).
3. En la terminal que se abre:

```bash
uv run pytest
```

Deberias ver **14 passed**. Si los ves, tu entorno esta listo.

> Apaga el codespace cuando termines: menu de comandos -> *Codespaces: Stop Current Codespace*.
> Se apaga solo a los 30 minutos de inactividad, pero apagarlo a mano cuida tu cuota.

### Opcion B — En tu maquina

Necesitas Python 3.13 y [uv](https://docs.astral.sh/uv/).

```bash
git clone <url-del-repositorio>
cd arandu
uv sync
uv run pytest
```

## Como esta organizado

```
src/arandu/
  modelo.py       entidades del dominio; nada de logica
  horarios.py     solapamiento de franjas (soporte de R5)
  reglas.py       una funcion por regla; ninguna conoce a las demas
  inscripcion.py  orquesta: aplica las reglas en el orden del contrato (R8)
  fixtures.py     datos del Instituto Arandu
tests/
  test_casos_limitrofes.py   los casos de borde de la especificacion
```

La separacion importa: **las reglas no deciden el orden y el orquestador no conoce las reglas
por dentro.** Es lo que permite auditar una regla sin leer todo el sistema.

## Probarlo a mano

```bash
uv run python
```

```python
from datetime import datetime
from arandu.fixtures import instituto_arandu, PERIODO_ACTUAL
from arandu.inscripcion import inscribir

inst = instituto_arandu()
ahora = datetime(2026, 9, 10, 20, 0)

print(inscribir(inst, "e1", "ALG1-A", PERIODO_ACTUAL, ahora))   # aceptada
print(inscribir(inst, "e1", "ALG2-A", PERIODO_ACTUAL, ahora))   # choque de horarios
print(inscribir(inst, "e1", "MAT1-A", PERIODO_ACTUAL, ahora))   # aceptada: contiguas, no chocan
```

## Simplificaciones declaradas de la v1

- **El sistema nunca lee el reloj: lo recibe.** Cada operacion toma un `ahora` explicito.
  Es lo que hace deterministas las pruebas.
- Las fechas son `datetime` sin zona y se interpretan en America/Asuncion.
- El estado vive en memoria. No hay persistencia, ni usuarios, ni concurrencia.

Fuera de alcance: lista de espera, aranceles, equivalencias, autenticacion, notificaciones.

## Uso de asistentes de IA

Este taller **espera** que uses asistentes de IA. Lo que se evalua no es escribir a mano:
es que lo que aceptas este verificado y que puedas explicar como llegaste ahi.
Registra tu uso en [`AI_USAGE.md`](AI_USAGE.md).
