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
from markdownwriter import *

# Optimal INOL values per exercise for a single workout:
# 
# < 0.4 - too easy
# 0.4 - 1.0 - optimal range for most athletes. An INOL value between 0.7 - 0.8 is a recommended starting point.
# 1.0 - 2.0 - tough workout, but good occasionally, especially for loading phases
# > 2.0 - very difficult and could lead to overtraining if performed regularly in most individuals
# Optimal INOL values per exercise across an entire week:
# 
# 2.0 - easy, good for reloading, could probably benefit from greater volume occasionally
# 2.0 - 3.0 - tougher, but doable, good for loading phases
# 3.0 - 4.0 - very tough, good for shocking your body, but not recommended for extended periods of time
# > 4.0 - not recommended


# globals

# current_max = 140



# max_exercise_inol = 2
# min_exercise_inol = 0.4
# max_set_inol = 0.5
# min_set_inol = 0.05

# intensity_increment = 5
# max_intensity = 95

# target_exercise_inol = 0.6


def pick_best_training_option(training_options, target_exercise_inol, go_hard=0):
    
    best_training_option = None
    
    for training_option in training_options:
    
        if best_training_option is None:
            best_training_option = training_option
        else:

            best_difference = getInolDifference(target_exercise_inol, best_training_option['exercise_inol']);

            training_option_difference = getInolDifference(target_exercise_inol, training_option['exercise_inol']);
            
            if training_option_difference == best_difference:
                logging.debug("Option {2} and {1} are the same as {0}: ".format(str(best_difference), str(training_option_difference), str(training_option['scheme'])))
                    
                if go_hard > 0:
                    logging.debug("Go Hard is set. Will pick shorter harder sessions")
                    
                    if training_option['set_inol'] > best_training_option['set_inol']:
                        best_training_option = training_option
            
            if training_option_difference < best_difference:
                logging.debug("Option {2} is better {1} < {0}: ".format(str(best_difference), str(training_option_difference), str(training_option['scheme'])))
                best_training_option = training_option
            else:
                logging.debug("Option {2} is worse {1} > {0}: ".format(str(best_difference), str(training_option_difference), str(training_option['scheme'])))
            
    return best_training_option         
        

