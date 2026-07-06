# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:
All tasks for Nick:
[high] Feed Bindi (due 2026-07-05) - pending
[medium] Play with Bindi (due 2026-07-06) - pending
[low] Groom Bindi (due 2026-07-07) - pending
[high] Feed Sushi (due 2026-07-06) - pending
[medium] Play with Sushi (due 2026-07-07) - pending
[low] Groom Sushi (due 2026-07-08) - pending

Task sheet for Bindi:

- Feed Bindi: Feed Bindi her favorite cat food.
- Play with Bindi: Spend 15 minutes playing with Bindi using her favorite toy.
- Groom Bindi: Groom Bindi to keep her coat healthy and shiny.

Task sheet for Sushi:

- Feed Sushi: Feed Sushi her favorite cat food.
- Play with Sushi: Spend 15 minutes playing with Sushi using her favorite toy.
- Groom Sushi: Groom Sushi to keep her coat healthy and shiny.

```
# e.g.:
# Daily plan for Biscuit (Golden Retriever):
#   08:00 — Morning walk (30 min) [priority: high]
#   09:00 — Feeding (10 min) [priority: high]
#   ...
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

## 📐 Smarter Scheduling

All scheduling logic lives in `pawpal_system.py`. Each feature and the method
that implements it:

| Feature                  | Method(s)                                                     | Notes                                                        |
| ------------------------ | ------------------------------------------------------------ | ----------------------------------------------------------- |
| Sort by time             | `Scheduler.sortByTime()` (→ module `sortByTime()`)           | Chronological agenda; untimed tasks sort last               |
| Sort by urgency          | `Scheduler.prioritize()`                                     | Priority rank, then due date                                |
| Filter by pet / status   | `Owner.filterTasks(status=, petName=)`                       | Also `filterTasks()` (status/priority), `getTasksForPet()`  |
| Conflict — exact time    | `Scheduler.conflictWarnings()`                               | Lightweight, returns warning strings, never raises          |
| Conflict — overlap       | `Scheduler.detectConflicts()` (helper `_firstOverlap()`)     | Sort-and-sweep of time windows                              |
| Recurring tasks          | `Task.nextOccurrence()`, `Plan.completeTask()` / `skipTask()`| Fixed cadence off each due date; `expandRecurring()` preview |
| Schedule building        | `Scheduler.buildSchedule()`                                  | Honors fixed times, packs untimed tasks into the gaps       |

### Sorting behavior

- **`Scheduler.sortByTime(tasks)`** — orders tasks chronologically using
  `sorted()` with a tuple `key` lambda: **due date → time of day → priority →
  title**. Because `dueTime` is a `datetime.time`, comparison is chronological
  with no `"HH:MM"` string-padding bugs; untimed (all-day) tasks sort after
  timed ones on the same day. Delegates to the module-level `sortByTime()` so
  there is a single implementation.
- **`Scheduler.prioritize(tasks)`** — the urgency sort used when packing:
  `PRIORITY_RANK` (high → medium → low), then due date.

### Filtering behavior

- **`Owner.filterTasks(status=None, petName=None)`** — filters across all pets
  by completion status (`"pending"` / `"done"`) and/or pet name
  (case-insensitive). Lives on `Owner` because it is the only object that knows
  both the tasks and which pet each belongs to.
- **`filterTasks(tasks, status=, priority=)`** (module-level) — a task-list
  helper for status/priority filtering that composes with sorting.
- **`Owner.getTasksForPet(petId)`** — per-pet lookup without scanning every pet.

### Conflict detection logic

Two complementary strategies:

- **`Scheduler.conflictWarnings(tasks)`** — the *lightweight* check. Buckets
  timed, pending tasks by `(dueDate, dueTime)` in a single `O(n)` pass and
  returns a human-readable warning **string** for any slot holding 2+ tasks
  (same pet or across pets). It **never raises** — callers print and continue.
  Trade-off: detects only exact-time ties, not overlapping durations.
- **`Scheduler.detectConflicts(tasks)`** — the richer check. Sorts by start
  time and sweeps once (`O(n log n)`), flagging tasks whose
  `[start, start + duration)` windows overlap. Returns `(earlier, later)` task
  pairs. Uses the `_firstOverlap()` helper (strict inequalities, so back-to-back
  tasks are not treated as clashing).

### Recurring task logic

- **`Task.recurrence`** (`"daily"` / `"weekly"`) and **`Task.interval`** define
  the rule; the stored task is the template.
- **`Task.nextOccurrence()`** — builds the next instance by advancing the
  task's **own due date** with `timedelta` (`days` for daily, `weeks` for
  weekly), so the cadence stays fixed no matter when you act. `timedelta`
  handles month/year rollover automatically.
- **`Plan.completeTask(task)`** — marks a task done (kept as a history entry)
  and, if it recurs, stores the next occurrence.
- **`Plan.skipTask(task)`** — drops the task (no history entry) but still rolls
  the series forward to the next occurrence.
- **`Task.occurrences(start, end)`** and **`expandRecurring(tasks, start, end)`**
  — materialize concrete dated occurrences within a window on demand (storage
  stays `O(1)` per recurring template).

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** _(optional)_: <!-- Insert a screenshot or link to a demo video here -->
