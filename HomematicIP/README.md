# HomematicIP Special Agent

Talks with eQ-3 cloud via REST-api to get data of heating thermostats.

Required: homematicip module (see https://github.com/hahn-th/homematicip-rest-api/), to be installed with `pip3 install homematicip` - but might lead to a broken installation, if the urllib3 folders in `$OMD_ROOT/local/lib/python3/` are not deleted afterwards. Urllib3 is not usable within Checkmk with a version >2 and is shipped with Checkmk anyways.

You can create your token with `$OMD_ROOT/local/lib/python3/bin/hmip_generate_auth_token.py` which comes with homematicip. 
