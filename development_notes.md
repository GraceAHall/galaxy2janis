Contents
- [Main features](#main-features)
- [Program execution](#program-execution)
- [Classes](#classes)
- [Datatype annotation](#datatype-annotation)

## Main features


## Program execution

This program treats the tool.xml as a collection of individual xml snippets. 

Independent xml snippets:
- <tool>
- <macros>
- <macro> / <xml>

If any of the elements above is encountered, its subtree is parsed as an independent piece of xml. The motivation is that a macro can contain arbitrary xml, and can be injected anywhere else (including into another macro) with the <expand> elem. 

The initial pass only aims to extract the important information from each xml snippet which is encountered (in the tool.xml or any imports). Tokens and macros are not resolved during this stage, only collected. 

After all individual pieces of xml are gathered, they are combined to fill in the final picture. At this stage, macros are expanded and tokens are resolved to their actual values. 

**overall workflow**
1. tool.xml is parsed. xml snippets from imports are handled immediately before proceeding. 
2. macros are expanded
3. tokens are resolved
4. input params which only serve to improve galaxy UI are removed
5. datatypes for input param and output data are annotated
6. command-line prefixes for input params and output data are found and linked



**parsing tool xml**
- <tool>
- <macros>
- <macro> / <xml>

For each xml snippet, it will be parsed according to the tag of the root elem. 
A <tool> needs to be handled differently to <macros> or <macro> / <xml> 
Each of these elems have their own SubtreeParser class which represents that object. The class has attributes for the important details to parse, and has methods to faciliate this. 

If the root elem is <tool>, As an example, if the snippet begins with the <tool> elem, a Tool()


**imports**
Each import is handled as a new, independent xml file. As soon as an import is discovered, it is parsed first before continuing. Each import returns a list of the independent xml snippets which were discovered in that file. 

Imports usually just contain macros with the <macros> elem as root.  





tool.xml parsing: 
    - the root element gets a SubtreeParser and begins parsing
    - if any macros elements are found, they get a SubtreeParser to parse the subtree beginning at the macros element
    - if any macro or xml elements are found, they each get a SubtreeParser to parse the subtree beginning at that element. 
    - if any imports are encountered, the file is opened with a new XMLParser. 



**type annotation**
- datatypes can only be inferred after all macros have been gathered and expanded. 




## Classes

For example, the ToolParser can parse subtrees beginning with the <tool> elem, and extracts all attributes needed to parse the tool.xml. It can parse all the tool input params, output data, command, tokens etc.  The MacroParser can parse subtrees beginning with <macro> and is similar to the ToolParser, but is less complex. 

For example, the Tool class (for subtrees beginning with the <tool> elem) has attributes to store all input params, tokens, the command section, the output data etc in the tool. It is the most broad class. 

The Macros class on the other hand (for subtrees beginning with the <macros> elem) only has attributes for imports, tokens and contained macros as only these can appear inside a <macros> elem.   

Each of these classes also has a SubtreeParser, which moves through the xml and delegates jobs to other classes. 

## Datatype annotation

**Data params**
- datatype specified in "format" attribute
- usually a single type, but is actually a list. eg bam,sam or fastq,fastqsanger,fastqgz. in this case, pick a  default. ie fastq,fastqsanger,fastqgz -> fastq
- some galaxy datatypes need to be mapped to real datatypes. eg interval -> BED


**Text, select... params**
 - if python can successfully interpret each item as a specific datatype, its that type

