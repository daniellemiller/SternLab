
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.gridspec as gridspec
import os.path
import pathlib
from file_utilities import *
from optparse import OptionParser
from cirseq_utilities import *
import pandas as pd
import numpy as np
from file_utilities import *
from optparse import OptionParser
from cirseq_utilities import *
import time
sns.set_context("talk")
start_time = time.time()



def main():
    # for Cluster
    parser = OptionParser("usage: %prog [options]")
    parser.add_option("-f", "--freqs_file_path", dest="freqs_file_path", help="path of the freqs file")
    parser.add_option("-v", "--virus", dest="virus", help="Virus name: CVB3 for CV; RVB14 for RV; PV for PV")
    parser.add_option("-s", "--seq_method", dest="seq_method", help="CirSeq or AccuNGS")
    parser.add_option("-c", "--sample", dest="sample_name", help="The name of the sample ie RV-p11")
    (options, args) = parser.parse_args()

    freqs_file = options.freqs_file_path
    virus = options.virus
    freqs_file = check_filename(freqs_file)
    seq_meth = options.seq_method
    sample = options.sample_name
    suffix = "%s.freqs" % sample

    #for Local
    # sample = "RV-p11"
    # suffix = "%s.freqs" % sample
    # freqs_file = "/sternadi/home/volume3/okushnir/AccuNGS/180503_OST_FINAL_03052018/merged/%s/q30_3UTR_new/%s" % \
    #              (sample, suffix)
    # virus = "RVB14"
    # seq_meth = "AccuNGS"



    # 1. Get freqs file and CirSeq running directory.
    path = freqs_file.split('/')[0:-1]
    out_dir = '' #the freqs directory
    for i in path:
        out_dir += str(i + '/')
    tmp_cirseq_dir = out_dir + 'tmp/'
    pathlib.Path(out_dir + 'plots/').mkdir(parents=True, exist_ok=True)
    out_plots_dir = out_dir + 'plots/'

    if virus == "CVB3":
        ncbi_id ="M16572"
    if virus == "RVB14":
        ncbi_id = "NC_001490"
    if virus == "RVB6":
        ncbi_id = "JQ747748"
    if virus == "PV":
        ncbi_id ="V01149"
    if virus == "rRNA":
        ncbi_id = "NR_003287.4"
    if virus == "mRNA_FB355642":
        ncbi_id = "FB355642"
    if virus == "mRNA_AB075490":
        ncbi_id = "AB075490"
    if virus == "mRNA_AK057879":
        ncbi_id = "AK057879"
    if virus == "mRNA_BC050745":
        ncbi_id = "BC050745"


    """2. Analyze those file and directory to get the number of tandem repeats of the cirseq,
    repeats length and the amount of reads per repeat"""

    if os.path.isfile(out_dir + '/repeat_summery.npy'):
            repeats_dict = np.load(out_dir + '/repeat_summery.npy').item() #dict for read vs. repeat  , encoding='latin1'
    else:
            print("Counting the repeats number")
            repeats_dict = get_repeats_num(tmp_cirseq_dir, out_dir) #dict for read vs. repeat

    if os.path.isfile(out_dir + '/length_df.csv'):
            read_and_repeat_length = pd.DataFrame.from_csv(out_dir + '/length_df.csv', sep=',', encoding='utf-8') #pandas_df for read and repeat length
    else:
            print("Getting the read and repeat length")
            read_and_repeat_length = get_read_and_repeat_length(tmp_cirseq_dir, out_dir) #pandas_df for read and repeat length


    """ 3. Adding mutation types to the freqs file"""
    if not os.path.isfile(freqs_file[0:-5] + "with.mutation.type.freqs"):
         append_mutation = find_mutation_type(freqs_file, ncbi_id)
    freqs_file_mutations = freqs_file[0:-5] + "with.mutation.type.freqs"

    # fetch ncbi data
    # pos = find_coding_region(ncbi_id)
    # print(pos)



    """4. Run bowtie2 for human rRNA, mRNA and the virus"""


    if virus == "RVB14":
        if seq_meth == "CirSeq":
            values = (19.32, 40.52, 45.17)
        elif seq_meth == "AccuNGS":
            values = (97, 0, 0)
    if virus == "CVB3":
        values = (96.09, 1.66, 1.18)
    if virus == "PV":
        values = (0, 0, 0)

    #   5. Subplots all relevant graph in subplots
    #      5.1. Distribution graph (=bowtie2 results)
    #      5.2. Multiple tandem repeat graph (repeat len)
    #      5.3. Reads length
    #      5.4. Amount of reads per repeat (Reads VS. Repeats Graph)
    #      5.5. Coverage
    #      5.6 Plot virus mutation frequencies(rates)

    plt.close('all')
    fig = plt.figure(figsize=(16, 9))
    gs = gridspec.GridSpec(3, 3)
    ax0 = plt.subplot(gs[0, 0])
    ax1 = plt.subplot(gs[0, 1])
    ax2 = plt.subplot(gs[0, 2])
    ax3 = plt.subplot(gs[1, 0])
    ax4 = plt.subplot(gs[1, 1:])
    ax5 = plt.subplot(gs[2:, :])
    # gs.tight_layout(fig)
    fig.subplots_adjust(hspace=0.3, wspace=0.21, top=0.93, bottom=0.05, right=0.96, left=0.05)

    fig.suptitle(suffix.split(sep='.')[0] + ' Analysis', fontsize=20)
    distribution_graph(values, ax0, virus)
    # ax0.set_title('Reads Distribution')

    repeat_len_graphs(read_and_repeat_length, ax1)
    # ax1.set_title('Multiple Tandem Repeat Degree')

    read_len_graphs(read_and_repeat_length, ax2)
    # ax2.set_title('Read length')

    read_repeat_graph(repeats_dict, ax3)
    # ax3.set_title('Amount of reads per repeat')

    coverage_graph(freqs_file, ax4)
    # ax4.set_title('Coverage')

    make_boxplot_mutation(freqs_file_mutations, ax5, out_plots_dir)
    # ax5.set_title(virus_name + ' Mutation Rates')

    # plt.show()
    plt.savefig(out_plots_dir + suffix.split(sep='.')[0] + '_Report.png', dpi=300)
    plt.close("all")
    print("The Plot is ready in the folder")

    fig2 = plt.figure(figsize=(16, 9))
    ax = plt.subplot()
    make_boxplot_transition_mutation(freqs_file_mutations, ax)
    plt.savefig(out_plots_dir + suffix.split(sep='.')[0] + '_Transitions_Report.png', dpi=300)
    plt.close("all")
    print("The Transition Plot is ready in the folder")

