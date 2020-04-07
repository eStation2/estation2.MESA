#
#	purpose: Define the processing chain for 'vgtproduct[FAPAR/FCOVER/LAI]' processing chains
#	author:  Vijay Charan Venkatachalam
#	date:	 07.08.2019
#   descr:	 Generate additional Derived products/implements processing chains
#	history: 1.0
#

from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from builtins import open
from future import standard_library

# Import std module

# Import eStation2 modules
from lib.python import functions
from lib.python import es_logging as log
from database import querydb

# Import third-party modules
from ruffus import *

from apps.processing import subprocess_std_stats
from apps.processing import subprocess_std_prods

standard_library.install_aliases()


#
#   Rational for 'active' flags:
#   A flag is defined for each product, with name 'activate_'+ prodname, ans initialized to 1: it is
#   deactivated only for optimization  - for 'secondary' products
#   In working conditions, products are activated by groups (for simplicity-clarity)
#
#   A list of 'final' (i.e. User selected) output products are defined (now hard-coded)
#   According to the dependencies, if set, they force the various groups

def create_pipeline(prod, starting_sprod, mapset, version, starting_dates=None, proc_lists=None,
                    update_stats=False, nrt_products=True):
    #   switch wrt groups - according to options
    #   ---------------------------------------------------------------------
    #   Create lists
    if proc_lists is None:
        proc_lists = functions.ProcLists()
    # DEFAULT: ALL off

    activate_10dstats_comput = 0  # 10d stats
    activate_10danomalies_comput = 0  # 10d anomalies

    activate_monthly_comput = 0  # monthly cumulation
    activate_monstats_comput = 0  # monthly stats
    activate_monanomalies_comput = 0  # monthly anomalies

    if nrt_products:
        activate_monthly_comput = 1  # monthly cumulation
        activate_monanomalies_comput = 1  # monthly anomalies
        activate_10danomalies_comput = 1  # 2.d

    if update_stats:
        activate_10dstats_comput = 1  # 10d stats
        activate_monstats_comput = 1  # monthly stats

    #   switch wrt single products: not to be changed !!
    activate_10davg_comput = 1
    activate_10dmin_comput = 1
    activate_10dmax_comput = 1
    activate_10ddiff_comput = 1
    activate_10dperc_comput = 1
    activate_10dnp_comput = 1
    activate_10dratio_comput = 1
    activate_10dstd_comput = 1
    activate_10dstandardized_comput = 1

    activate_1moncum_comput = 1
    activate_1monavg_comput = 1
    activate_1monmin_comput = 1
    activate_1monmax_comput = 1
    activate_1mondiff_comput = 1
    activate_1monstd_comput = 1
    activate_1monperc_comput = 1
    activate_1monnp_comput = 1
    activate_1monratio_comput = 1
    activate_1monstandardized_comput = 1

    # subprocess_stats = None
    # Intialize the stats subprocess
    subprocess_stats = subprocess_std_stats.SubProcessStatsES2(prod=prod, starting_sprod=starting_sprod, mapset=mapset,
                                                               version=version, starting_dates=starting_dates,
                                                               proc_lists=proc_lists, frequency='10d')

    #   ---------------------------------------------------------------------
    #   Average
    # subprocess_stats.create_basic_stats_proclist('Average')
    subprocess_stats.do_average()

    @active_if(activate_10dstats_comput, activate_10davg_comput)
    @collate(subprocess_stats.starting_files, formatter(subprocess_stats.formatter_in), subprocess_stats.formatter_out)
    def std_vgt_10davg(input_file, output_file):
        subprocess_std_stats.compute_average(input_file, output_file)

    #   ---------------------------------------------------------------------
    #   Minimum
    # subprocess_stats.create_basic_stats_proclist('Minimum')
    subprocess_stats.do_minimum()

    @active_if(activate_10dstats_comput, activate_10dmin_comput)
    @collate(subprocess_stats.starting_files, formatter(subprocess_stats.formatter_in), subprocess_stats.formatter_out)
    def std_vgt_10dmin(input_file, output_file):
        subprocess_std_stats.compute_minimum(input_file, output_file)

    #   ---------------------------------------------------------------------
    #   Maximum
    # subprocess_stats.create_basic_stats_proclist('Maximum')
    subprocess_stats.do_maximum()

    @active_if(activate_10dstats_comput, activate_10dmax_comput)
    @collate(subprocess_stats.starting_files, formatter(subprocess_stats.formatter_in), subprocess_stats.formatter_out)
    def std_vgt_10dmax(input_file, output_file):
        subprocess_std_stats.compute_maximum(input_file, output_file)

    #  ---------------------------------------------------------------------
    #  standard deviation
    # subprocess_stats.create_basic_stats_proclist('standard_deviation')
    subprocess_stats.do_standard_deviation()

    @active_if(activate_10dstats_comput, activate_10dstd_comput)
    # @follows(std_vgt_10davg)
    @collate(subprocess_stats.starting_files, formatter(subprocess_stats.formatter_in),
             add_inputs(subprocess_stats.ancillary_input), subprocess_stats.formatter_out)
    def vgt_ndvi_10dstddev(input_file, output_file):
        subprocess_std_stats.compute_product_std_deviation(input_file, output_file)

    # Intialize the 10d Prods subprocess
    subprocess_prods = subprocess_std_prods.SubProcessProdsES2(prod=prod, starting_sprod=starting_sprod, mapset=mapset,
                                                               version=version,
                                                               starting_dates=starting_dates, proc_lists=proc_lists,
                                                               frequency='10d')

    #   ---------------------------------------------------------------------
    #   10dDiff
    # subprocess_prods.create_basic_anomaly_proclist('10dDiff')
    subprocess_prods.do_absolute_difference()

    @active_if(activate_10danomalies_comput, activate_10ddiff_comput)
    @transform(subprocess_prods.starting_files, formatter(subprocess_prods.formatter_in),
               add_inputs(subprocess_prods.ancillary_input), subprocess_prods.formatter_out)
    def std_vgt_10ddiff(input_file, output_file):
        subprocess_std_prods.compute_absolute_diff(input_file, output_file)

    #   ---------------------------------------------------------------------
    #   10dperc
    # subprocess_prods.create_basic_anomaly_proclist('10dperc')
    subprocess_prods.do_percent_difference()

    # @follows(std_vgt_10davg)
    @active_if(activate_10danomalies_comput, activate_10dperc_comput)
    @transform(subprocess_prods.starting_files, formatter(subprocess_prods.formatter_in),
               add_inputs(subprocess_prods.ancillary_input), subprocess_prods.formatter_out)
    def std_vgt_10dperc(input_file, output_file):
        subprocess_std_prods.compute_percentage_diff_vs_avg(input_file, output_file)

    #   ---------------------------------------------------------------------
    #   10dnp
    # subprocess_prods.create_basic_anomaly_proclist('10dnp')
    subprocess_prods.do_normalized_anomaly()

    @active_if(activate_10danomalies_comput, activate_10dnp_comput)
    @transform(subprocess_prods.starting_files, formatter(subprocess_prods.formatter_in),
               add_inputs(subprocess_prods.ancillary_input_1, subprocess_prods.ancillary_input_2),
               subprocess_prods.formatter_out)
    def std_vgt_10dnp(input_file, output_file):
        subprocess_std_prods.compute_normalized_anomaly(input_file, output_file)

    # ---------------------------------------------------------------------
    #   10dratio
    # subprocess_prods.create_basic_anomaly_proclist('10dratio')
    subprocess_prods.do_ratio()

    @active_if(activate_10danomalies_comput, activate_10dratio_comput)
    @transform(subprocess_prods.starting_files, formatter(subprocess_prods.formatter_in),
               add_inputs(subprocess_prods.ancillary_input_1), subprocess_prods.formatter_out)
    def std_vgt_10dratio(input_file, output_file):
        subprocess_std_prods.compute_product_ratio(input_file, output_file)

    #   ---------------------------------------------------------------------
    #   Standardized 10d product
    # subprocess_prods.create_basic_anomaly_proclist('10standardized')
    subprocess_prods.do_standardized_prod()

    @active_if(activate_10danomalies_comput, activate_10dstandardized_comput)
    @transform(subprocess_prods.starting_files_10ddiff, formatter(subprocess_prods.formatter_in),
               add_inputs(subprocess_prods.ancillary_input), subprocess_prods.formatter_out)
    def vgt_ndvi_10dsndvi(input_file, output_file):
        subprocess_std_prods.compute_standardized_products(input_file, output_file)

    #   ---------------------------------------------------------------------
    #   3.a monthly product (avg)
    #   ---------------------------------------------------------------------
    subprocess_prods.do_monthly_prod()

    @active_if(activate_monthly_comput, activate_1moncum_comput)
    @collate(subprocess_prods.starting_files, formatter(subprocess_prods.formatter_in), subprocess_prods.formatter_out)
    def vgt_mon_prod(input_file, output_file):
        subprocess_std_prods.compute_monthly_prod_from_10d(input_file, output_file)

    #   ---------------------------------------------------------------------
    #   3.b monthly masks
    #   ---------------------------------------------------------------------
    # input_subprod_monthly = "mon"+starting_sprod
    # #output_sprod = proc_lists.proc_add_subprod("monndvi", "monthly_prod", False, True)
    #
    # in_prod_ident_monthly = functions.set_path_filename_no_date(prod, input_subprod_monthly,mapset, version, ext)
    #
    # input_dir_monthly =es2_data_dir+ \
    #                    functions.set_path_sub_directory(prod, input_subprod_monthly, 'Derived', version, mapset)
    #
    # starting_files_mon_prod = input_dir_monthly+"*"+in_prod_ident_monthly
    #
    # #   ---------------------------------------------------------------------
    # #   3.b  monthly stats
    # #   ---------------------------------------------------------------------
    #
    # #   ---------------------------------------------------------------------
    # #     avg x month
    # Intialize the stats subprocess by changing the frequency to monthly
    subprocess_stats.change_subProds_params(starting_sprod=starting_sprod, frequency='month')
    # subprocess_stats = subprocess_std_stats.SubProcessStatsES2(prod=prod, starting_sprod=starting_sprod, mapset=mapset,
    #                                                            version=version, starting_dates=starting_dates,
    #                                                            proc_lists=proc_lists, frequency='month')

    subprocess_stats.do_average()

    @active_if(activate_monstats_comput, activate_1monavg_comput)
    @collate(subprocess_stats.starting_files_mon_prod, formatter(subprocess_stats.formatter_in),
             subprocess_stats.formatter_out)
    @follows(vgt_mon_prod)
    def vgt_1monavg(input_file, output_file):
        subprocess_std_stats.compute_average(input_file, output_file)

    # #   ---------------------------------------------------------------------
    # #     min x month
    subprocess_stats.do_minimum()

    @active_if(activate_monstats_comput, activate_1monmin_comput)
    @collate(subprocess_stats.starting_files_mon_prod, formatter(subprocess_stats.formatter_in),
             subprocess_stats.formatter_out)
    @follows(vgt_1monavg)
    def vgt_1monmin(input_file, output_file):
        subprocess_std_stats.compute_minimum(input_file, output_file)

    #
    # #   ---------------------------------------------------------------------
    # #   NDV  max x month
    subprocess_stats.do_maximum()

    @active_if(activate_monstats_comput, activate_1monmax_comput)
    @collate(subprocess_stats.starting_files_mon_prod, formatter(subprocess_stats.formatter_in),
             subprocess_stats.formatter_out)
    @follows(vgt_1monmin)
    def vgt_1monmax(input_file, output_file):
        subprocess_std_stats.compute_maximum(input_file, output_file)

    # #  ---------------------------------------------------------------------
    # #  Monthly standard deviation () ->
    subprocess_stats.do_standard_deviation()

    @active_if(activate_monstats_comput, activate_1monstd_comput)
    @follows(vgt_1monavg)
    @collate(subprocess_stats.starting_files_mon_prod, formatter(subprocess_stats.formatter_in),
             add_inputs(subprocess_stats.ancillary_input), subprocess_stats.formatter_out)
    def vgt_1monstddev(input_file, output_file):
        subprocess_std_stats.compute_product_std_deviation(input_file, output_file)

    #   ---------------------------------------------------------------------
    #   3.d Product monthly anomalies
    #   ---------------------------------------------------------------------
    # Intialize the 10d Prods subprocess
    subprocess_prods.change_subProds_params(starting_sprod=starting_sprod, frequency='month')
    # subprocess_prods = subprocess_std_prods.SubProcessProdsES2(prod=prod, starting_sprod=starting_sprod, mapset=mapset, version=version,
    #                                                            starting_dates=starting_dates, proc_lists=proc_lists, frequency='month')

    #   ---------------------------------------------------------------------
    #    Absolute Difference x month
    subprocess_prods.do_absolute_difference()

    @active_if(activate_monanomalies_comput, activate_1mondiff_comput)
    # @follows(vgt_1monavg)
    @transform(subprocess_prods.starting_files_mon_prod, formatter(subprocess_prods.formatter_in),
               add_inputs(subprocess_prods.ancillary_input), subprocess_prods.formatter_out)
    def vgt_1mondiff(input_file, output_file):
        subprocess_std_prods.compute_absolute_diff(input_file, output_file)

    #   ---------------------------------------------------------------------
    #   1monperc
    subprocess_prods.do_percent_difference()

    # @follows(vgt_1monavg)
    @active_if(activate_monanomalies_comput, activate_1monperc_comput)
    @transform(subprocess_prods.starting_files_mon_prod, formatter(subprocess_prods.formatter_in),
               add_inputs(subprocess_prods.ancillary_input), subprocess_prods.formatter_out)
    def vgt_1monperc(input_file, output_file):
        subprocess_std_prods.compute_percentage_diff_vs_avg(input_file, output_file)

    #  ---------------------------------------------------------------------
    #  Monthly ratio (linearx2/avg) -> 0-100 % value
    subprocess_prods.do_ratio()

    @active_if(activate_monanomalies_comput, activate_1monratio_comput)
    @transform(subprocess_prods.starting_files_mon_prod, formatter(subprocess_prods.formatter_in),
               add_inputs(subprocess_prods.ancillary_input),
               subprocess_prods.formatter_out)
    # @follows(vgt_1monavg)
    def vgt_monthly_ratio(input_file, output_file):
        subprocess_std_prods.compute_product_ratio(input_file, output_file)

    #   ---------------------------------------------------------------------
    #   1monnp
    subprocess_prods.do_normalized_anomaly()

    # @follows(vgt_1monmax, vgt_1monmin)
    @active_if(activate_monanomalies_comput, activate_1monnp_comput)
    @transform(subprocess_prods.starting_files_mon_prod, formatter(subprocess_prods.formatter_in),
               add_inputs(subprocess_prods.ancillary_input_1, subprocess_prods.ancillary_input_2),
               subprocess_prods.formatter_out)
    def vgt_1monnp(input_file, output_file):
        subprocess_std_prods.compute_normalized_anomaly(input_file, output_file)

    #   ---------------------------------------------------------------------
    #   Standardized Product

    subprocess_prods.do_standardized_prod()

    @active_if(activate_monanomalies_comput, activate_1monstandardized_comput)
    # @follows(vgt_1mondiff, vgt_1monstddev)
    @transform(subprocess_prods.starting_files_mondiff, formatter(subprocess_prods.formatter_in),
               add_inputs(subprocess_prods.ancillary_input), subprocess_prods.formatter_out)
    def vgt_prod_1monstdprod(input_file, output_file):
        subprocess_std_prods.compute_standardized_products(input_file, output_file)

    return proc_lists


