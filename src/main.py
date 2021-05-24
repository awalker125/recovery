#!/usr/bin/python

import sys
from optparse import OptionParser
import logging
import os
import platform
import datetime
import time
import yaml
import math
import jmespath
import re
from collections import OrderedDict
from markdownwriter.MarkdownWriter import MarkdownWriter
from markdownwriter.MarkdownTable import MarkdownTable

inol_info_workout = """
Optimal INOL values per exercise for a single workout:

< 0.4 - too easy

0.4 - 1.0 - optimal range for most athletes. An INOL value between 0.7 - 0.8 is a recommended starting point.

1.0 - 2.0 - tough workout, but good occasionally, especially for loading phases

> 2.0 - very difficult and could lead to overtraining if performed regularly in most individuals
"""

inol_info_weekly = """
Optimal INOL values per exercise across an entire week:

2.0 - easy, good for reloading, could probably benefit from greater volume occasionally

2.0 - 3.0 - tougher, but doable, good for loading phases

3.0 - 4.0 - very tough, good for shocking your body, but not recommended for extended periods of time

> 4.0 - not recommended
"""


# def pick_best_training_option(training_options, target_exercise_inol, go_hard=0):
    
#     best_training_option = None
    
#     for training_option in training_options:
    
#         if best_training_option is None:
#             best_training_option = training_option
#         else:

#             best_difference = getInolDifference(target_exercise_inol, best_training_option['exercise_inol']);

#             training_option_difference = getInolDifference(target_exercise_inol, training_option['exercise_inol']);
            
#             if training_option_difference == best_difference:
#                 logging.debug("Option {2} and {1} are the same as {0}: ".format(str(best_difference), str(training_option_difference), str(training_option['scheme'])))
                    
#                 if go_hard > 0:
#                     logging.debug("Go Hard is set. Will pick shorter harder sessions")
                    
#                     if training_option['set_inol'] > best_training_option['set_inol']:
#                         best_training_option = training_option
            
#             if training_option_difference < best_difference:
#                 logging.debug("Option {2} is better {1} < {0}: ".format(str(best_difference), str(training_option_difference), str(training_option['scheme'])))
#                 best_training_option = training_option
#             else:
#                 logging.debug("Option {2} is worse {1} > {0}: ".format(str(best_difference), str(training_option_difference), str(training_option['scheme'])))
            
#     return best_training_option         


# def generate_training_options(current_max, min_reps, max_reps,intensity, min_sets, max_sets, min_set_inol, max_set_inol, min_exercise_inol, max_exercise_inol,rounding_format, sets=None, reps=None):


#     training_options = []
#     for r in range(min_reps, max_reps + 1):
#         logging.debug("using reps {0}".format(str(r)))
#         set_inol = calculate_set_inol(r, intensity)
#         logging.debug("set inol for {0} rep(s) @ {1} is {2}".format(str(r), str(intensity), str(set_inol)))
#         for s in range(min_sets, max_sets + 1):
#             exercise_inol = set_inol * s
#             volume = r * s
#             weight = current_max * (float(intensity) / 100)
            
            
#             weight_rounded = weight #Default to no rounding if there is no setting
            
#             if rounding_format == "records":
#                 weight_rounded = roundRecords(weight)
#             elif rounding_format == "olympic":
#                 weight_rounded = roundOlympiclifting(weight)
#             elif rounding_format == "power":
#                 weight_rounded = roundPowerlifting(weight)
#             else:
#                 logging.warn("Unknown format {0}".format(rounding_format))
                
            
#             scheme = str(s) + "x" + str(r) + "@" + str(intensity) + "%"
#             if set_inol > min_set_inol:
#                 if set_inol < max_set_inol:
#                     if exercise_inol > min_exercise_inol:
#                         if exercise_inol < max_exercise_inol:
#                             training_options.append(
#                                 {
#                                     "scheme":scheme,
#                                     "exercise_inol":exercise_inol,
#                                     "set_inol":set_inol,
#                                     "volume":str(volume),
#                                     "weight": str(weight),
#                                     "weight_rounded": str(weight_rounded),
#                                     #"weight_powerlifting": str(weight_powerlifting),
#                                     #"weight_olympic": str(weight_rounded)
#                                     })
    
