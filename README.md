

# Galaxy to Janis Translation

Galaxy2janis is a productivity tool which translates Galaxy tool wrappers and workflows into the Janis language. It accepts either a Galaxy wrapper (.xml) or workflow (.ga), and will produce a Janis definition (.py).

Galaxy2janis is currently available in pre-release form.

**Bugs:** Please submit any bugs by [raising an issue](https://github.com/GraceAHall/galaxy2janis/issues) to help improve the software!<br>
**Contributing:**  Please get in touch by [raising an issue](https://github.com/GraceAHall/galaxy2janis/issues) so we can communicate via email or zoom.<br>


## Contents

- [Quickstart Guide](#quickstart-guide)
- [Description](#description)
- [Translation (CWL / WDL / Nextflow)](#translation)
- [Supported Features](#supported-features)

## Quickstart Guide

Galaxy2janis is available as a PyPI package. 
It requires python ≥ 3.10. 

Quickstart:

```
# create & activate environemnt
python3.10 -m venv venv
source venv/bin/activate
```

```
# install package
pip install galaxy2janis
```

```
# tool translation
galaxy2janis tool [PATH]
galaxy2janis tool abricate/abricate.xml

# workflow translation
galaxy2janis workflow [PATH]
galaxy2janis workflow hybrid_assembly.ga
```

## Description

#### What does this program do?

Galaxy2janis is a *productivity tool*. 

Given a *galaxy tool wrapper* or *galaxy workflow*, it will extract as much information as possible, and will create a similar definition in ***[Janis](https://janis.readthedocs.io/en/latest/index.html)***. 

For tool translations, the main software requirement will be identified and translated to Janis. A container will also be identified which can run the output Janis tool.

For workflow translations, the workflow itself will be translated to a Janis definition, alongside each tool used in the workflow.

#### What does this program not do?

Provide *runnable* translations.

Galaxy2janis does not provide translations which are runnable. They are intended to be human readable, and to match the structure of the input workflow. Users are expected to make some ***manual edits*** to finalise the workflow. See the [Manual Edits Section](#manual-edits) for details. 

#### Inputs

*Tool translation*

A local copy of the galaxy tool wrapper is needed. To download a tool wrapper: 
- Select the tool in galaxy
- View its toolshed entry *(top-left caret dropdown, 'See in Tool Shed')*
- Download the wrapper as a zip file *(repository actions -> 'Download as a zip file')*

<img src='./media/download_wrapper.png' width='320px'>

The unzipped file is the wrapper for that galaxy tool. 

Once the wrapper has been obtained, the path to the specific tool to translate must be specified. For example, if you downloaded the abricate tool you may something similar to this structure:

```
abricate/
├── abricate.xml
├── macros.xml
└── test-data
    ├── Acetobacter.fna
    ├── MRSA0252.fna
    └── output_db-card.txt
```

To translate abricate.xml:
```
galaxy2janis tool abricate/abricate.xml
```

*Workflow Translation*

A local copy of the galaxy workflow is needed. There are two methods to download a workflow:

1. Download from workflow editor<br>
<img src='./media/download_workflow_editor.png' width='600px'>

2. Download from Galaxy Training Network (GTN)<br>
<img src='./media/download_workflow_gtn.png' width='380px'>

These will download a galaxy workflow file in *.ga* format. 

To translate the workflow:
```
galaxy2janis workflow downloaded_workflow.ga
```

Each tool used in the workflow will be downloaded from a remote repository automatically. 

#### Outputs

Tool translations produce a single Janis tool definition for in the input galaxy wrapper. 

Workflow translations produce an output folder containing multiple files. Workflows need multiple entities such as tool definitions, the main workflow file, scripts, and a place to provide input values to run the workflow. The current output structure is as follows: 

```
[translated_workflow]/
├── inputs.yaml             # input values
├── logs                
├── subworkflows    
├── tools                   # tool definitions
│   ├── scripts             # tool scripts
│   ├── untranslated        # untranslated tool logic (galaxy)
│   └── wrappers            # translated tool wrappers (galaxy)
└── workflow.py             # main workflow file
```

## Translation

#### Janis -> CWL / WDL / Nextflow

#### Manual Edits

up to you as a workflow developer. expected to be proficient in the target language. 
that said, you will need to know about the following aspects of galaxy wrappers.

- wrappers
    - cheetah
    - pre/post tasks (untranslated)
- wrapper scripts
- inputs.yaml

#### Tool Pre/Post Tasks

Galaxy tool wrappers may perform multiple tasks when executed. The main software tool being wrapped will execute, but some preprocessing or postprocessing steps may also be performed. A common structure is as follows:
- Preprocessing (symlinks / making directories / creating a genome index)
- Main software requirement (actual tool execution)
- Postprocessing (index or sort output / create additional output files / summaries)

Galaxy2janis translates the main software requirement into a Janis definition. Preprocessing and postprocessing are ignored. 

## Supported Features

- supported vs unsupported
- known issues