"""Graphs"""
#1.Distribution graph (=bowtie2 results)


def distribution_graph(val, ax, virus):
    """
    makes distribution graph
    :param val: values from bowtie2 alignment
    :param ax: ax location
    :param virus: Virus name
    :return:
    """
    column_number = 3

    ind = np.arange(column_number)  # the x locations for the groups
    width = 0.35  # the width of the bars
    rects1 = ax.bar(ind, val, width, color='DarkOrchid')
    ax.set_ylabel('% of Reads')
    ax.set_xticks(ind)
    ax.set_xticklabels((virus, 'mRNA', 'rRNA'))
    labelsy = np.arange(0, 50, 10)
    ax.set_yticklabels(labelsy)
    sns.set_style("darkgrid")
    ax.set_xlim(-0.5, 3)
    return ax


#2. Multiple tandem repeat graph (repeat len)
def repeat_len_graphs(dataframe, ax):
    """
     makes a repeat length graph
    :param dataframe: cirseq pipeline analysis dataframe
    :param ax: ax location
    :return:
    """
    sns.boxplot(x="count_nonzero", y="amax", data=dataframe, ax=ax, color='DarkOrchid')
    ax.set_xlabel("Number of Repeats")
    ax.set_ylabel("Repeat Length [bp]")
    labelsy = np.arange(0, 350, 50)
    labelsx = np.arange(1, len(dataframe["count_nonzero"]), 1)
    ax.set_yticklabels(labelsy)
    ax.set_xticklabels(labelsx)
    sns.set_style("darkgrid")
    return ax

#3. Reads length
def read_len_graphs(dataframe, ax):
    """
    Plots the reads VS. number of repeats graph
    :param dataframe: cirseq pipeline analysis dataframe
    :param ax: ax location
    :return:
    """
    graph = sns.boxplot(x="count_nonzero", y="sum", data=dataframe, ax=ax, color='DarkOrchid')
    ax.set_xlabel("Number of Repeats")
    ax.set_ylabel("Read Length [bp]")
    sns.set_style("darkgrid")


#4. Amount of reads per repeat (Reads VS. Repeats Graph)
def read_repeat_graph(repeat_summery, ax):
    """
    Pltos the Reads VS. Repeats Graph
    :param repeat_summery: Dictionary of the repeats from the stas file in the pipeline analysis
    :param ax:ax location
    :return:
    """
    keys = []
    values = []
    for key, val in repeat_summery.items():
        keys.append(key)
        values.append(val)
    graph = ax.bar(keys, values, color='DarkOrchid')
    ax.set_xlabel("Number of Repeats")
    ax.set_ylabel("Number of Reads")
    ax.set_xlim(min(keys)-0.5, max(keys)+0.5)
    ax.set_xticks(keys)
    ax.yaxis.get_major_formatter().set_powerlimits((0, 1))
    sns.set_style("darkgrid")
    return ax


#5. Coverage
def coverage_graph(freqs, ax):
    """
    Plots the coverage graph
    :param freqs: freqs file from the cirseq pipeline
    :param ax: ax location
    :return:
    """
    data = parse_reads(freqs)
    pos = data[0]
    reads = data[1]
    ax.plot(pos, reads, color='DarkOrchid')
    ax.set_xlabel("Position In The Genome [bp]")
    ax.set_ylabel("Number Of Reads")
    sns.set_style("darkgrid")
    ax.set_xlim(0, (max(pos)+10))
    ax.set_ylim(1, (max(reads)+1000000))
    ax.set_yscale("log")


