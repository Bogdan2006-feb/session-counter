from abc import ABC, abstractmethod
import json
import os


class Storage(ABC):

    @abstractmethod
    def save(self, dict) -> None:
        pass

    @abstractmethod
    def load(self) -> dict:
        pass


class FileStorage(Storage):

    def __init__(self, file_path: str = 'counter_data.json'):
        self.file_path = file_path
        self.temp_file_path = file_path + '.tmp'

    def save(self, data: dict) -> None:
        with open(self.temp_file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
            f.flush()
            os.fsync(f.fileno())

        os.replace(self.temp_file_path, self.file_path)

    def load(self) -> dict:
        if not os.path.exists(self.file_path):
            return {}

        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}