# HomematicIP Special Agent

This package contains checks for devices in the HomematicIP (eQ-3 cloud): 
* HomematicIP thermostats: Temperature sensors, RSSI value, valve position and the following states: battery, pending config, operation lock, valve state, reachability, duty cycle
* HomematicIP magnetic shutter contacts: Window state and RSSI value

Different levels and states can be set, defaults are given.

The homematicip pip package is required `pip3 install 'urllib3<2' homematicip` - see https://github.com/hahn-th/homematicip-rest-api/

You can create the necessary token with `$OMD_ROOT/local/lib/python3/bin/hmip_generate_auth_token.py` which comes with homematicip.

Due to the api-ratio we recommend to set the normal check interval for the agent to 15 minutes instead of 1 minute.

