from dataclasses import dataclass, field
from datetime import datetime
from typing import Set, Dict


@dataclass
class DataModel:
    total_visits: int = 0
    unique_ips: Set[str] = field(default_factory=set)
    visits_by_day: Dict[str, int] = field(default_factory=dict)
    visits_by_week: Dict[str, int] = field(default_factory=dict)
    visits_by_month: Dict[str, int] = field(default_factory=dict)
    devices: Dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            'total_visits': self.total_visits,
            'unique_ips': list(self.unique_ips),
            'visits_by_day': self.visits_by_day,
            'visits_by_week': self.visits_by_week,
            'visits_by_month': self.visits_by_month,
            'devices': self.devices
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'DataModel':
        obj = cls()
        obj.total_visits = data.get('total_visits', 0)
        obj.unique_ips = set(data.get('unique_ips', []))
        obj.visits_by_day = data.get('visits_by_day', {})
        obj.visits_by_week = data.get('visits_by_week', {})
        obj.visits_by_month = data.get('visits_by_month', {})
        obj.devices = data.get('devices', {})
        return obj

    def get_stats(self, period: str = 'all') -> dict:
        return {
            'total_visits': self.total_visits,
            'unique_visitors': len(self.unique_ips),
            'visits_by_day': self.visits_by_day,
            'visits_by_week': self.visits_by_week,
            'visits_by_month': self.visits_by_month,
            'devices': self.devices,
            'period': period
        }