# Ingress Python Learning Pack 📦

This is a **printable / downloadable learning sequence**. Each step maps directly to the MAVLink ingress system you are building. Follow **top to bottom**.

---

## Module 0 – Orientation (Read Only)

**Goal:** Know *why* the system is split.

* Concept: *Staffing Agency* architecture
* Files: `manager.py`, `router.py`, `data_manager.py`, `analyser.py`
* Skill: Mental separation of responsibilities

✅ Outcome: You can explain what each file does in one sentence.

---

## Module 1 – Python Memory (`self`, Classes)

**File:** `data_manager.py`
**Skills:**

* `class`, `__init__`, instance state
* Why `self` exists

**Practice:**

* Class that remembers a filename
* Method that writes using remembered state

✅ Outcome: You understand why filenames are *not* passed every call.

---

## Module 2 – Logic & State (Gap Detection)

**File:** `analyser.py`
**Skills:**

* Comparisons (`!=`, `+1`)
* Stateful variables

**Practice:**

* Detect skipped sequence numbers

✅ Outcome: You can explain MAVLink `seq` checking without code.

---

## Module 3 – Dictionaries & JSONL

**File:** `data_manager.py`
**Skills:**

* Python `dict`
* `json.dumps()`
* Append-only files

**Practice:**

* Turn message fields into one JSON line

✅ Outcome: You know why JSONL is used instead of CSV.

---

## Module 4 – Composition (Delegation)

**File:** `router.py`
**Skills:**

* Passing objects into objects
* Delegation vs doing work

**Practice:**

* Router calls `dm.save()` and `analyser.check()`

✅ Outcome: Router contains **no business logic**.

---

## Module 5 – Filesystem & Paths

**File:** `manager.py`
**Skills:**

* Relative vs absolute paths
* Creating directories safely

**Practice:**

* Create log folders before ingest starts

✅ Outcome: Ingress never crashes due to missing folders.

---

## Module 6 – MAVLink Handshake

**File:** `router.py`
**Skills:**

* `mavutil.mavlink_connection`
* Blocking receive

**Practice:**

* Print first received message type

✅ Outcome: You understand the MAVLink firehose model.

---

## Module 7 – Full Ingress Flow (Read Only)

**Files:** All
**Skills:**

* End-to-end packet lifecycle

**Flow:**
MAVLink → Router → DataManager + Analyser → Disk

✅ Outcome: You can debug ingress blindfolded.

---

## How to Use This

1. Treat each **Module as one study session**
2. Do **not skip** modules
3. Stop after each module and explain it aloud

---

## Next Step

When ready, we will:

* Merge Module 3 + 4
* Build a **mini blackbox recorder**


