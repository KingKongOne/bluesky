"""bluesky.models.fires"""

__author__ = "Joel Dubowy"
__copyright__ = "Copyright 2016, AirFire, PNW, USFS"

import abc
import copy
import datetime
import importlib
import json
import logging
import re
import sys
import traceback
import uuid

from bluesky import datautils, configuration
from bluesky.exceptions import (
    BlueSkyImportError, BlueSkyModuleError
)

__all__ = [
    'Fire',
    'FiresManager'
]


class Fire(dict):

    DEFAULT_TYPE = 'wildfire'
    DEFAULT_FUEL_TYPE = 'natural'

    def __init__(self, *args, **kwargs):
        super(Fire, self).__init__(*args, **kwargs)

        # private id used to identify fire from possibly multiple fires with
        # the same public 'id' (e.g. in FiresManager's failure handler)
        self._private_id = str(uuid.uuid1())

        # if id isn't specified, set to new guid
        if not self.get('id'):
            self['id'] = str(uuid.uuid1())[:8]

        if not self.get('type'):
            self['type'] = self.DEFAULT_TYPE
        # TODO: figure out how to not have to explicitly call _validate_type here
        else:
            self['type'] = self._validate_type(self['type'])

        if not self.get('fuel_type'):
            self['fuel_type'] = self.DEFAULT_FUEL_TYPE
        # TODO: figure out how to not have to explicitly call _validate_fuel_type here
        else:
            self['fuel_type'] =self._validate_fuel_type(self['fuel_type'])

    ## Properties

    @property
    def latitude(self):
        # This is if latitude is a true top level key
        if 'latitude' in self:
            return self['latitude']
        # This is if latitude is nested somewhere or needs to be derived
        if not hasattr(self, '_latitude'):
            if self.location and 'latitude' in self.location:
                self._latitude = self.location['latitude']
            elif self.location and 'perimeter' in self.location:
                # TODO: get centroid of perimeter(s); also, can't assume 3-deep nested
                # array (it's 3-deep for MultiPolygon, but not necessarily other shape types)
                # see https://en.wikipedia.org/wiki/Centroid
                self._latitude = self.location['perimeter']['coordinates'][0][0][0][1]
                self._longitude = self.location['perimeter']['coordinates'][0][0][0][0]
            elif self.location and 'shape_file' in self.location:
                raise NotImplementedError("Importing of shape data from file not implemented")
            else:
                raise ValueError("Insufficient location data required for "
                    "determining single lat/lng for fire")
        return self._latitude

    @property
    def longitude(self):
        # This is if longitude is a true top level key
        if 'longitude' in self:
            return self['longitude']
        # This is if longitude is nested somewhere or needs to be derived
        if not hasattr(self, '_longitude'):
            if self.location and 'longitude' in self.location:
                self._longitude = self.location['longitude']
            elif self.location and 'perimeter' in self.location:
                # TODO: get centroid of perimeter(s); also, can'st assume 3-deep nested
                # array (it's 3-deep for MultiPolygon, but not necessarily other shape types)
                # see https://en.wikipedia.org/wiki/Centroid
                self._latitude = self.location['perimeter']['coordinates'][0][0][0][1]
                self._longitude = self.location['perimeter']['coordinates'][0][0][0][0]
            elif self.location and 'shape_file' in self.location:
                raise NotImplementedError("Importing of shape data from file not implemented")
            else:
                raise ValueError("Insufficient location data required for "
                    "determining single lat/lng for fire")
        return self._longitude

    ## Validation

    VALID_TYPES = {
        'wildfire': 'wildfire',
        'wf': 'wildfire',
        'rx':'rx'
    }
    INVALID_TYPE_MSG = "Invalid fire 'type': {}"

    def _validate_type(self, val):
        val = val.lower()
        if val not in self.VALID_TYPES:
            raise ValueError(self.INVALID_TYPE_MSG.format(val))
        return self.VALID_TYPES[val]

    VALID_FUEL_TYPES = ('natural', 'activity', 'piles')
    INVALID_FUEL_TYPE_MSG = "Invalid fire 'fuel_type': {}"

    def _validate_fuel_type(self, val):
        val = val.lower()
        if val not in self.VALID_FUEL_TYPES:
            raise ValueError(self.INVALID_FUEL_TYPE_MSG.format(val))
        return val

    ## Getters and Setters

    def __setitem__(self, attr, val):
        k = '_validate_{}'.format(attr)
        if hasattr(self, k):
            val = getattr(self, k)(val)
        super(Fire, self).__setitem__(attr, val)

    def __getattr__(self, attr):
        if attr in self.keys():
            return self[attr]
        raise KeyError(attr)

    def __setattr__(self, attr, val):
        if not attr.startswith('_') and not hasattr(Fire, attr):
            self[attr] = val
        else:
            super(Fire, self).__setattr__(attr, val)


class FireEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'tolist'):
            return obj.tolist()

        return json.JSONEncoder.default(self, obj)


class FiresManager(object):

    def __init__(self):
        self._meta = {}
        self.modules = []
        self.fires = [] # this intitializes self._fires and self_fire_ids
        self._processed_run_id_wildcards = False

    ## Importing

    def add_fire(self, fire):
        self._fires = self._fires or {}
        if not self._fires.has_key(fire.id):
            self._fires[fire.id] = []
            self._fire_ids.add(fire.id)
        self._fires[fire.id].append(fire)


    def remove_fire(self, fire):
        # TODO: raise exception if fire doesn't exist ?
        if self._fires.has_key(fire.id):
            self._fires[fire.id] = [f for f in self._fires[fire.id]
                if f._private_id != fire._private_id]
            if len(self._fires[fire.id]) == 0:
                # that was last fire with that id
                self._fire_ids.remove(fire.id)
                self._fires.pop(fire.id)

    ## Merging Fires

    def merge_fires(self):
        """Merges fires that have the same id.
        """
        FiresMerger(self).merge()

    ## IO

    # TODO: Remove this method and use bluesky.io.Stream in code below instead
    # (would have a fair amoubnt of unit test updates)
    def _stream(self, file_name, flag): #, do_strip_newlines):
        if file_name:
            return open(file_name, flag)
        else:
            if flag == 'r':
                return sys.stdin
            else:
                return sys.stdout

    ##
    ## 'Public' Methods
    ##

    def _get_fire(self, fire):
        fires_with_id = self._fires.get(fire.id)
        if fires_with_id:
            fires_with_p_id = [f for f in fires_with_id
                if f._private_id == fire._private_id]
            if fires_with_p_id:
                # will be len == 1
                return fires_with_p_id[0]

    @property
    def fires(self):
        return [f for fire_id in self._fire_ids for f in self._fires[fire_id]]

    @fires.setter
    def fires(self, fires_list):
        self._fires = {}
        self._fire_ids = set()
        for fire in fires_list:
            self.add_fire(Fire(fire))

    @property
    def modules(self):
        return self._module_names

    RUN_ID_WILDCARDS = [
        (re.compile('{timestamp}'),
            lambda: datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S'))
        # TDOO: any other?
    ]

    @property
    def run_id(self):
        if not self._meta.get('run_id'):
            self._meta['run_id'] = str(uuid.uuid1())
        elif not self._processed_run_id_wildcards:
            logging.debug('filling in run_id wildcards')
            for m, f in self.RUN_ID_WILDCARDS:
                if m.search(self._meta['run_id']):
                    self._meta['run_id'] = self._meta['run_id'].replace(
                        m.pattern, f())
            self._processed_run_id_wildcards = True
        return self._meta['run_id']

    @modules.setter
    def modules(self, module_names):
        self._module_names = module_names
        self._modules = []
        for m in module_names:
            try:
                self._modules.append(importlib.import_module('bluesky.modules.%s' % (m)))
            except ImportError, e:
                if e.message == 'No module named {}'.format(m):
                    raise BlueSkyImportError("Invalid module '{}'".format(m))
                else:
                    logging.debug(traceback.format_exc())
                    raise BlueSkyImportError("Error importing module {}".format(m))

    @property
    def meta(self):
        return self._meta

    def get_config_value(self, *keys, **kwargs):
        return configuration.get_config_value(self.config, *keys, **kwargs)

    def set_config_value(self, value, *keys):
        self.config = self.config or dict()
        configuration.set_config_value(self.config, value, *keys)

    def merge_config(self, config_dict):
        self.config = self.config or dict()
        if config_dict:
            configuration.merge_configs(self.config, config_dict)

    # @property(self):
    # def meta(self):
    #     return self._meta

    def __getattr__(self, attr):
        """Provides get access to meta data

        Note: __getattr__ is called when the 'attr' isn't defined on self
        """
        return self._meta.get(attr)

    def __setattr__(self, attr, val):
        """Provides set access to meta data

        Note: __setattr__ is always called, whether or not 'attr' is defined
        on self.  So, we have to make sure this is meta data, and call super's
        __setattr__ if not.
        """
        if not attr.startswith('_') and not hasattr(FiresManager, attr):
            self._meta[attr] = val
        super(FiresManager, self).__setattr__(attr, val)

    def processed(self, module_name, version, **data):
        # TODO: determine module from call stack rather than require name
        # to be passed in.  Also get version from module's __version__
        v = {
            'module': module_name,
            'version': version,
        }
        if data:
            v.update(data)

        if not self.processing or self.processing[-1].keys() != ['module_name']:
            self.processing = self.processing or []
            self.processing.append(v)
        else:
            self.processing[-1].update(v)

    def summarize(self, **data):
        self.summary = self.summary or {}
        self.summary = datautils.deepmerge(self.summary, data)

    ## Loading data

    def load(self, input_dict):
        if not hasattr(input_dict, 'keys'):
            raise ValueError("Invalid fire data")

        # wipe out existing list of modules, if any
        self.modules = input_dict.pop('modules', [])

        # wipe out existing fires, if any
        self.fires = input_dict.pop('fire_information', [])

        self._meta = input_dict

        # HACK: access run id simply to trigger replacement of wildcars
        # Note: the check for 'run_id' in self._meta prevents it from being
        #  generated unnecessarily
        # TODO: always generate a run id (by removing the check)?
        if 'run_id' in self._meta:
            self.run_id

    def loads(self, input_stream=None, input_file=None):
        """Loads json-formatted fire data, creating list of Fire objects and
        storing other fields in self.meta.
        """
        if input_stream and input_file:
            raise RuntimeError("Don't specify both input_stream and input_file")
        if not input_stream:
            input_stream = self._stream(input_file, 'r')
        data = json.loads(''.join([d for d in input_stream]))
        return self.load(data)

    def run(self): #, module_names):
        failed = False
        for i in range(len(self._modules)):
            # if one of the modules already failed, then the only thing
            # we'll run from here on is the export module
            if failed and 'export' != self._module_names[i]:
                continue

            try:
                # initialize processing recotd
                self.processing = self.processing or []
                self.processing.append({
                    "module_name": self._module_names[i]
                })

                # 'run' modifies fires in place
                self._modules[i].run(self)
            except Exception, e:
                failed = True
                # when there's an error running modules, don't bail; continue
                # iterating through requested modules, executing only exports
                # and then raise BlueSkyModuleError, below, so that the calling
                # code can decide what to do (which, in the case of bsp and
                # bsp-web, is to dump the data as is)
                logging.error(e)
                tb = traceback.format_exc()
                logging.debug(tb)
                self.error = {
                    "module": self._module_names[i],
                    "message": str(e),
                    "traceback": str(tb)
                }

        if failed:
            # If there was a failure
            raise BlueSkyModuleError

    ## Filtering Fires

    def filter_fires(self):
        FiresFilter(self).filter()

    ## Failures

    @property
    def fire_failure_handler(self):
        """Context manager that moves failed fires

        The reason for defining a method that returns a context manager class,
        is that the closure allows the call to not have to pass in the
        fires_manager object itself.

            for fire in fires_manager.fires:
                with fires_manager.fire_failure_handler(fire):
                    ....

        as opposed to:

            for fire in fires_manager.fires:
                with fires_manager.fire_failure_handler(fires_manager, fire):
                    ....
        """
        fires_manager = self
        class klass(object):
            def __init__(self, fire):
                self._fire = fire

            def __enter__(self):
                pass

            def __exit__(self, e_type, value, tb):
                if e_type:
                    # there was a failure; first see if fire is in fact
                    # managed by fires_manager
                    f = fires_manager._get_fire(self._fire)
                    if f:
                        # Add error infromation to fire object.
                        # Note that error information will also be added to
                        # top level if skip_failed_fires == False
                        f.error = {
                            "type": value.__class__.__name__,
                            "message": value.message,
                            "traceback": str(traceback.format_exc(tb))
                        }
                        if fires_manager.skip_failed_fires:
                            # move fire to failed list, excluding it from
                            # future processing
                            if fires_manager.failed_fires is None:
                                fires_manager.failed_fires  = []
                            fires_manager.failed_fires.append(f)
                            # remove fire from good fires list
                            fires_manager.remove_fire(f)
                            return True
                        # else, let exception, if any, be raised
                    else:
                        # fire was not one of fires_manager's
                        # TODO: don't raise exception if configured not to
                        #  (maybe also controlled by
                        #   fires_manager.skip_failed_fires?)
                        raise RuntimeError("Fire {} ({}) not managed by "
                            "fires_manager".format(self._fire.id,
                            self._fire._private_id))

        return klass

    @property
    def skip_failed_fires(self):
        return not not self.get_config_value('skip_failed_fires')

    ## Dumping data

    def dump(self):
        # Don't include 'modules' in the output. The modules to be run may have
        # been specified on the command line or in the input json. Either way,
        # 'processing' contains a record of what modules were run (though it may
        # be fewer modules than what were requested, which would be the case
        # if there was a failure).  We don't want to include 'modules' in the
        # output because that breaks the ability to pipe the results into
        # another run of bsp.
        # TODO: keep track of whether modules were specified in the input
        # json or on the command line, and add them to the output if they
        # were in the input
        return dict(self._meta, fire_information=self.fires)

    def dumps(self, output_stream=None, output_file=None):
        if output_stream and output_file:
            raise RuntimeError("Don't specify both output_stream and output_file")
        if not output_stream:
            output_stream = self._stream(output_file, 'w')
        fire_json = json.dumps(self.dump(), cls=FireEncoder)
        output_stream.write(fire_json)


##
## Filtering and Merging Fires
##

class FiresActionBase(object):
    """Base class for merging or filtering fires
    """

    __metaclass__ = abc.ABCMeta

    def __init__(self, fires_manager):
        """Constructor

        args:
         - fires_manager -- FiresManager object whose fires are to be merged
        """
        self._fires_manager = fires_manager
        self._skip_failures = not not self._fires_manager.get_config_value(
            self.ACTION, 'skip_failures')

    ##
    ## Abstract methods
    ##

    @abc.abstractmethod
    #@property
    def _action(self):
        pass

    @abc.abstractmethod
    #@property
    def _error_class(self):
        pass

    ##
    ## Helper methods
    ##

    def _fail(self, fire, sub_msg):
        msg = "Failed to {} fire {} ({}): {}".format(
            self.ACTION, fire.id, fire._private_id, sub_msg)
        raise self._error_class(msg)


class FiresMerger(FiresActionBase):
    """Class for merging fires with the same id.

    e.g. For fires that have a separate listing for each day in their duration.

    Note: The logic in this class is organized as a saparate class primarily
    for maintainability, testibility, and readability.  It was originally in
    the FiresManager class.
    """

    ACTION = 'merge'
    @property
    def _action(self):
        return self.ACTION

    class MergeError(Exception):
        pass
    @property
    def _error_class(self):
        return self.MergeError

    ##
    ## Public API
    ##

    def merge(self):
        """Merges fires that have the same id.
        """
        for fire_id in self._fires_manager._fire_ids:
            if len(self._fires_manager._fires[fire_id]) > 1:
                self._merge_fire_id(fire_id)

    ##
    ## Merge Methods
    ##

    def _merge_fire_id(self, fire_id):
        """Actually does the merging of fires with a given id

        args:
         - fire_id -- common fire id

        For simplicity, the logic iterates once through the fires, in
        order. This might miss potential merges (e.g. if all but the
        first fire have the same location), but those should be
        edge cases.  So, it seems that it would be overengineering and not
        worth the hit to performance to check every pair of fires for
        mergeability.

        TODO: refactor inner loop logic into submethods
        """
        combined_fire = None
        for fire in self._fires_manager._fires[fire_id]:
            try:
                # TODO: iterate through and call all methods starting
                #   with '_check_'; would need to change _check_keys'
                #   signature to match the others
                self._check_keys(fire)
                self._check_location(fire, combined_fire)
                self._check_growth_windows(fire, combined_fire)
                self._check_event_of(fire, combined_fire)
                self._check_fire_and_fuel_types(fire, combined_fire)

                combined_fire = self._merge_into_combined_fire(fire,
                    combined_fire)

            except FiresMerger.MergeError, e:
                if not self._skip_failures:
                    raise ValueError(e.message)

        if combined_fire:
            # add_fire will take care of creating new list
            # and adding fire id in the case where all fires
            # were combined and thus all removed
            self._fires_manager.add_fire(combined_fire)


    def _merge_into_combined_fire(self, fire, combined_fire):
        """Merges fires into in-progress combined fire

        args:
         - fire -- fire to merge
         - combined_fire -- in-progress combined fire (which could be None)
        """
        if not combined_fire:
            # We need to instantiate a dict from fire in order to deepcopy id.
            # We need to deepcopy so that that modifications to
            # new_combined_fire don't modify fire
            new_combined_fire = Fire(copy.deepcopy(dict(fire)))
            self._fires_manager.remove_fire(fire)

        else:
            # See note, above, regarding instantiating dict and then deep copying
            new_combined_fire = Fire(copy.deepcopy(dict(combined_fire)))
            try:
                new_combined_fire.location['area'] += fire.location['area']

                self._merge_growth_into_combined_fire(fire, combined_fire, new_combined_fire)

                # TODO: merge anything else?

                # make sure remove_fire succeeds before
                # updating combined_fire
                self._fires_manager.remove_fire(fire)

            except Exception, e:
                self._fail(fire, e)

        return new_combined_fire

    def _merge_growth_into_combined_fire(self, fire, combined_fire,
            new_combined_fire):
        # factor by which we need to multiple combined_fire's growth pcts
        # (at this point, growth windows are defined or not defined for
        #  both fires)
        if combined_fire.get('growth'):
            c_growth_factor = float(combined_fire.location['area']) / float(
                new_combined_fire.location['area'])
            for g in new_combined_fire.growth:
                g['pct'] *= c_growth_factor

            # copy it to preserve old fire, in case theres a failure
            # downstream and we abort this merge
            new_growth = copy.deepcopy(fire.growth)
            # factor by which we need to multiple to-merge fire's growth pcts
            f_growth_factor = 1.0 - c_growth_factor
            for g in new_growth:
                g['pct'] *= f_growth_factor

            new_combined_fire.growth.extend(new_growth)
            new_combined_fire.growth.sort(key=lambda e: e['start'])

    ##
    ## Validation / Check Methods
    ##

    # TODO: maybe eventually be able to merge post-consumption, emissions,
    #   etc., but for now only support merging just-ingested fire data
    REQUIRED_MERGE_FIELDS = set(['location'])
    ALL_MERGEABLE_FIELDS = REQUIRED_MERGE_FIELDS.union(
        ["id", "event_of", "type", "fuel_type", "growth"])
    INVALID_KEYS_MSG =  "invalid data set"
    def _check_keys(self, fire):
        keys = set(fire.keys())
        if (not self.REQUIRED_MERGE_FIELDS.issubset(keys) or
                not keys.issubset(self.ALL_MERGEABLE_FIELDS)):
            self._fail(fire, self.INVALID_KEYS_MSG)

    LOCATION_MISMATCH_MSG = "locations don't match"
    def _check_location(self, fire, combined_fire):
        """Makes sure the locations are the same

        TODO: be more intelligent about comparing location; the
          current logic could return false positives (e.g. if one
          fire specifies a single coordinate and the other specifies
          a polygon starting at that coord)
        """
        if combined_fire and (
                fire.latitude != combined_fire.latitude or
                fire.longitude != combined_fire.longitude):
            self._fail(fire, self.LOCATION_MISMATCH_MSG)

    GROWTH_FOR_BOTH_OR_NONE_MSG = ("growth windows must be defined for both "
        "fires or neither in order to merge")
    OVERLAPPING_GROWTH_WINDOWS = "growth windows overlap"
    def _check_growth_windows(self, fire, combined_fire):
        """Makes sure growth windows are defined for all or none,
        and if defined, make sure they don't overlap

        Ultimately, overlapping growth windows could be handled,
        but at this point it would be overengineering.
        """
        if combined_fire and (
                bool(combined_fire.get('growth')) != bool(fire.get('growth'))):
            self._fail(fire, self.GROWTH_FOR_BOTH_OR_NONE_MSG)

        # TODO: check for overlaps

    EVENT_MISMATCH_MSG = "fire event ids don't match"
    def _check_event_of(self, fire, combined_fire):
        """Makes sure event ids, if both defined, are the same
        """
        c_event_id = combined_fire and combined_fire.get(
            'event_of', {}).get('id')
        f_event_id = fire.get('event_of', {}).get('id')
        if c_event_id and f_event_id and c_event_id != f_event_id:
            self._fail(fire, self.EVENT_MISMATCH_MSG)

    FIRE_TYPE_MISMATCH_MSG = "Fire types don't match"
    FUEL_TYPE_MISMATCH_MSG = "Fuel types don't match"
    def _check_fire_and_fuel_types(self, fire, combined_fire):
        """Makes sure fire and fuel types are the same
        """
        if combined_fire:
            if fire.type != combined_fire.type:
                self._fail(fire, self.FIRE_TYPE_MISMATCH_MSG)
            if fire.fuel_type != combined_fire.fuel_type:
                self._fail(fire, self.FUEL_TYPE_MISMATCH_MSG)


##
## Fires Filter
##

class FiresFilter(FiresActionBase):
    """Class for filtering fires by various criteria.

    Note: The logic in this class is organized as a saparate class primarily
    for maintainability, testibility, and readability.  Some of it was
    originally in the FiresManager class.
    """

    ACTION = 'filter'
    @property
    def _action(self):
        return self.ACTION

    class FilterError(Exception):
        pass
    @property
    def _error_class(self):
        return self.FilterError

    ##
    ## Public API
    ##

    NO_FILTERS_MSG = "No filters specified"
    MISSING_FILTER_CONFIG_MSG = "Specify config for each filter"
    def filter(self):
        """Merges fires that have the same id.
        """
        filter_config = self._fires_manager.get_config_value('filter')
        filter_fields = filter_config and [f for f in filter_config
            if f != 'skip_failures']
        if not filter_fields:
            if not self._skip_failures:
                raise self.FilterError(self.NO_FILTERS_MSG)
            # else, noop and return
        else:
            for f in filter_fields:
                try:
                    filter_getter = getattr(self, '_get_{}_filter'.format(f),
                        self._get_filter)
                    kwargs = filter_config.get(f)
                    if not kwargs:
                        if self._skip_failures:
                            continue
                        else:
                            raise self.FilterError(self.MISSING_FILTER_CONFIG_MSG)
                    kwargs.update(filter_field=f)
                    filter_func = filter_getter(**kwargs)
                except self.FilterError, e:
                    if self._skip_failures:
                        continue
                    else:
                        raise

                for fire in self._fires_manager.fires:
                    if filter_func(fire):
                        self._fires_manager.remove_fire(fire)
                        if self._fires_manager.filtered_fires is None:
                            self._fires_manager.filtered_fires  = []
                        # TDOO: add reason for filtering (specify at least filed)
                        self._fires_manager.filtered_fires.append(fire)

    ##
    ## Unterlying filter methods
    ##

    SPECIFY_WHITELIST_OR_BLACKLIST = "Specify whitelist or blacklist - not both"
    SPECIFY_FILTER_FIELD = "Specify attribute to filter on"
    def _get_filter(self, **kwargs):
        whitelist = kwargs.get('whitelist')
        blacklist = kwargs.get('blacklist')
        if (not whitelist and not blacklist) or (whitelist and blacklist):
            raise self.FilterError(self.SPECIFY_WHITELIST_OR_BLACKLIST)
        filter_field = kwargs.get('filter_field')
        if not filter_field:
            # This will never happen if called internally
            raise self.FilterError(self.SPECIFY_FILTER_FIELD)

        def _filter(fire):
            if whitelist:
                return not hasattr(fire, filter_field) or getattr(fire, filter_field) not in whitelist
            else:
                return hasattr(fire, filter_field) and getattr(fire, filter_field) in blacklist

        return _filter


    # TODO: specify generic **kwargs in methof signatures instead of specific
    #   keyword args to avoid TypeError (?) from being raised due to
    #   recognized keywords ? .... (what's desireable behavior?)

    def _get_location_filter(self, boundary=None):
        # TODO: Make sure boudary is defined; raise esxception if not
        # TDOD: return filter function that :
        #  - returns boolean
        #  - calls self._fail as necessary
        pass

    def _get_area_filter(self, min_area=None, max_area=None):
        # TODO: Make sure min and/or max are defined; raise esxception if not
        # TDOD: return filter function that :
        #  - returns boolean
        #  - calls self._fail as necessary
        pass