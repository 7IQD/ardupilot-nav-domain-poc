# Observability Engine Logic

## Chapter 1 — Ingress (Sprint Focus)

## Goal

Capture **raw reality exactly as received** and pass it downstream untouched.

Ingress is **not smart**.
Ingress is **truthful**.

> If Ingress thinks, the architecture leaks.

---

# Responsibility

## What Ingress DOES

* Accept live streams or replay logs
* Decode protocol (MAVLink, etc.)
* Timestamp
* Tag domain
* Persist raw packets

Output = **raw truth**

Nothing more.

---

## What Ingress NEVER DOES

* no calibration
* no unit conversion
* no filtering
* no health scoring
* no schema reshaping
* no STRUTS logic

If any of these appear → ❌ bug

---

# Flow

```
Packet arrives
   ↓
Decode
   ↓
Timestamp
   ↓
Tag domain
   ↓
Store raw
```

Stop.

---

# Repo Mapping (current)

```
src/ingress/
src/data_mart_ingest/
src/archive/ (sniffers/sim)
```

### Typical roles

* router / switch → route packets
* architect / decoder → parse protocol
* ingest_mavlink → capture
* raw vault/bin → storage

All = capture only

---

**Architect (Routing Brain)**
The Architect is the traffic police. For each packet, it answers one question: *“Which domain does this belong to?”* (Nav, Sys, Elec, Payload, etc.). It tags the packet with its identity and forwards it. No math, no transformation. Scaling is simple: add a new `payload_architect.py` for a new domain—everything else stays untouched.

**Decoder (Fact Extractor)**
The Decoder is the measurer. After routing, it pulls only basic facts (voltage, load, currents, angles) and stores them in a clean, canonical shape. No calculation or inference happens here. Adding a new domain simply means adding a corresponding decoder—nothing else changes.

**Together (Scalable Pattern)**
Architect decides *where*, Decoder decides *what*, and the Engine later decides *how/why*. This clear separation allows unlimited domains to be added via small, independent modules, keeping the core pipeline stable.

---

# Output Contract

Example (raw capture only):

```json (only for Examplanation Purpose)
{
  "ts": 1369102,
  "domain": "System",
  "packet": { MAVLink packet unchanged }
}
```

No renaming.
No interpretation.

---

# Scaling Benefit

Because Ingress is dumb:

* new protocol → add adapter only
* new hardware → no engine changes
* replay/live → same downstream path

Ingress becomes **plug-in based**, not fragile.

---

# Sprint Checklist (Fail-Fast)

Before moving on:

* [ ] All packets captured raw
* [ ] No math in ingress files
* [ ] No unit conversion
* [ ] No mart logic
* [ ] Replay works through same path

If all true → Ingress is DONE.

---

# One-Line Memory

**Ingress only listens and writes. It never thinks.**

---

Perfect — let’s **close the Ingress chapter cleanly** with a simple, layman-friendly **who-does-what flow**, mapped to your real files.

No theory. Just **roles + actions**.

---

# Chapter 1 — Ingress

## File Roles & Data Flow (Nav-POC)

## Big picture

Ingress = **receive → tag → store**

It behaves like a **CCTV recorder**.
It records everything. It judges nothing.

---

# Step-by-step flow (real files)

## 1️⃣ Packet arrives (live or replay)

**File**

```
data_mart_ingest/ingest_mavlink.py
```

**Role**
Protocol adapter

**Action**

* listens to MAVLink
* decodes bytes → Python dict

Think: *translator*

---

## 2️⃣ Route by domain

**Files**

```
ingress/action_map.py
ingress/anchor_registry.py
```

**Role**
Traffic controller

**Action**

* checks packet type
* decides domain (Nav / Sys / Estimator / etc.)

Think: *sorting desk*

---

## 3️⃣ Domain architect handles it

**Files**

```
ingress/nav_architect.py
ingress/sys_architect.py
```

**Role**
Domain tagger

**Action**

* attach domain label
* prepare record for storage
* NO interpretation

Think: *label sticker*

---

## 4️⃣ Persist raw truth

**File**

```
vault/clerk.py
```

**Role**
Storage writer

**Action**

* write raw packet to bronze ledger / DB
* timestamp it

Think: *hard disk recorder*

---

# Final result

Stored as:

```
timestamp | domain | raw_packet_blob
```

Still MAVLink-shaped.
Nothing cleaned. Nothing renamed.

---

# Visual summary

```
MAVLink
   ↓
ingest_mavlink  (decode)
   ↓
action_map      (route)
   ↓
architect       (tag)
   ↓
clerk           (store raw)
```

STOP.

No math.
No calibration.
No reshaping.

---

# One-line memory

**Ingress only listens, labels, and logs. It never thinks.**

Ingress chapter = complete.

