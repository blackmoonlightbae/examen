"""Orquestacion: evalua las reglas en el orden del contrato y decide.

R8 — orden de evaluacion: R1 -> R2 -> R7 -> R4 -> R5 -> R3.
Se rechaza con EL PRIMER motivo que aplique, no con la lista de todos los motivos.
El orden es parte del contrato: hace que el motivo de rechazo sea verificable.
"""

from datetime import datetime

from . import reglas
from .modelo import Estado, Inscripcion, Instituto, Motivo, Resultado

ORDEN_DE_EVALUACION = ("R1", "R2", "R7", "R4", "R5", "R3")


def inscribir(
    inst: Instituto,
    estudiante_id: str,
    comision_id: str,
    periodo_id: str,
    ahora: datetime,
) -> Resultado:
    """Intenta inscribir al estudiante en la comision. No lanza excepciones: devuelve Resultado."""
    est = inst.estudiantes[estudiante_id]
    com = inst.comisiones[comision_id]
    per = inst.periodos[periodo_id]
    mat = inst.materias[com.materia]

    comprobaciones = (
        lambda: reglas.r1_ventana(per, ahora),
        lambda: reglas.r2_correlatividad(inst, est, mat),
        lambda: reglas.r7_unicidad(inst, est, mat, per),
        lambda: reglas.r4_maximo(inst, est, per),
        lambda: reglas.r5_choque(inst, est, com, per),
        lambda: reglas.r3_cupo(inst, com, per),
    )

    for comprobar in comprobaciones:
        motivo = comprobar()
        if motivo is not None:
            return Resultado(aceptada=False, motivo=motivo)

    inst.inscripciones.append(
        Inscripcion(
            estudiante=estudiante_id,
            comision=comision_id,
            periodo=periodo_id,
            estado=Estado.ACTIVA,
            solicitada_en=ahora,
        )
    )
    return Resultado(aceptada=True)


def dar_de_baja(
    inst: Instituto,
    estudiante_id: str,
    comision_id: str,
    periodo_id: str,
    ahora: datetime,
) -> Resultado:
    """R6 — la baja se admite hasta el plazo del periodo, inclusive."""
    per = inst.periodos[periodo_id]
    if ahora > per.plazo_de_baja:
        return Resultado(aceptada=False, motivo=Motivo.R6_FUERA_DE_PLAZO)

    for i in inst.inscripciones:
        if (
            i.estudiante == estudiante_id
            and i.comision == comision_id
            and i.periodo == periodo_id
            and i.estado is Estado.ACTIVA
        ):
            i.estado = Estado.BAJA
            return Resultado(aceptada=True)

    return Resultado(aceptada=False, motivo=Motivo.R6_SIN_INSCRIPCION)
