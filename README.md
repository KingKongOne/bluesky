# BlueSky Pipeline

BlueSky Framework rearchitected as a pipeable collection of standalone modules.

## Non-python Dependencies

For the fuelbeds module, you'll need to manually install some
dependencies needed by the fccsmap package, which fuelbeds uses.
See the [fccsmap github page](https://github.com/pnwairfire/fccsmap)
for instructions.

Additionally, on ubuntu, you'll need to install libxml

    sudo apt-get install libxml2-dev libxslt1-dev

## Development

### Clone Repo

Via ssh:

    git clone git@github.com:pnwairfire/bluesky.git

or http:

    git clone https://github.com/pnwairfire/bluesky.git

### Install Dependencies

First, install pip (with sudo if necessary):

    apt-get install python-pip


Run the following to install python dependencies:

    pip install --no-binary gdal --trusted-host pypi.smoke.airfire.org -r requirements.txt

Run the following to install packages required for development and testing:

    pip install -r requirements-test.txt
    pip install -r requirements-dev.txt

#### Notes

##### pip issues

If you get an error like    ```AttributeError: 'NoneType' object has no
attribute 'skip_requirements_regex```, it means you need in upgrade
pip. One way to do so is with the following:

    pip install --upgrade pip

##### gdal issues

If, when you use fccsmap, you get the following error:

    *** Error: No module named _gdal_array

it's because your osgeo package (/path/to/site-packages/osgeo/) is
missing _gdal_array.so.  This happens when gdal is built on a
machine that lacks numpy.  The ```--no-binary :all:``` in the pip
install command, above, is meant to fix this issue.  If it doesn't work,
try uninstalling the gdal package and then re-installing it individually
with the ```--no-binary``` option to pip:

    pip uninstall -y GDAL
    pip install --no-binary :all: gdal==1.11.2

If this doesn't work, uninstall gdal, and then install it manually:

    pip uninstall -y GDAL
    wget https://pypi.python.org/packages/source/G/GDAL/GDAL-1.11.2.tar.gz
    tar xzf GDAL-1.11.2.tar.gz
    cd GDAL-1.11.2
    python setup.py install

### Setup Environment

This project contains a single package, ```bluesky```. To import bluesky
package in development, you'll have to add the repo root directory to the
search path. The ```bsp``` script does this automatically, if
necessary.

## Running tests

Use pytest:

    py.test
    py.test test/bluesky/path/to/some_tests.py

You can also use the ```--collect-only``` option to see a list of all tests.

    py.test --collect-only

See [pytest](http://pytest.org/latest/getting-started.html#getstarted) for more information about using pytest.

## Installation

### Installing With pip

First, install pip (with sudo if necessary):

    apt-get install python-pip
    pip install --upgrade pip

Then, to install, for example, v0.3.1, use the following (with sudo if necessary):

    pip install --no-binary gdal --trusted-host pypi.smoke.airfire.org -i http://pypi.smoke.airfire.org/simple bluesky==0.3.1

Or, if using the bluesky package in another project, add it to your project's
requirements.txt:

    -i http://pypi.smoke.airfire.org/simple/
    bluesky==0.3.1

See the Development > Install Dependencies > Notes section, above, for
notes on resolving pip and gdal issues.

## Usage:

### bsp

bsp is the main BlueSky executable.  It can be used for either or both of
the following:

 - to filter a set of fires by country code
 - **to run BlueSky modules (consumption, emissions, etc.) on fire data**

#### Getting Help

Use the ```-h``` flag for help:

    $ bsp -h
    Usage: bsp [options] [<module> ...]

    Options:
      -h, --help            show this help message and exit
      -l, --list-modules    lists available modules; order matters
      ...

Use the ```-l``` flag to see available BlueSky modules:

    $ bsp -l

    Available Modules:
            consumption
            emissions
            fuelbeds
            ...

#### Input / Output

The ```bsp``` executable inputs fire json data, and exports a modified version
of that fire json data.  You can input from stdin (via piping or redirecting)
or from file.  Likewise, you can output to stdout or to file.

Example of reading from and writing to file:

    $ bsp -i /path/to/input/fires/json/file.json -o /path/to/output/modified/fires/json/file.json fuelbeds consumption

Example of piping in and redirecting output to file

    $ cat /path/to/input/fires/json/file.json | bsp fuelbeds > /path/to/output/modified/fires/json/file.json

Example of redirecting input from and outputing to file:

    $ bsp fuelbeds consumption emissions < /path/to/input/fires/json/file.json > /path/to/output/modified/fires/json/file.json

Example of redirecting input from file and outputing to stdout

    $ bsp fuelbeds fuelloading < /path/to/input/fires/json/file.json

#### Data Format

```bsp``` supports inputting and outputing only json formatted fire data.
If you have csv formatted fire data, you can use ```bsp-csv2json``` to convert
your data to json format.  For example, assume fires.csv contains the
following data:

    id,event_id,latitude,longitude,type,area,date_time,elevation,slope,state,county,country,fips,scc,fuel_1hr,fuel_10hr,fuel_100hr,fuel_1khr,fuel_10khr,fuel_gt10khr,shrub,grass,rot,duff,litter,moisture_1hr,moisture_10hr,moisture_100hr,moisture_1khr,moisture_live,moisture_duff,consumption_flaming,consumption_smoldering,consumption_residual,consumption_duff,min_wind,max_wind,min_wind_aloft,max_wind_aloft,min_humid,max_humid,min_temp,max_temp,min_temp_hour,max_temp_hour,sunrise_hour,sunset_hour,snow_month,rain_days,heat,pm25,pm10,co,co2,ch4,nox,nh3,so2,voc,canopy,event_url,fccs_number,owner,sf_event_guid,sf_server,sf_stream_name,timezone,veg
    SF11C14225236095807750,SF11E826544,25.041,-77.379,RX,99.9999997516,201501200000Z,0.0,10.0,Unknown,,Unknown,-9999,2810015000,,,,,,,,,,,,10.0,12.0,12.0,22.0,130.0,150.0,,,,,6.0,6.0,6.0,6.0,40.0,80.0,13.0,30.0,4,14,7,18,5,8,,,,,,,,,,,,http://playground.dri.edu/smartfire/events/17cde405-cc3a-4555-97d2-77004435a020,,,17cde405-cc3a-4555-97d2-77004435a020,playground.dri.edu,realtime,-5.0,

running ```bsp-csv2json``` like so:

    bsp-csv2json -i fires.csv

would produce the following (written to stdout):

    {"fire_information": [{"slope": 10.0, "max_humid": 80.0, "co": "", "veg": "", "consumption_flaming": "", "max_temp": 30.0, "scc": 2810015000, "county": "", "fuel_1hr": "", "event_url": "http://playground.dri.edu/smartfire/events/17cde405-cc3a-4555-97d2-77004435a020", "timezone": -5.0, "owner": "", "min_temp": 13.0, "sunrise_hour": 7, "sunset_hour": 18, "rot": "", "id": "SF11C14225236095807750", "fuel_100hr": "", "fuel_10khr": "", "shrub": "", "min_wind_aloft": 6.0, "area": 99.9999997516, "event_id": "SF11E826544", "moisture_live": 130.0, "voc": "", "consumption_smoldering": "", "sf_stream_name": "realtime", "fuel_1khr": "", "min_humid": 40.0, "state": "Unknown", "rain_days": 8, "latitude": 25.041, "min_wind": 6.0, "type": "RX", "moisture_10hr": 12.0, "pm25": "", "sf_event_guid": "17cde405-cc3a-4555-97d2-77004435a020", "elevation": 0.0, "co2": "", "consumption_residual": "", "moisture_1khr": 22.0, "heat": "", "min_temp_hour": 4, "fips": -9999, "nh3": "", "max_temp_hour": 14, "max_wind_aloft": 6.0, "canopy": "", "duff": "", "date_time": "201501200000Z", "fuel_10hr": "", "moisture_duff": 150.0, "fuel_gt10khr": "", "pm10": "", "country": "Unknown", "litter": "", "longitude": -77.379, "moisture_1hr": 10.0, "so2": "", "ch4": "", "fccs_number": "", "consumption_duff": "", "nox": "", "moisture_100hr": 12.0, "grass": "", "snow_month": 5, "sf_server": "playground.dri.edu", "max_wind": 6.0}]}

You can pipe the output of ```bsp-csv2json``` directly into ```bsp```, as long
as you use the ingestions module, described below:

    bsp-csv2json -i fires.csv | bsp ingestion

Use the '-h' option to see more usage information for ```bsp-csv2json```.

#### Piping

As fire data flow through the modules within ```bsp```, the modules add to the
data without modifying what's already defined (with the exception of the
ingestion module, described below, which does modify the data).  Modules
further downstream generally work with data produced by upstream modules,
which means that order of module execution does matter.

You can run fires through a series of modules, capture the output, and
then run the output back into ```bsp``` as long as you start with a module
that doesn't depend on data updates made by any module not yet run.  For
example, assume that you start with the following fire data:

    {
        "fire_information": [
            {
                "id": "SF11C14225236095807750",
                "event_of": {
                    "id": "SF11E826544",
                    "name": "Natural Fire near Snoqualmie Pass, WA"
                },
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
                    "ecoregion": "southern",
                    "timezone": "-09:00"
                },
                "growth": [
                    {
                        "pct": 100,
                        "start": "20150120",
                        "end": "20150120"
                    }
                ]
            }
        ]
    }