def generate_training_options(current_max, min_reps, max_reps,intensity, min_sets, max_sets, min_set_inol, max_set_inol, min_exercise_inol, max_exercise_inol):
    training_options = []
    for r in range(min_reps, max_reps + 1):
        logging.debug("using reps {0}".format(str(r)))
        set_inol = calculate_set_inol(r, intensity)
        logging.debug("set inol for {0} rep(s) @ {1} is {2}".format(str(r), str(intensity), str(set_inol)))
        for s in range(min_sets, max_sets + 1):
            exercise_inol = set_inol * s
            volume = r * s
            weight = current_max * (float(intensity) / 100)
            weight_powerlifting = roundPowerlifting(weight)
            weight_olympic = roundOlympiclifting(weight)
            scheme = str(s) + "x" + str(r) + "@" + str(intensity) + "%"
            if set_inol > min_set_inol:
                if set_inol < max_set_inol:
                    if exercise_inol > min_exercise_inol:
                        if exercise_inol < max_exercise_inol:
                            training_options.append(
                                {
                                    "scheme":scheme,
                                    "exercise_inol":exercise_inol,
                                    "set_inol":str(set_inol),
                                    "volume":str(volume),
                                    "weight": str(weight),
                                    "weight_powerlifting": str(weight_powerlifting),
                                    "weight_olympic": str(weight_olympic)
                                    })
    
    return training_options

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
        print "verbose enabled"
 
    # if not options.intensity:
    #    parser.error("intensity is required")
    
    if not options.output:
        parser.error("output is required")
    
    if not options.config:
        parser.error("config is required")
             
    setupLogging(log_location, this, now, options.verbose)

    if os.path.isfile(options.config):
        logging.debug("found config file {0}".format(options.config))
    else:    
        logging.error("{0} does not exist".format(options.config))
        os.sys.exit(99)
    


    logging.info("bootstrap info")
    

    logging.info('this=' + this)

    if not ensureDir(options.output):
        logging.fatal("{0} does not exist and could not be created".format(options.output))
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
    full_training_summary["workload_exercise"] = dict()
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
        # dict
        defaults = exercise["defaults"]
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
            logging.debug("Week")
            logging.debug(week)
            # Merge the defaults into the overrides
            merged_week = merge_defaults(defaults, week)
            logging.debug("Merged Week")
            logging.debug(merged_week)
            
            # Generate training options
            training_options = generate_training_options(current_max, merged_week["min_reps"], merged_week["max_reps"], merged_week["intensity"], merged_week["min_sets"], merged_week["max_sets"], merged_week["min_set_inol"], merged_week["max_set_inol"], merged_week["min_exercise_inol"], merged_week["max_exercise_inol"])
             
            logging.debug(training_options)
            
            if options.save:
                # Sort training options
                sorted_training_options = sorted(training_options, key=lambda k: (k['exercise_inol'], k['set_inol'], k['volume']))
        
                logging.debug("\n" + yaml.dump(sorted_training_options, default_flow_style=False))
    
                # write training options
                output_file_name = "training_options_" + safe_string(name) + "_" + str(training_day) + "_" + str(merged_week["intensity"]) + "_" + str(merged_week["max_reps"]) + "_" + str(merged_week["max_sets"])
      
                output_file_path = options.output + "/" + output_file_name + ".yaml"
                
                with open(output_file_path, 'w') as outfile:
                    yaml.dump(sorted_training_options, outfile, default_flow_style=False)


            # We pick a training option 
            best_training_option = pick_best_training_option(training_options, merged_week["target_exercise_inol"])
            
            logging.debug("found best training {0} option for week {1}s".format(str(best_training_option), str(week)))
            
            best_training_option["week"] = merged_week["week"]
            best_training_option["amrap_target"] = calculate_target_amrap(current_max, merged_week["intensity"])
            
            training_plan["weeks"].append(best_training_option)
         
        full_training_plan_items.append(training_plan)


    logging.debug("full_training_plan_items")
    logging.debug(full_training_plan_items)    

    # sorted_full_training_plan_items = sorted(full_training_plan_items, key=lambda k: (k['training_day']))

    summary_categories_search = jmespath.compile('[].category')
    summary_training_days_search = jmespath.compile('[].training_day')
    
    summary_categories = summary_categories_search.search(full_training_plan_items)
    summary_training_days = summary_training_days_search.search(full_training_plan_items)
    
    # Remove dups
    summary_categories = list(OrderedDict.fromkeys(summary_categories))
    summary_training_days = list(OrderedDict.fromkeys(summary_training_days))
    # weeks= weeks_search.search(sorted_full_training_plan_items)
    # parsed = jmespath.compile('[].category')
    logging.debug(summary_categories)
    logging.debug(summary_training_days)
    # logging.info(weeks)

    for c in summary_categories:
        summary_exercises_search = jmespath.compile("[?category=='{0}'].name[]".format(c))
        summary_exercises = summary_exercises_search.search(full_training_plan_items)
        
        summary_exercises = list(OrderedDict.fromkeys(summary_exercises))
        
        logging.debug(summary_exercises)
        
        for e in summary_exercises:
            
            weeks_search = jmespath.compile("[?category=='{0}' && name=='{1}'].weeks[].week".format(c, e))
            weeks = weeks_search.search(full_training_plan_items)
            # remove dups
            weeks = list(OrderedDict.fromkeys(weeks))
            logging.debug(weeks)
            
            for w in weeks:
                # we write weeks in yaml as 1 2 3 4 5 etc
                week_index = w - 1
                summary_excercise_inol_search = jmespath.compile("[?category=='{0}' && name=='{1}'].weeks[{2}].exercise_inol".format(c, e, week_index))
                summary_excercise_inol = summary_excercise_inol_search.search(full_training_plan_items)
                
                logging.debug(summary_excercise_inol)
                logging.debug(type(summary_excercise_inol))
                # logging.info(len(summary_excercise_inol))
                # full_training_summary["workload_all"][w] = "test"
                if not w in full_training_summary["workload_all"]:
                    # we should only ever get one inol back per excercise
                    logging.debug(summary_excercise_inol[0])
                    full_training_summary["workload_all"][w] = summary_excercise_inol[0]
                    logging.debug(full_training_summary["workload_all"][w])
                else:
                    # we should only ever get one inol back per excercise
                    logging.debug(summary_excercise_inol[0])
                    full_training_summary["workload_all"][w] += summary_excercise_inol[0]
                    logging.debug(full_training_summary["workload_all"][w])
                # full_training_summary["workload_all"][w][e] = "test"
            

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
    
    age_weight_string = "Age: {0} Weight: {1}".format(str(config["age"]), str(config["weight"]))
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
                md_category = "Category: {0}".format(str(x["category"]))
                md.addParagraph(md_category, 1, 'bold')
                
                summary_table = MarkdownTable([u"Weeks", u"Max"])
                summary_table.addRow([ str(len(x["weeks"])), str(x["current_max"])])
                md.addTable(summary_table)
                
                md.addSimpleLineBreak()
                training_table = MarkdownTable([u"Week", u"Sets/Reps", u"kg", u"inol", u"INOL", u"AMRAP"])
                for w in x["weeks"]:
                    training_table.addRow([str(w["week"]), w["scheme"], str(w["weight_olympic"]), str(w["set_inol"]), str(w["exercise_inol"]), str(w["amrap_target"])])
                md.addTable(training_table)

                md.addParagraph("Notes", 1, 'italic')
                md.addList(x['notes'], False, 0)
    
    md.addHeader("Workload", 2)
    
    md.addHeader("All", 3)
    workload_summary_all_table = MarkdownTable([u"Week", u"INOL"])
    for w, i in full_training_summary["workload_all"].iteritems():
        logging.debug(w)
        logging.debug(i)
        workload_summary_all_table.addRow([str(w), str(i)])
    md.addTable(workload_summary_all_table)
    
    md.addHeader("Category", 3)
    md.addHeader("Exercise", 3)
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

def roundOlympiclifting(x, precision=0, base=1):
    return round(base * round(float(x) / base), precision)    
    
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
        print "enable verbose"
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
