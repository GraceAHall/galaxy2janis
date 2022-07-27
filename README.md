

# Galaxy to Janis Translation

## Foreword

Galaxy2janis is currently available in pre-release form. <br>
It requires python ≥ 3.10. 

- [Description](#description)
- [Quickstart Guide](#quickstart-guide)
- [Program Execution](#program-execution)

## Description

Galaxy2janis translates Galaxy tools and workflows into the Janis language. It parses a given Galaxy tool wrapper (.xml) or workflow (.ga) into an equivalent Janis definition (.py).

Galaxy tool wrappers may incorporate multiple tasks when executed, and usually include:
- preprocessing (symlinks, making directories, formatting inputs)
- running the main software requirement (actual tool execution)
- postprocessing (often to create additional outputs for the user)

Galaxy2janis translates the main software requirement into a Janis definition. Preprocessing and postprocessing are ignored. 

## Quickstart Guide

```
### translating a single tool
# local
python galaxy2janis.py tool --dir path_to_wrapper_folder --xml tool.xml
# remote url 
python galaxy2janis.py tool --remote_url https://toolshed.g2.bx.psu.edu/repos/devteam/fastqc/archive/e7b2202befea.tar.gz

### translating all tools in a Galaxy workflow
python galaxy2janis.py workflow path_to_workflow.ga
```

galaxy2janis has two main *run modes* - single tool, and workflow mode.

When in *tool* mode a single Galaxy wrapper will be translated. The Galaxy wrapper folder (containing the tool XML and any required macro XML files) can be stored locally, or a tarball url download link can be supplied if the wrapper is held in an online repository such as the [main toolshed](https://toolshed.g2.bx.psu.edu/). When the wrapper is local, the wrapper folder `--dir` and the specific XML to translate `--xml` must be referenced. When using a download link, only the `--remote_url` option needs to be supplied. 

When in *workflow* mode, only the path to the Galaxy workflow is required. Each tool used in the workflow will be downloaded from a remote repository automatically. The main software requirement for each downloaded tool wrapper will then be translated into a Janis definition. 


## Program Execution

galaxy2janis has 6 distinct stages
1. [Loading Runtime Settings](#loading-runtime-settings)
2. [Parsing Tool XML](#parsing-tool-xml)
3. [Identifying the Main Software Requirement](#identifying-the-main-software-requirement)
4. [Determining Inputs, Options, Outputs](#determining-inputs,-options,-outputs)
5. [Fetching a Relevant Biocontainer](#fetching-a-relevant-biocontainer)
6. [Writing a Janis Definition](#writing-a-janis-definition)

Each stage has multiple substeps (outlined below)

### Loading Runtime Settings

1. CLI settings are interpreted and validated 
2. Either the tool or workflow execution path is chosen
3. Local tool wrappers are validated
4. Remote tool wrappers and downloaded and validated
5. Settings class is created to handle all runtime settings and access to filepaths

### Parsing Tool XML

1. Galaxy source is used to load the XML into a Galaxy tool representation
2. Galaxy tool representation is transformed into an internal representation

### Identifying the Main Software Requirement

1. A valid command line string is created for each test case in the wrapper
2. The ***\<command>*** section is also treated as a command line string after simplification and expanding hidden values
3. For each command line (tests + expanded ***\<command>*** section), each individual statement is assessed to determine which executes the main software requirement

A valid command line is created for each ***\<test>*** in the wrapper. This is done by providnig the test inputs to the Galaxy tool evaluation engine which uses a set of tool inputs + the ***\<command>*** section to produce an actual command line string for execution. 

For the command line which represents the ***\<command>*** section of the Tool XML, any param with 'hidden' values (select and boolean params with multiple possible values) are expanded to produce a command line for each possible realised value. For example, if the Tool XML ***\<command>*** section has a select param with 5 possible values, 5 command line strings will be created, where each has one of these values. If the ***\<command>*** section has a select param with 4 options and a boolean param with 2 values, 6 command line strings will be created in total. The test and XML command line strings are pooled and are each used as examples to provide evidence of the structure of the main software requirement, how it is executed, and its options. 

Identifying the main software requirement uses a combination of string similarity between the tool id and the name of each software requirement. Identifying the specific statement within a command line which executes this software requirement is predominantly achieved by assessing the similarity between the first word of the statement and the name of the main software requirement. Other heuristics are in place, including ruling out statements which start with known common linux commands (ie 'ln', 'mv', 'cp'), and identifying statements which have the most reference to Galaxy input params.

### Determining Inputs, Options, Outputs

For each command line string (from tests and expanded XML ***\<command>*** section):
1. The string is preprocessed to expand key=val pairs
2. The individual 'words' (and quoted sections) are given a ***Token*** which best describes the construct (eg INTEGER, STRING, ENV_VAR, GALAXY_VAR, REDIRECT etc)
3. Each param with an `argument="--example"` attribute in the tool's input param list is search in the string to identify whether the argument can be found. If so it is identified as a Flag or an Option. 
4. The string is finally parsed left to right in a greedy approach identifying all the CommandComponents (Positionals, Flags, Options, Redirects, and StreamMerges) in the string
5. This information is fed into the current understanding of the Command as a whole
    - New CommandComponents are added to our knowledge pool
    - Existing CommandComponents are updated to include any new information we discovered from this string
6. The steps above are repeated for the next command line string until no more strings are left. 

### Fetching a Relevant Biocontainer

After the main software requirement has been identified in previous steps, a biocontainer url needs to be found which provides an image link to the container for that software and version. 

1. The name of the main software requirement is search using GA4GH's biocontainers api
2. The result with most similar name to the software is chosen
3. The biocontainer version closest matching the requirement version is chosen (usually an exact version match)
4. Another request is made using this software name and version to identify the specific biocontainer url for use. 

### Writing a Janis Definition

By this stage only a few things need to happen to write a Janis definition. 

1. The leading positionals which are invariant (usually just the main software requirement name and possibly the run mode) are marked as base command
2. Datatypes for each CommandComponent are inferred using the Galaxy tool params and the observed values for those CommandComponents
3. Outputs which are defined as Galaxy output params are formatted into Outputs
4. The required Janis imports are recorded using the CommandComponents and Outputs (datatypes, selectors, janis core imports like CommandToolBuilder etc)
5. The Janis definition is written using templates. Information is drawn from the complete knowledge of the Tool XML and the Command identified for the main software requirement. 
    - Imports
    - Inputs
    - Outputs
    - CommandToolBuilder

