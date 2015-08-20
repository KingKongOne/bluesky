# BlueSky Web

## APIs

### POST /api/v1/run/

This API requires posted JSON with three top level keys -
'modules', 'fires', and 'config'.
The 'fires' key lists the one or more fires to process. The 'modules' key is
the order specific list of modules through which the fires should be run.
The 'config' key specifies configuration data and other control parameters.

#### Fire Fields

The top level 'fires' object has data added to it as it moves through
the pipeline of modules.  Each module has its own set of required and optional
fields that it uses, so that the set of data needed for each fire depends
on the modules to be run. Generally, the further you are along the pipeline
of modules, the more data you need.  (Note, however, that some data required
by earlier modules can be dropped when you pipe the fire data into downstream
modules.)

##### fuelbeds

###### Required
 - ...

###### Optional
 - ...

##### consumption

###### Required
 - ...

###### Optional
 - 'fires' > 'location' > 'ecoregion'
 - 'fires' > 'type' -- fire type (ex. 'rx' or 'natural')

##### emissions

###### Required
 - ...

###### Optional
 - ...

##### localmet

###### Required
 - ...

###### Optional
 - ...

##### timeprofile

###### Required
 - ...

###### Optional
 - ...

##### plumerise

###### Required
 - ...

###### Optional
 - ...

##### dispersion

###### Required
 - ...

###### Optional
 - ...

##### visualization

###### Required
 - ...

###### Optional
 - ...

##### export

###### Required
 - ...

###### Optional
 - ...

#### Config Fields

The 'config' object has sub-objects specific to the modules to be run, as
well as top level fields that apply to multiple modules. As with
the fire data, each module has its own set of required and optional fields.


##### fuelbeds

###### Required
 - ...

###### Optional
 - ...

##### consumption

###### Required
 - ...

###### Optional
 - ...

##### emissions

###### Required
 - ...

###### Optional
 - ...

##### localmet

###### Required
 - ...

###### Optional
 - ...

##### timeprofile

###### Required
 - 'config' > 'start' -- modeling start time (ex. "20150121T000000Z")
 - 'config' > 'end' -- modeling end time (ex. "20150123T000000Z")

###### Optional
 - ...

##### plumerise

###### Required
 - ...

###### Optional
 - ...

##### dispersion

###### Required
 - 'config' > 'start' -- modeling start time (ex. "20150121T000000Z")
 - 'config' > 'end' -- modeling end time (ex. "20150123T000000Z")
 - 'config' > 'met_domain' -- met domain (ex. "PNW-4km")

###### Optional
 - 'config' > 'dispersion' > 'module' -- dispersion module; defaults to "hysplit"

##### visualization

###### Required
 - ...

###### Optional
 - ...

##### export

###### Required
 - ...

###### Optional
 - ...

#### Examples

##### Running ```fuelbeds```, ```consumption```, and ```emissions```:

This example requires very little data, since it's starting off with ```fuelbeds```,
one of the earlier modules in the pipeline.

    $ curl 'http://hostname/api/v1/run/' -H 'Content-Type: application/json' -d '
    {
        "modules": ["fuelbeds", "consumption", "emissions"],
        "fires": [
            {
                "id": "SF11C14225236095807750",
                "event_id": "SF11E826544",
                "name": "Natural Fire near Snoqualmie Pass, WA",
                "location": {
                    "perimeter": {
                        "type": "MultiPolygon",
                        "coordinates": [
                            [
                                [
                                    [-121.4522115, 47.4316976],
                                    [-121.3990506, 47.4316976],
                                    [-121.3990506, 47.4099293],
                                    [-121.4522115, 47.4099293],
                                    [-121.4522115, 47.4316976]
                                ]
                            ]
                        ]
                    },
                    "ecoregion": "southern"
                }
            }
        ]
    }'

Another exmaple, with fire location data specified as lat + lng + size

    $ curl 'http://hostname/api/v1/run/' -H 'Content-Type: application/json' -d '
    {
        "modules": ["fuelbeds", "consumption", "emissions"],
        "fires": [
            {
                "id": "SF11C14225236095807750",
                "event_id": "SF11E826544",
                "name": "Natural Fire near Snoqualmie Pass, WA",
                "location": {
                    "latitude": 47.4316976,
                    "longitude": -121.3990506,
                    "area": 200
                }
            }
        ]
    }'

##### Running  ```localmet```, ```timeprofile```, ```plumerise```, ```dispersion```, ```visualization```, ```export```:

