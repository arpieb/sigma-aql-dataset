# Sigma-AQL Dataset

Provide a ready-built dataset of matched Sigma-AQL rule files, generated using rules provided in [SigmaHQ/sigma](https://github.com/SigmaHQ/sigma) and the field-level [PySigma IBM QRadar AQL backend](https://github.com/IBM/pySigma-backend-QRadar-aql).

## Installation

1. Clone repo as usual
2. Create + activate virtual environment
3. Install deps defined in `requirements.py3`
4. (Optionally) install deps defined in `dev-requirements.py3` if  you want to use any of them for PR work
5. Run it!

## Running

```bash
NAME
    main.py - Main converter function

SYNOPSIS
    main.py SIGMA_PATH <flags>

DESCRIPTION
    Main converter function

POSITIONAL ARGUMENTS
    SIGMA_PATH
        Base path to search for sigma rules

FLAGS
    -d, --dataset_path=DATASET_PATH
        Default: 'dataset'
        Base output path for dataset
    -g, --glob_path=GLOB_PATH
        Default: '**/*.yml'
        Glob path pattern to match files under sigma_path

NOTES
    You can also use flags syntax for POSITIONAL ARGUMENTS
```

Sample run to load from the cloned `SigmaHQ/sigma` repo in a sibling folder:

```bash
python main.py ../sigma/rules
```

This will generate Sigma and AQL rule files under the `dataset_path` folder with identical filenames in separate subfolders; filenames are SHA256 hashes generated from the Sigma rule definition.  All logging messages will be written to `sigma-aql-dataset.log` in the current working directory, being overwritten on each run.  Logging level is INFO by default, but can be set using the `LOG_LEVEL` env var.

```bash
LOG_LEVEL=debug python main.py ../sigma/rules
```