#     return training_options

def get_weight_rounded(weight,weight_format):
   
    if weight_format == "records":
        return roundRecords(weight)
    elif weight_format == "olympic":
        return roundOlympiclifting(weight)
    elif weight_format == "power":
        return roundPowerlifting(weight)
    else:
        logging.warn("Unknown format {0}".format(weight_format))
        return roundOlympiclifting(weight)

# def get_training(current_max, week, weight_format):


#     training = []

#     logging.debug("week before")
#     logging.debug(week)

#     exercise_inol = 0
#     exercise_volume = 0
#     for s in week["sets"]:
#         logging.debug("set before")
#         s["set_inol"] = calculate_set_inol(s["reps"], s["intensity"])
#         sets_inol = s["set_inol"] * s["count"]
#         exercise_inol += sets_inol

#         #Volume
#         s["volume"] = s["reps"] * s["count"]
#         exercise_volume += s["volume"]

#         s["weight"] = current_max * (float(s["intensity"]) / 100)

#         weight_rounded = s["weight"] #Default to no rounding if there is no setting
        

#         if weight_format == "records":
#             weight_rounded = roundRecords(s["weight"])
#         elif weight_format == "olympic":
#             weight_rounded = roundOlympiclifting(s["weight"])
#         elif weight_format == "power":
#             weight_rounded = roundPowerlifting(s["weight"])
#         else:
#             logging.warn("Unknown format {0}".format(weight_format))

#         s["weight_rounded"] = weight_rounded
#         s["scheme"]  = str(s["count"]) + "x" + str( s["reps"]) + "@" + str(s["intensity"]) + "%"
#         logging.debug("set after")
#         logging.debug(s)

#     logging.debug("week after")    
#     logging.debug(week)

#     # training.append({   "week": week["week"],
#     #                     "exercise_inol":exercise_inol,
#     #                     "exercise_volume": exercise_volume,
#     #                     "sets": week["sets"]
#     #                     })

#     # for r in range(min_reps, max_reps + 1):
#     #     logging.debug("using reps {0}".format(str(r)))
#     #     set_inol = calculate_set_inol(r, intensity)
#     #     logging.debug("set inol for {0} rep(s) @ {1} is {2}".format(str(r), str(intensity), str(set_inol)))
#     #     for s in range(min_sets, max_sets + 1):
#     #         exercise_inol = set_inol * s
#     #         volume = r * s
#     #         weight = current_max * (float(intensity) / 100)
            
            
#     #         weight_rounded = weight #Default to no rounding if there is no setting
            
#     #         if rounding_format == "records":
#     #             weight_rounded = roundRecords(weight)
#     #         elif rounding_format == "olympic":
#     #             weight_rounded = roundOlympiclifting(weight)
#     #         elif rounding_format == "power":
#     #             weight_rounded = roundPowerlifting(weight)
#     #         else:
#     #             logging.warn("Unknown format {0}".format(rounding_format))
                
            
#     #         scheme = str(s) + "x" + str(r) + "@" + str(intensity) + "%"
#     #         if set_inol > min_set_inol:
#     #             if set_inol < max_set_inol:
#     #                 if exercise_inol > min_exercise_inol:
#     #                     if exercise_inol < max_exercise_inol:
#     #                         training_options.append(
#     #                             {
#     #                                 "scheme":scheme,
#     #                                 "exercise_inol":exercise_inol,
#     #                                 "set_inol":set_inol,
#     #                                 "volume":str(volume),
#     #                                 "weight": str(weight),
#     #                                 "weight_rounded": str(weight_rounded),
#     #                                 #"weight_powerlifting": str(weight_powerlifting),
#     #                                 #"weight_olympic": str(weight_rounded)
#     #                                 })
    
#     #return training

