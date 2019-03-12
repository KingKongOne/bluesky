"""bluesky.dispersers.hysplit.hysplit_utils

Generic hysplit utility module created in large part for ease of testing

TODO: refactor this as a class
"""

__author__ = "Joel Dubowy and Sonoma Technology, Inc."

import datetime
import logging
import math
from functools import reduce

from bluesky.exceptions import BlueSkyConfigurationError
from bluesky.models.fires import Fire
from .. import PHASES, TIMEPROFILE_FIELDS
from bluesky.config import Config

__all__ = [
    'create_fire_sets', 'create_fire_tranches'
    ]

##
## Tranching
##

def create_fire_sets(fires):
    """Creates sets of fires, grouping by location

    A single fire location may show up multiple times if it lasted multiple days,
    since there's one FireLocationData per location per day.  We don't want to
    split up any location into multiple tranches, so we'll group FireLocationData
    objects by location id and then tranche the location fire sets.

    @todo: make sure fire locations from any particular event don't get split up into
      multiple HYSPLIT runs ???  (use fires[N]['metadata']['sf_event_guid']) ?
    """

    fires_dict = {e: [] for e in set([f.id for f in fires])}
    for f in fires:
        fires_dict[f.id].append(f)
    return  list(fires_dict.values())

def create_fire_tranches(fire_sets, num_processes):
    """Creates tranches of FireLocationData, each tranche to be processed by its
    own HYSPLIT process.

    @todo: More sophisticated tranching (ex. taking into account acreage, location, etc.).
    """

    n_sets = len(fire_sets)
    num_processes = min(n_sets, num_processes)  # just to be sure
    min_n_fire_sets_per_process = n_sets // num_processes
    extra_fire_cutoff = n_sets % num_processes

    logging.info("Running %d HYSPLIT49 Dispersion model processes "
        "on %d fires (i.e. events)" % (num_processes, n_sets))
    logging.info(" - %d processes with %d fires" % (
        num_processes - extra_fire_cutoff, min_n_fire_sets_per_process))
    if extra_fire_cutoff > 0:
        logging.info(" - %d processes with %d fires" % (
            extra_fire_cutoff, min_n_fire_sets_per_process+1))

    idx = 0
    fire_tranches = []
    for nproc in range(num_processes):
        s = idx
        idx += min_n_fire_sets_per_process
        if nproc < extra_fire_cutoff:
            idx += 1
        tranche_fire_sets = fire_sets[s:idx]
        logging.debug("Process %d:  %d fire sets" % (nproc, len(tranche_fire_sets)))
        fires = reduce(lambda x,y: x + y, tranche_fire_sets)
        fire_tranches.append(fires)
    return fire_tranches

def compute_num_processes(num_fire_sets, **tranching_config):
    """Determines number of HYSPLIT tranches given the number of fires sets
    and various tranching related config variables.

    Args:
     - num_fire_sets -- number of sets of fires, each set represeting a fire over
       possibly multiple days

    Tranching config options:
     - num_processes -- if specified and greater than 0, this value is returned
     - num_fires_per_process -- if num_processes isn't specified and this value
       is (and is greater than 0), then the num_processes is set to the min value
       such that not process has more than num_fires_per_process fires (unless
       num_processes_max, below, is specified)
     - num_processes_max -- max number of processes; only comes into play if
       num_processes isn't specified but num_fires_per_process is, and
       num_fires_per_process is greater than num_processes_max
    """
    num_processes = tranching_config.get('num_processes', 0)
    num_fires_per_process = tranching_config.get('num_fires_per_process', 0)
    num_processes_max = tranching_config.get('num_processes_max', 0)
    parinit_or_pardump = tranching_config.get('parinit_or_pardump', False)

    # in case num_fire_sets is zero, set to 1 so that we get at least
    # one process
    num_fire_sets = num_fire_sets or 1
    if 1 <= num_processes:
        computed_num_processes = min(num_fire_sets, num_processes)
    elif 1 <= num_fires_per_process:
        computed_num_processes = math.ceil(
            float(num_fire_sets) / num_fires_per_process)
        if 1 <= num_processes_max:
            computed_num_processes = min(computed_num_processes,
                num_processes_max)
    else:
        computed_num_processes = 1

    # if reading or writing parainit file, max out num processes
    if parinit_or_pardump:
        computed_num_processes = max(computed_num_processes,
            tranching_config.get('num_processes', 0),
            tranching_config.get('num_processes_max', 0))

    logging.debug('Parallel HYSPLIT? num_fire_sets=%s, %s -> num_processes=%s' %(
        num_fire_sets, ', '.join(['%s=%s'%(k,v) for k,v in tranching_config.items()]),
        computed_num_processes
    ))

    return int(computed_num_processes)


