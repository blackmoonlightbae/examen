"""Solapamiento de franjas horarias. Soporte de la regla R5.

Dos franjas se solapan si caen el mismo dia y sus intervalos se cruzan. El contacto
exacto extremo con extremo no es solapamiento: una clase que termina 21:00 y otra que
empieza 21:00 son compatibles.
"""

from collections.abc import Iterable

from .modelo import Franja


def se_solapan(a: Franja, b: Franja) -> bool:
    """True si `a` y `b` comparten dia y se cruzan en el tiempo."""
    if a.dia != b.dia:
        return False
    return a.inicio < b.fin and b.inicio < a.fin


def chocan(unas: Iterable[Franja], otras: Iterable[Franja]) -> bool:
    """True si alguna franja de `unas` se solapa con alguna de `otras`."""
    otras = tuple(otras)
    return any(se_solapan(a, b) for a in unas for b in otras)
