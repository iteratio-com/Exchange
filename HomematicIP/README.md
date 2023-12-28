# HomematicIP Special Agent

Talks with eQ-3 cloud via REST-api to get data of heating thermostats.

Required: homematicip module (see https://github.com/hahn-th/homematicip-rest-api/), to be installed with `pip3 install 'urllib3<2' homematicip`.

You can create your token with `$OMD_ROOT/local/lib/python3/bin/hmip_generate_auth_token.py` which comes with homematicip. 
And it is recommended to let the agent run every 15 minutes instead of every minute to avoid being throttled for the usage of the REST-Api.