##
## Dummy Fires
##

DUMMY_EMISSIONS = (
    "pm2.5", "pm10", "co", "co2", "ch4", "nox",
    "nh3", "so2", "voc", "pm", "nmhc"
)
DUMMY_EMISSIONS_VALUE = 0.00001
DUMMY_HOURS = 24
# Note: DUMMY_PLUMERISE_HOUR is slightly different than
#    MISSING_PLUMERISE_HOUR
# TODO: should they be the same and thus consolidated?
# TODO: make sure these dummy plumerise values don't have unexpected consequences
DUMMY_PLUMERISE_HOUR = dict(
    heights=[1000 + 100*n for n in range(21)],
    emission_fractions=[0.5] * 20,
    smolder_fraction=0.0
)

# Note: dummy_timeprofile_hour is slightly different than
#    MISSING_TIMEPROFILE_HOUR
# TODO: should they be the same and thus consolidated?
def dummy_timeprofile_hour(num_hours):
    return {
        d: 1.0 / float(num_hours) for d in TIMEPROFILE_FIELDS
    }

def generate_dummy_fire(model_start, num_hours, grid_params):
    """Returns dummy fire formatted like
    """
    logging.info("Generating dummy fire for HYSPLIT")
    f = Fire(
        # let fire autogenerate id
        area=1,
        latitude=grid_params['center_latitude'],
        longitude=grid_params['center_longitude'],
        # TODO: look up offset from lat, lng, and model_start
        utc_offset=0, # since plumerise and timeprofile will have utc keys
        plumerise={},
        timeprofile={},
        emissions={
            p: {
                e: DUMMY_EMISSIONS_VALUE for e in DUMMY_EMISSIONS
            } for p in PHASES
        }
    )
    for hour in range(num_hours):
        dt = model_start + datetime.timedelta(hours=hour)
        dt = dt.strftime('%Y-%m-%dT%H:%M:%S')
        f['plumerise'][dt] = DUMMY_PLUMERISE_HOUR
        f['timeprofile'][dt] = dummy_timeprofile_hour(num_hours)

    return f

def fill_in_dummy_fires(fire_sets, fires, num_processes, model_start,
        num_hours, grid_params):
    # TODO: create a dummy fire for each process no matter what
    #   (in case whatever fires are assigned to a process are
    #   filtered by hysplit?)
    if len(fire_sets) < num_processes:
        for i in range(num_processes - len(fire_sets)):
            f = generate_dummy_fire(
                model_start, num_hours, grid_params)
            fires.append(f)
            fire_sets.append([f])


##
## Dispersion Grid
##

KM_PER_DEG_LAT = 111
DEG_LAT_PER_KM = 1.0 / KM_PER_DEG_LAT
RADIANS_PER_DEG = math.pi / 180.0
KM_PER_DEG_LNG_AT_EQUATOR = 111.32

def km_per_deg_lng(lat):
    return KM_PER_DEG_LNG_AT_EQUATOR * math.cos(RADIANS_PER_DEG * lat)

def square_grid_from_lat_lng(lat, lng, spacing_latitude,
        spacing_longitude, length, input_spacing_in_degrees=False):
    """Computes

    args
     - lat -- latitude of grid center
     - lng -- longitude of grid center
     - spacing_latitude -- height of grid cell, in km or degrees lat
     - spacing_longitude -- width of grid cell, in km or degrees lon
     - length -- length of each side of grid, in km
     - input_spacing_in_degrees -- by default, assumes spacing is in km
    """
    logging.debug("calculating {length}x{length} grid with lat/lng "
        "spacing {sp_lat}/{sp_lng} {spacing_unit} around {lat},{lng}".format(
        length=length, sp_lat=spacing_latitude, sp_lng=spacing_longitude,
        spacing_unit='degrees' if input_spacing_in_degrees else 'km',
        lat=lat, lng=lng))
    k_p_lng = km_per_deg_lng(lat)
    if not input_spacing_in_degrees:
        # convert from km to lat/lng; all other projections
        # are assumed to be spaced in km
        spacing_latitude /= KM_PER_DEG_LAT
        spacing_longitude /= k_p_lng
    d = {
        "center_latitude": lat,
        "center_longitude": lng,
        "height_latitude": DEG_LAT_PER_KM * length, # height in degrees
        "width_longitude": length / k_p_lng,  # width in degrees
        "spacing_longitude": spacing_longitude, # grid width in degrees
        "spacing_latitude": spacing_latitude # grid height in degrees
    }
    # TODO: truncate grid to keep from crossing pole? equator?
    return d

