#!/usr/bin/env python

__author__ = "Joel Dubowy"
__copyright__ = "Copyright 2015, AirFire, PNW, USFS"

import copy
import csv
import glob
import logging
import os
import subprocess
import sys
import traceback
import uuid

from pyairfire import scripting

# Hack to put the repo root dir at the front of sys.path so that
# the local bluesky package is found
# app_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
#    os.path.abspath(__file__)))))
# sys.path.insert(0, app_root)

# We're running bluesky via the package rather than by running the bsp script
# to allow breaking into the code (with pdb)
from bluesky import models

# TODO: rename this script

# TODO: use a regression testing framework?

REQUIRED_ARGS = [
]

OPTIONAL_ARGS = [
    {
        'short': '-i',
        'long': '--scenario-id',
        'help': 'to run just one of the scenarios'
    }
]

EXAMPLES_STR = """
"""

BASE_FIRE = {
    "event_of": {
        "name": "regression test fire"
        # "id" to be filled in
    },
    "fuelbeds": [{
        # "fccs_id" to be filled in
        # "pct" to be filled in
    }],
    "location": {
        "latitude": 47.4316976,
        "longitude": -121.3990506,
        "utc_offset": "-09:00"
    }
}


def load_csv(filename):
    data = []
    with open(filename) as f:
        return [r for r in csv.DictReader(f)]

def load_scenario(input_filename):
    """Loads scenario input file and instantiates a fires_manager object
    to run bsp.

    Note that we have two options:
     - create one fire with N fuelbeds, or
     - create N fires, each with 1 fuelbed

    Either should work, assuming the ecoregion is the same for each row
    in the scenario (which is currently the case).  In case this changes
    and the assumption is broken, we'll go with creating N fires.
    """
    fires_manager = models.fires.FiresManager()
    rows = load_csv(input_filename)
    total_area = sum([int(r['area']) for r in rows])
    for row_dict in rows:
        fire = models.fires.Fire(copy.deepcopy(BASE_FIRE))
        fire.event_of["id"] = str(uuid.uuid1())
        area = int(row_dict['area'])
        fire.location['area'] = area
        fire.location['ecoregion'] = row_dict['ecoregion']
        fire.location['fuel_moisture_duff_pct'] = int(row_dict['fm_duff'])
        fire.location['fuel_moisture_1000hr_pct'] = int(row_dict['fm_1000hr'])
        fire.location['canopy_consumption_pct'] = int(row_dict['can_con_pct'])
        fire.location['shrub_blackened_pct'] = int(row_dict['shrub_black_pct'])
        fire.location['pile_blackened_pct'] = int(row_dict['pile_black_pct'])
        fire.location['output_units'] = row_dict['units']
        fire.fuelbeds[0]['fccs_id'] = row_dict['fuelbeds']
        fire.fuelbeds[0]['pct'] = float(area) / float(total_area)
        fires_manager.add_fire(fire)
    return fires_manager

