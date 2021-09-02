

## Datatypes

**Data params**
- datatype specified in "format" attribute
- usually a single type, but is actually a list. eg bam,sam or fastq,fastqsanger,fastqgz. in this case, pick a  default. ie fastq,fastqsanger,fastqgz -> fastq
- some galaxy datatypes need to be mapped to real datatypes. eg interval -> BED


**Text, select... params**
 - if python can successfully interpret each item as a specific datatype, its that type