def grid_params_from_grid(grid, met_info={}):
    """
    Note: this function does not support boundaries spanning the
    international date line.  (i.e. NE lng > SW lng)
    """
    logging.info("Calculating grid parameters form boundary and spacing.")

    if not grid:
        raise ValueError("Dispersion grid must be defined either in the "
            "config or in the top level met object.")
    projection = grid.get('projection', met_info.get('projection'))
    spacing = grid.get('spacing', met_info.get('spacing'))
    if not spacing:
        raise ValueError("grid spacing must be defined either in user "
            "defined grid or in met object.")
    grid_boundary = grid.get('boundary', met_info.get('boundary'))
    if not grid_boundary:
        raise ValueError("grid boundary must be defined either in user "
            "defined grid or in met object.")
    # TODO: check that sw and ne lat/lng's are defined

    # TODO: support crossing international date line?
    if grid_boundary['sw']['lng'] >= grid_boundary['ne']['lng']:
        raise ValueError("grid boundaries spanning internation "
            "date line or with zero width not supported.")
    if grid_boundary['sw']['lat'] >= grid_boundary['ne']['lat']:
        raise ValueError("SW lat must be less than NE lat.")

    lat_center = (grid_boundary['sw']['lat'] + grid_boundary['ne']['lat']) / 2
    lng_center = (grid_boundary['sw']['lng'] + grid_boundary['ne']['lng']) / 2
    height_lat = grid_boundary['ne']['lat'] - grid_boundary['sw']['lat']
    width_lng = grid_boundary['ne']['lng'] - grid_boundary['sw']['lng']
    if projection != "LatLon":
        spacing = spacing / km_per_deg_lng(lat_center)

    return {
        "spacing_latitude": spacing,
        "spacing_longitude": spacing,
        "center_latitude": lat_center,
        "center_longitude": lng_center,
        "height_latitude": height_lat,
        "width_longitude": width_lng
    }

def get_grid_params(met_info={}, fires=None, allow_undefined=False):
    config = Config.get('dispersion', 'hysplit')

    # defaults to 'LatLon' in config defaults
    is_deg = config.get('projection')

    if config.get("USER_DEFINED_GRID"):
        # This supports BSF config settings
        # User settings that can override the default concentration grid info
        logging.info("User-defined sampling/concentration grid invoked")
        grid_params = {
            "center_latitude": config.get("CENTER_LATITUDE"),
            "center_longitude": config.get("CENTER_LONGITUDE"),
            "height_latitude": config.get("HEIGHT_LATITUDE"),
            "width_longitude": config.get("WIDTH_LONGITUDE"),
            "spacing_longitude": config.get("SPACING_LONGITUDE"),
            "spacing_latitude": config.get("SPACING_LATITUDE")
        }
        # BSF assumed lat/lng if USER_DEFINED_GRID; this support km spacing
        if not is_deg:
            grid_params["spacing_longitude"] /= km_per_deg_lng(
                grid_params["center_latitude"])
            grid_params["spacing_latitude"] /= KM_PER_DEG_LAT

    elif config.get('grid'):
        grid_params = grid_params_from_grid(
            config['grid'], met_info)

    elif config.get('compute_grid'):
        if not fires or len(fires) != 1:
            # TODO: support multiple fires
            raise ValueError("Option to compute grid only supported for "
                "runs with one fire")
        if (not config.get('spacing_latitude')
                or not config.get('spacing_longitude')):
            raise BlueSkyConfigurationError("Config settings "
                "'spacing_latitude' and 'spacing_longitude' required "
                "to compute hysplit grid")
        grid_params = square_grid_from_lat_lng(
            fires[0]['latitude'], fires[0]['longitude'],
            config.get('spacing_latitude'), config.get('spacing_longitude'),
            config.get('grid_length'), input_spacing_in_degrees=is_deg)

    elif met_info and met_info.get('grid'):
        grid_params = grid_params_from_grid(
            met_info['grid'], met_info)

    elif allow_undefined:
        grid_params = {}

    else:
        raise BlueSkyConfigurationError("Specify hysplit dispersion grid")

    logging.debug("grid_params: %s", grid_params)

    return grid_params