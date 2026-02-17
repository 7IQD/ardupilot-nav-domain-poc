#!/usr/bin/env python3
import os
from pymavlink import mavutil

# ------------------------
# 1️⃣ Project Paths
# ------------------------
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BIN_FILE = os.path.join(ROOT_DIR, "logs", "clean", "clean_20260213_133342.BIN")
OUTPUT_DIR = os.path.join(ROOT_DIR, "logs", "nav_analysis")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Report file
report_file = os.path.join(OUTPUT_DIR, "nav_log_report.txt")

# ------------------------
# 2️⃣ NAV Message Config
# ------------------------
NAV_WHITELIST = ['ATT', 'POS', 'GPS', 'XKF1', 'NKF1', 'AHR2', 'CTUN', 'MAG']

counts = {}
nav_total = 0
other_total = 0

# ------------------------
# 3️⃣ Analyze BIN
# ------------------------
print(f"🧐 Analyzing {os.path.basename(BIN_FILE)}...")

if not os.path.exists(BIN_FILE):
    print(f"❌ ERROR: BIN file not found at {BIN_FILE}")
    exit(1)

mav = mavutil.mavlink_connection(BIN_FILE)
while True:
    m = mav.recv_match()
    if not m:
        break

    m_type = m.get_type()
    counts[m_type] = counts.get(m_type, 0) + 1

    if m_type in NAV_WHITELIST:
        nav_total += 1
    else:
        other_total += 1

# ------------------------
# 4️⃣ Prepare Report
# ------------------------
sorted_counts = dict(sorted(counts.items(), key=lambda x: x[1], reverse=True))

report_lines = []
report_lines.append("\n--- 📊 NAV LOG TOPOGRAPHY ---")
report_lines.append(f"Total Messages: {nav_total + other_total}")
report_lines.append(f"NAV Recorded:   {nav_total} ({(nav_total/(nav_total+other_total))*100:.1f}%)")
report_lines.append(f"Other Dropped:  {other_total}\n")

report_lines.append("--- 📝 Top Message Types ---")
for i, (mtype, count) in enumerate(sorted_counts.items()):
    marker = "⭐ [NAV]" if mtype in NAV_WHITELIST else "   [SKIP]"
    report_lines.append(f"{marker} {mtype.ljust(15)} : {count}")
    if i >= 15:  # top 16 message types
        break

# ------------------------
# 5️⃣ Print & Save
# ------------------------
report_content = "\n".join(report_lines)
print(report_content)

with open(report_file, "w") as f:
    f.write(report_content)

print(f"\n✅ Analysis complete. Report saved to: {report_file}")