def main():
    
    start = time.time()
   
    this = os.path.splitext(os.path.basename(__file__))[0]
    whereami = os.path.dirname(__file__)
    
    this_platform = platform.system()
    log_location = "/var/tmp"
    
    now = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    
    if this_platform == "Windows":
        log_location = "C:\\" + log_location
    
    if whereami == ".":
        whereami = os.getcwd()
    
    
    
    parser = OptionParser()
    parser.add_option("--verbose", action="store_true", dest="verbose", help="turn on verbose output")
    parser.add_option("--save", action="store_true", dest="save", help="save raw yamls")
    
    parser.add_option("--output", help="where to write the versions")
    parser.add_option("--config", help="config file to use in yaml format")
    

    (options, args) = parser.parse_args()
    
    if options.verbose:
        print("verbose enabled")
 
    # if not options.intensity:
    #    parser.error("intensity is required")
    
    if not options.output:
        parser.error("output is required")
    
    if not options.config:
        parser.error("config is required")
             
    setupLogging(log_location, this, now, options.verbose)

    if os.path.isfile(options.config):
        #logging.debug("found config file {0}".format(options.config))
        logging.debug(f"found config file {options.config}")
    else:    
        #logging.error("{0} does not exist".format(options.config))
        logging.error(f"{options.config} does not exist".format(options.config))
        os.sys.exit(99)
    


    logging.info("bootstrap info")
    

    logging.info('this=' + this)

    if not ensureDir(options.output):
        logging.fatal(f"{options.output} does not exist and could not be created")
        sys.exit(94)

    config = []

    with open(options.config, 'r') as config_file:
        config = yaml.load(config_file)

    logging.debug(config)
    logging.info("name: " + config["name"])
    logging.info("weight: " + str(config["weight"]))
    training_days = config["training_days"]
    logging.debug(training_days)
    plan = config["plan"]
    logging.debug(plan)


    full_training_plan_items = []
    full_training_plan = dict()
    full_training_plan["plan"] = full_training_plan_items
    
    full_training_summary = dict()
    full_training_summary["workload_all"] = dict()
    full_training_summary["workload_category"] = dict()
    full_training_summary["workload_daily"] = dict()
    
    full_training_plan["summary"] = full_training_summary
    
    for exercise in plan:
        logging.debug("Exercise")
        logging.debug(exercise)
        # string
        name = exercise["name"]
        category = exercise["category"]
        training_day = exercise["training_day"]
        # float
        current_max = exercise["current_max"]
        # String
        weight_format = exercise["format"]
        # array
        notes = exercise["notes"]
        weeks = exercise["weeks"]
        
        training_plan = dict()
        training_plan["training_day"] = training_day
        training_plan["name"] = name
        training_plan["category"] = category
        training_plan["current_max"] = current_max
        training_plan["notes"] = notes
        training_plan["weeks"] = []
        for week in weeks:
            



            exercise_inol = 0
            exercise_volume = 0
            exercise_work = 0
            for s in week["sets"]:

                if "weight" in s:
                    logging.debug(f"weight {s['weight']} in setting. Calculating intensity...")
                    intensity = (s['weight'] / current_max) * 100
                    logging.debug(f"calculated intensity {intensity}")
                    s["intensity"] = f"{intensity:.0f}"
                    logging.debug(f"rounded intensity {s['intensity']}")
                else:
                    if not "intensity" in s:
                        msg = f"Either weight or intensity is required... {s}"
                        logging.error(msg)
                        raise RuntimeError(msg)

                #INOL
                s["set_inol"] = calculate_set_inol(s["reps"], float(s["intensity"]))
                sets_inol = s["set_inol"] * s["count"]
                exercise_inol += sets_inol

                #Volume Reps
                s["volume"] = s["reps"] * s["count"]
                exercise_volume += s["volume"]

                #Weight
                if not "weight" in s:
                    s["weight"] = current_max * (float(s["intensity"]) / 100)
                s["weight_rounded"] = get_weight_rounded(s["weight"],weight_format)

                #work
                s["work"] = s["weight"] * s["reps"] * s["count"]
                exercise_work += s["work"]

                #Schema
                #s["scheme"]  = str(s["count"]) + "x" + str( s["reps"]) + "@" + str(s["intensity"]) + "%"
                #s["scheme"]  = f"{str(s['count'])}x{str( s['reps'])}@{str(s['intensity'])}%"
                s["scheme"]  = f"{s['count']}x{s['reps']}@{s['intensity']}%"

                #s["scheme"]  = str(s["count"]) + "x" + str( s["reps"]) + "@" + str(s["intensity"]) + "% =" + str(s["weight_rounded"]) + "kg, inol=" + str(s["set_inol"])

                #Amrap target 
                s["amrap_target"]  = calculate_target_amrap(current_max, s["intensity"])
            
            week["exercise_inol"] = exercise_inol
            week["exercise_volume"] = exercise_volume
            week["exercise_work"] = exercise_work
            logging.debug("Appending" + str(week))
            training_plan["weeks"].append(week)
            logging.debug(training_plan)
            
         
        full_training_plan_items.append(training_plan)

    logging.debug(training_plan)    
    # logging.debug("full_training_plan_items")
    # logging.debug(full_training_plan_items)    

    # sorted_full_training_plan_items = sorted(full_training_plan_items, key=lambda k: (k['training_day']))

    summary_categories_search = jmespath.compile('[].category')
    summary_training_days_search = jmespath.compile('[].training_day')
    summary_weeks_search = jmespath.compile('[].weeks[].week')
    
    summary_categories = summary_categories_search.search(full_training_plan_items)
    summary_training_days = summary_training_days_search.search(full_training_plan_items)
    summary_weeks = summary_weeks_search.search(full_training_plan_items)
    # Remove dups
    summary_categories = list(OrderedDict.fromkeys(summary_categories))
    summary_training_days = list(OrderedDict.fromkeys(summary_training_days))
    summary_weeks = list(OrderedDict.fromkeys(summary_weeks))
    
    # weeks= weeks_search.search(sorted_full_training_plan_items)
    # parsed = jmespath.compile('[].category')
    logging.debug(summary_categories)
    logging.debug(summary_training_days)
    logging.debug("Weeks")
    logging.debug(summary_weeks)
    # logging.info(weeks)

    #Weekly summary of everything
    for w in summary_weeks:
        week_index = w - 1
        
        search_inol = jmespath.compile(f"[].weeks[{week_index}].exercise_inol")
        search_volume = jmespath.compile(f"[].weeks[{week_index}].exercise_volume")
        search_work = jmespath.compile(f"[].weeks[{week_index}].exercise_work")
        results_inol = search_inol.search(full_training_plan_items)
        results_volume = search_volume.search(full_training_plan_items)
        results_work = search_work.search(full_training_plan_items)
        
        logging.debug("all results")
        logging.debug(results_inol)
        logging.debug(results_volume)
        logging.debug(results_work)
        
        if not w in full_training_summary["workload_all"]:
            full_training_summary["workload_all"][w] = dict()
            full_training_summary["workload_all"][w]["inol"] =0
            full_training_summary["workload_all"][w]["volume"] = 0
            full_training_summary["workload_all"][w]["work"] =0

        for result_inol in results_inol:
            full_training_summary["workload_all"][w]["inol"] += result_inol
            logging.debug(full_training_summary["workload_all"][w]["inol"])

        for result_volume in results_volume:
            full_training_summary["workload_all"][w]["volume"] += result_volume
            logging.debug(full_training_summary["workload_all"][w]["volume"])
               
        for result_work in results_work:
            full_training_summary["workload_all"][w]["work"] += result_work
            logging.debug(full_training_summary["workload_all"][w]["work"])

    #Weekly summary broken into categories
    for c in summary_categories:
        for w in summary_weeks:
            week_index = w - 1
        
            search_inol = jmespath.compile(f"[?category=='{c}'].weeks[{week_index}].exercise_inol")
            search_volume = jmespath.compile(f"[?category=='{c}'].weeks[{week_index}].exercise_volume")
            search_work = jmespath.compile(f"[?category=='{c}'].weeks[{week_index}].exercise_work")
            results_inol = search_inol.search(full_training_plan_items)
            results_volume = search_volume.search(full_training_plan_items)
            results_work = search_work.search(full_training_plan_items)

            logging.debug("category results")
            logging.debug(results_inol)
            logging.debug(results_volume)
            logging.debug(results_work)
        
            if not c in full_training_summary["workload_category"]:
                full_training_summary["workload_category"][c] = dict()
            
            if not w in full_training_summary["workload_category"][c]:
                full_training_summary["workload_category"][c][w] = dict()
                full_training_summary["workload_category"][c][w]["inol"] =0
                full_training_summary["workload_category"][c][w]["volume"] = 0
                full_training_summary["workload_category"][c][w]["work"] =0
        
            for result_inol in results_inol:
                full_training_summary["workload_category"][c][w]["inol"] += result_inol
                logging.debug(full_training_summary["workload_category"][c][w]["inol"])

            for result_volume in results_volume:
                full_training_summary["workload_category"][c][w]["volume"] += result_volume
                logging.debug(full_training_summary["workload_category"][c][w]["volume"])

            for result_work in results_work:
                full_training_summary["workload_category"][c][w]["work"] += result_work
                logging.debug(full_training_summary["workload_category"][c][w]["work"])

    #Weekly summary broken into days
    for d in summary_training_days:
        for w in summary_weeks:
            week_index = w - 1
        
            search_inol = jmespath.compile(f"[?training_day==`{d}`].weeks[{week_index}].exercise_inol")
            search_volume = jmespath.compile(f"[?training_day==`{d}`].weeks[{week_index}].exercise_volume")
            search_work = jmespath.compile(f"[?training_day==`{d}`].weeks[{week_index}].exercise_work")
            results_inol = search_inol.search(full_training_plan_items)
            results_volume = search_volume.search(full_training_plan_items)
            results_work = search_work.search(full_training_plan_items)

            logging.debug("daily results")
            logging.debug(results_inol)
            logging.debug(results_volume)
            logging.debug(results_work)
        
            if not d in full_training_summary["workload_daily"]:
                full_training_summary["workload_daily"][d] = dict()
            
            if not w in full_training_summary["workload_daily"][d]:
                full_training_summary["workload_daily"][d][w] = dict()
                full_training_summary["workload_daily"][d][w]["inol"] =0
                full_training_summary["workload_daily"][d][w]["volume"] = 0
                full_training_summary["workload_daily"][d][w]["work"] =0
        
            for result_inol in results_inol:
                full_training_summary["workload_daily"][d][w]["inol"] += result_inol
                logging.debug(full_training_summary["workload_daily"][d][w]["inol"])

            for result_volume in results_volume:
                full_training_summary["workload_daily"][d][w]["volume"] += result_volume
                logging.debug(full_training_summary["workload_daily"][d][w]["volume"])

            for result_work in results_work:
                full_training_summary["workload_daily"][d][w]["work"] += result_work
                logging.debug(full_training_summary["workload_daily"][d][w]["work"])


    logging.debug(full_training_summary)           


    if options.save:
        training_plan_file_name = "training_plan_" + safe_string(str(config["name"]))
        training_plan_file_path = options.output + "/" + training_plan_file_name + ".yaml"
       
        with open(training_plan_file_path, 'w') as outfile:
            yaml.dump(full_training_plan, outfile, default_flow_style=False)

    ### INPUT ###
    outputfile = options.output + "/README.md"
    file_md = open(outputfile, "w+")
    
    md = MarkdownWriter()
    
    # Title
    md.addHeader(str(config["name"]), 1)
    
    # md.addSimpleLineBreak()
    
    #age_weight_string = "Age: {0} Weight: {1}".format(str(config["age"]), str(config["weight"]))
    age_weight_string = f"Age: {config['age']} | Weight: {config['weight']}"
    md.addParagraph(age_weight_string, 1)
    # md.addHorizontalRule()
    
    md.addHeader("Plan", 2)
    
    for i in range(1, 8):
        md.addHeader(training_days[i], 3)
        md.addSimpleLineBreak()
        # md.addParagraph( training_days[i], 0 )  
        
        for x in full_training_plan["plan"]:
            if x["training_day"] == i:
                logging.debug(x)
                
                md.addHeader(x["name"], 4)
                #md_category = "Category: {0} Max: {1}".format(str(x["category"]),str(x["current_max"]))
                md_category = f"Category: {x['category']} | Max: {x['current_max']}"
                #md_max = "Max: {0}".format(str(x["current_max"]))
                #md.addParagraph(md_category, 1, 'bold')
                md.addText(md_category,"bold")

                
                # summary_table = MarkdownTable([u"Weeks", u"Max"])
                # summary_table.addRow([ str(len(x["weeks"])), str(x["current_max"])])
                # md.addTable(summary_table)
                
                md.addSimpleLineBreak()
                # training_table = MarkdownTable([u"Week", u"Sets/Reps", u"kg", u"inol", u"INOL", u"AMRAP"])
                # #training_table = MarkdownTable([u"Week", u"Sets/Reps", u"kg", u"inol", u"INOL"])

                # for w in x["weeks"]:
                #     #week_table = MarkdownTable([u"Week", u"Sets/Reps", u"kg", u"inol", u"INOL"])
                #     logging.debug(w)
                #     for s in w["sets"]:
                #         logging.debug(s)
                #     #    week_table.addRow([str(w["week"]), w["scheme"], str(w["weight_rounded"]), str("%.2f" %  w["set_inol"]), str("%.2f" %  w["exercise_inol"])])
                #         #training_table.addRow([str(w["week"]), w["scheme"], str(w["weight_rounded"]), str("%.2f" %  w["set_inol"]), str("%.2f" %  w["exercise_inol"]), str(w["amrap_target"])])
                #         training_table.addRow([str(w["week"]), s["scheme"], str(s["weight_rounded"]), str("%.2f" %  s["set_inol"]), str("%.2f" %  w["exercise_inol"]), str(s["amrap_target"])])
                
                # md.addTable(training_table)

                # md.addParagraph("Notes", 1, 'italic')
                # md.addList(x['notes'], False, 0)

                
                #training_table = MarkdownTable([u"Week", u"Sets/Reps", u"kg", u"inol", u"INOL"])

                for w in x["weeks"]:
                    # week_summary_table = MarkdownTable([u"Week", u"INOL"])
                    # week_summary_table.addRow([str(w["week"]),str("%.2f" %  w["exercise_inol"])])
                    # md.addTable(week_summary_table)
                    # md.addSimpleLineBreak()

                    week_summary = f"Week: {w['week']} | INOL: {w['exercise_inol']:.2f} | Work {w['exercise_work']:.0f}kg | Volume {w['exercise_volume']}"
                    md.addParagraph(week_summary, 1, 'bold')

                    week_training_table = MarkdownTable([u"Sets/Reps", u"kg", u"inol", u"AMRAP"])

                    #week_table = MarkdownTable([u"Week", u"Sets/Reps", u"kg", u"inol", u"INOL"])
                    logging.debug(w)
                    for s in w["sets"]:
                        logging.debug(s)
                    #    week_table.addRow([str(w["week"]), w["scheme"], str(w["weight_rounded"]), str("%.2f" %  w["set_inol"]), str("%.2f" %  w["exercise_inol"])])
                        #training_table.addRow([str(w["week"]), w["scheme"], str(w["weight_rounded"]), str("%.2f" %  w["set_inol"]), str("%.2f" %  w["exercise_inol"]), str(w["amrap_target"])])
                        week_training_table.addRow([s["scheme"], str(s["weight_rounded"]), str("%.2f" %  s["set_inol"]), str(s["amrap_target"])])
                
                    md.addTable(week_training_table)
                    md.addSimpleLineBreak()

                md.addParagraph("Notes", 1, 'italic')
                md.addList(x['notes'], False, 0)
    

    md.addHeader("Workload", 2)
    
    md.addHeader("All", 3)
    workload_summary_all_table = MarkdownTable([u"Week", u"INOL",u"Volume",u"Work"])
    for w, i in full_training_summary["workload_all"].items():
        logging.debug(w)
        logging.debug(i)
        workload_summary_all_table.addRow([str(w), f"{i['inol']:.2f}", f"{i['volume']}", f"{i['work']:.0f}kg"])
    md.addTable(workload_summary_all_table)
    md.addSimpleLineBreak()
    
    md.addHeader("Category", 3)
    for c in full_training_summary["workload_category"]:
        md.addHeader(c, 4)
        workload_summary_category_table = MarkdownTable([u"Week", u"INOL",u"Volume",u"Work"])
        for w, i in full_training_summary["workload_category"][c].items():
            logging.debug(w)
            logging.debug(i)
            workload_summary_category_table.addRow([str(w),f"{i['inol']:.2f}", f"{i['volume']}", f"{i['work']:.0f}kg"])
        md.addTable(workload_summary_category_table)
        md.addSimpleLineBreak()
        
    md.addHeader("Daily", 3)
    for d in full_training_summary["workload_daily"]:
        md.addHeader(training_days[d], 4)
        workload_summary_daily_table = MarkdownTable([u"Week", u"INOL",u"Volume",u"Work"])
        for w, i in full_training_summary["workload_daily"][d].items():
            logging.debug(w)
            logging.debug(i)
            workload_summary_daily_table.addRow([str(w),f"{i['inol']:.2f}", f"{i['volume']}", f"{i['work']:.0f}kg"])
        md.addTable(workload_summary_daily_table)
        md.addSimpleLineBreak()
    
    md.addHeader("Info",2)
    md.addHeader("Workout", 3)
    md.addText(inol_info_workout)
    md.addHeader("Weekly", 3)
    md.addText(inol_info_weekly)
    
    ### OUTPUT ###
    file_md.write(md.getStream())
    file_md.close()
    
    end = time.time()
    
    elapse = end - start
    
    logging.info("Created plan {0} in {1}s".format(outputfile, elapse))
    