Assume that this data is in a file called fires.json, and that you run
it through the fuelbeds module, with the following:

    bsp -i fires.json fuelbeds

You would get the following output (which is the input json with the addition
of the 'fuelbeds' array in the fire object, plus 'processing' and 'summary'
fields):

    {
        "fire_information": [
            {
                "event_of": {
                    "id": "SF11E826544",
                    "name": "Natural Fire near Snoqualmie Pass, WA"
                },
                "fuelbeds": [
                    {
                        "fccs_id": "49",
                        "pct": 50.0
                    },
                    {
                        "fccs_id": "46",
                        "pct": 50.0
                    }
                ],
                "growth": [
                    {
                        "end": "20150120",
                        "pct": 100,
                        "start": "20150120"
                    }
                ],
                "id": "SF11C14225236095807750",
                "location": {
                    "area": 2398.94477979842,
                    "ecoregion": "southern",
                    "perimeter": {
                        "coordinates": [
                            [
                                [
                                    [
                                        -121.4522115,
                                        47.4316976
                                    ],
                                    [
                                        -121.3990506,
                                        47.4316976
                                    ],
                                    [
                                        -121.3990506,
                                        47.4099293
                                    ],
                                    [
                                        -121.4522115,
                                        47.4099293
                                    ],
                                    [
                                        -121.4522115,
                                        47.4316976
                                    ]
                                ]
                            ]
                        ],
                        "type": "MultiPolygon"
                    },
                    "timezone": "-09:00"
                }
            }
        ],
        "processing": [
            {
                "fccsmap_version": "0.1.7",
                "module": "bluesky.modules.fuelbeds",
                "version": "0.1.0"
            }
        ],
        "summary": {
            "fuelbeds": [
                {
                    "fccs_id": "46",
                    "pct": 50.0
                },
                {
                    "fccs_id": "49",
                    "pct": 50.0
                }
            ]
        }
    }


