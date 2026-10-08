"""Sector interface for the F3 coupling loop (Phase 2, M0; decision N3 is the Proposed record of these choices).

A sector is a self-contained piece of the model with named, typed inputs and outputs. The coupling loop (``f3.core.model``)
advances all sectors with a fixed step (D-003: 0.25 year) and moves values between them by name. The interface is kept to
what S1 (population), S3 (AI) and FaIR (climate, annual) need; everything else is deliberately left out and listed in
``docs/coupling-interface.md`` under "Not in this interface".

Rules
-----
* A sector integrates itself inside ``advance`` (S1 uses RK4). The loop does not integrate for it.
* Values cross sector boundaries **at step boundaries**. Within one step a coupled input is the other sector's value at the
  *start* of the step, held constant (explicit coupling, first-order accurate in the loop step). Because every sector reads
  the start-of-step values, the order in which sectors are advanced does not matter.
* Exception: a sector whose output is a recorded series (``ReplaySector``) can be asked for its value at any time inside the
  step. This is how a sector is tested alone against a reference's recorded inputs (the Phase 1 method).
* Units are strings and must match exactly across a coupling; there is no automatic conversion, so a unit change is an
  explicit, visible adapter.
"""

from __future__ import annotations

from typing import Dict, Mapping, Optional


class Context:
    """What a sector sees while it advances: its inputs, by name, at a query time inside the current step."""

    def __init__(self, sector: "Sector", wiring: Mapping[str, tuple], snapshot: Mapping[str, Mapping[str, float]],
                 sectors: Mapping[str, "Sector"]):
        self._sector = sector
        self._wiring = wiring
        self._snapshot = snapshot
        self._sectors = sectors

    def input(self, name: str, t: float) -> float:
        """Value of input ``name`` at time ``t`` (``t`` is within the current step)."""
        try:
            src_name, out_name = self._wiring[name]
        except KeyError:
            raise KeyError(f"input {name!r} of sector {self._sector.name!r} is not wired") from None
        src = self._sectors[src_name]
        if src.exact_in_time:
            return src.output_at(out_name, t)
        return self._snapshot[src_name][out_name]


class Sector:
    """Base class. Subclasses set ``name``, ``inputs``, ``outputs`` (name -> unit) and implement the three methods."""

    name: str = ""
    #: input name -> unit
    inputs: Mapping[str, str] = {}
    #: output name -> unit
    outputs: Mapping[str, str] = {}
    #: advance every ``period`` years instead of every loop step; must be a multiple of the loop step. None = every step.
    period: Optional[float] = None
    #: True if ``output_at`` can answer for any time (recorded series); False for sectors that hold values per step.
    exact_in_time: bool = False

    def reset(self, t0: float, t1: float, dt: float) -> None:
        """Set the initial state at ``t0``. ``t1`` and ``dt`` are given so a sector can check its own switch times."""
        raise NotImplementedError

    def current_outputs(self) -> Dict[str, float]:
        """Outputs at the sector's current time (the end of the last ``advance``, or ``t0`` after ``reset``)."""
        raise NotImplementedError

    def advance(self, t: float, h: float, ctx: Context) -> None:
        """Integrate from ``t`` to ``t + h``. ``h`` is the loop step, or ``period`` for a slow sector."""
        raise NotImplementedError

    def output_at(self, name: str, t: float) -> float:
        """Only for ``exact_in_time`` sectors."""
        raise NotImplementedError(f"sector {self.name!r} cannot give an output at an arbitrary time")
