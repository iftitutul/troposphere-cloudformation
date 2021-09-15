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
#t.set_version('2010-09-09')
t.set_description("AWS Cloudformation For VPC Template")

# User Input
input_pub_az_amount = int(input('In how many different AZs you want to create PUBLIC subnets? (max. 3): '))
#input_pri_az_amount = int(input('In how many different AZs you want to create PRIVATE subnets? (max. 3): '))

input_env_param = t.add_parameter(
    Parameter(
        "AWSenv",
        Type = "String",
        Description = "AWS Environment Type",
        Default = "Growth-Dev",
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
ref_stack_name = Ref('AWS::StackName')

# Create VPC
VPC = t.add_resource(
    VPC(
        'VPC', 
        CidrBlock = FindInMap("AWSenvtoVPC", Ref(input_env_param), "vpc"),
        Tags = Tags(
            Application = ref_stack_id,
            Name = Ref(input_env_param)
        )
    )
)

#Create Internet Gateway
internetGateway = t.add_resource(
    InternetGateway(
        'InternetGateway',
        Tags=Tags(
            Application = ref_stack_id,
            Name = Join("",[Ref(input_env_param),("-IG")])
            ) 
    )
)

#Attach Internet Gateway to the VPC
gatewayAttachment = t.add_resource(
    VPCGatewayAttachment(
        'AttachGateway',
        VpcId=Ref(VPC),
        InternetGatewayId=Ref(internetGateway)
    )
)

#Create default Main Public RouteTable
mainRouteTable = t.add_resource(
    RouteTable(
        'MainRouteTable',
        VpcId=Ref(VPC),
        Tags=Tags(
            Application=ref_stack_id,
            Name = Join("",[Ref(input_env_param),("-Public-RT")])
        )
    )
)

#Create default route 0.0.0.0/0 in the Public RouteTable
route = t.add_resource(
    Route(
        'Route',
        DependsOn='AttachGateway',
        GatewayId=Ref('InternetGateway'),
        DestinationCidrBlock='0.0.0.0/0',
        RouteTableId=Ref(mainRouteTable),
    )
)

#Create Public Subnets and associate them with MainRouteTable
for i in range(input_pub_az_amount):
    if i == 0: AZ = Join("",[Ref(input_env_param),("-Pub-1")])
    elif i == 1: AZ = Join("",[Ref(input_env_param),("-Pub-2")])
    elif i == 2: AZ = Join("",[Ref(input_env_param),("-Pub-3")])
    input_number_of_public_subnets = int(input('How many PUBLIC subnets in ' + AZ + ' AZ you need?: ')) #user input request
    while input_number_of_public_subnets > 0:
        subnet_logical_id = 'PubSubnet' + str(input_number_of_public_subnets) + AZ.replace("-", "")
        input_number_of_public_subnets -= 1
        input_pub_subnet_cidr = input('Public Subnet ' + subnet_logical_id + ' desired CIDR (ex. 10.0.1.0/24): ') #user input request

        #Create Public Subnet
        subnet = t.add_resource(
        Subnet(
            subnet_logical_id,
            CidrBlock = input_pub_subnet_cidr,
            VpcId = Ref(VPC),
            AvailabilityZone = AZ,
            Tags = Tags(
                Application = ref_stack_id,
                Name = Join("",[Ref(input_env_param),("subnet_logical_id")])
                ) 
           )
        )

        #Create RouteTable Association (MAIN)
        UniqueSubnetRouteTableAssociation = 'SubnetRouteTableAssociation' + subnet_logical_id
        subnetRouteTableAssociation = t.add_resource(
        SubnetRouteTableAssociation(
            UniqueSubnetRouteTableAssociation,
            SubnetId = Ref(subnet),
            RouteTableId = Ref(mainRouteTable),
           )
        )




# Finally, write the template to a file
with open('./vpc.yaml', 'w') as f:
    f.write(t.to_yaml())