This output could be piped back into ```bsp``` and run through the consumption
module, like so:

    bsp -i fires.json fuelbeds | bsp consumption

yielding the following augmented output:

    {
        "fire_information": [
            {
                "event_of": {
                    "id": "SF11E826544",
                    "name": "Natural Fire near Snoqualmie Pass, WA"
                },
                "fuelbeds": [
                    {
                        "consumption": {
                            /* ...consumption output... */
                        },
                        "fccs_id": "49",
                        "pct": 50.0,
                        "fuel_loadings": {
                            /* ...fuel loadings... */
                        }
                    },
                    {
                        "consumption": {
                            /* ...consumption output... */
                        },
                        "fccs_id": "46",
                        "pct": 50.0,
                        "fuel_loadings": {
                            /* ...fuel loadings... */
                        }
                    }
                ],
                "growth": [
                    {
                        "end": "20150120",
                        "pct": 100,
                        "start": "20150120"
                    }
                ],
                "id": "SF11C14225236095807750",
                "location": {
                    "area": 2398.94477979842,
                    "ecoregion": "southern",
                    "perimeter": {
                        "coordinates": [
                            [
                                [
                                    [-121.4522115,47.4316976],
                                    [-121.3990506,47.4316976],
                                    [-121.3990506,47.4099293],
                                    [-121.4522115,47.4099293],
                                    [-121.4522115,47.4316976]
                                ]
                            ]
                        ],
                        "type": "MultiPolygon"
                    },
                    "timezone": "-09:00"
                }
            }
        ],
        "processing": [
            {
                "fccsmap_version": "0.1.7",
                "module": "bluesky.modules.fuelbeds",
                "version": "0.1.0"
            },
            {
                "consume_version": "4.1.2",
                "module": "bluesky.modules.consumption",
                "version": "0.1.0"
            }
        ],
        "summary": {
            "consumption": {
                /* ...summary consumption data... */
            },
            "fuelbeds": [
                {
                    "fccs_id": "46",
                    "pct": 50.0
                },
                {
                    "fccs_id": "49",
                    "pct": 50.0
                }
            ]
        }
    }


