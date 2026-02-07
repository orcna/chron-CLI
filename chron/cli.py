#!/usr/bin/env python3
import sys
import argparse
from datetime import timedelta

from chron.tracker import (
    Tracker,
    ActiveSessionError,
    NoActiveSessionError,
)

from chron.storage import Storage, StorageError

storage = Storage()
tracker = Tracker(storage)

def fmt(seconds: int) -> str:
    h = seconds // 3600
    m = (seconds % 3600) // 60
    return f"{h}h {m}m"

def cmd_start(args):
    try:
        s = tracker.start(args.activity)
        print(f"▶️ started: {s['activity']}")
    except ActiveSessionError as e:
        print(e)


def cmd_stop(args):
    try:
        finished = tracker.stop()
        storage.save_session(finished)
        print("⏹️ stopped")
    except (NoActiveSessionError, StorageError) as e:
        print(e)


def build_parser():
    parser = argparse.ArgumentParser(prog="chron")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_start = sub.add_parser("start")
    p_start.add_argument("activity")
    p_start.set_defaults(func=cmd_start)

    p_stop = sub.add_parser("stop")
    p_stop.set_defaults(func=cmd_stop)

    p_status = sub.add_parser("status")
    p_status.set_defaults(func=cmd_status)

    p_log = sub.add_parser("log")
    log_sub = p_log.add_subparsers(dest="scope", required=False)

    p_log_today = log_sub.add_parser("today")
    p_log_today.set_defaults(func=cmd_log)

    p_log_all = log_sub.add_parser("all")
    p_log_all.set_defaults(func=cmd_log_all)

    p_summary = sub.add_parser("summary")
    sum_sub = p_summary.add_subparsers(dest="scope", required=False)

    p_sum_today = sum_sub.add_parser("today")
    p_sum_today.set_defaults(func=cmd_summary_today)

    p_sum_all = sum_sub.add_parser("all")
    p_sum_all.set_defaults(func=cmd_summary_all)

    p_habit = sub.add_parser("habit")
    habit_sub = p_habit.add_subparsers(dest="cmd", required=True)

    p_habit_add = habit_sub.add_parser("add")
    p_habit_add.add_argument("name")
    p_habit_add.set_defaults(func=cmd_habit_add)

    p_habit_log = habit_sub.add_parser("log")
    p_habit_log.add_argument("name")
    p_habit_log.add_argument("count", nargs="?", type=int, default=1)
    p_habit_log.set_defaults(func=cmd_habit_log)

    p_habit_summary = habit_sub.add_parser("summary")
    p_habit_summary.set_defaults(func=cmd_habit_summary)


    p_habit_status = habit_sub.add_parser("status")
    p_habit_status.set_defaults(func=cmd_habit_status)

    p_habit_weekly = habit_sub.add_parser("weekly")
    p_habit_weekly.set_defaults(func=cmd_habit_weekly)

    p_friction = sub.add_parser("friction")
    f_sub = p_friction.add_subparsers(dest="cmd", required=True)

    p_f_log = f_sub.add_parser("log")
    p_f_log.add_argument("name")  # <-- BU ŞART
    p_f_log.add_argument("count", nargs="?", type=int, default=1)
    p_f_log.set_defaults(func=cmd_friction_log)

    p_f_today = f_sub.add_parser("today")
    p_f_today.set_defaults(func=cmd_friction_today)

    p_f_weekly = f_sub.add_parser("weekly")
    p_f_weekly.set_defaults(func=cmd_friction_weekly)

    # default
    p_summary.set_defaults(func=cmd_summary_today)

    p_note = sub.add_parser("note")
    p_note.add_argument("text")
    p_note.set_defaults(func=cmd_note)

    p_fullsum = sub.add_parser("fullsum")
    p_fullsum.set_defaults(func=cmd_fullsum)

    # default: chron log  → today
    p_log.set_defaults(func=cmd_log)

    return parser

def format_duration(td: timedelta) -> str:
    seconds = int(td.total_seconds())
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02}:{m:02}:{s:02}"


def cmd_status(args):
    session = tracker.status()

    if not session:
        print("🟢 no active session")
        return

    print(f"⏳ active: {session['activity']}")
    print(f"started: {session['start'][11:16]}")
    print(f"elapsed: {format_duration(session['elapsed'])}")

