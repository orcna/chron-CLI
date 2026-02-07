from datetime import datetime, date, timedelta
from collections import defaultdict



class ActiveSessionError(Exception):
    pass


class NoActiveSessionError(Exception):
    pass

class Tracker:
    def __init__(self, storage):
        self.storage = storage

    def start(self, activity: str):
        if self.storage.load_active():
            raise ActiveSessionError("active session already exists")

        session = {
            "activity": activity,
            "start": datetime.now().isoformat(),
        }

        self.storage.save_active(session)
        return session

    def stop(self):
        session = self.storage.load_active()
        if not session:
            raise NoActiveSessionError("no active session")

        session["end"] = datetime.now().isoformat()
        self.storage.clear_active()
        return session

    def logs_today(self):
        logs = self.storage.load_logs()
        today = date.today().isoformat()

        result = []
        for s in logs:
            if s["start"][:10] == today:
                start = datetime.fromisoformat(s["start"])
                end = datetime.fromisoformat(s["end"])
                s["duration"] = end - start
                result.append(s)

        return result

    def logs_all(self):
        logs = self.storage.load_logs()
        grouped = defaultdict(list)

        for s in logs:
            day = s["start"][:10]
            start = datetime.fromisoformat(s["start"])
            end = datetime.fromisoformat(s["end"])
            s["duration"] = end - start
            grouped[day].append(s)

        # günleri yeni → eski sırala
        return dict(sorted(grouped.items(), reverse=True))

    def summary_today(self):
        logs = self.logs_today()
        return self._summarize(logs)

    def summary_all(self):
        logs = self.storage.load_logs()
        sessions = []

        for s in logs:
            start = datetime.fromisoformat(s["start"])
            end = datetime.fromisoformat(s["end"])
            s["duration"] = end - start
            sessions.append(s)

        return self._summarize(sessions)

    def _summarize(self, sessions):
        totals = defaultdict(timedelta)
        total_time = timedelta()

        for s in sessions:
            totals[s["activity"]] += s["duration"]
            total_time += s["duration"]

        return total_time, dict(totals)

    def status(self):
        session = self.storage.load_active()
        if not session:
            return None

        start = datetime.fromisoformat(session["start"])
        now = datetime.now()

        elapsed = now - start
        session["elapsed"] = elapsed

        return session

    def habit_add(self, name: str):
        data = self.storage.load_habits()
        if name not in data:
            data[name] = {}
        self.storage.save_habits(data)

    def habit_log(self, name: str, count: int = 1):
        data = self.storage.load_habits()
        today = date.today().isoformat()

        if name not in data:
            raise ValueError("habit not found")

        data[name][today] = data[name].get(today, 0) + count
        self.storage.save_habits(data)

    def habit_today(self):
        data = self.storage.load_habits()
        today = date.today().isoformat()

        result = {}
        for habit, days in data.items():
            if today in days:
                result[habit] = days[today]

        return result

    def habit_summary_today(self):
        data = self.storage.load_habits()
        today = date.today().isoformat()

        result = {}
        for habit, days in data.items():
            if today in days:
                result[habit] = days[today]

        return result

    def friction_log(self, name: str, count: int = 1):
        data = self.storage.load_friction()
        today = date.today().isoformat()

        if today not in data:
            data[today] = {}

        data[today][name] = data[today].get(name, 0) + count
        self.storage.save_friction(data)

    def friction_today(self):
        data = self.storage.load_friction()
        today = date.today().isoformat()
        return data.get(today, {})

    def friction_weekly(self):
        data = self.storage.load_friction()
        today = date.today()
        start = today - timedelta(days=6)

        totals = defaultdict(int)
        for day, frictions in data.items():
            d = date.fromisoformat(day)
            if start <= d <= today:
                for name, c in frictions.items():
                    totals[name] += c

        return dict(totals)

    def habit_summary_weekly(self):
        data = self.storage.load_habits()
        today = date.today()
        start_day = today - timedelta(days=6)

        totals = defaultdict(int)

        for habit, days in data.items():
            for day, value in days.items():
                d = date.fromisoformat(day)
                if start_day <= d <= today:
                    totals[habit] += value

        return dict(totals)

    def note(self, text: str):
        # aktif session varsa -> ona yaz
        active = self.storage.load_active()
        if active:
            active["note"] = text
            self.storage.update_active(active)
            return {
                "target": "active",
                "text": text
            }

        # aktif yoksa -> gün notu
        notes = self.storage.load_notes()
        today = date.today().isoformat()

        if today not in notes:
            notes[today] = []

        notes[today].append(text)
        self.storage.save_notes(notes)

        return {
            "target": "day",
            "date": today,
            "text": text
        }
    def fullsum_weekly(self):
        today = date.today()
        start = today - timedelta(days=6)

        # ---- TIME ----
        time_totals = defaultdict(int)
        total_seconds = 0

        logs = self.storage.load_logs()  # sende adı load_log ise onu değiştir
        for s in logs:
            d = date.fromisoformat(s["start"][:10])
            if start <= d <= today:
                start_dt = datetime.fromisoformat(s["start"])
                end_dt = datetime.fromisoformat(s["end"])
                dur = int((end_dt - start_dt).total_seconds())

                time_totals[s["activity"]] += dur
                total_seconds += dur

        # ---- FRICTION ----
        friction = self.friction_weekly()

        # ---- HABITS ----
        habits = self.habit_summary_weekly()

        # ---- NOTES ----
        notes = self.storage.load_notes()
        note_days = [
            d for d in notes.keys()
            if start <= date.fromisoformat(d) <= today
        ]

        return {
            "time": {
                "total": total_seconds,
                "by_activity": dict(time_totals),
            },
            "friction": friction,
            "habits": habits,
            "notes_count": len(note_days),
        }