Though there would be no reason to do so in this situation, you could re-run
the fuelbeds module in the second pass throgh ```bsp```, like so:

    bsp -i fires.json fuelbeds | bsp fuelbeds consumption

The second pass through the fuelbeds module would reinitialize the fuelbeds
array created by the first pass through the module. After running through
consumption, you would get the same output as above.  Though this re-running
of the fuelbeds module is pointless in this example, there may be situations
where you'd like to re-run your data through a module without starting from
the beginning of the pipeline.

Here's an example that runs through comsumption, captures the output, then
runs the output back through consumption and on through emissions:

    bsp -i fires.json fuelbeds consumption -o fires-c.json
    cat fires-c.json | bsp consumption emissions > fires-e.json

```fires-c.json``` would contain the output listed above.  ```fires-e.json```
would contain this output, agumented with emissions data:

    {
        "fire_information": [
            {
                "event_of": {
                    "id": "SF11E826544",
                    "name": "Natural Fire near Snoqualmie Pass, WA"
                },
                "fuelbeds": [
                    {
                        "consumption": {
                            /* ...consumption output... */
                        },
                        "emissions": {
                            /* ...emissions output... */
                        },
                        "fccs_id": "49",
                        "pct": 50.0,
                        "fuel_loadings": {
                            /* ...fuel loadings... */
                        }
                    },
                    {
                        "consumption": {
                            /* ...consumption output... */
                        },
                        "emissions": {
                            /* ...emissions output... */
                        },
                        "fccs_id": "46",
                        "pct": 50.0,
                        "fuel_loadings": {
                            /* ...fuel loadings... */
                        }
                    }
                ],
                "growth": [
                    {
                        "end": "20150120",
                        "pct": 100,
                        "start": "20150120"
                    }
                ],
                "id": "SF11C14225236095807750",
                "location": {
                    "area": 2398.94477979842,
                    "ecoregion": "southern",
                    "perimeter": {
                        "coordinates": [
                            [
                                [
                                    [
                                        -121.4522115,
                                        47.4316976
                                    ],
                                    [
                                        -121.3990506,
                                        47.4316976
                                    ],
                                    [
                                        -121.3990506,
                                        47.4099293
                                    ],
                                    [
                                        -121.4522115,
                                        47.4099293
                                    ],
                                    [
                                        -121.4522115,
                                        47.4316976
                                    ]
                                ]
                            ]
                        ],
                        "type": "MultiPolygon"
                    },
                    "timezone": "-09:00"
                }
            }
        ],
        "processing": [
            {
                "fccsmap_version": "0.1.7",
                "module": "bluesky.modules.fuelbeds",
                "version": "0.1.0"
            },
            {
                "consume_version": "4.1.2",
                "module": "bluesky.modules.consumption",
                "version": "0.1.0"
            },
            {
                "consume_version": "4.1.2",
                "module": "bluesky.modules.consumption",
                "version": "0.1.0"
            },
            {
                "ef_set": "feps",
                "emitcalc_version": "0.3.2",
                "module": "bluesky.modules.emissions",
                "version": "0.1.0"
            }
        ],
        "summary": {
            "consumption": {
                /* ...summary consumption data... */
            },
            "emissions": {
                /* ...summary emissions data... */
            },
            "fuelbeds": [
                {
                    "fccs_id": "46",
                    "pct": 50.0
                },
                {
                    "fccs_id": "49",
                    "pct": 50.0
                }
            ]
        }
    }


##### Pretty-Printing JSON Output