#6. Mutation Rates
def make_boxplot_mutation(freqs_file, ax):
    """
    Plots the mutation frequencies boxplot
    :param freqs_file: pandas DataFrame after find_mutation_type function
    :param ax: ax location
    :return:
    """
    data = pd.read_table(freqs_file)
    data.reset_index(drop=True, inplace=True)
    flag = '-' in data.Base.values
    if flag is True:
        data = data[data.Ref != '-']
        data = data[data.Base != '-']
        data.reset_index(drop=True, inplace=True)
        # data['abs_counts'] = data['Freq'] * data["Read_count"]  # .apply(lambda x: abs(math.log(x,10))/3.45)
        # data['Frequency'] = data['abs_counts'].apply(lambda x: 1 if x == 0 else x) / data["Read_count"]
        # raise Exception("This script does not support freqs file with deletions, for support please contact Maoz ;)"
    data['Base'].replace('T', 'U', inplace=True)
    data['Ref'].replace('T', 'U', inplace=True)
    min_read_count = 100000
    data = data[data['Pos'] == np.round(data['Pos'])]  # remove insertions
    data['Pos'] = data[['Pos']].apply(pd.to_numeric)
    data = data[data['Read_count'] > min_read_count]
    data['mutation_type'] = data['Ref'] + data['Base']
    data = data[data['Ref'] != data['Base']]
    data = data[data["Base"] != "-"]
    data['abs_counts'] = data['Freq'] * data["Read_count"]  # .apply(lambda x: abs(math.log(x,10))/3.45)
    data['Frequency'] = data['abs_counts'].apply(lambda x: 1 if x == 0 else x) / data["Read_count"]
    data["Mutation"] = data["Ref"] + "->" + data["Base"]
    sns.set_palette(sns.color_palette("Paired", 12))
    g1 = sns.boxplot(x="Mutation Type", y="Frequency", hue="Mutation", data=data,
                     hue_order=["C->U", "U->C", "G->A", "A->G", "C->A", "G->U", "U->G", "U->A", "G->C", "A->C",
                                "A->U", "C->G"], order=["Synonymous", "Non-Synonymous", "Premature Stop Codon"], ax=ax)
    g1.set(yscale="log")
    plt.legend(bbox_to_anchor=(1.0, 1), loc=2, borderaxespad=0., fontsize=6)
    g1.set_ylim(10 ** -6, 1)
    g1.tick_params(labelsize=7)

def make_boxplot_transition_mutation(freqs_file, ax, output_dir):
    """
    Plots the mutation frequencies boxplot
    :param freqs_file: pandas DataFrame after find_mutation_type function
    :param ax: ax location
    :return:
    """
    data = pd.read_table(freqs_file)
    data.reset_index(drop=True, inplace=True)
    flag = '-' in data.Base.values
    if flag is True:
        data = data[data.Ref != '-']
        data = data[data.Base != '-']
        data.reset_index(drop=True, inplace=True)
        # data['abs_counts'] = data['Freq'] * data["Read_count"]  # .apply(lambda x: abs(math.log(x,10))/3.45)
        # data['Frequency'] = data['abs_counts'].apply(lambda x: 1 if x == 0 else x) / data["Read_count"]
        # raise Exception("This script does not support freqs file with deletions, for support please contact Maoz ;)"
    data['Base'].replace('T', 'U', inplace=True)
    data['Ref'].replace('T', 'U', inplace=True)
    min_read_count = 100000
    data = data[data['Pos'] == np.round(data['Pos'])]  # remove insertions
    data['Pos'] = data[['Pos']].apply(pd.to_numeric)
    data = data[data['Read_count'] > min_read_count]
    data['mutation_type'] = data['Ref'] + data['Base']
    data = data[data['Ref'] != data['Base']]
    data = data[data["Base"] != "-"]
    data['abs_counts'] = data['Freq'] * data["Read_count"]  # .apply(lambda x: abs(math.log(x,10))/3.45)
    data['Frequency'] = data['abs_counts'].apply(lambda x: 1 if x == 0 else x) / data["Read_count"]
    data["Mutation"] = data["Ref"] + "->" + data["Base"]
    data.to_csv(output_dir + "data_mutation.csv", sep=',', encoding='utf-8')
    sns.set_palette(sns.color_palette("Paired", 12))

    g1 = sns.factorplot(x="Mutation Type", y="Frequency", data=data, col="Mutation",
                     col_order=["C->U", "U->C", "G->A", "A->G"], kind="box")
    g1.set_xticklabels(["Synonymous", "Non\nSynonymous", "Premature\nStop Codon"], fontsize=10)
    g1.set_xlabels('')
    g1.set(yscale="log", ylim=(0.000001, 0.01))


if __name__ == "__main__":
    main()
