# 🛸 Stage 1: O-Level Ingress Architecture – Data / Layer Documentation

## 1. Purpose
Provide a simple, clear architecture for capturing, routing, decoding, and storing MAVLink messages in a beginner-friendly O-Level Ingress system.

---

## 2. Layered Architecture Overview

| Layer | Component | Responsibility | Data Flow / State |
|-------|----------|----------------|-----------------|
| **Transport / Connection Layer** | `mavutil.mavlink_connection` | Connect to SITL / Drone, receive raw MAVLink packets | **Input:** MAVLink UDP/TCP packets <br> **Output:** `msg` objects to Switch |
| **Switch Layer (Routing)** | `IngressSwitch` | Routes messages based on `msgid` to appropriate decoders | **Input:** `msg` <br> **Output:** Forwarded `msg` to registered `DomainDecoder` |
| **Decoder Layer (Domain Brain)** | `DomainDecoder` (GPS, Attitude, etc.) | Process domain-specific messages, maintain minimal **state** | **Input:** `msg` <br> **State:** Last received messages per type <br> **Output:** Processed info / debug logs |
| **Storage / Logger Layer** | `DataManager` | Persist raw bytes of messages to disk | **Input:** `msg.get_msgbuf()` <br> **Output:** Binary storage for auditing / replay |
| **Integrity / Audit Layer** | `analyser.py` | Verify consistency of stored messages | **Input:** Stored database <br> **Output:** Registry depth, binary size confirmation |

---

## 3. Data Flow Description

[MAVLink Drone / SITL]
|
v
[Transport Layer: Connection]
|
v
[Switch Layer: IngressSwitch]
|-- msgid=GPS --> [GPSDecoder] --+
|-- msgid=ATT --> [AttitudeDecoder] --> [DataManager]
|-- msgid=BATT --> [BatteryDecoder] --> [DataManager]
|
v
[Storage / Logger Layer: DataManager]
|
v
[Integrity / Audit Layer: analyser.py]


**Notes:**
- Each message follows a **linear path**: capture → route → decode → store → audit.
- **Switch Layer** is stateless; decisions are based only on `msgid`.
- **Decoder Layer** holds **state** to track last values (e.g., last GPS coordinate).
- **DataManager** ensures reliable persistence; later stages can replay or analyze data.

---

## 4. Sample Data Structure

**Binary Storage Entry (via DataManager):**

+----------------+----------------+----------------+
| Header (4B) | Msg Length (2B)| MAVLink Payload|
+----------------+----------------+----------------+

- Header: unique Inode or packet ID
- Msg Length: size of MAVLink message
- Payload: raw MAVLink bytes

**Decoder State Example (Python dict):**
```python
{
    "GPS_RAW_INT": {"lat": 12345678, "lon": 87654321, "alt": 120},
    "ATTITUDE": {"roll": 0.1, "pitch": -0.2, "yaw": 1.57}
}

5. Responsibilities Summary
| Responsibility                     | Layer / Component |
| ---------------------------------- | ----------------- |
| Capture messages from SITL / Drone | Transport Layer   |
| Route messages to correct domain   | Switch Layer      |
| Parse & store domain-specific info | Decoder Layer     |
| Persist raw packets                | Storage Layer     |
| Confirm database integrity         | Audit Layer       |

| Responsibility                     | Layer / Component |
| ---------------------------------- | ----------------- |
| Capture messages from SITL / Drone | Transport Layer   |
| Route messages to correct domain   | Switch Layer      |
| Parse & store domain-specific info | Decoder Layer     |
| Persist raw packets                | Storage Layer     |
| Confirm database integrity         | Audit Layer       |

6. Next Steps for Stage 2

Introduce multi-domain parallel decoding.

Add lightweight filtering / preprocessing in the switch.

Enable real-time statistics / packet counters per domain.