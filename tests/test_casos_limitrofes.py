"""Los siete casos limitrofes de la especificacion, uno por test.

Si alguno de estos falla, la implementacion no cumple el contrato del dominio,
aunque los casos obvios pasen.
"""

from datetime import datetime, time, timedelta

import pytest

from arandu.fixtures import PERIODO_ACTUAL, instituto_arandu
from arandu.inscripcion import dar_de_baja, inscribir
from arandu.modelo import Comision, Franja, Motivo

DENTRO = datetime(2026, 9, 10, 20, 0)


@pytest.fixture
def inst():
    return instituto_arandu()


def test_solicitud_exactamente_en_la_apertura_se_acepta(inst):
    apertura = inst.periodos[PERIODO_ACTUAL].apertura
    r = inscribir(inst, "e2", "PROG1-A", PERIODO_ACTUAL, apertura)
    assert r.aceptada


def test_solicitud_exactamente_en_el_cierre_se_acepta(inst):
    cierre = inst.periodos[PERIODO_ACTUAL].cierre
    r = inscribir(inst, "e2", "PROG1-A", PERIODO_ACTUAL, cierre)
    assert r.aceptada


def test_solicitud_un_minuto_despues_del_cierre_se_rechaza(inst):
    tarde = inst.periodos[PERIODO_ACTUAL].cierre + timedelta(minutes=1)
    r = inscribir(inst, "e2", "PROG1-A", PERIODO_ACTUAL, tarde)
    assert not r.aceptada and r.motivo is Motivo.R1_FUERA_DE_VENTANA


def test_baja_exactamente_en_el_plazo_se_acepta(inst):
    assert inscribir(inst, "e2", "PROG1-A", PERIODO_ACTUAL, DENTRO).aceptada
    plazo = inst.periodos[PERIODO_ACTUAL].plazo_de_baja
    assert dar_de_baja(inst, "e2", "PROG1-A", PERIODO_ACTUAL, plazo).aceptada


def test_clases_contiguas_no_son_choque(inst):
    # ALG1-A termina 21:00, MAT1-A empieza 21:00, mismo dia.
    assert inscribir(inst, "e1", "ALG1-A", PERIODO_ACTUAL, DENTRO).aceptada
    r = inscribir(inst, "e1", "MAT1-A", PERIODO_ACTUAL, DENTRO)
    assert r.aceptada, "el contacto extremo con extremo no debe contar como choque"


def test_clases_solapadas_si_son_choque(inst):
    assert inscribir(inst, "e1", "ALG1-A", PERIODO_ACTUAL, DENTRO).aceptada
    r = inscribir(inst, "e1", "ALG2-A", PERIODO_ACTUAL, DENTRO)
    assert not r.aceptada and r.motivo is Motivo.R5_CHOQUE_DE_HORARIOS


def test_cupo_lleno_con_una_baja_previa_deja_lugar(inst):
    # ALG1-A tiene cupo 2.
    assert inscribir(inst, "e1", "ALG1-A", PERIODO_ACTUAL, DENTRO).aceptada
    assert inscribir(inst, "e2", "ALG1-A", PERIODO_ACTUAL, DENTRO).aceptada
    assert inscribir(inst, "e3", "ALG1-A", PERIODO_ACTUAL, DENTRO).motivo is Motivo.R3_SIN_CUPO

    assert dar_de_baja(inst, "e2", "ALG1-A", PERIODO_ACTUAL, DENTRO).aceptada
    r = inscribir(inst, "e3", "ALG1-A", PERIODO_ACTUAL, DENTRO)
    assert r.aceptada, "la baja debe liberar el cupo de inmediato"


def test_correlativa_cursada_y_reprobada_no_habilita(inst):
    # e1 curso PROG1 con 45: reprobada. WEB1 requiere PROG1 aprobada.
    inst.comisiones["WEB1-A"] = Comision(
        "WEB1-A", "WEB1", 30, (Franja(3, time(8, 0), time(10, 0)),)
    )
    r = inscribir(inst, "e1", "WEB1-A", PERIODO_ACTUAL, DENTRO)
    assert not r.aceptada and r.motivo is Motivo.R2_CORRELATIVA_PENDIENTE


def test_correlativa_aprobada_si_habilita(inst):
    # e1 aprobo ALG1 con 85. ALG2 requiere ALG1.
    r = inscribir(inst, "e1", "ALG2-A", PERIODO_ACTUAL, DENTRO)
    assert r.aceptada


def test_materia_sin_correlativas_no_activa_r2(inst):
    assert inscribir(inst, "e2", "MAT1-A", PERIODO_ACTUAL, DENTRO).aceptada


def test_reinscripcion_tras_baja_en_el_mismo_periodo(inst):
    assert inscribir(inst, "e1", "PROG1-A", PERIODO_ACTUAL, DENTRO).aceptada
    assert dar_de_baja(inst, "e1", "PROG1-A", PERIODO_ACTUAL, DENTRO).aceptada
    r = inscribir(inst, "e1", "PROG1-A", PERIODO_ACTUAL, DENTRO)
    assert r.aceptada, "R7 solo mira inscripciones activas"


def test_misma_materia_en_otra_comision_se_rechaza(inst):
    assert inscribir(inst, "e2", "PROG1-A", PERIODO_ACTUAL, DENTRO).aceptada
    r = inscribir(inst, "e2", "PROG1-B", PERIODO_ACTUAL, DENTRO)
    assert not r.aceptada and r.motivo is Motivo.R7_MATERIA_DUPLICADA


def test_cupo_cero_rechaza_siempre(inst):
    r = inscribir(inst, "e1", "BD1-B", PERIODO_ACTUAL, DENTRO)
    assert not r.aceptada and r.motivo is Motivo.R3_SIN_CUPO


def test_orden_de_evaluacion_el_primer_motivo_manda(inst):
    """Fuera de ventana Y sin cupo: debe rechazar por R1, que va primero."""
    tarde = datetime(2026, 10, 1, 20, 0)
    r = inscribir(inst, "e1", "BD1-B", PERIODO_ACTUAL, tarde)
    assert r.motivo is Motivo.R1_FUERA_DE_VENTANA, "R1 se evalua antes que R3"
