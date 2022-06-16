

# Galaxy to Janis Tool / Workflow Translation

## NOTE

***[ATTENTION]*** gxtool2janis is in active development and has not yet reached a first version release. 

This release has been made available for the BYOD showcase, and is pre-alpha stage. 

A production ready version will be available mid-late 2022. 


## Contents

- [installation](#installation)
- [Quickstart Guide](#quickstart-guide)
- [Description](#description)
- [Troubleshooting](#troubleshooting)


## Installation

gxtool2janis requires python ≥ 3.10. Please ensure this is available before executing the following: 

```
# clone repo
git clone https://github.com/GraceAHall/gxtool2janis

# setup environment (takes ~15 min)
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# to test your installation
python src/gxtool2janis.py tool --dir sample/tools/abricate --xml abricate.xml
python src/gxtool2janis.py workflow sample/workflows/simple_workflow.ga
```


## Quickstart Guide

```
### translating a tool
python src/gxtool2janis.py tool --dir [WRAPPER FOLDER] --xml [WRAPPER FILENAME]

### translating a workflow
python src/gxtool2janis.py workflow [WORKFLOW PATH]
```

gxtool2janis has two main *run modes* - tool, and workflow mode.

When in *tool* mode a single Galaxy wrapper will be translated. The path to the Galaxy wrapper folder (containing the tool XML and any required macro XML files) must be provided to the `--dir` argument, and the specific XML to translate must be provided with `--xml`.  The output will be a janis definition of the tool present at `parsed/tools/` folder. 

When in *workflow* mode, only the the Galaxy workflow.ga file is required. Each tool used in the workflow will be downloaded from a remote repository automatically and translated during execution. The output will be a janis definition of the workflow present at `parsed/workflows/`, including definitions for each required tool. 


## Description

gxtool2janis is a program which translates software in Galaxy tool wrappers to a Janis tool definition. It parses a Galaxy tool XML file to identify the main software requirement the wrapper is invoking, then determines the inputs, options, and outputs of this software. It then writes an equivalent definition for the software tool in Janis, and provides a link to the relevant biocontainer so the tool may be executed as part of a workflow translated by Janis. 

Galaxy tool wrappers may incorporate multiple tasks when executed, and usually include:
- preprocessing (symlinks, making directories, formatting inputs)
- running the main software requirement (actual tool execution)
- postprocessing (often to create additional outputs for the user)

gxtool2janis translates the main software requirement into a Janis definition. Preprocessing and postprocessing are ignored. 

gxtool2janis has been recently expanded to translate entire Galaxy workflows.  


## Troubleshooting

***[ATTENTION]*** As this program is in active development, things may break or be wildly different in each release. 

If you have questions, please raise an 'issue' in the issues tab above. We will do our best to help. 

Common issues: 

`requests.exceptions.ConnectionError`: simply re-run the program
