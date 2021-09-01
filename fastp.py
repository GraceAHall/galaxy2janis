

from janis_core import (
    CommandToolBuilder,
    InputSelector,
    ToolInput,
    ToolOutput
)

from janis_bioinformatics.data_types import Fastq

from janis_core.types.common_data_types import Boolean, String, Int, File


fastp_inputs=[
        ToolInput(
            'fastq1',
            Fastq,
            prefix='--in1',
            doc="First fastq input. If paired end, input2 is used for the other PE fastq"
        ),
        ToolInput(
            'fastq2',
            Fastq(optional=True),
            prefix='--in2',
            doc="[Optional] Second fastq input. To be used for paired end data."
        ),
        ToolInput(
            'fastq1_out',
            String,
            prefix='--out1',
            default='fastp_out1.fq',
            doc="Output filename for fastq1",
        ),
        ToolInput(
            'fastq2_out',
            String(optional=True),
            prefix='--out2',
            default='fastp_out2.fq',
            doc="[Optional] Output filename for fastq2. To be used for paired end data.",
        ),
        ToolInput(
            'adapter_sequence',
            String(optional=True),
            prefix='--adapter_sequence',
            doc="[Optional] Sequencing adaptor used. Leave blank to auto-detect.",
        ),
        ToolInput(
            'max_len', 
            Int(optional=True),
            prefix='--max_len1',
            doc="[Optional] Max read length",
        ),
        ToolInput(
            'min_len',
            Int(optional=True),
            prefix='--length_required',
            doc="[Optional] Min read length after filtering. Reads lower than this will be discarded. Default is 15",
        ),
        ToolInput(
            'min_avg_qual',
            Int(optional=True),
            prefix='--average_qual',
            doc="[Optional] if one read's average quality score < min_avg_qual, then this read/pair is discarded. Default 0 means no requirement",
        ),
        ToolInput(
            'n_base_limit',
            Int(optional=True),
            prefix='--n_base_limit',
            doc="[Optional] if one read's number of N base is >n_base_limit, then this read/pair is discarded. Default is 5",
        ),
        ToolInput(
            'qualified_quality_phred',
            Int(optional=True),
            prefix='--qualified_quality_phred',
            doc="[Optional] the quality value that a base is qualified. Default 15 means phred quality >=Q15 is qualified.",
        ),
        ToolInput(
            'unqualified_percent_limit',
            Int(optional=True),
            prefix='--unqualified_percent_limit',
            doc="[Optional] how many percents of bases are allowed to be unqualified (0~100). Default 40 means 40%",
        ),
        ToolInput(
            'cut_front',
            Boolean(optional=True),
            prefix='--cut_front',
            doc="[Optional] move a sliding window from front (5') to tail, drop the bases in the window if its mean quality < threshold, stop otherwise.",
        ),
        ToolInput(
            'cut_tail',
            Boolean(optional=True),
            prefix='--cut_tail',
            doc="[Optional] move a sliding window from tail (3') to front, drop the bases in the window if its mean quality < threshold, stop otherwise.",
        ),
        ToolInput(
            'cut_window_size',
            Int(optional=True),
            prefix='--cut_window_size',
            doc="[Optional] the window size option shared by cut_front, cut_tail or cut_sliding. Range: 1~1000, default: 4",
        ),
        ToolInput(
            'cut_mean_quality',
            Int(optional=True),
            prefix='--cut_mean_quality',
            doc="[Optional] the mean quality requirement option shared by cut_front, cut_tail or cut_sliding. Range: 1~36 default: 20 (Q20)",
        ),
        ToolInput(
            'html_report_out',
            String(optional=True),
            prefix='--html',
            default="fastp_report.html",
            doc="[Optional] the html format report file name",
        )
    ]

fastp_outputs=[
        ToolOutput(
            "fastq1_out", 
            Fastq,
            selector=InputSelector("fastq1_out")
        ),
        ToolOutput(
            "fastq2_out", 
            Fastq(optional=True),
            selector=InputSelector("fastq2_out")
        ),
        ToolOutput(
            "html_report_out", 
            File,
            selector=InputSelector("html_report_out")
        )
    ]

fastp = CommandToolBuilder(
    tool='fastp',
    base_command=["fastp"],
    inputs=fastp_inputs,
    outputs=fastp_outputs,
    container='docker.io/biocontainers/fastp:v0.20.1_cv1',
    version='v0.20.1_cv1'
)



if __name__ == "__main__":
    fastp().translate(
        "wdl", to_console=True
    )