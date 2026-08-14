# Drone Log Analysis — Investigation Flow

This flow is used consistently to study existing open-source drone
log-analysis tools.

The objective is to understand how telemetry is represented and
presented, not simply to list application features.

## Investigation Flow

Existing Drone Tool
        ↓
Data Source
        ↓
Standard / Protocol / Format
        ↓
Data + Semantic Model
        ↓
Metadata
        ↓
Time / Sampling
        ↓
Stream Integrity
        ↓
Presentation
        ↓
Parameter Relationships
        ↓
Domain Representation
        ↓
Drill-down / Evidence
        ↓
Expert Investigation
        ↓
Observed Gap
        ↓
Research Requirement

## Investigation Questions

### 1. Data Source

What telemetry or log data does the tool consume?

### 2. Standard / Protocol / Format

What standard, protocol, file format or schema is used?

- Who defines it?
- Who maintains it?
- Is it open?
- What version is used?
- How is it extended?

### 3. Data + Semantic Model

How are the following represented?

- message
- field
- parameter
- instance
- value
- unit
- status

Where does the meaning of each item come from?

### 4. Metadata

What metadata is available?

Where does it come from?

- log
- protocol/schema
- application
- external definition
- user configuration

### 5. Time / Sampling

How are observations ordered and timed?

Determine:

- timestamp source
- timestamp resolution
- observation ordering
- recording frequency
- different sampling rates
- missing observations
- interpolation
- resampling

### 6. Stream Integrity

How can the user identify:

- missing observations
- irregular sampling
- stale values
- timestamp problems
- interrupted streams
- other data-quality conditions?

### 7. Presentation

How does the tool present telemetry?

For example:

- tables
- graphs
- maps
- dashboards
- filters
- overlays
- hierarchical views

### 8. Parameter Relationships

How can the user investigate:

- one parameter
- multiple parameters
- parameter dependencies
- intra-domain relationships
- inter-domain relationships

### 9. Domain Representation

Does the tool explicitly represent functional domains such as:

- NAV
- EST
- COM
- SYS
- POWER

Or must the expert construct these relationships manually?

### 10. Drill-down / Evidence

Can the user move from:

mission
→ domain
→ message
→ parameter
→ event
→ observation
→ source data

?

Can an analytical presentation be traced back to its supporting
observations?

### 11. Expert Investigation

What does the expert have to do manually to investigate an incident
or abnormal behaviour?

Record:

- manual steps
- interpretation required
- information that must be combined
- information that must be reconstructed

### 12. Observed Gap

What remains difficult, unavailable or dependent on manual
reconstruction?

A gap must be supported by evidence.

### 13. Research Requirement

Only after the gap is established should a possible research
requirement be recorded.

## Evaluation Rule

For important capabilities record:

**What?**

What does the tool provide?

**How?**

How does it represent or implement it?

**Consequence?**

What does that approach make easier, harder or dependent on manual
expert work?

## Evidence Sources

Findings should be established, where possible, from:

1. official documentation;
2. source code;
3. practical testing with representative flight logs.

Do not claim a limitation from documentation alone when the behaviour
can be verified experimentally.

## Research Discipline

The investigation describes the existing ecosystem before proposing
a new solution.

Do not assume a research gap before completing the investigation.