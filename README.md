# GalaxyAPI
## Build & Run

### Requirements
1. Install [Docker](https://docs.docker.com/install/linux/docker-ce/) (19.03 or similar)
2. Install Python 2.7 or 3+ (for running scripts)

### Building docker image

Simply run `./build.sh` and wait for a while

### Running docker image
1. Create a directory with endpoints descriptions. 
Put descriptions into this directory and put SQL files into subdirectory named `sql`   
2. Write a configuration file based on  example `galaxy_api.ini.example`
If you don't need HTTPS remove entire SSL section of configuration
3. Run image via `./run.py <config-file-name>`

## Dev environment
### Install
1. python > 3.7
1. core dependencies `pip install -r requirements.txt`
1. test dependencies `pip install -r test_requirements.txt`
1. [ODBC Driver 17 for SQL Server](https://www.microsoft.com/en-us/download/details.aspx?id=56567)
### Settings
Create `galaxy_api.ini` based on `galaxy_api.ini.example` and fill it with actual database credentials

**Never commit** `galaxy_api.ini`
