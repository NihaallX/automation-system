# File Processing Automation System

## Overview

This is a small Python automation script that processes files from an input folder, validates required inputs, and generates a summary and a log file.  
The focus is on **clear structure**, **safe failure**, and **predictable behavior**.

## What the program does

- Reads files from an input folder
- Validates that required inputs exist
- Fails early with clear errors if validation fails
- Generates:
  - a summary file with basic statistics
  - a log file describing what happened

## Folder Structure Used

```
innovative/
├── process.py
├── README.md
├── input/
│   └── (one or more files)
└── output/
    ├── summary.json
    └── processing.log
```

## How to Run

```bash
python process.py
```

Optional arguments:

```bash
python process.py -i <input_folder (add path of your folder to run)> 
python process.py --verbose
```

Requirements:
- Python 3.6+
- Standard library only

## Validation Rules

The program checks the following before processing:

1. Input folder exists
2. Input folder is readable
3. Input folder contains at least one file
4. Files are readable

## Failure Behavior

If validation fails:

- A clear error message is printed
- The error is written to the log file
- The program exits safely (non-zero exit code)
- No partial processing is done

This avoids silent or misleading output.

## Output Files

### summary.json

Contains:
- total number of files
- total size
- line counts (for text files)
- basic per-file details

### processing.log

Contains:
- validation steps
- errors (if any)
- processing summary
- final success or failure status

Logs are written even when the program fails.

## Design Choices (Brief)

- **Standard library only**: keeps the script simple and portable
- **Fail-early validation**: prevents partial or incorrect output
- **Folder-based workflow**: mirrors real automation pipelines
- **Clear logging**: supports unattended runs and debugging

## Edge Case Considered

**Empty input folder**

The program detects this during validation. It exits with a clear error instead of producing empty output.

## One Improvement for Scale

If this needed to scale:

**Add parallel file processing** using `concurrent.futures`

This would speed up large folders without changing core logic.

## Example Successful Run

```
📂 Input:  D:\spec-driven-projects\innovative\input
📂 Output: D:\spec-driven-projects\innovative\output
------------------------------------------------------------
🔍 Validating inputs...

  ✓ Input folder exists
  ✓ Path is a directory
  ✓ Folder is readable
  ✓ Found 10 file(s)
  ✓ All files are readable

✅ Validation passed - 10 file(s) ready
------------------------------------------------------------
📊 Processing files...

  [1/10] .gitignore
  [2/10] components.json
  [3/10] eslint.config.mjs
  [4/10] next-env.d.ts
  [5/10] next.config.ts
  [6/10] package-lock.json
  [7/10] package.json
  [8/10] postcss.config.mjs
  [9/10] README.md
  [10/10] tsconfig.json

✅ Processed 10 file(s) successfully
------------------------------------------------------------
📝 Output files created:
  • Summary: summary.json
  • Log:     processing.log
------------------------------------------------------------
📈 SUMMARY STATISTICS

  Total Files:   10
  Text Files:    10
  Binary Files:  0
  Total Size:    234.47 KB (0.23 MB)
  Total Lines:   6,977
------------------------------------------------------------
============================================================
                   COMPLETED SUCCESSFULLY
============================================================
Duration: 0.08 seconds
Output:   D:\spec-driven-projects\innovative\output
============================================================
```

See [example_output.txt](example_output.txt) for the full example output.

## Conclusion

This system prioritizes:

- **clarity**
- **safe failure**
- **maintainable structure**

It is intentionally simple, predictable, and suitable for automation workflows where reliability matters more than features.
