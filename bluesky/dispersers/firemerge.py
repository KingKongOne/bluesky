import itertools
from collections import defaultdict

import afconfig
from afdatetime import parsing as datetime_parsing

from bluesky.exceptions import BlueSkyConfigurationError
from bluesky.models.fires import Fire
from bluesky import locationutils

class BaseFireMerger(oject):

    def _sum_data(self, data1, data2):
        summed_data = {}
        for k in set(data1.keys()).union(data2.keys()):
            if k not in data1:
                summed_data[k] = data2[k]
            elif k not in data2:
                summed_data[k] = data1[k]
            else:
                # we know that data1 and data2 will have the same structure,
                # so that, if 'k' is in both dicts, that values will both be
                # either numeric or dicts
                if isinstance(data1[k], dict):
                    summed_data[k] = self._sum_data(data1[k], data2[k])
                else:
                    summed_data[k] = data1[k] + data2[k]

        return summed_data


class FireMerger(BaseFireMerger):

    def merge(self, fires):
        fires_by_lat_lng = defaultdict(lambda: [])
        for f in sorted(fires, key=lambda f: f['start']):
            key = (f.latitude, f.longitude)
            merged = False

            # Sort fires_by_lat_lng[key] for unit testing purposes - for
            # deterministic behavior (since f could potentially merge with
            # possibly multiple fires in fires_by_lat_lng[key])
            # TODO: this shouldn't be a significant performance hit, but
            #   currently unit tests are structured so that the sorting
            #   doesn't come into play, so we could remove it for now.
            for i, f_merged in enumerate(sorted(fires_by_lat_lng[key], key=lambda f: f['start'])):
                if (not self._do_fires_overlap(f, f_merged)
                        and not self._do_fire_metas_conflict(f, f_merged)):
                    # replace f_merged with f_merged merged with f
                    fires_by_lat_lng[key][i] = self._merge_two_fires(f_merged, f)
                    merged = True

            if not merged:
                # just add it
                fires_by_lat_lng[key].append(f)

        # return flattened list
        return list(itertools.chain.from_iterable(fires_by_lat_lng.values()))

    def _do_fires_overlap(self, f1, f2):
        return (f1['start'] < f2['end']) and (f2['start'] < f1['end'])

    def _do_fire_metas_conflict(self, f1, f2):
        for k in set(f1['meta'].keys()).intersection(f2['meta'].keys()):
            if f1['meta'][k] != f2['meta'][k]:
                return True

        return False

    def _merge_two_fires(self, f_merged, f):
        new_f_merged = Fire(
            # We'll let the new fire be assigned a new id
            # It's possible, but not likely, that locations from different
            # fires will get merged together.  This set of original fire
            # ids isn't currently used other than in log messages, but
            # could be used in tranching
            original_fire_ids=f_merged.original_fire_ids.union(f.original_fire_ids),
            # we know at this point that their meta dicts don't conflict
            meta=dict(f_merged.meta, **f.meta),
            # there may be a gap between f_merged['end'] and f['start']
            # but no subsequent fires will be in that gap, since
            # fires were sorted by 'start'
            # Note: we need to use f_merged['start'] instead of f_merged.start
            #   because the Fire model has special property 'start' that
            #   returns the first start time of all active_areas in the fire's
            #   activity, and since we're not using nested activity here,
            #   f_merged.start returns 'None' rather than the actual value
            #   set in _add_location
            start=f_merged['start'],
            # end will only be used when merging fires
            # Note: see note about 'start', above
            end=f['end'],
            area=f_merged.area + f.area,
            # f_merged and f have the same lat,lng (o.w. they wouldn't
            # be merged)
            latitude=f_merged.latitude,
            longitude=f_merged.longitude,
            # the offsets could be different, but only if on DST transition
            # TODO: Should we worry about this?  If so, we should add same
            #   utc offset to criteria for deciding to merge or not
            utc_offset=f_merged.utc_offset,
            plumerise=self._merge_hourly_data(
                f_merged.plumerise, f.plumerise, f['start']),
            timeprofiled_area=self._merge_hourly_data(
                f_merged.timeprofiled_area, f.timeprofiled_area, f['start']),
            timeprofiled_emissions=self._merge_hourly_data(
                f_merged.timeprofiled_emissions, f.timeprofiled_emissions,
                f['start']),
            consumption=self._sum_data(f_merged.consumption, f.consumption)
        )
        if 'heat' in f_merged or 'heat' in f:
            new_f_merged['heat'] = f_merged.get('heat', 0.0) + f.get('heat', 0.0)
        return new_f_merged

    def _merge_hourly_data(self, data1, data2, start2):
        pruned_data2 = {k: v for k, v in data2.items()
            if self._on_or_after(k, start2)}
        return dict(data1, **pruned_data2)

    def _on_or_after(self, dt1, dt2):
        # make sure same type, and convert to datetimes if not
        if type(dt1) != type(dt2):
            dt1 = datetime_parsing.parse(dt1)
            dt2 = datetime_parsing.parse(dt2)
        return dt1 >= dt2