#   ---------------------------------------------------------------------


#   Run the pipeline
def processing_std_vgt(res_queue, pipeline_run_level=0, pipeline_printout_level=0, pipeline_printout_graph_level=0,
                       prod='', starting_sprod='', mapset='', version='', starting_dates=None, update_stats=False,
                       nrt_products=True, write2file=None, logfile=None, touch_only=False, upsert_db=False):
    spec_logger = log.my_logger(logfile)
    spec_logger.info("Entering routine %s" % 'processing_std_vgt')

    proc_lists = None

    proc_lists = create_pipeline(prod=prod, starting_sprod=starting_sprod, mapset=mapset, version=version,
                                 starting_dates=starting_dates, proc_lists=proc_lists, update_stats=update_stats,
                                 nrt_products=nrt_products)

    if write2file is not None:
        fwrite_id = open(write2file, 'w')
    else:
        fwrite_id = None

    if upsert_db:
        tasks = pipeline_get_task_names()
        spec_logger.info("Updating DB for the pipeline %s" % tasks[0])
        # Get input product info
        input_product_info = querydb.get_product_out_info(allrecs=False,
                                                          productcode=prod,
                                                          subproductcode=starting_sprod,
                                                          version=version)

        for my_sprod in proc_lists.list_subprods:
            # my_sprod.print_out()
            status = querydb.update_processing_chain_products(prod, version, my_sprod, input_product_info)

        spec_logger.info("Updating DB Done - Exit")
        # return proc_lists

    if pipeline_run_level > 0:
        spec_logger.info("Run the pipeline %s" % 'processing_std_vgt')
        pipeline_run(touch_files_only=touch_only, verbose=pipeline_run_level, logger=spec_logger,
                     log_exceptions=spec_logger,
                     history_file='/eStation2/log/.ruffus_history_{0}_{1}.sqlite'.format(prod, starting_sprod))
        tasks = pipeline_get_task_names()
        spec_logger.info("Run the pipeline %s" % tasks[0])
        spec_logger.info("After running the pipeline %s" % 'processing_std_vgt')

    if pipeline_printout_level > 0:
        pipeline_printout(verbose=pipeline_printout_level, output_stream=fwrite_id,
                          history_file='/eStation2/log/.ruffus_history_{0}_{1}.sqlite'.format(prod, starting_sprod))

    if pipeline_printout_graph_level > 0:
        pipeline_printout_graph('flowchart.jpg')

    if write2file is not None:
        fwrite_id.close()

    # res_queue.put(proc_lists)
    return True


