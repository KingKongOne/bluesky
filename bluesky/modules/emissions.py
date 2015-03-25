"""bluesky.modules.consumption
"""

__author__      = "Joel Dubowy"
__copyright__   = "Copyright 2015, AirFire, PNW, USFS"

import logging

from emitcalc.calculator import EmissionsCalculator
from eflookup.fccs2ef.lookup import Fccs2Ef

__all__ = [
    'run'
]

def run(fires):
    logging.debug("Running emissions module (NOOP)")
    calculator = EmissionsCalculator(Fccs2Ef())
    for fire in fires:
        for fb in fire.fuelbeds:
            is_rx = fire.get('type') == "rx"
            fb['emissions'] = calculator.calculate([fb["fccs_id"]], fb["consumption"], is_rx)
