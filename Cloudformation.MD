### Subnet Calculator https://tidalmigrations.com/subnet-builder/
------

### Convert the template to yaml file

```
python src/vpc.py
```

### Create Stack
```
aws cloudformation --profile <profile-name> --region <region-name> create-stack --stack-name Troposphere-vpc --template-body file://vpc.yaml
``` 

### Create Stack with Parameters
```
aws cloudformation --profile <profile-name> --region <region-name> create-stack --stack-name Troposphere-vpc --template-body file://vpc.yaml --parameters ParameterKey=AWSenv,ParameterValue=Growth-Prod
``` 
 
### Update Stack
```
aws cloudformation --profile <profile-name> --region <region-name> update-stack --stack-name Troposphere-vpc --template-body file://vpc.yaml
```

### Update Stack with Parameters
```
aws cloudformation --profile <profile-name> --region <region-name> update-stack --stack-name Troposphere-vpc --template-body file://vpc.yaml --parameters ParameterKey=AWSenv,ParameterValue=Growth-Prod
``` 

### Delete Stack
```
aws cloudformation --profile <profile-name> --region <region-name> update-stack --stack-name Troposphere-vpc
```