PHASE_TRANSLATIONS = {
    "Flame": "flaming",
    "Smold": "smoldering",
    "Resid": "residual"
}
CONSUPTION_OUTPUT_HEADER_TRANSLATIONS = {
    #"Fuelbeds": [],
    # ignore "Filename"
    "Total Consumption": ["summary", "total", "total"],
    "Canopy Consumption": ["summary", "canopy", "total"],
    "Shrub Consumption": ["summary", "shrub", "total"],
    "Herb Consumption": ["summary", "nonwoody", "total"],
    "Wood Consumption": ["summary", "woody_fuels", "total"],
    "LLM Consumption": ["summary", "litter-lichen-moss", "total"],
    "Ground Consumption": ["summary", "ground_fuels", "total"],
    "C_total_F": ["summary", "total", "flaming"],
    "C_canopy_F": ["summary", "canopy", "flaming"],
    "C_shrub_F": ["summary", "shrub", "flaming"],
    "C_herb_F": ["summary", "nonwoody", "flaming"],
    "C_wood_F": ["summary", "woody_fuels", "flaming"],
    "C_llm_F": ["summary", "litter-lichen-moss", "flaming"],
    "C_ground_F": ["summary", "ground_fuels", "flaming"],
    "C_total_S": ["summary", "total", "smoldering"],
    "C_canopy_S": ["summary", "canopy", "smoldering"],
    "C_shrub_S": ["summary", "shrub", "smoldering"],
    "C_herb_S": ["summary", "nonwoody", "smoldering"],
    "C_wood_S": ["summary", "woody_fuels", "smoldering"],
    "C_llm_S": ["summary", "litter-lichen-moss", "smoldering"],
    "C_ground_S": ["summary", "ground_fuels", "smoldering"],
    "C_total_R": ["summary", "total", "residual"],
    "C_canopy_R": ["summary", "canopy", "residual"],
    "C_wood_R": ["summary", "woody_fuels", "residual"],
    "C_llm_R": ["summary", "litter-lichen-moss", "residual"],
    "C_ground_R": ["summary", "ground_fuels", "residual"],
    "C_overstory_crown": ["canopy", "overstory", "total"],
    "C_midstory_crown": ["canopy", "midstory", "total"],
    "C_understory_crown": ["canopy", "understory", "total"],
    "C_snagC1F_crown": ["canopy", "snags_class_1_foliage", "total"],
    "C_snagC1F_wood": ["canopy", "snags_class_1_no_foliage", "total"],
    "C_snagC1_wood": ["canopy", "snags_class_1_wood", "total"],
    "C_snagC2_wood": ["canopy", "snags_class_2", "total"],
    "C_snagC3_wood": ["canopy", "snags_class_3", "total"],
    "C_ladder": ["canopy", "ladder_fuels", "total"],
    "C_shrub_1live": ["shrub", "primary_dead", "total"],
    "C_shrub_1dead": ["shrub", "primary_live", "total"],
    "C_shrub_2live": ["shrub", "secondary_dead", "total"],
    "C_shrub_2dead": ["shrub", "secondary_live", "total"],
    "C_herb_1live": ["nonwoody", "primary_dead", "total"],
    "C_herb_1dead": ["nonwoody", "primary_live", "total"],
    "C_herb_2live": ["nonwoody", "secondary_dead", "total"],
    "C_herb_2dead": ["nonwoody", "secondary_live", "total"],
    "C_wood_1hr": ["woody_fuels", "1-hr_fuels", "total"],
    "C_wood_10hr": ["woody_fuels", "10-hr_fuels", "total"],
    "C_wood_100hr": ["woody_fuels", "100-hr_fuels", "total"],
    "C_wood_S1000hr": ["woody_fuels", "1000-hr_fuels_sound", "total"],
    "C_wood_R1000hr": ["woody_fuels", "1000-hr_fuels_rotten", "total"],
    "C_wood_S10khr": ["woody_fuels", "10000-hr_fuels_sound", "total"],
    "C_wood_R10khr": ["woody_fuels", "10000-hr_fuels_rotten", "total"],
    "C_wood_S+10khr": ["woody_fuels", "10k+-hr_fuels_sound", "total"],
    "C_wood_R+10khr": ["woody_fuels", "10k+-hr_fuels_rotten", "total"],
    "C_stump_sound": ["woody_fuels", "stumps_sound", "total"],
    "C_stump_rotten": ["woody_fuels", "stumps_rotten", "total"],
    "C_stump_lightered": ["woody_fuels", "stumps_lightered", "total"],
    "C_litter": ["litter-lichen-moss", "litter", "total"],
    "C_lichen": ["litter-lichen-moss", "lichen", "total"],
    "C_moss": ["litter-lichen-moss", "moss", "total"],
    "C_upperduff": ["ground_fuels", "duff_upper", "total"],
    "C_lowerduff": ["ground_fuels", "duff_lower", "total"],
    "C_basal_accum": ["ground_fuels", "basal_accumulations", "total"],
    "C_squirrel": ["ground_fuels", "squirrel_middens", "total"]
}
# EMISSIONS_OUTPUT_HEADER_TRANSLATIONS = {
#     "CH4 Emissions": ["ch4", "total"],
#     "CO Emissions": ["co", "total"],
#     "CO2 Emissions": ["co2", "total"],
#     "NMHC Emissions": ["nmhc", "total"],
#     "PM Emissions": ["pm", "total"],
#     "PM10 Emissions": ["pm10", "total"],
#     "PM25 Emissions": ["pm25", "total"],
#     "E_ch4_F": ["ch4", "flaming"],
#     "E_co_F": ["co", "flaming"],
#     "E_co2_F": ["co2", "flaming"],
#     "E_nmhc_F": ["nmhc", "flaming"],
#     "E_pm_F": ["pm", "flaming"],
#     "E_pm10_F": ["pm10", "flaming"],
#     "E_pm25_F": ["pm25", "flaming"],
#     "E_ch4_S": ["ch4", "smoldering"],
#     "E_co_S": ["co", "smoldering"],
#     "E_co2_S": ["co2", "smoldering"],
#     "E_nmhc_S": ["nmhc", "smoldering"],
#     "E_pm_S": ["pm", "smoldering"],
#     "E_pm10_S": ["pm10", "smoldering"],
#     "E_pm25_S": ["pm25", "smoldering"],
#     "E_ch4_R": ["ch4", "residual"],
#     "E_co_R": ["co", "residual"],
#     "E_co2_R": ["co2", "residual"],
#     "E_nmhc_R": ["nmhc", "residual"],
#     "E_pm_R": ["pm", "residual"],
#     "E_pm10_R": ["pm10", "residual"],
#     "E_pm25_R": ["pm25", "residual"]
# }
# EMISSIONS_STRATUM_OUTPUT_HEADER_TRANSLATIONS
#     "CH4_canopy": ["stratum_ch4_canopy", "total"],
#     "CH4_shrub": ["stratum_ch4_shrub", "total"],
#     "CH4_herb": ["stratum_ch4_nonwoody", "total"],
#     "CH4_wood": ["stratum_ch4_woody_fuels", "total"],
#     "CH4_llm": ["stratum_ch4_litter-lichen-moss", "total"],
#     "CH4_ground": ["stratum_ch4_ground_fuels", "total"],
#     "CO_canopy": ["stratum_co_canopy", "total"],
#     "CO_shrub": ["stratum_co_shrub", "total"],
#     "CO_herb": ["stratum_co_nonwoody", "total"],
#     "CO_wood": ["stratum_co_woody_fuels", "total"],
#     "CO_llm": ["stratum_co_litter-lichen-moss", "total"],
#     "CO_ground": ["stratum_co_ground_fuels", "total"],
#     "CO2_canopy": ["stratum_co2_canopy", "total"],
#     "CO2_shrub": ["stratum_co2_shrub", "total"],
#     "CO2_herb": ["stratum_co2_nonwoody", "total"],
#     "CO2_wood": ["stratum_co2_woody_fuels", "total"],
#     "CO2_llm": ["stratum_co2_litter-lichen-moss", "total"],
#     "CO2_ground": ["stratum_co2_ground_fuels", "total"],
#     "NMHC_canopy": ["stratum_nmhc_canopy", "total"],
#     "NMHC_shrub": ["stratum_nmhc_shrub", "total"],
#     "NMHC_herb": ["stratum_nmhc_nonwoody", "total"],
#     "NMHC_wood": ["stratum_nmhc_woody_fuels", "total"],
#     "NMHC_llm": ["stratum_nmhc_litter-lichen-moss", "total"],
#     "NMHC_ground": ["stratum_nmhc_ground_fuels", "total"],
#     "PM_canopy": ["stratum_pm_canopy", "total"],
#     "PM_shrub": ["stratum_pm_shrub", "total"],
#     "PM_herb": ["stratum_pm_nonwoody", "total"],
#     "PM_wood": ["stratum_pm_woody_fuels", "total"],
#     "PM_llm": ["stratum_pm_litter-lichen-moss", "total"],
#     "PM_ground": ["stratum_pm_ground_fuels", "total"],
#     "PM10_canopy": ["stratum_pm10_canopy", "total"],
#     "PM10_shrub": ["stratum_pm10_shrub", "total"],
#     "PM10_herb": ["stratum_pm10_nonwoody", "total"],
#     "PM10_wood": ["stratum_pm10_woody_fuels", "total"],
#     "PM10_llm": ["stratum_pm10_litter-lichen-moss", "total"],
#     "PM10_ground": ["stratum_pm10_ground_fuels", "total"],
#     "PM25_canopy": ["stratum_pm25_canopy", "total"],
#     "PM25_shrub": ["stratum_pm25_shrub", "total"],
#     "PM25_herb": ["stratum_pm25_nonwoody", "total"],
#     "PM25_wood": ["stratum_pm25_woody_fuels", "total"],
#     "PM25_llm": ["stratum_pm25_litter-lichen-moss", "total"],
#     "PM25_ground": ["stratum_pm25_ground_fuels", "total"]
# }
HEAT_OUTPUT_HEADER_TRANSLATIONS = {
    "Total Heat Release": ["heat", "total"],
    "Flaming Heat Release": ["heat", "flaming"],
    "Smoldering Heat Release": ["heat", "smoldering"],
    "Residual Heat Release": ["heat", "residual"]
}
def load_output(input_filename):
    # Consumption + emissions by fuelbed and fuel category
    consumption_output_filename = input_filename.replace('.csv', '_out.csv')
    expected_partials = {
        "consumption": {},
        "heat": {}
    }
    for r in load_csv(consumption_output_filename):
        for k in r:
            if k in CONSUPTION_OUTPUT_HEADER_TRANSLATIONS:
                c, sc, p = CONSUPTION_OUTPUT_HEADER_TRANSLATIONS[k]
                expected_partials['consumption'][c] = expected_partials.get(c, {})
                expected_partials['consumption'][c][sc] = expected_partials[c].get(sc, {})
                expected_partials['consumption'][c][sc] = expected_partials[c].get(sc, {})
                expected_partials['consumption'][c][sc][p] = r[k]
            elif k in HEAT_OUTPUT_HEADER_TRANSLATIONS:
                p = HEAT_OUTPUT_HEADER_TRANSLATIONS[k]
                expected_partials['heat'][p] = r[k]

    # total Emissions
    input_dir, input_filename = os.path.split(input_filename)
    emissions_output_filename = os.path.join(input_dir,
        "feps_input_em_{}".format(input_filename))
    expected_total_emissions =  {
        PHASE_TRANSLATIONS[r.pop('Phase')]: {k: [v] for k, v in r.items()}
            for r in load_csv(emissions_output_filename)
    }
    # TODO: delete the following if the above works
    # expected_emissions = {}
    # for r in load_csv(emissions_output_filename):
    #     expected_emissions[r.pop('Phase')] = {k: [v] for k, v in r.items()}

    return expected_partials, expected_total_emissions

def check(actual, expected_partials, expected_total_emissions):
    for phase in expected_total_emissions:
        for species in expected_emissions[phase]:
            # TODO: add asserts
            #import pdb;pdb.set_trace()
            pass

def run(args):
    pattern = '{}/data/scen_{}.csv'.format(
        os.path.abspath(os.path.dirname(__file__)),
        args.scenario_id or '[0-9]')
    for input_filename in glob.glob(pattern):
        fires_manager = load_scenario(input_filename)
        fires_manager.set_config_value('consume', 'emissions', 'efs')
        fires_manager.modules = ['consumption', 'emissions']
        fires_manager.run()
        actual = fires_manager.dump()
        expected_partials, expected_total_emissions = load_output(input_filename)
        check(actual, expected_partials, expected_total_emissions)

if __name__ == "__main__":
    parser, args = scripting.args.parse_args(REQUIRED_ARGS, OPTIONAL_ARGS,
        epilog=EXAMPLES_STR)

    try:
        run(args)

    except Exception, e:
        logging.error(e)
        logging.debug(traceback.format_exc())
        scripting.utils.exit_with_msg(e)
