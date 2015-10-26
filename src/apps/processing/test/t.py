starting_files = [("a.1.fastq", "a.2.fastq"),
                  ("b.1.fastq", "b.2.fastq"),
                  ("c.1.fastq", "c.2.fastq")]


for ff_pair in starting_files:
        open(ff_pair[0], "w")
        open(ff_pair[1], "w")


from ruffus import *

#
#   STAGE 1 fasta->sam
#
@transform(starting_files,                     # Input = starting files
           suffix(".1.fastq"),                 #         suffix = .1.fastq
           ".sam")                             # Output  suffix = .sam
def map_dna_sequence(input_files,
                    output_file):
    # remember there are two input files now
    ii1 = open(input_files[0])
    ii2 = open(input_files[1])
    oo = open(output_file, "w")

#
#   STAGE 2 sam->bam
#
@transform(map_dna_sequence,                   # Input = previous stage
            suffix(".sam"),                    #         suffix = .sam
            ".bam")                            # Output  suffix = .bam
def compress_sam_file(input_file,
                      output_file):
    ii = open(input_file)
    oo = open(output_file, "w")

#
#   STAGE 3 bam->statistics
#
@transform(compress_sam_file,                  # Input = previous stage
            suffix(".bam"),                    #         suffix = .bam
            ".statistics",                     # Output  suffix = .statistics
            "use_linear_model")                # Extra statistics parameter
def summarise_bam_file(input_file,
                       output_file,
                       extra_stats_parameter):
    """
    Sketch of real analysis function
    """
    ii = open(input_file)
    oo = open(output_file, "w")

pipeline_run()

