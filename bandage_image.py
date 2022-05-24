
# NOTE
# This is an automated translation of the 'bandage_image' version '0.8.1' tool from a Galaxy XML tool wrapper.  
# Translation was performed by the gxtool2janis program (in-development)


import sys
sys.path.append('/home/grace/work/pp/gxtool2janis')


from janis_core import (
    CommandToolBuilder, 
    ToolMetadata,
    ToolInput, 
    ToolOutput,
    Array,
    Optional,
    UnionType,
    Stdout
)
from janis_unix.data_types.text import TextFile
from data.datatypes.galaxy import Jpg
from janis_core.types.common_data_types import Int
from janis_core.types.common_data_types import String
from janis_core.types.common_data_types import Boolean
from janis_core import WildcardSelector


metadata = ToolMetadata(
    short_documentation="visualize de novo assembly graphs",
    keywords=[],
    contributors=['gxtool2janis'],
    dateCreated="2022-05-24",
    dateUpdated="2022-05-24",
    version="0.8.1",
    doi="https://doi.org/10.1093/bioinformatics/btv383",
    citation="https://doi.org/10.1093/bioinformatics/btv383",
    documentationUrl=None,
    documentation="""


**Bandage Overview**

Bandage is a GUI program that allows users to interact with the assembly graphs made by de novo assemblers such as Velvet, SPAdes, MEGAHIT and others.
De novo assembly graphs contain not only assembled contigs but also the connections between those contigs, which were previously not easily accessible. Bandage visualises assembly graphs, with connections, using graph layout algorithms. Nodes in the drawn graph, which represent contigs, can be automatically labelled with their ID, length or depth. Users can interact with the graph by moving, labelling and colouring nodes. Sequence information can also be extracted directly from the graph viewer. By displaying connections between contigs, Bandage opens up new possibilities for analysing and improving de novo assemblies that are not possible by looking at contigs alone.

Bandage works with Graphical Fragment Assembly (GFA) files. For more information about this file format, see here_

.. _here: https://gfa-spec.github.io/GFA-spec/GFA2.html
    

**Command Documentation**

``Bandage image`` will generate an image file of the graph visualisation.

.. image:: $PATH_TO_IMAGES/bandage_graph.png
   :alt: example bandage plot

    """
)

inputs = [
	# Positionals
	ToolInput(
		'input_file',
		TextFile,
		position=1,
		default=None,
		doc="Graphical Fragment Assembly. Supports multiple assembly graph formats: LastGraph (Velvet), FASTG (SPAdes), Trinity.fasta, ASQG and GFA.",
	),
	ToolInput(
		'out_jpg',
		String,
		position=2,
		default=None,
		doc="None",
	),
	# Flags
	ToolInput(
		'lengths',
		Boolean(optional=True),
		prefix='--lengths',
		position=3,
		default=True,
		doc="None",
	),
	ToolInput(
		'names',
		Boolean(optional=True),
		prefix='--names',
		position=3,
		default=True,
		doc="None",
	),
	# Options
	ToolInput(
		'fontsize',
		Int(optional=True),
		prefix='--fontsize',
		position=3,
		default=5,
		doc="Font size. Node font size?",
	),
	ToolInput(
		'height',
		Int(optional=True),
		prefix='--height',
		position=3,
		default=1000,
		doc="Image height. If only height or width is set, the other will be determined automatically. If both are set, the image will be exactly that size. Default: 1000.",
	),
	ToolInput(
		'width',
		Int(optional=True),
		prefix='--width',
		position=3,
		default=100,
		doc="Image width. If only height or width is set, the other will be determined automatically. If both are set, the image will be exactly that size. Default: not set.",
	),
]
outputs = [
	ToolOutput(
		'outfile',
		Array(Jpg),
		selector=WildcardSelector("out.*"),
		doc="Assembly Graph Image",
	),
]

bandage_image = CommandToolBuilder(
    tool="bandage_image",
    version="0.8.1",
    metadata=metadata,
    container="quay.io/biocontainers/bandage:0.8.1--hb59a952_0",
    base_command=['Bandage', 'image'],
    inputs=inputs,
    outputs=outputs
)


if __name__ == "__main__":
    bandage_image().translate(
        "wdl", to_console=True
    )

