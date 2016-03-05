"""bluesky.modules.consumption"""

__author__ = "Joel Dubowy"
__copyright__ = "Copyright 2016, AirFire, PNW, USFS"

import logging

import consume

from bluesky import datautils
from bluesky.consumeutils import _apply_settings, FuelLoadingsManager

__all__ = [
    'run'
]

__version__ = "0.1.0"

def run(fires_manager):
    """Runs the fire data through consumption calculations, using the consume
    package for the underlying computations.

    Args:
     - fires_manager -- bluesky.models.fires.FiresManager object
    """
    logging.debug("Running consumption module")
    # TODO: don't hard code consume_version; either update consume to define
    # it's version in consume.__version__, or execute pip:
    #   $ pip freeze |grep consume
    #  or
    #   $ pip show apps-consume4|grep "^Version:"
    fires_manager.processed(__name__, __version__,
        consume_version="4.1.2")

    # TODO: get msg_level and burn_type from fires_manager's config
    msg_level = 2  # 1 => fewest messages; 3 => most messages

    all_fuel_loadings = fires_manager.get_config_value('consumption',
        'fuel_loadings')
    fuel_loadings_manager = FuelLoadingsManager(all_fuel_loadings=all_fuel_loadings)

    _validate_input(fires_manager)

    # TODO: can I safely instantiate one FuelConsumption object and
    # use it across all fires, or at lesat accross all fuelbeds within
    # a single fire?
    for fire in fires_manager.fires:
        with fires_manager.fire_failure_handler(fire):
            _run_fire(msg_level, fuel_loadings_manager, fire)

    fires_manager.summarize(
        consumption=datautils.summarize(fires_manager.fires, 'consumption'))
    fires_manager.summarize(
        heat=datautils.summarize(fires_manager.fires, 'heat'))

def _run_fire(msg_level, fuel_loadings_manager, fire):
    logging.debug("Consume consumption - fire {}".format(fire.id))

    # TODO: set burn type to 'activity' if fire.fuel_type == 'piles' ?
    if fire.fuel_type == 'piles':
        raise ValueError("Consume can't be used for fuel type 'piles'")
    burn_type = fire.fuel_type

    # TODO: can I run consume on all fuelbeds at once and get per-fuelbed
    # results?  If it is simply a matter of parsing separated values from
    # the results, make sure that running all at once produces any performance
    # gain; if it doesn't, then it might not be worth the trouble
    for fb in fire.fuelbeds:
        fuel_loadings_csv_filename = fuel_loadings_manager.generate_custom_csv(
            fb['fccs_id'])

        fc = consume.FuelConsumption(
            fccs_file=fuel_loadings_csv_filename) #msg_level=msg_level)

        fb['fuel_loadings'] = fuel_loadings_manager.get_fuel_loadings(fb['fccs_id'], fc.FCCS)

        fc.burn_type = burn_type
        fc.fuelbed_fccs_ids = [fb['fccs_id']]

        # Note: if we end up running fc on all fuelbeds at once, use lists
        # for the rest
        # Note: consume expects area, but disregards it when computing
        #  consumption values - it produces tons per unit area (acre?), not
        #  total tons; the consumption values will be multiplied by area, below
        area = (fb['pct'] / 100.0) * fire.location['area']
        fc.fuelbed_area_acres = [area]
        fc.fuelbed_ecoregion = [fire.location['ecoregion']]

        _apply_settings(fc, fire['location'], burn_type)
        _results = fc.results()
        if _results:
            # TODO: validate that _results['consumption'] and
            #   _results['heat'] are defined
            fb['consumption'] = _results['consumption']
            fb['consumption'].pop('debug', None)
            fb['heat'] = _results['heat release']

            # multiply each consumption and heat value by area if
            # output_inits is 'tons_ac',
            # TODO: multiple by area even if user sets output_units to 'tons',
            #   because consume doesn't seem to be multiplying by area for us
            #   even when 'tons' is specified
            if fc.output_units == 'tons_ac':
                datautils.multiply_nested_data(fb["consumption"], area)
                datautils.multiply_nested_data(fb["heat"], area)

        else:
            # TODO: somehow get error information from fc object; when
            #   you call fc.results() in an error situation, it writes to
            #   stdout or stderr (?), something like:
            #
            #     !!! Error settings problem, the following are required:
            #            fm_type
            #   it would be nice to access that error message here and
            #   include it in the exception message
            raise RuntimeError("Failed to calculate consumption for fire "
                "{} fuelbed {}".format(fire.id, fb['fccs_id']))

    # Aggregate consumption over all fuelbeds; include only per-phase totals,
    # not per category > sub-category > phase
    fire.consumption = datautils.summarize([fire], 'consumption',
        include_details=False)

REQUIRED_TOP_LEVEL_FIELDS = ['fuelbeds', 'location']
REQUIRED_LOCATION_FIELDS = ['area']
def _validate_input(fires_manager):
    for fire in fires_manager.fires:
        with fires_manager.fire_failure_handler(fire):
            for k in REQUIRED_TOP_LEVEL_FIELDS:
                if not fire.get(k):
                    raise ValueError("Missing '{}' data required for "
                        "computing consumption".format(k))
            # location fields
            for k in REQUIRED_LOCATION_FIELDS:
                if not fire.location.get(k):
                    raise ValueError("Fire location data must define '{}' "
                    "for computing consumption".format(k))
            if not fire.location.get('ecoregion'):
                # import EcoregionLookup here so that, if fires do have
                # ecoregion defined, consumption can be run without mapscript
                # and other dependencies installed
                from bluesky.ecoregion.lookup import EcoregionLookup
                fire.location['ecoregion'] = EcoregionLookup().lookup(
                    fire.latitude, fire.longitude)
            for fb in fire.fuelbeds:
                if not fb.get('fccs_id') or not fb.get('pct'):
                    raise ValueError("Each fuelbed must define 'id' and 'pct'")
