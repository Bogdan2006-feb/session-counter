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

    def add_visit(self, ip: str, cookie: Optional[str] = None) -> None:
        visitor_id = f"{ip}:{cookie}" if cookie else ip

        with self.lock:
            self.data.total_visits += 1
            self.data.unique_ips.add(visitor_id)

            today = datetime.now().strftime('%Y-%m-%d')
            self.data.visits_by_day[today] = self.data.visits_by_day.get(today, 0) + 1

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

    def save(self) -> None:
        with self.lock:
            self._save_internal()