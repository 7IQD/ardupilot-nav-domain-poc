# DIY

Absolutely — let’s **divide the template into reusable, clear parts** for your Black Book. Keep it **step-by-step, readable, and meaningful**.

---

# Black Book Template — Python Code Explained (Stepwise)

---

## **Part 1 — Common Python Modules**

**Python:**

```python
import pandas as pd
import os
import time
```

**Layman:**

* `pandas` → handles tabular data like Excel, lets us save packets efficiently.
* `os` → manages folders/files on disk.
* `time` → provides timestamps for packets.

**Key Principle:**

> Always import globally used libraries once. This chapter explains their purpose for all classes.

---

## **Part 2 — Class Initialization (`__init__`)**

**Python:**

```python
class NavArchitect:
    def __init__(self, limit=50):
        self.buffer = []
        self.limit = limit
        self.vault_b = "bin/vault/vault_b"
        os.makedirs(self.vault_b, exist_ok=True)
```

**Layman:**

* `__init__` sets up memory and storage when the object is created.
* `self.buffer` → temporary workspace for incoming packets.
* `self.limit` → max packets before writing to disk.
* `self.vault_b` → folder for storing raw packets.
* `os.makedirs(..., exist_ok=True)` → creates folder if it doesn’t exist.

**Key Principle:**

> Initialization ensures the “work desk” (buffer) and “filing cabinet” (vault) are ready before the session starts.

---

## **Part 3 — Recording Packets (`record`)**

**Python:**

```python
def record(self, msg, inode, mission_id, src_sys, src_comp):
    data = msg.to_dict()
    data['mission_id'] = mission_id
    data['inode']      = inode
    data['src_sys']    = src_sys
    data['src_comp']   = src_comp
    data['mavpackettype'] = msg.get_type()
    data['seq_no'] = msg.get_seq()
    data['wall_ns'] = time.time_ns()
    data['best_ts'] = getattr(msg, 'time_boot_ms', getattr(msg, 'time_usec', getattr(msg, 'timestamp', None)))
    self.buffer.append(data)
    if len(self.buffer) >= self.limit:
        self.flush()
```

**Layman:**

* Converts raw MAVLink packet → dict for easier handling.
* Adds **identity** (mission, inode, system, component).
* Adds **protocol info** (type, sequence, timestamps).
* Stores packet temporarily in memory (`buffer`).
* Flushes to disk automatically if buffer full.

**Key Principle:**

> Record method handles **what packet is and where it comes from**, but does **no heavy math or calibration**.

---

## **Part 4 — Flushing to Disk (`flush`)**

**Python:**

```python
def flush(self):
    if not self.buffer:
        return
    df = pd.DataFrame(self.buffer)
    filename = f"nav_raw_{time.time_ns()}.parquet"
    df.to_parquet(os.path.join(self.vault_b, filename), index=False)
    self.buffer = []
```

**Layman:**

* Converts memory buffer → table (DataFrame).
* Writes to **Parquet** (efficient, schema-preserving columnar format).
* Clears buffer for next batch.

**Why Parquet:**

> Efficient, consistent, and compact storage. Perfect for downstream Data Mart reading.

---

## **Part 5 — Stop Method**

**Python:**

```python
def stop(self):
    self.flush()
```

**Layman:**

* Ensures any remaining packets in memory are saved when session ends.

**Key Principle:**

> Never lose packets — the last flush guarantees completeness.

---

## **Part 6 — Data Flow Summary**

**Layman Flow:**

```
Packet arrives → record() → add identity & metadata → buffer → flush() → Parquet in vault
Stop → flush any remaining packets
```

**Rule of Thumb:**

* **Ingress only**: record & lightly tag.
* **Downstream**: compute, fuse, calibrate (Refinery/Cal Engine).

---

✅ This gives a **precise, modular template** you can reuse across the Black Book, and separates **common Python logic (os/pandas/timestamps)** from **class-specific data handling**.

---

If you want, I can now **draw a one-page visual “Ingress Data Flow”** using this template — perfect to insert into the Black Book for stepwise understanding.

Do you want me to do that next?
