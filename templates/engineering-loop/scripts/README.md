# WetoLoop validator scripts

These dependency-light Python scripts validate WetoLoop Engineering Loop activity artifacts.
They are the initial validator baseline for WetoLoop `0.0.1` and will progressively move
behind the WetoLoop CLI and harness contracts.

## Requirements

- Python 3.10+
- UTF-8 execution

On Windows/PowerShell, prefer explicit UTF-8 when running Python:

```powershell
$env:PYTHONUTF8='1'
$env:PYTHONIOENCODING='utf-8'
python -X utf8 <script> ...
```

## Aggregate validation

```bash
python -X utf8 templates/engineering-loop/scripts/validate_plan.py --plan <activity-directory>
```

Individual validators can also be called with `--plan` when investigating a failure.

## Safety

- Validators are read-only.
- Paths are resolved relative to the activity manifest and must remain contained.
- Validator output is intended to be deterministic and machine-readable.
- Raw shell command strings are not accepted as harness commands.
