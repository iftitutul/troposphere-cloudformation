from typing import Type
import troposphere.ec2 as ec2
from troposphere import (
    FindInMap,
    Join,
    Parameter,
    Ref,
    Tags,
    Template,
    Select,
    GetAZs,
    GetAtt,
    Cidr,
)

from troposphere.ec2 import (
    VPC,
    InternetGateway,
    NatGateway,
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
#input_az_amount = int(input('In how many different AZs you want to create subnets? (max. ): '))
input_az_amount = 2


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

t.add_mapping(
    "AWSenvtopubsubnet",
    {
        "Growth-Dev": {
            "pubsubnet1": "10.0.0.0/28",
            "pubsubnet2": "10.0.0.16/28",
        },
        "Growth-Stage": {
            "pubsubnet1": "10.1.0.0/28",
            "pubsubnet2": "10.1.0.16/28",
        },
        "Growth-Prod": {
            "pubsubnet1": "10.2.0.0/28",
            "pubsubnet2": "10.2.0.16/28",
        },
    }
)

t.add_mapping(
    "AWSenvtoprivatesubnet",
    {
        "Growth-Dev": {
            "pvtsubnet1": "10.0.0.32/28",
            "pvtsubnet2": "10.0.0.48/28",
        },
        "Growth-Stage": {
            "pvtsubnet1": "10.1.0.32/28",
            "pvtsubnet2": "10.1.0.48/28",
        },
        "Growth-Prod": {
            "pvtsubnet1": "10.2.0.32/28",
            "pvtsubnet2": "10.2.0.48/28",
        },
    }
)

t.add_mapping(
    "AWSenvtoprotectedsubnet",
    {
        "Growth-Dev": {
            "protectedsubnet1": "10.0.0.64/28",
            "protectedsubnet2": "10.0.0.80/28",
        },
        "Growth-Stage": {
            "protectedsubnet1": "10.1.0.64/28",
            "protectedsubnet2": "10.1.0.80/28",
        },
        "Growth-Prod": {
            "protectedsubnet1": "10.2.0.64/28",
            "protectedsubnet2": "10.2.0.80/28",
        },
    }
)

t.add_mapping(
    "AWSenvtoVPCdns",
    {
        "Growth-Dev": {
            "dnshostnamesenabled": "False",
        },
        "Growth-Stage": {
            "dnshostnamesenabled": "True",
    
        },
        "Growth-Prod": {
            "dnshostnamesenabled": "True",
        },
    }
)

ref_stack_id = Ref('AWS::StackId')
ref_stack_name = Ref('AWS::StackName')

# Create VPC
VPC = t.add_resource(
    VPC(
        'VPC', 
        CidrBlock = FindInMap('AWSenvtoVPC', Ref(input_env_param), 'vpc'),
        EnableDnsSupport = True,
        EnableDnsHostnames = FindInMap('AWSenvtoVPCdns', Ref(input_env_param), 'dnshostnamesenabled'),
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
        Tags = Tags(
            Application = ref_stack_id,
            Name = Join("",[Ref(input_env_param),("-IG")])
            ) 
    )
)

#Attach Internet Gateway to the VPC
gatewayAttachment = t.add_resource(
    VPCGatewayAttachment(
        'AttachGateway',
        VpcId = Ref(VPC),
        InternetGatewayId = Ref(internetGateway)
    )
)

#Create default Main Public RouteTable
mainRouteTable = t.add_resource(
    RouteTable(
        'MainRouteTable',
        VpcId = Ref(VPC),
        Tags = Tags(
            Application = ref_stack_id,
            Name = Join("",[Ref(input_env_param),("-Public-RT")])
        )
    )
)

#Create default route 0.0.0.0/0 in the Public RouteTable
route = t.add_resource(
    Route(
        'Route',
        DependsOn = 'AttachGateway',
        GatewayId = Ref('InternetGateway'),
        DestinationCidrBlock = '0.0.0.0/0',
        RouteTableId = Ref(mainRouteTable),
    )
)

# Create Public Subnet
for i in range(input_az_amount):
    public_subnet = t.add_resource(Subnet(
        'PublicSubnet'+ str(i+1),
        VpcId=Ref(VPC),
        AvailabilityZone = Select(i, GetAZs(Ref("AWS::Region"))),
        CidrBlock = FindInMap("AWSenvtopubsubnet", Ref(input_env_param), "pubsubnet"+ str(i+1)),
        #CidrBlock = Select(i+4, Cidr(GetAtt(VPC, 'CidrBlock'), 16, 8)),
        Tags = Tags(
                Application = ref_stack_id,
                Name = Join("",[Ref(input_env_param),("-PublicSubnet"+ str(i+1))])
        ) 
    )
)
    
    public_subnet_attachment = t.add_resource(SubnetRouteTableAssociation(
        'SubnetPublicToRouteTableAttachment' + str(i+1),
        SubnetId = Ref(public_subnet),
        RouteTableId = Ref(mainRouteTable),
    )
)

# Private Routing table
privateRouteTable = t.add_resource(RouteTable(
  "PrivateRouteTable",
  VpcId = Ref(VPC),
  Tags = Tags(
            Application = ref_stack_id,
            Name = Join("",[Ref(input_env_param),("-Private-RT")])
        )
  )
)

# Create Private Subnet
for i in range(input_az_amount):
    private_subnet = t.add_resource(Subnet(
        'privateSubnet'+ str(i+1),
        VpcId=Ref(VPC),
        AvailabilityZone = Select(i, GetAZs(Ref("AWS::Region"))),
        CidrBlock = FindInMap("AWSenvtoprivatesubnet", Ref(input_env_param), "pvtsubnet"+ str(i+1)),
        #CidrBlock = Select(i+4, Cidr(GetAtt(VPC, 'CidrBlock'), 16, 8)),
        Tags = Tags(
                Application = ref_stack_id,
                Name = Join("",[Ref(input_env_param),("-pvtSubnet"+ str(i+1))])
        ) 
    )
)
    
    private_subnet_attachment = t.add_resource(SubnetRouteTableAssociation(
        'SubnetprivateToRouteTableAttachment' + str(i+1),
        SubnetId = Ref(private_subnet),
        RouteTableId = Ref(privateRouteTable),
        )
)

# Create protected Subnet
for i in range(input_az_amount):
    protected_subnet = t.add_resource(Subnet(
        'protectedSubnet'+ str(i+1),
        VpcId = Ref(VPC),
        AvailabilityZone = Select(i, GetAZs(Ref("AWS::Region"))),
        CidrBlock = FindInMap("AWSenvtoprotectedsubnet", Ref(input_env_param), "protectedsubnet"+ str(i+1)),
        #CidrBlock = Select(i+4, Cidr(GetAtt(VPC, 'CidrBlock'), 16, 8)),
        Tags = Tags(
                Application = ref_stack_id,
                Name = Join("",[Ref(input_env_param),("-protectedSubnet"+ str(i+1))])
        ) 
    )
)

    # Protected Routing table   
    protectedRouteTable = t.add_resource(RouteTable(
        'ProtectedRouteTable'+ str(i+1),
        VpcId = Ref(VPC),
        Tags = Tags(
                Application = ref_stack_id,
                Name = Join("", [Ref(input_env_param),("-Protected-RT"+ str(i+1))])
        )
    )
)

    protected_subnet_attachment = t.add_resource(SubnetRouteTableAssociation(
        'SubnetprotectedToRouteTableAttachment'+ str(i+1),
        SubnetId = Ref(protected_subnet),
        RouteTableId = Ref(protectedRouteTable)
    )
)

    # Create NAT EIP
    nat_eip = t.add_resource(ec2.EIP(
        'EIP' + str(i+1),
        Domain="vpc",
        Tags=Tags(
            Application = ref_stack_id,
            Name = Join("",[Ref(input_env_param),("-NatGW-EIP-"+ str(i+1))])
        )
    )
)

    # Create NAT Gateway for Protected Subnet
    nat_gateway = t.add_resource(ec2.NatGateway(
        'natgatway'+ str(i+1),
        AllocationId = GetAtt(nat_eip,'AllocationId'),
        SubnetId = Ref(protected_subnet),
        Tags = Tags(
            Application = ref_stack_id,
            Name = Join("",[Ref(input_env_param),("-NatGW-"+ str(i+1))])
        )
    )
)

    #Create default route 0.0.0.0/0 in the Nat RouteTable
    nat_route = t.add_resource(Route(
            'natRoute' + str(i+1),
            DependsOn = nat_gateway,
            NatGatewayId = Ref(nat_gateway),
            DestinationCidrBlock = '0.0.0.0/0',
            RouteTableId = Ref(protectedRouteTable),
    )
)

# Finally, write the template to a file
with open('./vpc.yaml', 'w') as f:
    f.write(t.to_yaml())

