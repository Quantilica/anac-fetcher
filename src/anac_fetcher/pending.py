"""Aviso de período pendente sem publicação há meses.

Entradas ``pending_publication`` (período que a ANAC pode ainda não ter publicado)
não dão erro no 404. Para que um arquivo renomeado não fique "pendente" para
sempre, o ``sync`` e o ``check`` emitem um WARNING quando o período pendente mais
antigo que deu 404 está a mais de :data:`PENDING_WARN_MONTHS` meses de hoje.
"""

from __future__ import annotations

import datetime as dt
from collections.abc import Iterable
from typing import Any

from .catalog_movimentacao import LAST_PUBLISHED

# Meses de calendário sem publicação a partir dos quais o aviso aparece. A
# movimentação aeroportuária tem defasagem de meses; seis ainda é normal.
PENDING_WARN_MONTHS = 6


def _index(year: int, month: int) -> int:
    return year * 12 + (month - 1)


def stale_pending_message(
    pending_404: Iterable[dict[str, Any]], today: dt.date | None = None
) -> str | None:
    """Mensagem de aviso, ou ``None``, para as entradas pendentes que deram 404.

    Args:
        pending_404: Entradas ``pending_publication`` cujo 404 o host tolerou.
        today: Data de referência (testes); padrão hoje.

    Returns:
        Uma linha com o grupo, o mês mais antigo sem publicação, quantos meses
        faz e a sugestão de conferir o nome ou rodar ``discover``; ``None`` se o
        período mais antigo está a ``PENDING_WARN_MONTHS`` meses ou menos de hoje
        (ou se não há entrada com ano e mês).
    """
    today = today or dt.date.today()
    oldest: dict[str, tuple[int, int]] = {}
    for entry in pending_404:
        year, month = entry.get("year"), entry.get("month")
        if not isinstance(year, int) or not isinstance(month, int):
            continue
        group = str(entry.get("group"))
        if group not in oldest or (year, month) < oldest[group]:
            oldest[group] = (year, month)
    lines = []
    for group, (year, month) in sorted(oldest.items()):
        age = _index(today.year, today.month) - _index(year, month)
        if age <= PENDING_WARN_MONTHS:
            continue
        last = ""
        if group == "movimentacao-aeroportuaria":
            last_year, last_month = LAST_PUBLISHED
            last = f" (último mês confirmado no catálogo: {last_year}-{last_month:02d})"
        lines.append(
            f"{group}: sem publicação desde {year}-{month:02d} ({age} meses){last}; "
            "a fonte pode ter mudado o nome do arquivo: confira o endereço ou "
            "rode 'discover'"
        )
    if not lines:
        return None
    return "[Alerta] período pendente sem publicação há meses: " + " | ".join(lines)
