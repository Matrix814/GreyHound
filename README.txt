The [Tool Name Here] is a program created to aid in Network Threat Hunting and investigation.

In a basic overview it consists of a series of Text Based UIs to run Elastic Queries and perform some analytics on the results.

The program operates by performing Elastisearch Queries against a node (Defined InitialConfig).
Inside of InitialConfig ensure that:
node(IP and port of Elastic Instance)
index(The index within Elastic that you are performing the analysis on)
Start Date (The date that collection of Network Traffic Began on)


The current modules it supports are:
1) Enumeration suite of tools
2) Non-Standard Protocol Tool
3) Network Protocol Analyzer

IP ENUMERATION:
IP Enumerations goal is provide a faster way to check internal ips, determine what services are running on an IP, and to create information to create a fleshed out connection map of an IP

  -Internal and Public Facing IPs:
    +This sub tool generates the query to look for all live internal IP addresses over a specified range of time as well as any Mission Partner specified Public Facing IP addresses.
    +It possesses the capability to scan the entire date range of collection in less than an hour

  -Enumerate a single IP:
    + This sub tool will generate a profile of the IP address that you enter for the entire date range of collection.
    + It will ask the user to enter it by the Command Line (It has error handling)

  - Connection Enumeration of an IP Address
    + This sub tool will create a profile of every connection to the IP address that will be collected via the command line. The user will also need to specify the date range that they want to search between

[Configuration files and their location here]
  -Internal & Public Facing IPs:
    +The text file to specify the Public Facing IPs are located at /[tool]/PASSIVE_ENUMERATION/Whitelist/public_facing_ips.txt
      *The Ips can be listed out on each line one by one or by using the CIDR Notation (ex:192.168.0.0/24)
    +The Result of the initial scan is in:
      /MostRecentCollection/InternalIPEnumerationRange[FirstDay][LastDay].json
    +The Result is a json containing a dictionary of:
      *IP:
        -Non-ephemeral source ports
        -Non-ephemeral destination ports
        -Protocols seen in the traffic

  -Single IP:
    +The Result of the single ip scan is in:
    /Archive/[IP Address that was searched][FirstDay][LastDay]_[IP Address that was searched].json
    +The Result is a json containing a dictionary of:
      *IP:
        -Non-ephemeral source ports
        -Non-ephemeral destination ports
        -Protocols seen in the traffic

-Connections to specified IP:
  +The Result of the Connections to specified IP scan is in:
  /Archive/ips_connected_[IP to scan]/[Result for each ip].json
  Each File is the connection summary for a IP connected to the user specified IP
  +The Result is a json containing a dictionary of:
    *IP:
      -Non-ephemeral source ports
      -Non-ephemeral destination ports
      -Protocols seen in the traffic


NONSTANDARD PORT PROTOCOL ANALYZER:
The Nonstandard port protocol analyzer has two main functions:
1) The mass scan of the top 200 most used protocols
2) The user can enter the protocols that they wish to search format
Whichever option the user chooses it will then look for the ports that are associated with that protocol and then report any traffic that is not tied to an authorized port-protocol pair. it will store the information in a dictionary(json) where the keys are the IPs(Source and Destination) Then stores a list of the ports and timestamps that are associated with that pair

[Describe Output, Provide Sample Output and describe output, and provide location of output]
Underneath NONSTANDARD/Results/it will create a file for each protocol that contains the a dictionary where each key is the connection between 2 IP addresses and contains lists of:
-Timestamps of Connections
-Protocols used
-Ports used



NETWORK PROTOCOL ANALYZER:
[Break it down for each protocol supported]
-[Insert Description Here]
-[Describe the configuration files and their location here]
-[Describe Output, Provide Sample Output and describe output, and provide location of output]