class PlumeMerger(BaseFireMerger):

    def __init__(self, config):
        self._set_config(config)

    def _set_config(self, config):
        if config:
            try:
                self.spacing = afconfig.get_config_value(
                    config, 'grid', 'spacing')
                self.swLat = afconfig.get_config_value(
                    config, 'grid', 'boundary', 'sw', 'lat')
                self.swLng = afconfig.get_config_value(
                    config, 'grid', 'boundary', 'sw', 'lng')
                self.neLat = afconfig.get_config_value(
                    config, 'grid', 'boundary', 'ne', 'lat')
                self.neLng = afconfig.get_config_value(
                    config, 'grid', 'boundary', 'ne', 'lng')
                if (self.spacing and self.swLat and self.swLng
                        and self.neLat and self.neLng):
                    return

            except Exception as e:
                pass

        # The config wasn't defined at all, or one of the required fields
        # wasn't defined, or the config was otherwise invalid
        raise BlueSkyConfigurationError(
            "Missing or invalid plume_merge configuration")

    def merge(self, fires):
        fire_buckets = self._bucket_fires(fires)
        merged_fires = []
        for b in fire_buckets:
            # create new fire out of all fires in the bucket
            merged_fires.append(self._merge_fires(b))

        return merged_fires

    def _bucket_fires(self, fires):
        buckets = defaultdict(lambda: [])
        for f in fires:
            # we can assume that lat and lng are defined
            if (f.latitude >= self.swLat and f.latitude <= self.neLat
                    and f.longitude >= self.swLng and f.longitude <= self.neLng):
                latIdx = int((f.latitude - self.swLat) / self.spacing)
                lngIdx = int((f.longitude - self.swLng) / self.spacing)
                buckets[(latIdx, lngIdx)].append(f)

            # else, fire will be excluded

        # we don't need to know the grid cell each bucket belongs to
        return list(buckets.values())

    def _merge_fires(self, fires):
        if len(fires) == 1:
            return fires[0]

        latLng = self._get_centroid(fires)

        new_f_merged = Fire(
            # We'll let the new fire be assigned a new id
            # It's possible, but not likely, that locations from different
            # fires will get merged together.  This set of original fire
            # ids isn't currently used other than in log messages, but
            # could be used in tranching
            original_fire_ids=set.union(*[f.original_fire_ids for f in fires]),
            meta=self._merge_meta(fires),
            # Note: we need to use f['start'] instead of f.start
            #   because the Fire model has special property 'start' that
            #   returns the first start time of all active_areas in the fire's
            #   activity, and since we're not using nested activity here,
            #   f.start returns 'None' rather than the actual value
            #   set in _add_location
            start=min([f['start'] for f in fires]),
            # end will only be used when merging fires
            # Note: see note about 'start', above
            end=max([f['end'] for f in fires]),
            area=sum([f.area for f in fires]),
            latitude=latLng.latitude,
            longitude=latLng.longitude,
            # the offsets could be different, but just take first
            # TODO: look up utc offset of centroid potision
            utc_offset=fires[0].utc_offset,
            plumerise=self._merge_plumerise(fires),
            timeprofiled_area=self._sum_data(fires, 'timeprofiled_area'),
            timeprofiled_emissions=self._sum_data(fires, 'timeprofiled_emissions'),
            consumption=self._sum_data(fires, 'consumption')
        )
        if 'heat' in f_merged or 'heat' in f:
            new_f_merged['heat'] = f_merged.get('heat', 0.0) + f.get('heat', 0.0)
        return new_f_merged

    def _get_centroid(self, fires):
        points = [{
            'lng': float(f.longitude),
            'lat':float(p.latitude)
        } for f in fires]

        return locationutils.LatLng({'specified_points': points})

    def _merge_meta(self, fires):
        # TODO: how to merge possibly conflicting meta data;
        # TODO: log warning if conflicting meta
        meta = {}
        for f in meta:
            meta.update(f.meta)
        return meta

    def _sum_data(self, fires, field):
        data = fires[0][field]
        for f in fires[1:]:
            # TODO: make sure the recursive call in
            #    BaseFireMerger._sum_data calls itself
            #    and not PlumeMerger._sum_data
            data = super()._sum_data(data, f[field])
        return data

    def _merge_plumerise(self, fires):
        # TODO: make sure all fires have the same number of plume heights
        #   and abort if not
        num_heights = len(fires[0].plumerise.values()[0]['heights'])
        plumerise = {}
        for dt in set.union([list(f['plumerise'].keys()) for f in fires]):
            levels = []
            for f in fires:
                if dt in f.plumerise and dt in f.timeprofiled_emissions:
                    for i in range(len(f.plumerise[dt]['heights'])):

                        pm25 = f.timeprofiled_emissions[dt].get('PM2.5')
                        # weight the fractions based on PM2.5 emissions levels
                        levels.extend(
                            (f.plumerise[dt]['heights'][i],
                                f.plumerise[dt]['emission_fractions'][i] * pm25)
                        )

            # sort by height
            levels.sort(key=lambda e: e[0])
            min_height = levels[0][0]
            max_height = levels[-1][0]
            height_diff = max_height - min_height
            bucketed_levels = [[]] * num_heights
            for l in levels:
                idx = int( () / height_diff)
            # TODO: combine
            # TODO: Normalize emissions_factors