To get indented and formated output like the above examples, try
[json.tool](https://docs.python.org/2.7/library/json.html).  It will
work only if you let the results go to STDOUT.  For example:

    bsp -i fires.json fuelbeds | python -m json.tool

#### Ingestion

For each fire, the ingestion module does the following:

 1. Moves the raw fire object to the 'parsed_input' array under the ingestion module's processing record -- In so doing, it keeps a record of the initial data, which will remain untouched.
 2. Copies recognized fields back into a fire object under the 'fire_information' array -- In this step, it looks for nested fields both in the correctly nested
locations as well as in the root fire object.
 3. Validates the fire data -- For example, if there is no location information, or if the nested location is insufficient, a ```ValueError``` is raised.

Some proposed but not yet implemented tasks:

 1. Copy custom fields up to the top level -- i.e. user-identified fields that should also be copied from the input data up to the top level can be configured.
 2. Set defaults -- There are no hardcoded defaults, but defaults could be configured
 3. Sets derived fields -- There's no current need for this, but an example would be to derive

##### Ingestion example

###### Example 1

Assume you start with the following data:

    {
        "fire_information": [
            {
                    "location": {
                        "latitude": 47.4316976,
                        "longitude": -121.3990506
                    },
                    "area": 200,
                    "timezone": "-09:00",
                    "name": "event name",
                    "event_id": "jfkhfdskj"
            }
        ]
    }

It would become:

    {
        "fire_information": [
            {
                "event_of": {
                    "id": "jfkhfdskj",
                    "name": "event name"
                },
                "id": "7e10cd4a",
                "location": {
                    "area": 200,
                    "latitude": 47.4316976,
                    "longitude": -121.3990506,
                    "timezone": "-09:00"
                }
            }
        ],
        "processing": [
            {
                "module": "bluesky.modules.ingestion",
                "parsed_input": [
                    {
                        "area": 200,
                        "event_id": "jfkhfdskj",
                        "id": "7e10cd4a",
                        "location": {
                            "latitude": 47.4316976,
                            "longitude": -121.3990506
                        },
                        "name": "event name",
                        "timezone": "-09:00"
                    }
                ],
                "version": "0.1.0"
            }
        ]
    }

Notice:
 - The 'raw' input under processing isn't purely raw, as the fire has been assigned an id ("4b94a511").  This is the one auto-generated field that you will find under 'processing' > 'parsed_input'.  If the fire object already contains an id, it will be used, in which case the raw fire input is in fact exactly what the user input.
 - The 'area' and 'timezone' keys are initially defined at the top level, but, after ingestion, are under the 'location' object.  Similarly, 'name' gets moved under 'event_of' (since names apply to fire events, not to fire locations).
 - The 'event_id' key gets moved under 'event_of' and is renamed 'id'.

###### Example 2

As a fuller example, starting with the following input data (which we'll
assume is in fires.json):

    {
        "fire_information": [
            {
                "id": "SF11C14225236095807750",
                "event_of": {
                    "id": "SF11E826544",
                    "name": "Natural Fire near Snoqualmie Pass, WA"
                },
                "location": {
                    "latitude": 47.4316976,
                    "longitude": -121.3990506,
                    "area": 200,
                    "timezone": "-09:00",
                    "foo": "bar"
                },
                "ecoregion": "southern",
                "growth": [
                    {
                        "pct": 100.0,
                        "start": "20150120",
                        "end": "20150120"
                    }
                ],
                "bar": 123
            }
        ]
    }

if you pass this data through ingestion:

    bsp -i fires.json ingestion

you'll end up with this:

    {
        "fire_information": [
            {
                "event_of": {
                    "id": "SF11E826544",
                    "name": "Natural Fire near Snoqualmie Pass, WA"
                },
                "growth": [
                    {
                        "end": "20150120",
                        "pct": 100.0,
                        "start": "20150120"
                    }
                ],
                "id": "SF11C14225236095807750",
                "location": {
                    "area": 200,
                    "ecoregion": "southern",
                    "latitude": 47.4316976,
                    "longitude": -121.3990506,
                    "timezone": "-09:00"
                }
            }
        ],
        "processing": [
            {
                "module": "bluesky.modules.ingestion",
                "parsed_input": [
                    {
                        "bar": 123,
                        "ecoregion": "southern",
                        "event_of": {
                            "id": "SF11E826544",
                            "name": "Natural Fire near Snoqualmie Pass, WA"
                        },
                        "growth": [
                            {
                                "end": "20150120",
                                "pct": 100.0,
                                "start": "20150120"
                            }
                        ],
                        "id": "SF11C14225236095807750",
                        "location": {
                            "area": 200,
                            "foo": "bar",
                            "latitude": 47.4316976,
                            "longitude": -121.3990506,
                            "timezone": "-09:00"
                        }
                    }
                ],
                "version": "0.1.0"
            }
        ]
    }

Notice:
 - "foo" and "bar" were ignored (though left in the recorded raw input)
 - "ecoregion" got moved under "location"

#### Notes About Input Fire Data

##### Perimeter vs. Lat + Lng + Area

One thing to note about the fire data is that the location can be specified by
a single lat/lng pair with area (assumed to be acres) or by perimeter polygon
data. The following is an example of the former:

    {
        "fire_information": [
            {
                "id": "SF11C14225236095807750",
                "event_of": {
                    "id": "SF11E826544",
                    "name": "Natural Fire near Snoqualmie Pass, WA"
                },
                "location": {
                    "latitude": 47.123,
                    "longitude": -120.379,
                    "area": 200,
                    "ecoregion": "southern"
                },
                "growth": [
                    {
                        "pct": 100,
                        "start": "20150120",
                        "end": "20150120"
                    }
                ]
            }
        ]
    }

while the following is an example of the latter:

    {
        "fire_information": [
            {
                "id": "SF11C14225236095807750",
                "event_of": {
                    "id": "SF11E826544",
                    "name": "Natural Fire near Snoqualmie Pass, WA"
                },
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
                },
                "growth": [
                    {
                        "pct": 100,
                        "start": "20150120",
                        "end": "20150120"
                    }
                ]
            }
        ]
    }

