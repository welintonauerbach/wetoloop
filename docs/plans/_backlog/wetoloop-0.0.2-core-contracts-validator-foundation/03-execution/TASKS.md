# Task Graph

| Task | Outcome | Depends on | Requirements | Gate |
|---|---|---|---|---|
| T01 | Establish canonical validator authority | none | REQ-VAL-001, REQ-VAL-003 | focused |
| T02 | Build shared structured schema validation | T01 | REQ-SCH-001, REQ-SCH-002 | focused |
| T03 | Align Definition and Design semantic validators | T02 | REQ-DEF-001 | focused |
| T04 | Define execution impact, verification and reuse contracts | T02 | REQ-EXE-001, REQ-EXE-002, REQ-STA-001, REQ-STA-002, REQ-CACHE-001 | focused |
| T05 | Validate Test Strategy, Harness, Lifecycle and final report | T02 | REQ-TST-001, REQ-HAR-001, REQ-LIF-001, REQ-FIN-001 | focused |
| T06 | Complete aggregate validation orchestration | T03, T04, T05 | REQ-VAL-002 | focused |
| T07 | Create self-contained conformance suite | T06 | REQ-FIX-001, REQ-CONF-001 | focused-conformance |
| T08 | Dogfood 0.0.2 and execute final package gate | T07 | REQ-TST-002, REQ-TST-003, REQ-REL-001 | package |

## DAG

```text
T01
 |
 v
T02
 |
 +--------------------+--------------------+
 |                    |                    |
 v                    v                    v
T03                  T04                  T05
 |                    |                    |
 +--------------------+--------------------+
                      |
                      v
                     T06
                      |
                      v
                     T07
                      |
                      v
                     T08
```

Execute one dependency-eligible task at a time. Every requirement has one implementation owner. T08 is the only task authorized to run the cold complete package gate and release migration.
