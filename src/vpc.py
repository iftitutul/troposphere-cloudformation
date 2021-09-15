import troposphere.ec2 as ec2
from troposphere import (
    Base64,
    FindInMap,
    GetAtt,
    Join,
    Name,
    Output,
    Parameter,
    Ref,
    Tags,
    Template,
)

from troposphere.ec2 import (
    VPC,
    InternetGateway,
    NetworkAcl,
    NetworkAclEntry,
    Route,
    RouteTable,
    Subnet,
    SubnetNetworkAclAssociation,
    SubnetRouteTableAssociation,
    VPCGatewayAttachment,
)

t = Template()
#t.set_version("2021-09-14")
t.set_description("AWS Cloudformation For VPC Template")

# User Inpu
input_env = t.add_parameter(
    Parameter(
        "AWSenv",
        Type = "String",
        Description = "AWS Environment Type",
        Default = "dev",
        AllowedValues = [
            "Growth-Dev",
            "Growth-Stage",
            "Growth-Prod"
        ]
    )
)

t.add_mapping(
    "AWSenvtoVPC",
    {
        "Growth-Dev": {"vpc": "10.0.0.0/24"},
        "Growth-Stage": {"vpc": "10.1.0.0/25"},
        "Growth-Prod": {"vpc": "10.2.0.0/25"},
    },
)


ref_stack_id = Ref("AWS::StackId")


VPC = t.add_resource(
    VPC(
        'VPC', 
        CidrBlock = "10.10.0.0/16",
        Tags = Tags(
            Application = ref_stack_id,
        )
    )
)

# Finally, write the template to a file
with open('vpc.yaml', 'w') as f:
    f.write(t.to_yaml())
##
## aws cloudformation --profile ax-test create-stack troposphere-vpc --template-body file://vpc.yaml 
