"""Pruebas de hallazgos sobre la rama parcial-b.

Cada prueba sale del contrato (docs/reglas-del-dominio.md, v1), no del codigo.
En parcial-b TIENEN que fallar; en main deberian pasar.

Generado con asistencia de IA (Claude) - uso declarado en Fase 2.
"""
from types import SimpleNamespace as NS

from arandu import reglas


def _instituto(comisiones=None, activas_de=None, activas_en=None, minimo=4):
    """Instituto minimo con solo lo que las reglas consultan."""
    return NS(
        planes={"P1": NS(minimo_aprobacion=minimo)},
        comisiones=comisiones or {},
        activas_de=lambda est_id, periodo_id: activas_de or [],
        activas_en=lambda comision_id, periodo_id: activas_en or [],
    )


PERIODO = NS(id="2026-2")
PERIODO_ANTERIOR = "2026-1"


# --- Defecto: R2 correlatividad (reglas.py, r2_correlatividad) --------------
# Contrato R2: "Una materia con correlativas requeridas admite inscripcion
# solo si el estudiante tiene TODAS ellas aprobadas al momento de la solicitud."
def test_r2_rechaza_si_falta_una_de_las_correlativas():
    materia = NS(codigo="PROG2", plan="P1", correlativas=["PROG1", "MATE1"])
    est = NS(
        id="E1",
        plan="P1",
        historial=[  # PROG1 aprobada, MATE1 nunca aprobada
            NS(materia="PROG1", periodo=PERIODO_ANTERIOR, nota_final=5),
        ],
    )
    inst = _instituto()

    motivo = reglas.r2_correlatividad(inst, est, materia)

    assert motivo == reglas.Motivo.R2_CORRELATIVA_PENDIENTE


# --- Defecto: R7 unicidad (reglas.py, r7_unicidad) --------------------------
# Contrato R7: "Un estudiante no puede tener dos inscripciones activas a la
# misma materia en el mismo periodo, aunque sean comisiones distintas."
def test_r7_rechaza_misma_materia_en_otra_comision():
    c1 = NS(id="C1", materia="PROG1", cupo=30)
    c2 = NS(id="C2", materia="PROG1", cupo=30)  # misma materia, otra comision
    est = NS(id="E1", plan="P1", historial=[])
    ya_inscripto = NS(estudiante="E1", comision="C1", periodo=PERIODO.id)
    inst = _instituto(comisiones={"C1": c1, "C2": c2}, activas_de=[ya_inscripto])

    motivo = reglas.r7_unicidad(inst, est, c2, PERIODO)

    assert motivo == reglas.Motivo.R7_MATERIA_DUPLICADA


# --- Defecto: R3 cupo (reglas.py, r3_cupo / cupo_efectivo) -----------------
# Contrato R3: "Cada inscripcion activa ocupa un lugar [...] Cuando las
# inscripciones activas igualan el cupo, se rechaza."
# => con 9 activas y cupo 10 queda un lugar. El contrato no menciona
#    ninguna reserva para recursantes.
def test_r3_acepta_si_queda_un_lugar():
    comision = NS(id="C1", materia="PROG1", cupo=10)
    activas = [NS(estudiante=f"E{n}", comision="C1") for n in range(9)]  # 9 de 10
    inst = _instituto(comisiones={"C1": comision}, activas_en=activas)

    motivo = reglas.r3_cupo(inst, comision, PERIODO)

    assert motivo is None
