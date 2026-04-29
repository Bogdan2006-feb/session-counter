from dataclasses import dataclass, field
from datetime import datetime
from typing import Set, Dict


@dataclass
class DataModel:
    total_visits: int = 0
    unique_ips: Set[str] = field(default_factory=set)
    visits_by_day: Dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            'total_visits': self.total_visits,
            'unique_ips': list(self.unique_ips),
            'visits_by_day': self.visits_by_day
        }

    @classmethod
    def from_dict(cls, dict) -> 'DataModel':
        obj = cls()
        obj.total_visits = data.get('total_visits', 0)
        obj.unique_ips = set(data.get('unique_ips', []))
        obj.visits_by_day = data.get('visits_by_day', {})
        return obj

    def get_stats(self, period: str = 'all') -> dict:
        if period == 'all':
            return {
                'total_visits': self.total_visits,
                'unique_visitors': len(self.unique_ips),
                'period': 'all_time'
            }
        elif period == 'today':
            today = datetime.now().strftime('%Y-%m-%d')
            today_visits = self.visits_by_day.get(today, 0)
            return {
                'total_visits': today_visits,
                'unique_visitors': len(self.unique_ips),
                'period': 'today'
            }
        else:
            return {
                'total_visits': self.total_visits,
                'unique_visitors': len(self.unique_ips),
                'period': period
            }