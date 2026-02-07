# chron

A local-first, output-oriented time tracker for the terminal.

chron is not a todo app.
It’s a tiny CLI that helps you see **where time actually goes** — and what tends to block you.

## Why

Most trackers answer: “How long did I work?”
chron tries to answer: “What did I work on — and what got in the way?”

It’s built for low-friction logging:
- track sessions (`start/stop`)
- log friction (anxiety, tired, bored…)
- log habits (cigarettes, beer, spending…)
- leave notes (on an active session or as a day note)
- view logs & summaries

## Features

- **Local-first**: data is stored on your machine only (no cloud, no telemetry).
- **Crash-safe tracking**: active session is persisted (`active.json`).
- **Daily flow**:
  - `log` shows raw sessions
  - `summary` shows aggregated totals
  - `today` is a quick daily pulse
- **Habits**: count/amount tracking (e.g., cigarettes, spending).
- **Friction**: lightweight blockers tracking (e.g., anxiety, tired).
- **Notes**:
  - attaches to active session if present
  - otherwise saved as a day note

## Install (dev)

Editable install:

```bash
python -m pip install -e .