def processing_std_vgt_stats_only(res_queue, pipeline_run_level=0, pipeline_printout_level=0,
                                  pipeline_printout_graph_level=0, prod='', starting_sprod='', mapset='', version='',
                                  starting_dates=None, write2file=None, logfile=None, touch_only=False,
                                  upsert_db=False):
    result = processing_std_vgt(res_queue, pipeline_run_level=pipeline_run_level,
                                pipeline_printout_level=pipeline_printout_level,
                                pipeline_printout_graph_level=pipeline_printout_graph_level, prod=prod,
                                starting_sprod=starting_sprod, mapset=mapset, version=version,
                                starting_dates=starting_dates, update_stats=True, nrt_products=False,
                                write2file=write2file, logfile=logfile, upsert_db=upsert_db, touch_only=touch_only)

    return result


def processing_std_vgt_prods_only(res_queue, pipeline_run_level=0, pipeline_printout_level=0,
                                  pipeline_printout_graph_level=0, prod='', starting_sprod='', mapset='', version='',
                                  starting_dates=None, write2file=None, logfile=None, touch_only=False,
                                  upsert_db=False):
    result = processing_std_vgt(res_queue, pipeline_run_level=pipeline_run_level,
                                pipeline_printout_level=pipeline_printout_level,
                                pipeline_printout_graph_level=pipeline_printout_graph_level, prod=prod,
                                starting_sprod=starting_sprod, mapset=mapset, version=version,
                                starting_dates=starting_dates, update_stats=False, nrt_products=True,
                                write2file=write2file, logfile=logfile, upsert_db=upsert_db, touch_only=touch_only)

    return result


def processing_std_vgt_all(res_queue, pipeline_run_level=0, pipeline_printout_level=0,
                           pipeline_printout_graph_level=0, prod='', starting_sprod='', mapset='', version='',
                           starting_dates=None, write2file=None, logfile=None, touch_only=False, upsert_db=False):
    result = processing_std_vgt(res_queue, pipeline_run_level=pipeline_run_level,
                                pipeline_printout_level=pipeline_printout_level,
                                pipeline_printout_graph_level=pipeline_printout_graph_level, prod=prod,
                                starting_sprod=starting_sprod, mapset=mapset, version=version,
                                starting_dates=starting_dates, update_stats=True, nrt_products=True,
                                write2file=write2file, logfile=logfile, upsert_db=upsert_db, touch_only=touch_only)

    return result
