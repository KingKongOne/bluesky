import os

TOP_LEVEL = {
    "skip_failed_fires": False,
    "skip_failed_sources": False,
    "statuslogging": {
        "enabled": False,
        "api_endpoint": None,
        "api_key": None,
        "api_secret": None,
        "process": None,
        "domain": None
    }
}

_HYSPLIT_BDYFILES_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    'dispersers/hysplit/bdyfiles')
MODULE_LEVEL = {
    "load": {
        "sources": []
        # Each source has some subset of the following defined, but
        # there are no defaults to be defined here
        #  'name'
        #  'format'
        #  'type'
        #  'date_time'
        #  'file'*** -- *required* for each file type source-- file containing fire data; e.g. '/path/to/fires.csv'; may contain format codes that conform to the C standard (e.g. '%Y' for four digit year, '%m' for zero-padded month, etc.)
        #  'events_file'*** -- *optional* for each file type source-- file containing fire events data; e.g. '/path/to/fire_events.csv'; may contain format codes that conform to the C standard (e.g. '%Y' for four digit year, '%m' for zero-padded month, etc.)
        #  "wait": None, #{"strategy": None,"time": None,"max_attempts": None}
    },
    "ingestion": {
        "keep_emissions": False,
        "keep_heat": False
    },
    "merge": {
        "skip_failures": False
    },
    "filter": {
        "skip_failures": False
        # The following filter-specific sub-dicts have to be commented out
        # in the defaults, since each one's presence/absence determines whether
        # or not the filter is run.  There are no default values anywa
        # for the filter-specific options
        #   "country": {"whitelist": None, "blacklist": None},
        #   "area": {"min": None, "max": None}
        #   "location": {"boundary": {
        #     "sw": { "lat":None, "lng": None},
        #     "ne": { "lat":None, "lng": None}}}
    },
    "splitgrowth": {
        "record_original_growth": False
    },
    "fuelbeds": {
        # The following defaults are defined in the fccsmap package,
        # so they could be removed from here
        "fccs_version": "2",
        "is_alaska": False,
        "ignored_percent_resampling_threshold": 99.9,
        "ignored_fuelbeds": ['0', '900'],
        "no_sampling": False,

        # The following defaults are defined in the fccsmap package
        # and are based on the location of the pacakge in the file
        # system. So, let fccsmap set defaults
        # "fccs_fuelload_file": None,
        # "fccs_fuelload_param": None,
        # "fccs_fuelload_grid_resolution": None,

        # the following defaults are *not* defined in fccsmap package
        "truncation_percentage_threshold": 90.0,
        "truncation_count_threshold": ; 5
    },
    "consumption": {
        "fuel_loadings": None,
        "default_ecoregion": None,
        "ecoregion_lookup_implemenation": "ogr"
    },
    "emissions": {
        # Note that 'efs' is deprecated, and so is not listed here
        "model": "feps",
        "include_emissions_details": False,
        "species": [],
        "fuel_loadings": None
    },
    "findmetdata": {
        "met_root_dir": None,
        # We need to default time_window as None, since it will be used
        # if it is defined, even if the first and last hours are None
        "time_window": None, # {"first_hour": None,"last_hour": None}

        # We need to default wait to None, since being set to None
        # or empty dict in the config indicates that we don't want
        # to wait (which is the default behavior)
        "wait": None, # {"strategy": None,"time": None,"max_attempts": None},

        "met_format": "arl",
        "arl": {
            # The following two defaults are dfined in the met package
            # TODO: should we comment them out here and leave "arl"
            #    sub-config as an empty dict
            "index_filename_pattern": "arl12hrindex.csv",
            "max_days_out": 4
        }
    },
    "localmet": {
        # The following default is defined in the met package,
        # so we won't define it here
        # "time_step": 1
    },
    "timeprofiling": {
        "hourly_fractions": None
    },

    "plumerising": {
        "model": "feps",
        "feps": {
            "working_dir": None
            # The following defaults are defined in the plumerise
            # package, so we won't set them here
            # "feps_weather_binary": "feps_weather",
            # "feps_plumerise_binary": "feps_plumerise",
            # "plume_top_behavior": "auto",
        },
        "sev": {
            # The following defaults are defined in the plumerise
            # package, so we won't set them here
            # "alpha": 0.24
            # "beta": 170
            # "ref_power": 1e6
            # "gamma": 0.35
            # "delta": 0.6
            # "ref_n": 2.5e-4
            # "gravity": 9.8
            # "plume_bottom_over_top": 0.5
        }
    },
    "extrafiles": {
        "sets": [],
        "dest_dir": None,
        "emissionscsv": {
            "filename": None
        }
        "firescsvs": {
            "fire_locations_filename": "fire_locations.csv",
            "fire_events_filename": "fire_events.csv"

        }
    },
    "dispersion": {
        "model": "hysplit",
        "start": None,
        "num_hours": None,
        "output_dir": None,
        "working_dir": None,
        "handle_existing": "fail",
        "hsyplit": {
            "skip_invalid_fires": False,

            # NOTE: executables are no longer configurable.  It is assumed that any
            # executable upon which hysplit depends is in a directory in the search path.
            # This is a security measure for when hysplit is executed via web requests.

            ## Grid

            # Note about the grid:  There are three ways to specify the dispersion grid.
            # If USER_DEFINED_GRID is set to true, hysplit will expect BlueSky framework's
            # user defined grid settings ('CENTER_LATITUDE', 'CENTER_LONGITUDE',
            # 'WIDTH_LONGITUDE', 'HEIGHT_LATITUDE', 'SPACING_LONGITUDE', and
            # 'SPACING_LONGITUDE').  Otherwise, it will look in 'config' > 'dispersion' >
            # 'hysplit' > 'grid' for 'boundary', 'spacing', and 'domain' fields.  If not
            # defined, it will look for 'boundary', 'spacing', and 'domain' in the top level
            # 'met' object.

            # User defined concentration grid option
            "USER_DEFINED_GRID": False,
            "CENTER_LATITUDE": None,
            "CENTER_LONGITUDE": None,
            "WIDTH_LONGITUDE": None,
            "HEIGHT_LATITUDE": None,
            # *required* if either COMPUTE_GRID or USER_DEFINED_GRID is true
            "SPACING_LONGITUDE": None,
            "SPACING_LATITUDE": None,

            # There are no default 'grid' parameter, and the presence/absence
            # of a grid definition is used in the logic in the code.  So,
            # leave it commented out
            #"grid": {
            #    "spacing": None,
            #    "domain": None,
            #    "boundary": {
            #     "sw": { "lat":None, "lng": None},
            #     "ne": { "lat":None, "lng": None}}
            #}

            # computing grid around fire
            "COMPUTE_GRID": False, # Program to convert raw HYSPLIT output to netCDF
            "GRID_LENGTH": 2000, # km

            # Optimize (i.e. decrease) concentration grid resolution based on number of fires
            "OPTIMIZE_GRID_RESOLUTION": = False,
            "MAX_SPACING_LONGITUDE": = 0.50,
            "MAX_SPACING_LATITUDE": = 0.50,

            ## Resource Files

            # Ancillary data files (note: HYSPLIT4.9 balks if it can't find ASCDATA.CFG)
            #  The code will default to using
            "ASCDATA_FILE": os.path.join(_HYSPLIT_BDYFILES_PATH, 'ASCDATA.CFG'),
            "LANDUSE_FILE": os.path.join(_HYSPLIT_BDYFILES_PATH, 'LANDUSE.ASC'),
            "ROUGLEN_FILE": os.path.join(_HYSPLIT_BDYFILES_PATH, 'ROUGLEN.ASC'),


            ## Other

            "CONVERT_HYSPLIT2NETCDF": True,
            "output_file_name": "hysplit_conc.nc",

            "SMOLDER_HEIGHT": 10.0,

            # Height in meters of the top of the model domain
            "TOP_OF_MODEL_DOMAIN": 30000.0,

            # List of vertical levels for output sampling grid
            "VERTICAL_LEVELS": [100],

            # Factor for reducing the number of vertical emission levels
            "VERTICAL_EMISLEVELS_REDUCTION_FACTOR": 1,

            # Method of vertical motion calculation in HYSPLIT
            # Choices: DATA, ISOB, ISEN, DENS, SIGMA, DIVERG, ETA
            "VERTICAL_METHOD": "DATA",

            ## HYSPLIT Setup variables

            # Location of particle initialization input files
            "DISPERSION_FOLDER": "./input/dispersion",

            # conversion modules
            #    0 - none
            #    1 - matrix
            #    2 - 10% / hour
            #    3 - PM10 dust storm simulation
            #    4 - Set concentration grid identical to the meteorology grid (not in GUI)
            #    5 - Deposition Probability method
            #    6 - Puff to Particle conversion (not in GUI)
            #    7 - Surface water pollutant transport
            "ICHEM": 0,

            "FIRE_INTERVALS": [0, 100, 200, 500, 1000],

            # name of the particle initialization input file
            # NOTE: must be limited to 80 chars max (i think, rcs)
            "PARINIT": "./input/dispersion/PARINIT",

            "NINIT": 0
            # Stop processing if no particle initialization file is found and NINIT != 0
            "STOP_IF_NO_PARINIT": True,

            # Create a particle initialization input file
            "MAKE_INIT_FILE": False,

            # name of the particle initialization output file
            # NOTES: must be limited to 80 chars max (i think, rcs)
            #        also, MPI runs will append a .NNN at the end
            #        based on the CPU number. subsequent restarts must
            #        use the same number of CPUs as the original that
            #        created the dump files. code will warn if there
            #        are few files than CPUs but will ignore files
            #        for cases when more files than CPUs.
            "PARDUMP": './input/dispersion/PARDUMP',

            # Number of hours from the start of the simulation to write the particle
            # initialization file (NOTE: unlike the comments in the v7 hysplit module,
            # negative values do not actually appear to be supported as NDUMP must be
            # greater than 0 for this to occur)
            "NDUMP": 0, # TODO: should this be 24 ?

            # The repeat interval at which the particle initialization file will be
            # written after NDUMP
            "NCYCL": 0, # TODO: should this be 24 ?

            ## ADVANCED Setup variable options

            # Minimum size in grid units of the meteorological sub-grid
            #         default is 10 (from the hysplit user manual). however,
            #         once hysplit complained and said i need to raise this
            #         variable to some value around 750...leaving w/default
            #         but change if required.
            "MGMIN": 10,

            # Maximum length of a trajectory in hours
            "KHMAX": 72,

            # Number of hours between emission start cycles
            "QCYCLE": 1.0,

            # NINIT: Read a particle initialization input file?
            # 0 - horizontal & vertical particle
            # 1 - horizontal gaussian puff, vertical top hat puff
            # 2 - horizontal & vertical top hat puff
            # 3 - horizontal gaussian puff, verticle particle
            # 4 - horizontal top hat puff, verticle particle
            "INITD": 0,

            # used to calculate the time step integration interval
            "TRATIO": 0.750,
            "DELT": 0.0,

            # particle release limits. if 0 is provided then the values are calculated
            # based on the number of sources: numpar" = num_sources" = num_fires*num_heights)
            # and maxpar" = numpar*1000/ncpus
            "NUMPAR": 1000,
            "MAXPAR": 10000000,

            #
            # MPI options
            #
            # This flag triggers MPI with multpile cores/processors on a single (local) node via MPICH2
            "MPI": False,

            # Number of processors/cores per HYSPLIT Process
            "NCPUS": 1,

            # Optional tranching of dispersion calculation using multiple HYSPLIT processes
            # There are two options:
            #  - Specify the number of processes (NPROCESSES) and let BlueSky determine
            #    how many fires are input into each process
            #  - Specify the number of fires per process (NFIRES_PER_PROCESS) and
            #    let BlueSky determine how many processes need to be run, up to an
            #    optional max (NPROCESSES_MAX).  The NFIRES_PER_PROCESS/NPROCESSES_MAX
            #    option is ignored if NPROCESSES is set to 1 or greater
            "NPROCESSES": 1,
            "NFIRES_PER_PROCESS": -1,
            "NPROCESSES_MAX": -1,

            # Machines file (TODO: functionality for multiple nodes)
            #MACHINEFILE": machines,

            #
            # CONTROL vars:
            #

            # sampling interval type, hour & min (default 0 1 0)
            # type of 0 gives the average over the interval
            "SAMPLING_INTERVAL_TYPE": 0,
            "SAMPLING_INTERVAL_HOUR": 1,
            "SAMPLING_INTERVAL_MIN": 0,

            # particle stuff (1.0 use default hysplit values)
            # diamater in micrometer, density in g/cc.
            "PARTICLE_DIAMETER": 1.0,
            "PARTICLE_DENSITY": 1.0,
            "PARTICLE_SHAPE": 1.0,

            # dry deposition vars (0.0 use default hysplit values)
            # velocity is m/s and weight is g/mol.
            "DRY_DEP_VELOCITY": 0.0,
            "DRY_DEP_MOL_WEIGHT": 0.0,
            "DRY_DEP_REACTIVITY": 0.0,
            "DRY_DEP_DIFFUSIVITY": 0.0,
            "DRY_DEP_EFF_HENRY": 0.0,

            # wet deposition vars (0.0 use default hysplit values)
            # in-cloud scav is L/L, below cloud is 1/s.
            "WET_DEP_ACTUAL_HENRY": 0.0,
            "WET_DEP_IN_CLOUD_SCAV": 0.0,
            "WET_DEP_BELOW_CLOUD_SCAV": 0.0,

            # radioactive decay half live in days (0.0 is default, ie: no decay)
            "RADIOACTIVE_HALF_LIVE": 0.0,

            # number of hours to offset start of dispersion
            "DISPERSION_OFFSET": 0
        },
        "vsmoke": {
            #  - ***'config' > 'dispersion' > 'vsmoke' > 'TEMP_FIRE' -- temperature of fire (F), default: 59.0
            #  - ***'config' > 'dispersion' > 'vsmoke' > 'PRES'*** -- *optional* -- Atmospheric pressure at surface (mb); default: 1013.25
            #  - ***'config' > 'dispersion' > 'vsmoke' > 'IRHA'*** -- *optional* -- Period relative humidity; default: 25
            #  - ***'config' > 'dispersion' > 'vsmoke' > 'LTOFDY'*** -- *optional* -- Is fire before sunset?; default: True
            #  - ***'config' > 'dispersion' > 'vsmoke' > 'STABILITY'*** -- *optional* -- Period instability class - 1 -> extremely unstable; 2 -> moderately unstable; 3 -> slightly unstable; 4 -> near neutral; 5 -> slightly stable; 6 -> moderately stable; 7 -> extremely stable; default: 4
            #  - ***'config' > 'dispersion' > 'vsmoke' > 'MIX_HT'*** -- *optional* -- Period mixing height (m); default: 1500.0
            #  - ***'config' > 'dispersion' > 'vsmoke' > 'OYINTA'*** -- *optional* -- Period's initial horizontal crosswind dispersion at the source (m); default: 0.0
            #  - ***'config' > 'dispersion' > 'vsmoke' > 'OZINTA'*** -- *optional* -- Period's initial vertical dispersion at the surface (m); default: 0.0
            #  - ***'config' > 'dispersion' > 'vsmoke' > 'BKGPMA'*** -- *optional* -- Period's background PM (ug/m3); default: 0.0
            #  - ***'config' > 'dispersion' > 'vsmoke' > 'BKGCOA'*** -- *optional* -- Period's background CO (ppm); default: 0.0
            #  - ***'config' > 'dispersion' > 'vsmoke' > 'THOT'*** -- *optional* -- Duration of convective period of fire (decimal hours); default: 4
            #  - ***'config' > 'dispersion' > 'vsmoke' > 'TCONST'*** -- *optional* -- Duration of constant emissions period (decimal hours); default: 4
            #  - ***'config' > 'dispersion' > 'vsmoke' > 'TDECAY'*** -- *optional* -- Exponential decay constant for smoke emissions (decimal hours); default: 2
            #  - ***'config' > 'dispersion' > 'vsmoke' > 'EFPM'*** -- *optional* -- Emission factor for PM2.5 (lbs/ton); default: 30
            #  - ***'config' > 'dispersion' > 'vsmoke' > 'EFCO'*** -- *optional* -- Emission factor for CO (lbs/ton); default: 250
            #  - ***'config' > 'dispersion' > 'vsmoke' > 'ICOVER'*** -- *optional* -- Period's cloud cover (tenths); default: 0
            #  - ***'config' > 'dispersion' > 'vsmoke' > 'CEIL'*** -- *optional* -- Period's cloud ceiling height (feet); default: 99999
            #  - ***'config' > 'dispersion' > 'vsmoke' > 'CC0CRT'*** -- *optional* -- Critical contrast ratio for crossplume visibility estimates; default: 0.02
            #  - ***'config' > 'dispersion' > 'vsmoke' > 'VISCRT'*** -- *optional* -- Visibility criterion for roadway safety; default: 0.125
            #  - ***'config' > 'dispersion' > 'vsmoke' > 'GRAD_RISE'*** -- *optional* -- Plume rise: TRUE -> gradual to final ht; FALSE ->mediately attain final ht; default: True
            #  - ***'config' > 'dispersion' > 'vsmoke' > 'RFRC'*** -- *optional* -- Proportion of emissions subject to plume rise; default: -0.75
            #  - ***'config' > 'dispersion' > 'vsmoke' > 'EMTQR'*** -- *optional* -- Proportion of emissions subject to plume rise for each period; default: -0.75
            #  - ***'config' > 'dispersion' > 'vsmoke' > 'KMZ_FILE'*** -- *optional* -- default: "smoke_dispersion.kmz"
            #  - ***'config' > 'dispersion' > 'vsmoke' > 'OVERLAY_TITLE'*** -- *optional* -- default: "Peak Hourly PM2.5"
            #  - ***'config' > 'dispersion' > 'vsmoke' > 'LEGEND_IMAGE'*** -- *optional* -- absolute path nem to legend; default: "aqi_legend.png" included in bluesky package
            #  - ***'config' > 'dispersion' > 'vsmoke' > 'JSON_FILE'*** -- *optional* -- name of file to write GeoJSON dispersion data; default: "smoke_dispersion.json"
            #  - ***'config' > 'dispersion' > 'vsmoke' > 'CREATE_JSON'*** -- *optional* -- whether or not to create the GeoJSON file; default: True
            #  - ***'config' > 'dispersion' > 'vsmoke' > 'DUTMFE'*** -- *optional* -- UTM displacement of fire east of reference point; default: 0
            #  - ***'config' > 'dispersion' > 'vsmoke' > 'DUTMFN'*** -- *optional* -- UTM displacement of fire north of reference point; default: 100
            #  - ***'config' > 'dispersion' > 'vsmoke' > 'XBGN'*** -- *optional* -- What downward distance to start calculations (km); default: 150
            #  - ***'config' > 'dispersion' > 'vsmoke' > 'XEND'*** -- *optional* -- What downward distance to end calculation (km) - 200km max; default: 200
            #  - ***'config' > 'dispersion' > 'vsmoke' > 'XNTVL'*** -- *optional* -- Downward distance interval (km) - 0 results in default 31 distances; default: 0.05
            #  - ***'config' > 'dispersion' > 'vsmoke' > 'TOL'*** -- *optional* -- Tolerance for isopleths; detault: 0.1
        }
    },
    "visualization": {
        "target": "'dispersion'"
        "hysplit": {
            "fire_locations_csv_filename": 'fire_locations.csv',
            "fire_events_csv_filename": 'fire_events.csv',
            "smoke_dispersion_kmz_filename": 'smoke_dispersion.kmz',
            "fire_kmz_filename": 'fire_locations.kmz',
            "prettykml": False,
            "output_dir": None,
            "images_dir": None,
            "data_dir": "",
            "blueskykml_config": {
                'SmokeDispersionKMLInput': {
                    # Use google's fire icon instead of BlueSkyKml's built-in icon
                    # (if an alternative isn't already specified)
                    # TODO: should we be using google's icon as the default?
                    'FIRE_EVENT_ICON': "http://maps.google.com/mapfiles/ms/micons/firedept.png"
                },
                'DispersionGridOutput': {
                    # If not set by user, it will be set to
                    # output_dir/images_dir
                    'OUTPUT_DIR': None
                }
            }

            # The following defaults are defined in the blueskykml package,
            # so they don't need to be defined here
            #"layers": [0],
        }
    },
    "export": {
        "modes": [],
        "extra_exports": [],
        "email": {
            # - ***'config' > 'export' > 'email' > 'recipients'*** -- *required* --
            # - ***'config' > 'export' > 'email' > 'sender'*** -- *optional* -- defaults to 'bsp@airfire.org'
            # - ***'config' > 'export' > 'email' > 'subject'*** -- *optional* -- defaults to 'bluesky run output'
            # - ***'config' > 'export' > 'email' > 'smtp_server'*** -- *optional* -- defaults to 'localhost'
            # - ***'config' > 'export' > 'email' > 'smtp_port'*** -- *optional* -- defaults to 1025
            # - ***'config' > 'export' > 'email' > 'smtp_starttls'*** -- *optional* -- defaults to False
            # - ***'config' > 'export' > 'email' > 'username'*** -- *optional* --
            # - ***'config' > 'export' > 'email' > 'password'*** -- *optional* --
        },
        "localsave": {

            #  - ***'config' > 'export' > 'localsave' > 'output_dir_name'*** -- *optional* -- defaults to run_id, which is generated if not defined
            #  - ***'config' > 'export' > 'localsave' > 'extra_exports_dir_name'*** -- *optional* -- generated from extra_exports mode name(s) if not defined
            #  - ***'config' > 'export' > 'localsave' > 'json_output_filename'*** -- *optional* -- defaults to 'output.json'
            #  - ***'config' > 'export' > 'localsave' > 'dest_dir'*** - *required* -- destination directory to contain output directory
            #  - ***'config' > 'export' > 'localsave' > 'handle_existing'*** - *optional* -- how to handle case where output dir already exists; options: 'replace', 'write_in_place', 'fail'; defaults to 'fail'
        },
        "upload": {
            #  - ***'config' > 'export' > 'upload' > 'output_dir_name'*** -- *optional* -- defaults to run_id, which is generated if not defined
            #  - ***'config' > 'export' > 'upload' > 'extra_exports_dir_name'*** -- *optional* -- generated from extra_exports mode name(s) if not defined
            #  - ***'config' > 'export' > 'upload' > 'json_output_filename'*** -- *optional* -- defaults to 'output.json'

            #  - ***'config' > 'export' > 'upload' > 'tarball_name'*** - *optional* -- defaults to '<output_dir>.tar.gz'
            #  - ***'config' > 'export' > 'upload' > 'scp' > 'host'*** - *required* if uploading via scp (which is currently the only supported upload mode) -- hostname of server to scp to
            #  - ***'config' > 'export' > 'upload' > 'scp' > 'user'*** - *optional* if uploading via scp (which is currently the only supported upload mode) -- username to use in scp; defaults to 'bluesky'
            #  - ***'config' > 'export' > 'upload' > 'scp' > 'port'*** - *optional* if uploading via scp (which is currently the only supported upload mode) -- port to use in scp; defaults to 22
            #  - ***'config' > 'export' > 'upload' > 'scp' > 'dest_dir'*** - *required* if uploading via scp (which is currently the only supported upload mode) -- destination directory on remote host to contain output directory
        }
    }

}