def cmd_log(args):
    sessions = tracker.logs_today()

    if not sessions:
        print("📭 no logs yet")
        return

    print(f"📅 {sessions[0]['start'][:10]}")

    for s in sessions:
        dur = format_duration(s["duration"])
        print(f"- {s['activity']:<10} {dur}")

def cmd_log_all(args):
    data = tracker.logs_all()

    if not data:
        print("📭 no logs yet")
        return

    for day, sessions in data.items():
        print(f"\n📅 {day}")
        for s in sessions:
            dur = format_duration(s["duration"])
            print(f"- {s['activity']:<10} {dur}")

def print_summary(title, total, by_activity):
    print(f"🧠 Summary ({title})")
    print(f"Total time: {format_duration(total)}\n")

    for act, dur in sorted(
        by_activity.items(),
        key=lambda x: x[1],
        reverse=True,
    ):
        print(f"- {act:<10} {format_duration(dur)}")


def cmd_summary_today(args):
    total, data = tracker.summary_today()
    if total.total_seconds() == 0:
        print("📭 no data")
        return
    print_summary("today", total, data)


def cmd_summary_all(args):
    total, data = tracker.summary_all()
    if total.total_seconds() == 0:
        print("📭 no data")
        return
    print_summary("all time", total, data)

def cmd_habit_add(args):
    tracker.habit_add(args.name)
    print(f"➕ habit added: {args.name}")


def cmd_habit_log(args):
    tracker.habit_log(args.name, args.count)
    print(f"✍️ logged: {args.name} (+{args.count})")


def cmd_habit_status(args):
    data = tracker.habit_today()
    if not data:
        print("🟢 no habits logged today")
        return

    print("📌 habits today:")
    for h, c in data.items():
        print(f"- {h}: {c}")

def cmd_habit_summary(args):
    data = tracker.habit_summary_today()

    if not data:
        print("🟢 no habits today")
        return

    print("📊 Habit summary (today)\n")
    for h, v in data.items():
        if h in ("spend", "money", "expense"):
            print(f"- {h:<10}: ₺{v}")
        else:
            print(f"- {h:<10}: {v}")

def cmd_habit_weekly(args):
    data = tracker.habit_summary_weekly()

    if not data:
        print("🟢 no habits in last 7 days")
        return

    print("📊 Habit summary (last 7 days)\n")
    for h, v in data.items():
        if h in ("spend", "money", "expense"):
            print(f"- {h:<10}: ₺{v}")
        else:
            print(f"- {h:<10}: {v}")

def cmd_friction_log(args):
    tracker.friction_log(args.name, args.count)
    print(f"⚠ friction logged: {args.name} x{args.count}")

def cmd_note(args):
    res = tracker.note(args.text)
    if res["target"] == "active":
        print("📝 noted on active session")
    else:
        print(f"📝 noted for {res['date']}")

def cmd_friction_today(args):
    data = tracker.friction_today()
    if not data:
        print("🟢 no friction today")
        return

    print("⚠ friction today:")
    for k, v in data.items():
        print(f"- {k}: {v}")


def cmd_friction_weekly(args):
    data = tracker.friction_weekly()
    if not data:
        print("🟢 no friction last 7 days")
        return

    print("⚠ friction (last 7 days):")
    for k, v in sorted(data.items(), key=lambda x: x[1], reverse=True):
        print(f"- {k}: {v}")

def cmd_fullsum(args):
    data = tracker.fullsum_weekly()

    print("📊 FULL SUMMARY (last 7 days)\n")

    # TIME
    print("⏱ Time")
    print(f"- total      : {fmt(data['time']['total'])}")

    for act, sec in sorted(
        data["time"]["by_activity"].items(),
        key=lambda x: x[1],
        reverse=True,
    ):
        print(f"- {act:<10}: {fmt(sec)}")

    # FRICTION
    if data["friction"]:
        print("\n⚠ Friction")
        for k, v in data["friction"].items():
            print(f"- {k:<10}: {v}")

    # HABITS
    if data["habits"]:
        print("\n🔁 Habits")
        for k, v in data["habits"].items():
            if k in ("spend", "money", "expense"):
                print(f"- {k:<10}: ₺{v}")
            else:
                print(f"- {k:<10}: {v}")

    # NOTES
    print(f"\n📝 Notes\n- {data['notes_count']} day notes")

def main():
    args = build_parser().parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
