## Troposphere - library to create AWS Cloudformation Templates

#### Solution should be written in Python3 and use the Troposphere library which is used to generate Cloudformation templates. 
-----------------------------

The Growth team has created 3 new AWS accounts (Growth-Dev, Growth-Stage, Growth-Prod)and would like you to develop a solution to create Cloudformation templates that set-up some
base infrastructure.

Some considerations:
- They may want to use the same tool to add additional accounts in the future.
- How you might test/validate your generated templates.

They have requested that the tool initially creates templates for the accounts as follows:
- Each account should have a VPC with
  - Dev:
    - VPC IP: 10.0.0.0
    - Netmask: 255.255.255.0
    - DNS Support enabled
    - Default instance tenancy
  - Stage: 
    - VPC IP: 10.1.0.0
    - Netmask: 255.255.192.0
    - DNS Support and DNS Hostnames enabled
    - Default instance tenancy
  - Prod:
    - VPC IP: 10.2.0.0
    - Netmask: 255.255.192.0
    - DNS Support and DNS Hostnames enabled
    - Default instance tenancy

Each account should have the following multi-az subnets. The VPC IPs should bespread as evenly as possible between the az’s.
  - Private:
    - No internet access
  - Public
    - Outbound internet access
  - Protected
    - Outbound internet access via NAT

Tags should be added to each resource for billing purposes. You may decide which tags to add.

-------------------------

### Reference:
- https://blog.spikeseed.cloud/easy-infrastructure-as-code-with-troposphere/
- https://github.com/cloudtools/troposphere
- https://github.com/arhs/spikeseed-cloud-labs/tree/master/troposphere
- https://github.com/dsouzajude/troposphere-demo
- https://medium.com/@it.melnichenko/python-script-with-troposphere-library-which-automatically-creates-cloudformation-template-for-you-98cc76ca72f3