def getInolDifference(target_exercise_inol, exercise_inol):
    return math.fabs(target_exercise_inol - exercise_inol)
    
def roundPowerlifting(x, precision=1, base=2.5):
    return round(base * round(float(x) / base), precision)

#round to 0.5 kg now we have the competition disks and for Erin Bench
def roundOlympiclifting(x, precision=0, base=1):
    return round(base * round(float(x)/base),precision)   

def roundRecords(x, precision=1, base=0.5):
    return round(base * round(float(x)/base),precision) 
 
def calculate_set_inol(reps, intensity):
    return float(reps) / (100 - intensity)

def calculate_target_amrap(current_max, intensity):
    
    weight = current_max * (float(intensity) / 100)
    reps = (current_max - weight) / (weight * 1 / 30)

    return int(round(reps))

    
def ensureDir(path):
    
    if os.path.isdir(path):
        logging.debug("{0} exists and is a directory".format(path))
        return True
    
    try:
        logging.debug("making " + path) 
        os.makedirs(path)
        return True
    except Exception as e:
        if not os.path.isdir(path):
            logging.error("Could not make " + path + " {0}): {1} ".format(e.errno, e.strerror)) 
            raise
        
def safe_string(string):
    string = re.sub('[^a-zA-Z0-9]+', '_', string)
    string = re.sub('\s+', '_', string)
    return string.lower()
  
def merge_defaults(defaults, week):
    merged = defaults.copy()  # start with defaults's keys and values
    merged.update(week)  # modifies merged with week's keys and values & returns None
    return merged

    

def setupLogging(log_location, this, now, verbose):


    level = logging.INFO
    if verbose:
        print("enable verbose")
        level = logging.DEBUG
        # set up logging to file - see previous section for more details
    logging.basicConfig(level=level,
                    # format='%(asctime)s %(name)-12s %(levelname)-8s (%(threadName)-10s) %(message)s',
                    format='%(asctime)s %(levelname)-8s (%(threadName)-10s) %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename=log_location + '/' + this.upper() + "_" + now + '.txt',
                    filemode='w')
    # define a Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler(sys.stdout)

        
  
        
    # set a format which is simpler for console use
    formatter = logging.Formatter('%(levelname)-8s (%(threadName)-10s) %(message)s')
    # tell the handler to use this format
    console.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger('').addHandler(console)

    # Now, we can log to the root logger, or any other logger. First the root...
    logging.debug('logging initialised')
    
    logging.debug("debug is on")  


if __name__ == '__main__':
 main()
