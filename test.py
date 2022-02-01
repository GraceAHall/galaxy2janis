
import sys
import os
sys.path.append(os.getcwd() + "\src")

from janis_core import WildcardSelector, Optional, CommandToolBuilder, InputSelector, ToolInput, Array, UnionType, Stdout, ToolOutput
from janis_core.types.common_data_types import Boolean
from types.galaxy import Gff
from janis_unix.data_types.html import HtmlFile
from types.galaxy import Gff3
from janis_bioinformatics.data_types.bed import bed
from janis_core.types.common_data_types import Int
from janis_core.types.common_data_types import Float
from janis_unix.data_types.tsv import Tsv
from janis_bioinformatics.data_types.fasta import Fasta
from janis_core.types.common_data_types import String
from janis_unix.data_types.text import TextFile
from types.galaxy import Pdf





ToolInput(
    "ilens",
    Tsv,
    prefix="--ilens",
    position=1,
    doc="tabular report"
)

ToolOutput(
    "output_ilens",
    Tsv,
    selector=InputSelector("ilens"),
    doc="tabular report"
)


ToolInput(
    "report",
    Tsv,
    position=3,
    doc="summary report"
)

ToolOutput(
    "output_report",
    Stdout(Tsv),
    doc="summary report"
)
