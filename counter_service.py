import threading
from datetime import datetime
from typing import Optional
from data_model import DataModel
from storage import Storage, FileStorage


class CounterService:

    def __init__(self, storage: Optional[Storage] = None):
        self.storage = storage or FileStorage()
        self.lock = threading.Lock()
        self.data = DataModel()
        self.load()

    def add_visit(self, ip: str, user_agent: str, cookie: Optional[str] = None) -> None:
        visitor_id = f"{ip}:{cookie}" if cookie else ip

        now = datetime.now()
        day_key = now.strftime('%Y-%m-%d')

        iso_cal = now.isocalendar()
        week_key = f"{iso_cal[0]}-W{iso_cal[1]}"

        month_key = now.strftime('%Y-%m')

        device_name = user_agent.split('/')[0] if '/' in user_agent else user_agent
        if len(device_name) > 20: device_name = device_name[:20] + "..."

        with self.lock:
            self.data.total_visits += 1
            self.data.unique_ips.add(visitor_id)

            self.data.visits_by_day[day_key] = self.data.visits_by_day.get(day_key, 0) + 1
            self.data.visits_by_week[week_key] = self.data.visits_by_week.get(week_key, 0) + 1
            self.data.visits_by_month[month_key] = self.data.visits_by_month.get(month_key, 0) + 1
            self.data.devices[device_name] = self.data.devices.get(device_name, 0) + 1

            self._save_internal()

    def get_stats(self, period: str = 'all') -> dict:
        with self.lock:
            return self.data.get_stats(period)

    def reset(self) -> None:
        with self.lock:
            self.data = DataModel()
            self._save_internal()

    def _save_internal(self) -> None:
        self.storage.save(self.data.to_dict())

    def load(self) -> None:
        with self.lock:
            data_dict = self.storage.load()
            if data_dict:
                self.data = DataModel.from_dict(data_dict)