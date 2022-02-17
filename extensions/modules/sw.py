"""Module containing classes and helper functions for the FFG SW TTRPG."""

from dataclasses import dataclass, field
from itertools import chain
from enum import Enum, auto
from typing import Union
from random import choice

class SWSymbols(str, Enum):
	_generate_next_value_ = lambda n, *a: n
	TRIUMPH = TR = auto()
	SUCCESS = SU = auto()
	ADVANTAGE = AD = auto()
	BLANK = BL = auto()
	THREAT = TH = auto()
	FAILURE = FA = auto()
	DESPAIR = DE = auto()
	LIGHT= LI = auto()
	DARK = DA = auto()

@dataclass(frozen=True, eq=True, order=True)
class _SWDie:
	faces: tuple[tuple[SWSymbols]] = field(compare=False, repr=False)
	color: str

def _parse_swdie(raw: str,  color: str) -> tuple[Union[tuple[tuple[SWSymbols]], str]]:
	"""
	Turn a string into a tuple of faces, where a "face" is a tuple of symbols.
	Then pass that tuple, plus the color, wrapped in another tuple for parsing as a _Die
	"""
	return tuple(tuple(SWSymbols[face[i:i+2]] for i in range(0, len(face), 2)) for face in raw.split(" ")), color

class SWDice(_SWDie, Enum):
	PROFICIENCY = YELLOW = Y = _parse_swdie("TRSU SUSU SUSU SUAD SUAD SUAD ADAD ADAD SU SU AD BL", "YELLOW")
	ABILITY = GREEN = G = _parse_swdie("SUSU SUAD ADAD SU SU AD AD BL", "GREEN")
	BOOST = BLUE = B = _parse_swdie("SUAD ADAD SU AD BL BL", "BLUE")
	FORCE = WHITE = W = _parse_swdie("LILI LILI LILI LI LI DADA DA DA DA DA DA DA", "WHITE")
	SETBACK = BLACK = K = _parse_swdie("FA FA TH TH BL BL", "BLACK")
	DIFFICULTY = PURPLE = P = _parse_swdie("FAFA FATH THTH FA TH TH TH BL", "PURPLE")
	CHALLENGE = RED = R = _parse_swdie("DEFA FAFA FAFA FATH FATH THTH THTH FA FA TH TH BL", "RED")

class Roll(dict):
	_cancels = ((SWSymbols.SU, SWSymbols.FA), (SWSymbols.AD, SWSymbols.TH))
	def __init__(self, **dice: int):
		for name, num in dice.items():
			if (die := SWDice[name.upper()]) in self:
				raise KeyError(f"Die \"{name}\" declared twice")
			self[die] = num

		self._results = dict()
		for die, num in self.items():
			self._results[die] = tuple(choice(die.faces) for _ in range(num))

		flat = tuple(chain(*chain(*self._results.values())))
		count = {sym:flat.count(sym) for sym in SWSymbols}
		count[SWSymbols.BL] = 0
		for a, b in self._cancels:
			count[a] -= (m := min(count[a], count[b]))
			count[b] -= m
		self._total = {k:v for k,v in count.items() if v} or {SWSymbols.BL: 1}

	@property
	def results(self):
		return self._results.copy()

	@property
	def total(self):
		return self._total.copy()
