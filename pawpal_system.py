from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional


@dataclass
class Owner:
    name: str
    email: str
    preferences: List[str] = field(default_factory=list)
    daily_available_minutes: int = 0

    def add_preference(self, preference: str) -> None:
        pass

    def remove_preference(self, preference: str) -> None:
        pass

    def get_availability(self) -> int:
        pass


@dataclass
class Pet:
    name: str
    species: str
    age: int
    size: str
    energy_level: str
    care_notes: List[str] = field(default_factory=list)

    def update_health_notes(self, note: str) -> None:
        pass

    def needs_today(self) -> List[str]:
        pass


@dataclass
class CareTask:
    title: str
    category: str
    duration_minutes: int
    priority: str
    recurring: bool = False
    notes: str = ""
    completed: bool = False

    def estimate_effort(self) -> int:
        pass

    def mark_complete(self) -> None:
        pass


@dataclass
class DailyPlan:
    date: date
    tasks: List[CareTask] = field(default_factory=list)
    owner: Optional[Owner] = None
    pet: Optional[Pet] = None

    def generate_plan(self) -> List[CareTask]:
        pass

    def add_task(self, task: CareTask) -> None:
        pass

    def remove_task(self, task: CareTask) -> None:
        pass

    def explain_plan(self) -> str:
        pass
