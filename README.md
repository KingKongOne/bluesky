# BlueSky Pipeline

BlueSky Framework rearchitected as a pipeable collection of standalone modules.

## Development

### Install Dependencies

Run the following to install dependencies:

    pip install -r requirements.txt

Run the following for installing development dependencies (such as for running
tests):

    pip install -r dev-requirements.txt

### Setup Environment

This project contains a single package, ```bluesky```. To import bluesky
package in development, you'll have to add the repo root directory to the
search path. The ```./bin/bsp``` script does this automatically, if
necessary.

## Running tests

Use pytest:

    py.test
    py.test test/bluesky/path/to/some_tests.py

You can also use the ```--collect-only``` option to see a list of all tests.

    py.test --collect-only

See [pytest](http://pytest.org/latest/getting-started.html#getstarted) for more information about using pytest.

## Installation

The repo is currently private. So, you need to be on the FERA bitbucket team
to install from the bitbucket repo.

### Installing With pip

First, install pip:

    sudo apt-get install python-pip

Then, to install, for example, v0.1.0, use the following:

    sudo pip install git+ssh://git@bitbucket.org/fera/airfire-bluesky-pipeline@v0.1.0

Or, if using the bluesky package in another project, add it to your project's
requirements.txt:

    git+ssh://git@bitbucket.org/fera/airfire-bluesky-pipeline@v0.1.0

If you get an error like    ```AttributeError: 'NoneType' object has no
attribute 'skip_requirements_regex```, it means that you need in upgrade pip.
One way to do so is with the following:

    pip install --upgrade pip

## Usage:

### bsp

bsp is the main BlueSky executable.  It can be used for any combination of
the following:

 - to translate CSV-formatted fire data to JSON, and vice versa
 - to filter a set of fires by country code
 - **to run BlueSky modules (consumption, emissions, etc.) on fire data**

#### Getting Help

Use the ```-h``` flag for help:

    $ ./bin/bsp -h
    Usage: bsp [options] [<module> ...]

    Options:
      -h, --help            show this help message and exit
      -l, --list-modules    lists modules available to use in pipeline; order
                            matters
      ...

Use the ```-l``` flag to see available BlueSky modules:

    $ ./bin/bsp -l

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

    $ ./bsp -i /path/to/input/fires/json/file.json -o /path/to/output/modified/fires/json/file.json fuelbeds consumption

Example of piping in and redirecting output to file

    $ cat /path/to/input/fires/json/file.json | ./bsp > /path/to/output/modified/fires/json/file.json fuelbeds

Example of redirecting input from and outputing to file:

    $ ./bin/bsp fuelbeds consumption emissions < /path/to/input/fires/json/file.json > /path/to/output/modified/fires/json/file.json

Example of redirecting input from file and outputing to stdout

    $ ./bin/bsp fuelbeds fuelloading < /path/to/input/fires/json/file.json

```bsp``` supports inputting and outputing both json and csv formatted fire data.
(The default expected format is JSON.) The following example reads in CSV fire
data from file, filters out all but USA filures, and outputs JSON formated data
to stdout

    $ ./bin/bsp -i /path/to/input/fires/csv/file.csv --input-format=CSV -w USA fuelbeds consumption

#### Piping

As fire data flow through modules within ```bsp```, the modules add to the
data without modified what's already defined.  Modules further downstream
generally work with data produced by upstream modules, which meands that
order of module execution does matter.

You can run fires through a serious of modules, capture the output, and
then run the output back into ```bsp``` as long as you start with a module
that doesn't depend on the data having been processed by another module
that hasn't yet been run.  For example, assume you start with the following
fire data:

    [
        {
            "id": "SF11C14225236095807750",
            "name": "Some Rx Fire in the Bahamas with consumption inputs provided",
            "type": "Rx",
            "latitude": 25.041,
            "longitude": -77.379,
            "area": 99.9999997516,
            "start": "20150120T000000Z",
            "ecoregion": "western",
            "fuel_moisture_1000hr_pct": 50,
            "fuel_moisture_10hr_pct": 60,
            "fuel_moisture_duff_pct": 45,
            "end": "",
            "county": "",
            "country": "BS",
            "slope": 10.0,
            "windspeed": 8,
            "canopy_consumption_pct": 2,
            "shrub_blackened_pct": 45,
            "fm_type": "ADJ-Th",
            "days_since_rain": 4,
            "length_of_ignition": 23,
            "output_units": "tons",
            "max_humid": 80.0,
            "elevation": 0.0,
            "timezone": -5.0,
            "event_id": "SF11E826544",
            "state": "KS"
        }
    ]

Assume this data is in a file called fires.json, and you run it through the
fuelbeds module, with the following:

    ./bin/bsp -i fires.json fuelbeds

You would get the folloing output (which is the input json with the addition
of 'fuelbeds' array):

    [{
        "slope": 10.0,
        "max_humid": 80.0,
        "elevation": 0.0,
        "fuelbeds": [{
            "fccs_id": 16,
            "pct": 100
        }],
        "county": "",
        "windspeed": 8,
        "fm_type": "ADJ-Th",
        "shrub_blackened_pct": 45,
        "timezone": -5.0,
        "ecoregion": "western",
        "id": "SF11C14225236095807750",
        "canopy_consumption_pct": 2,
        "fuel_moisture_10hr_pct": 60,
        "end": "",
        "name": "Some Rx Fire in the Bahamas with consumption inputs provided",
        "area": 99.9999997516,
        "event_id": "SF11E826544",
        "country": "BS",
        "days_since_rain": 4,
        "longitude": -77.379,
        "output_units": "tons",
        "start": "20150120T000000Z",
        "state": "KS",
        "fuel_moisture_duff_pct": 45,
        "length_of_ignition": 23,
        "fuel_moisture_1000hr_pct": 50,
        "latitude": 25.041,
        "type": "Rx"
    }]

This output could be piped back into ```bsp``` and run through the consumption
module, like so:

    ./bin/bsp -i fires.json fuelbeds | ./bin/bsp consumption

yielding the following augmented output:

    [{
        "slope": 10.0,
        "max_humid": 80.0,
        "elevation": 0.0,
        "fuelbeds": [{
            "fccs_id": 16,
            "consumption": {
                "litter-lichen-moss": {
                    "litter": {
                        "smoldering": [0.26488],
                        "total": [2.6488],
                        "flaming": [2.3839200000000003],
                        "residual": [0.0]
                    },
                    "lichen": {
                        "smoldering": [0.0],
                        "total": [0.0],
                        "flaming": [0.0],
                        "residual": [0.0]
                    },
                    "moss": {
                        "smoldering": [0.0],
                        "total": [0.0],
                        "flaming": [0.0],
                        "residual": [0.0]
                    }
                },
                /* ... (there would be more fuel categories fields here) ... */
                "summary": {
                    "litter-lichen-moss": {
                        "smoldering": [0.26488],
                        "total": [2.6488],
                        "flaming": [2.3839200000000003],
                        "residual": [0.0]
                    },
                    /* ... (there would be more fuel categories fields here) ... */
                    "total": {
                        "smoldering": [2.411645203171406],
                        "total": [10.843917000136159],
                        "flaming": [6.9149277822157575],
                        "residual": [1.5173440147489938]
                    }
                }
            },
            "pct": 100
        }],
        "county": "",
        "windspeed": 8,
        "fm_type": "ADJ-Th",
        "shrub_blackened_pct": 45,
        "timezone": -5.0,
        "ecoregion": "western",
        "id": "SF11C14225236095807750",
        "canopy_consumption_pct": 2,
        "fuel_moisture_10hr_pct": 60,
        "end": "",
        "name": "Some Rx Fire in the Bahamas with consumption inputs provided",
        "area": 99.9999997516,
        "event_id": "SF11E826544",
        "country": "BS",
        "days_since_rain": 4,
        "longitude": -77.379,
        "output_units": "tons",
        "start": "20150120T000000Z",
        "state": "KS",
        "fuel_moisture_duff_pct": 45,
        "length_of_ignition": 23,
        "fuel_moisture_1000hr_pct": 50,
        "latitude": 25.041,
        "type": "Rx"
    }]

Though there would be no reason to do so in this situation, you could re-run
the fuelbeds module in the second pass throgh ```bsp```, like so:

    ./bin/bsp -i fires.json fuelbeds | ./bin/bsp fuelbeds consumption

The second pass through the fuelbeds module would reinitialize the fuelbeds
array array created by the first pass through the module. After running
through consumption, you get the same output as above.  Though this re-running
of the fuelbeds module is pointless in this example, there may be situations
where you'd like to re-run your data through a module without starting from
the beginning of the pipeline.

Here's an example that runs through comsumption, captures the output, then
runs the output back through consumption and on through emissions:

    ./bin/bsp -i fires.json fuelbeds consumption -o fires-c.json
    cat fires-c.json | ./bin/bsp consumption emissions > fires-e.json

```fires-c.json``` would contain the output listed above.  ```fires-e.json```
would contain this output, agumented with emissions data:

    [{
        "slope": 10.0,
        "max_humid": 80.0,
        "elevation": 0.0,
        "fuelbeds": [{
            "fccs_id": 16,
            "pct": 100,
            "consumption": {
                "litter-lichen-moss": {
                    "litter": {
                        "smoldering": [0.26488],
                        "total": [2.6488],
                        "flaming": [2.3839200000000003],
                        "residual": [0.0]
                    },
                    "lichen": {
                        "smoldering": [0.0],
                        "total": [0.0],
                        "flaming": [0.0],
                        "residual": [0.0]
                    },
                    "moss": {
                        "smoldering": [0.0],
                        "total": [0.0],
                        "flaming": [0.0],
                        "residual": [0.0]
                    }
                },
                /* ... (there would be more fuel categories fields here) ... */
                "summary": {
                    "litter-lichen-moss": {
                        "smoldering": [0.26488],
                        "total": [2.6488],
                        "flaming": [2.3839200000000003],
                        "residual": [0.0]
                    },
                    /* ... (there would be more fuel categories fields here) ... */
                    "total": {
                        "smoldering": [2.411645203171406],
                        "total": [10.843917000136159],
                        "flaming": [6.9149277822157575],
                        "residual": [1.5173440147489938]
                    }
                }
            },
            "emissions": {
                "litter-lichen-moss": {
                    "litter": {
                        "smoldering": {
                            "CH3CH2OH": [0.16952320000000001],
                            "CH3COOH": [2.3632593600000003],
                            "CH3OH": [1.0918353599999999],
                            "C2H8N2": [0.02277968],
                            "isomer2_C9H8O": [0.016422559999999999],
                            "isomer2_C6H8": [0.0068868799999999997],
                            "C9H12": [0.010595200000000001],
                            /* ... (there would be more emissions data here) ... */
                        },
                        "flaming": {
                            "CH3CH2OH": [1.5257088000000003],
                            "CH3COOH": [21.269334240000003],
                            "CH3OH": [9.8265182400000004],
                            "C2H8N2": [0.20501712],
                            "isomer2_C9H8O": [0.14780304000000002],
                            "isomer2_C6H8": [0.061981920000000003],
                            "C9H12": [0.095356800000000019],
                            /* ... (there would be more emissions data here) ... */
                        }
                    },
                    "lichen": {
                        "smoldering": {
                            /* ... (there would be emissions data here) ... */
                        },
                        "flaming": {
                            /* ... (there would be emissions data here) ... */
                        }
                    },
                    "moss": {
                        "smoldering": {
                            /* ... (there would be emissions data here) ... */
                        },
                        "flaming": {
                            /* ... (there would be emissions data here) ... */
                        }
                    }
                },
                /* ... (there would be more fuel categories fields here) ... */
                "summary": {
                    "litter-lichen-moss": {
                        "smoldering": {
                            "CH3CH2OH": [0.16952320000000001],
                            "CH3COOH": [2.3632593600000003],
                            "CH3OH": [1.0918353599999999],
                            "C2H8N2": [0.02277968],
                            "isomer2_C9H8O": [0.016422559999999999],
                            "isomer2_C6H8": [0.0068868799999999997],
                            "C9H12": [0.010595200000000001],
                            /* ... (there would be emissions data here) ... */
                        },
                        "flaming": {
                            "CH3CH2OH": [1.5257088000000003],
                            "CH3COOH": [21.269334240000003],
                            "CH3OH": [9.8265182400000004],
                            "C2H8N2": [0.20501712],
                            "isomer2_C9H8O": [0.14780304000000002],
                            "isomer2_C6H8": [0.061981920000000003],
                            "C9H12": [0.095356800000000019],
                            /* ... (there would be emissions data here) ... */
                        }
                    },
                    /* ... (there would be more fuel categories fields here) ... */
                    "total": {
                        "smoldering": {
                            "CH3CH2OH": [1.5434529300296997],
                            "CH3COOH": [21.516698502695284],
                            "CH3OH": [9.9408015274725354],
                            "C2H8N2": [0.2074014874727409],
                            "isomer2_C9H8O": [0.14952200259662718],
                            "isomer2_C6H8": [0.062702775282456547],
                            "C9H12": [0.096465808126856234],
                            /* ... (there would be emissions data here) ... */
                        },
                        "flaming": {
                            "CH3CH2OH": [4.4255537806180847],
                            "CH3COOH": [61.694985672928993],
                            "CH3OH": [28.503332318293353],
                            "C2H8N2": [0.5946837892705551],
                            "isomer2_C9H8O": [0.42872552249737694],
                            "isomer2_C6H8": [0.17978812233760968],
                            "C9H12": [0.27659711128863029],
                            /* ... (there would be emissions data here) ... */
                        }
                    }
                }
            }
        }],
        "county": "",
        "windspeed": 8,
        "fm_type": "ADJ-Th",
        "shrub_blackened_pct": 45,
        "timezone": -5.0,
        "ecoregion": "western",
        "id": "SF11C14225236095807750",
        "canopy_consumption_pct": 2,
        "fuel_moisture_10hr_pct": 60,
        "end": "",
        "name": "Some Rx Fire in the Bahamas with consumption inputs provided",
        "area": 99.9999997516,
        "event_id": "SF11E826544",
        "country": "BS",
        "days_since_rain": 4,
        "longitude": -77.379,
        "output_units": "tons",
        "start": "20150120T000000Z",
        "state": "KS",
        "fuel_moisture_duff_pct": 45,
        "length_of_ignition": 23,
        "fuel_moisture_1000hr_pct": 50,
        "latitude": 25.041,
        "type": "Rx"
    }]
