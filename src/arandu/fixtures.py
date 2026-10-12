"""Datos de prueba del Instituto Arandu.

Un periodo, siete materias, ocho comisiones y tres estudiantes. Lo minimo para que
los siete casos limitrofes de las reglas sean reproducibles.
"""

from datetime import datetime, time

from .modelo import (
    Comision,
    Estudiante,
    Franja,
    Instituto,
    Materia,
    NotaHistorica,
    Periodo,
    Plan,
)

LUN, MAR, MIE, JUE, VIE = 0, 1, 2, 3, 4

PERIODO_ACTUAL = "2026-2"

# Un instante comodo, dentro de la ventana, para usar de referencia en ejemplos.
AHORA = datetime(2026, 9, 10, 20, 0)


def instituto_arandu() -> Instituto:
    """Construye un Instituto nuevo. Cada llamada devuelve estado limpio."""
    plan = Plan(codigo="AS-2026", minimo_aprobacion=60.0, maximo_materias=6)

    materias = [
        Materia("ALG1", "Algoritmos I", plan.codigo),
        Materia("ALG2", "Algoritmos II", plan.codigo, correlativas=("ALG1",)),
        Materia("PROG1", "Programacion I", plan.codigo),
        Materia("WEB1", "Desarrollo Web I", plan.codigo, correlativas=("PROG1",)),
        Materia("BD1", "Bases de Datos I", plan.codigo, correlativas=("ALG1",)),
        Materia("MAT1", "Matematica I", plan.codigo),
        Materia("RED1", "Redes I", plan.codigo),
    ]

    comisiones = [
        # Termina 21:00. MAT1-A empieza 21:00 el mismo dia: contiguas, NO chocan.
        Comision("ALG1-A", "ALG1", cupo=2, franjas=(Franja(LUN, time(18, 30), time(21, 0)),)),
        Comision("MAT1-A", "MAT1", cupo=30, franjas=(Franja(LUN, time(21, 0), time(22, 30)),)),
        # Se solapa con ALG1-A: choque real.
        Comision("ALG2-A", "ALG2", cupo=30, franjas=(Franja(LUN, time(20, 0), time(22, 0)),)),
        Comision("PROG1-A", "PROG1", cupo=30, franjas=(Franja(MIE, time(19, 0), time(21, 30)),)),
        Comision("PROG1-B", "PROG1", cupo=30, franjas=(Franja(JUE, time(19, 0), time(21, 30)),)),
        Comision("BD1-A", "BD1", cupo=30, franjas=(Franja(MAR, time(19, 0), time(21, 30)),)),
        # Cupo cero: rechaza siempre.
        Comision("BD1-B", "BD1", cupo=0, franjas=(Franja(VIE, time(19, 0), time(21, 30)),)),
        Comision("RED1-A", "RED1", cupo=30, franjas=(Franja(VIE, time(19, 0), time(21, 30)),)),
    ]

    estudiantes = [
        # Aprobo ALG1 (85). Curso PROG1 y la reprobo (45): no habilita WEB1.
        Estudiante(
            "e1",
            "Ana Benitez",
            plan.codigo,
            historial=(
                NotaHistorica("ALG1", "2026-1", 85.0),
                NotaHistorica("PROG1", "2026-1", 45.0),
            ),
        ),
        Estudiante("e2", "Bruno Caceres", plan.codigo),
        Estudiante("e3", "Carla Duarte", plan.codigo),
    ]

    return Instituto(
        planes={plan.codigo: plan},
        materias={m.codigo: m for m in materias},
        comisiones={c.id: c for c in comisiones},
        periodos={
            PERIODO_ACTUAL: Periodo(
                id=PERIODO_ACTUAL,
                apertura=datetime(2026, 9, 1, 8, 0),
                cierre=datetime(2026, 9, 15, 23, 59),
                plazo_de_baja=datetime(2026, 9, 30, 23, 59),
            )
        },
        estudiantes={e.id: e for e in estudiantes},
        inscripciones=[],
    )
