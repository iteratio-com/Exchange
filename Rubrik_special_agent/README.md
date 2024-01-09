# Rubrik REST API Special Agent

Will create piggyback data for nodes and includes the following Checks: Cluster System Status, Compliance 24 Hours (Cluster sided), Disk, Node Hardware Health, Node Status (Node sided)

Host label for cluster hosts -> rubrikDevice:cluster 
Host label for nodes -> rubrikDevice:node

0.1.0 initial version
0.2.0 Agent works
0.3.0 added some endpoints
0.3.1 some more endpoints added
0.4.0 Piggyback output
0.4.5 System Status Check
0.5.0 Hardware health for partitions and FRUS
0.6.0 Disk check
0.6.1 Default values cleaned
0.7.0 Node check, host label rubrikNode:yes, compliance report check
0.8.0 Normalized namings
0.9.0 Filesystem levels
0.9.2 Description updated
0.9.3 Import fixed
0.9.5 Typings added by mgo
0.9.6 Checkmk 2.2.0 compatibility 
0.9.7 Hardware health parsing adjusted
0.9.8 Threshholds for snapshots added
0.9.9 Metrics for compliance report service added
1.0.0 Small patches
1.1.0 Consolidated agent endpoint requests
1.1.1 Node disk status parser fixed
1.1.2 Added checks man pages
1.2.0 Added service choices
1.2.1 Delete token in any case at the end
1.2.2 Catching if tokens are used
1.2.3 Agent error into Check\_MK service output

The (deprecated) version for 2.1.0 is `rubrik_agent-0.9.3.mkp`.
Current version for 2.2.0 is `rubrik_agent-1.2.3.mkp`.

Thanks to my colleague Mathias for supporting me by giving hints and and treating me to keep my code clean!
