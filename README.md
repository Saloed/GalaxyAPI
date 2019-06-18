# GalaxyAPI
## Dev environment
### Install
1. python > 3.7
1. core dependencies `pip install -r requirements.txt`
1. test dependencies `pip install -r test_requirements.txt`
1. [ODBC Driver 17 for SQL Server](https://www.microsoft.com/en-us/download/details.aspx?id=56567)
### Settings
Create `galaxy_api/local_settings.py` based on `galaxy_api/local_settings.py.example` and fill it with actual database credentials

**Never commit** `galaxy_api/local_settings.py`