### Web APIs

See [BlueSky Web](bluesky/web/README.md)

## Required and Optional Fields

### 'fire_information' Fields

The top level 'fire_information' object has data added to it as it moves through
the pipeline of modules.  Each module has its own set of required and optional
fields that it uses, so that the set of data needed for each fire depends
on the modules to be run. Generally, the further you are along the pipeline
of modules, the more data you need.  (Note, however, that some data required
by earlier modules can be dropped when you pipe the fire data into downstream
modules.)

##### fuelbeds

 - ...

##### consumption

 - ***'fire_information' > 'location' > 'ecoregion'*** -- *optional*
 - ***'fire_information' > 'type'*** -- *optional* -- fire type (ex. 'rx' or 'natural')

##### emissions

 - ...

##### localmet

 - ...

##### timeprofiling

 - ***'fire_information' > 'growth'*** -- *required* -- array of growth objects, each
  containing 'start', 'end', and 'pct'; if only one object,
  pct can be omitted and is assumed to be 100.0

##### plumerise

 - ...

##### dispersion

 - ...

##### visualization

 - ...

##### export

 - ...

### 'config' Fields

The 'config' object has sub-objects specific to the modules to be run, as
well as top level fields that apply to multiple modules. As with
the fire data, each module has its own set of required and optional fields.


##### fuelbeds

 - ...

##### consumption

 - ...

##### emissions

 - ***'config' > 'efs'*** -- *optional* -- emissions factors set; 'urbanski' or 'feps'; default 'feps'
 - ***'config' > 'species'*** -- *optional* -- whitelist of species to compute emissions levels for

##### localmet

 - ...

##### timeprofiling

 - ***'config' > 'start'*** -- *required* -- modeling start time (ex. "20150121T000000Z")
 - ***'config' > 'end'*** -- *required* -- modeling end time (ex. "20150123T000000Z")
 - ***'config' > 'timeprofiling' > 'hourly_fractions' *** -- *optional* --


##### plumerise

 - ...

##### dispersion

 - ***'config' > 'start'*** -- *required* -- modeling start time (ex. "20150121T000000Z")
 - ***'config' > 'end'*** -- *required* -- modeling end time (ex. "20150123T000000Z")
 - ***'config' > 'met_domain'*** -- *required* -- met domain (ex. "PNW-4km")
 - ***'config' > 'dispersion' > 'module'*** -- *optional* -- dispersion module; defaults to "hysplit"

##### visualization

 - ...

##### export

 - ...

## Vagrant

