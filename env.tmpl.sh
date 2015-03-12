# The scrapers are configured via environment variables
# which are documented here.
source `pwd`/env/bin/activate

# Database, must be postgres
export DATABASE_URI='postgresql://localhost/mozambique'

# Data storage path
export DATA_PATH=`pwd`/data


# Uploading the gazette:
export DOCCLOUD_USER=''
export DOCCLOUD_PASS=''

# Optional:
# export DOCCLOUD_HOST='https://sourceafrica.net'
# export DOCCLOUD_PROJECTID='230'
