"""Entidades del dominio. Todas inmutables salvo la inscripcion, que cambia de estado.

Las marcas de tiempo son `datetime` sin zona y se interpretan en America/Asuncion.
Es una simplificacion declarada de la v1: el sistema nunca lee el reloj, lo recibe.
"""

from dataclasses import dataclass, field
from datetime import datetime, time
from enum import Enum


class Estado(str, Enum):
    ACTIVA = "activa"
    BAJA = "baja"


class Motivo(str, Enum):
    """Motivo de rechazo. El prefijo nombra la regla que lo produjo."""

    R1_FUERA_DE_VENTANA = "R1_fuera_de_ventana"
    R2_CORRELATIVA_PENDIENTE = "R2_correlativa_pendiente"
    R7_MATERIA_DUPLICADA = "R7_materia_duplicada"
    R4_MAXIMO_SUPERADO = "R4_maximo_superado"
    R5_CHOQUE_DE_HORARIOS = "R5_choque_de_horarios"
    R3_SIN_CUPO = "R3_sin_cupo"
    R6_FUERA_DE_PLAZO = "R6_fuera_de_plazo_de_baja"
    R6_SIN_INSCRIPCION = "R6_inscripcion_inexistente"


@dataclass(frozen=True)
class Franja:
    """Un bloque de clase semanal. `dia`: 0 = lunes ... 6 = domingo."""

    dia: int
    inicio: time
    fin: time


@dataclass(frozen=True)
class Plan:
    codigo: str
    minimo_aprobacion: float = 60.0
    maximo_materias: int = 6


@dataclass(frozen=True)
class Materia:
    codigo: str
    nombre: str
    plan: str
    correlativas: tuple[str, ...] = ()


@dataclass(frozen=True)
class Comision:
    id: str
    materia: str
    cupo: int
    franjas: tuple[Franja, ...]


@dataclass(frozen=True)
class Periodo:
    id: str
    apertura: datetime
    cierre: datetime
    plazo_de_baja: datetime


@dataclass(frozen=True)
class NotaHistorica:
    materia: str
    periodo: str
    nota_final: float


@dataclass(frozen=True)
class Estudiante:
    id: str
    nombre: str
    plan: str
    historial: tuple[NotaHistorica, ...] = ()


@dataclass
class Inscripcion:
    estudiante: str
    comision: str
    periodo: str
    estado: Estado
    solicitada_en: datetime


@dataclass(frozen=True)
class Resultado:
    """Salida de una operacion. Si `aceptada` es False, `motivo` dice por que."""

    aceptada: bool
    motivo: Motivo | None = None


@dataclass
class Instituto:
    """Estado completo del sistema. En la v1 vive en memoria."""

    planes: dict[str, Plan] = field(default_factory=dict)
    materias: dict[str, Materia] = field(default_factory=dict)
    comisiones: dict[str, Comision] = field(default_factory=dict)
    periodos: dict[str, Periodo] = field(default_factory=dict)
    estudiantes: dict[str, Estudiante] = field(default_factory=dict)
    inscripciones: list[Inscripcion] = field(default_factory=list)

    def activas_de(self, estudiante: str, periodo: str) -> list[Inscripcion]:
        return [
            i
            for i in self.inscripciones
            if i.estudiante == estudiante and i.periodo == periodo and i.estado is Estado.ACTIVA
        ]

    def activas_en(self, comision: str, periodo: str) -> list[Inscripcion]:
        return [
            i
            for i in self.inscripciones
            if i.comision == comision and i.periodo == periodo and i.estado is Estado.ACTIVA
        ]