This example assumes you've already run up through emissions.  The consumption data
that would have nested along side the emissions data has been stripped out, since
it's not needed.

    $ curl 'http://hostname/api/v1/run/' -H 'Content-Type: application/json' -d '
    {
        "modules": ["localmet", "timeprofile", "plumerise", "dispersion", "visualization", "export"],
        "fires": [
            {
                "id": "SF11C14225236095807750",
                "event_id": "SF11E826544",
                "name": "Natural Fire near Snoqualmie Pass, WA",
                "location": {
                    "latitude": 47.4316976,
                    "longitude": -121.3990506,
                    "area": 200
                },
                "fuelbeds": [
                    {
                        "fccs_id": "49",
                        "pct": 50.0,
                        "emissions": {
                            'ground fuels': {
                                'basal accumulations': {
                                    'flaming': {
                                        'PM2.5': [
                                            3.3815120047017005e-05
                                        ]
                                    },
                                    'residual': {
                                        'PM2.5': [
                                            4.621500211796271e-01
                                        ]
                                    },
                                    'smoldering': {
                                        'PM2.5': [
                                            6.424985839975172e-06
                                        ]
                                    }
                                }
                            }
                            /* ... (other emissions data) ... */
                        }
                    }
                ],
                "time": {
                    "start": "20150120T000000Z",
                    "end": "20150121T000000Z"
                }
            }
        ],
        "config": {
            "localmet": {
                /* ... */
            },
            "timeprofile": {
                "module": "standard" /* or "feps_rx_timing" or "custom" */
            },
            "plumerise": {
                "module": "sev"
            },
            "dispersion": {
                "module": "hysplit",
                "start": "20150121T000000Z",
                "end": "20150123T000000Z",
                "met_domain": "PNW-4km"
            },
            "visualization": {
                /* ... */
            },
            "export"" {
                "module": "playground" /* or "bs_daily" */
            }
        }
    }'

The nested keys in the emissions data are arbitrary.  The timeprofile
module simply expects a hierarchy of keys.  Generally speaking, the hiearchy
is of the form:

    'emissions' > 'category' > 'subcategory' > 'phase' > 'species'

where the 'category' and 'subcategory' keys correspond to fuel types, but could
be anything.

The fact that the emissions data is in an array is because the consumption
module (more specifically, the underlying 'consume' module) outputs arrays.
The length of each array equals the number of fuelbeds passed into consume.
Since consume is called on each fuelbed separately, the arrays of consumption
and emissions data will all be of length 1.

##### Running ```ingestion```, ```fuelbeds```, ```consumption```, ```emissions```, ```localmet```, ```timeprofile```, ```plumerise```, ```dispersion```, ```visualization```, ```export```:

    $ curl 'http://hostname/api/v1/run/' -H 'Content-Type: application/json' -d '
    {
        "modules": ["timeprofile", "plumerise", "dispersion"],
        "fires": [
            {
                "id": "SF11C14225236095807750",
                "event_id": "SF11E826544",
                "name": "Natural Fire near Snoqualmie Pass, WA",
                "location": {
                    "latitude": 47.4316976,
                    "longitude": -121.3990506,
                    "area": 200
                }
                "time": {
                    "start": "20150120T000000Z",
                    "end": "20150121T000000Z"
                }
            }
        ]
    }

## API Aliase

### POST /api/v1/playground/1/

This is just an alias for ```/api/v1/run/```, and running ```ingestion```,
```fuelbeds```, ```consumption```, ```emissions``` - i.e. you don't have
to specify the 'modules' key.  Also

### POST /api/v1/playground/2/

This is just an alias for ```/api/v1/run/```, and running ```localmet```,
```timeprofile```, ```plumerise```, ```dispersion```, ```visualization```,
```export```.  As with /1/, you don't have to specify either the 'modules'
key or the export type.

Example:

    $ curl 'http://hostname/api/v1/playground/2/' -H 'Content-Type: application/json' -d '
    {
        "fires": [
            {
                "id": "SF11C14225236095807750",
                "event_id": "SF11E826544",
                "name": "Natural Fire near Snoqualmie Pass, WA",
                "location": {
                    "latitude": 47.4316976,
                    "longitude": -121.3990506,
                    "area": 200
                },
                "fuelbeds": [
                    {
                        "fccs_id": "49",
                        "pct": 50.0,
                        "emissions": {
                            'ground fuels': {
                                'basal accumulations': {
                                    'flaming': {
                                        'PM2.5': [
                                            3.3815120047017005e-05
                                        ]
                                    },
                                    'residual': {
                                        'PM2.5': [
                                            4.621500211796271e-01
                                        ]
                                    },
                                    'smoldering': {
                                        'PM2.5': [
                                            6.424985839975172e-06
                                        ]
                                    }
                                }
                            }
                            /* ... (other emissions data) ... */
                        }
                    }
                ],
                "time": {
                    "start": "20150120T000000Z",
                    "end": "20150121T000000Z"
                }
            }
        ],
        "config": {
            "start": "20150121T000000Z",
            "end": "20150123T000000Z",
            "met_domain": "PNW-4km",
            "timeprofile": {
                "module": "custom"
            }
        }
    }'
