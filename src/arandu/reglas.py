"""Las reglas del dominio, una funcion por regla.

Cada funcion devuelve el `Motivo` del rechazo, o `None` si la regla no se opone.
Ninguna regla conoce a las demas ni decide el orden: de eso se ocupa `inscripcion.py`.
"""

from datetime import datetime

from .horarios import chocan
from .modelo import Comision, Estudiante, Instituto, Materia, Motivo, Periodo


def r1_ventana(periodo: Periodo, ahora: datetime) -> Motivo | None:
    """La solicitud cae dentro de [apertura, cierre], ambos extremos incluidos."""
    if periodo.apertura <= ahora <= periodo.cierre:
        return None
    return Motivo.R1_FUERA_DE_VENTANA


def r2_correlatividad(inst: Instituto, est: Estudiante, materia: Materia) -> Motivo | None:
    """Todas las correlativas requeridas estan aprobadas.

    Aprobada = nota final registrada >= el minimo del plan. Cursada y reprobada no habilita.
    """
    if not materia.correlativas:
        return None
    minimo = inst.planes[est.plan].minimo_aprobacion
    aprobadas = {n.materia for n in est.historial if n.nota_final >= minimo}
    if set(materia.correlativas) <= aprobadas:
        return None
    return Motivo.R2_CORRELATIVA_PENDIENTE


def r7_unicidad(inst: Instituto, est: Estudiante, materia: Materia, periodo: Periodo) -> Motivo | None:
    """No hay otra inscripcion ACTIVA a la misma materia en el mismo periodo."""
    for i in inst.activas_de(est.id, periodo.id):
        if inst.comisiones[i.comision].materia == materia.codigo:
            return Motivo.R7_MATERIA_DUPLICADA
    return None


def r4_maximo(inst: Instituto, est: Estudiante, periodo: Periodo) -> Motivo | None:
    """El estudiante no supera el maximo de inscripciones activas del plan."""
    maximo = inst.planes[est.plan].maximo_materias
    if len(inst.activas_de(est.id, periodo.id)) >= maximo:
        return Motivo.R4_MAXIMO_SUPERADO
    return None


def r5_choque(inst: Instituto, est: Estudiante, comision: Comision, periodo: Periodo) -> Motivo | None:
    """Las franjas de la comision no se solapan con ninguna inscripcion activa."""
    for i in inst.activas_de(est.id, periodo.id):
        if chocan(comision.franjas, inst.comisiones[i.comision].franjas):
            return Motivo.R5_CHOQUE_DE_HORARIOS
    return None


def r3_cupo(inst: Instituto, comision: Comision, periodo: Periodo) -> Motivo | None:
    """Quedan lugares. Las bajas no ocupan cupo."""
    if len(inst.activas_en(comision.id, periodo.id)) >= comision.cupo:
        return Motivo.R3_SIN_CUPO
    return None
