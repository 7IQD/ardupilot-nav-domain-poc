# Diagnosis Flow

## Steps

1. Availability
   Check if GPS data exists

2. Integrity
   Validate NSats and Status fields

3. Distribution
   Count occurrences of NSats and Status

4. State Mapping
   Convert values into states (HEALTHY, DEGRADED, LOSS)

5. Mismatch Detection
   Identify disagreement between sensor and flight controller

6. Windowing
   Compress rows into time-based windows

7. Verdict
   Assign root cause, confidence, and fixes