If you'd like to use vagrant to spin up virtual machines for running BlueSky
Pipeline, look in the
[vagrant/](https://github.com/pnwairfire/bluesky/tree/master/vagrant)
directory, which contains Vagrantfiles and provisioning scripts.

### Get Vagrant + Virtualization Software

[Vagrant](http://www.vagrantup.com/downloads.html)

Virtualization software options:

 - [VirtualBox](https://www.virtualbox.org/wiki/Downloads)
 - [VMWare](https://my.vmware.com/web/vmware/info/slug/desktop_end_user_computing/vmware_fusion/6_0)
 - [Other options](https://www.google.com/?gws_rd=ssl#q=Virtualization+software)

Note that the one Vagrantfile currently in the repo is configured to use virtualbox.

### Basic usage

First, if you haven't already, clone this repo and cd into one of the
VM-specific subdirectories under
[vagrant/](https://github.com/pnwairfire/bluesky/tree/master/vagrant):

    git clone https://github.com/pnwairfire/bluesky.git
    cd airfire-bluesky-framework/vagrant/<one-of-the-VMs>/

To spin it up and ssh into the vm, use the following:

    vagrant up
    vagrant provision
    vagrant ssh

#### Provisioning

Note that ```vagrant up``` should provision, but it for some reason
doesn't always do so.  Also note that ```vagrant provision``` may
give the following error

    SSH authentication failed! This is typically caused by the public/private
    keypair for the SSH user not being properly set on the guest VM. Please
    verify that the guest VM is setup with the proper public key, and that
    the private key path for Vagrant is setup properly as well.

If it does, add your key to the vagrant user's authorized_keys file
and then try provisioning again. Note that the default password for
the 'vagrant' user is 'vagrant'. You'll need since your key isn't
yet in authorized_keys.

    vagrant ssh
    echo your_public_key >> .ssh/authorized_keys
    exit
    vagrant provision

If the provisioning fails to install bsp with an error related
to lxml, ssh into the box, manually reinstall the xml libs, and
try installing bsp:

    vagrant ssh
    sudo apt-get  install libxml2-dev libxslt1-dev
    sudo pip install --no-binary gdal --trusted-host pypi.smoke.airfire.org -i http://pypi.smoke.airfire.org/simple bluesky

#### ssh / scp

Besides using ```vagrant ssh```, You can ssh/scp directly to the vm.
The host and port depend on what's in the Vagrantfile and what the
provider (VirtualBox, VMWare, etc) overrides.
You'll see the ssh address when you execute 'vagrant up'.  It will
look like the following in the output:

    default: SSH address: 127.0.0.1:2222

#### Running bsp on vagrant vm

Now you're ready to run bsp:

    vagrant ssh
    echo '{
        "fire_information": [
            {
                "id": "SF11C14225236095807750",
                "event_of": {
                    "id": "SF11E826544",
                    "name": "Natural Fire near Snoqualmie Pass, WA"
                },
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
                },
                "growth": [
                    {
                        "pct": 100,
                        "start": "20150120",
                        "end": "20150120"
                    }
                ]
            }
        ]
    }' > fires.json
    bsp -i fires.json ingestion fuelbeds

## Bluesky web API

One component of the bluesky package is a tornado web service, wrapping bsp,
that can be started by simply running ```bsp-web```.

### Usage

For API usage, see it's separate [README.md](./bluesky/web/README.md).

### Fabric

For the convenience of those wishing to run the web service on a remove server,
the bluesky git repo contains a fabfile defining tasks for setting up,
deploying to, and restarting the service on a remote server.

To see what tasks are available, clone the repo, cd into repo, and run

    git clone https://github.com/pnwairfire/bluesky.git
    cd bluesky
    BLUESKYWEB_SERVERS=username@hostname fab -l

(The 'BLUESKYWEB_SERVERS=username@hostname' is needed because it's used to set
the role definitions, which are be done at the module scope.)

To see documentation for a specific task, use the '-d' option. E.g.:

    BLUESKYWEB_SERVERS=username@hostname fab -d deploy


An example with two remote servers

    BLUESKYWEB_SERVERS=username-a@hostname-a,username-b@hostname-b fab setup
    BLUESKYWEB_SERVERS=username-a@hostname-a,username-b@hostname-b fab deploy

Note that the deploy task takes care of restarting.
