import json
from pathlib import Path
from datetime import datetime, date


class StorageError(Exception):
    pass


class Storage:
    def __init__(self):
        self.base = Path.home() / ".chron"
        self.base.mkdir(exist_ok=True)

        self.active_file = self.base / "active.json"
        self.log_file = self.base / "log.json"

        
    def load_logs(self) -> list[dict]:
        if not self.log_file.exists():
            return []
        return json.loads(self.log_file.read_text())
    # -------- ACTIVE --------

    def save_active(self, session: dict):
        self.active_file.write_text(json.dumps(session))

    def load_active(self) -> dict | None:
        if not self.active_file.exists():
            return None
        return json.loads(self.active_file.read_text())

    def clear_active(self):
        if self.active_file.exists():
            self.active_file.unlink()

    # -------- LOG --------

    def save_session(self, session: dict):
        data = []
        if self.log_file.exists():
            data = json.loads(self.log_file.read_text())

        data.append(session)
        self.log_file.write_text(json.dumps(data, indent=2))

        # -------- HABITS --------

    def load_habits(self) -> dict:
        if not (self.base / "habits.json").exists():
            return {}
        return json.loads((self.base / "habits.json").read_text())

    def save_habits(self, data: dict):
        (self.base / "habits.json").write_text(
            json.dumps(data, indent=2)
        )

    def load_friction(self) -> dict:
        path = self.base / "friction.json"
        if not path.exists():
            return {}
        return json.loads(path.read_text(encoding="utf-8"))

    def save_friction(self, data: dict) -> None:
        path = self.base / "friction.json"
        path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

    def load_notes(self) -> dict:
        path = self.base / "notes.json"
        if not path.exists():
            return {}
        return json.loads(path.read_text(encoding="utf-8"))

    def save_notes(self, data: dict):
        path = self.base / "notes.json"
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def update_active(self, session: dict):
        """active.json'ı güncelle (note/flag vs eklemek için)."""
        path = self.base / "active.json"
        path.write_text(json.dumps(session, ensure_ascii=False, indent=2), encoding="utf-8")
