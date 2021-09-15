### Subnet Calculator https://tidalmigrations.com/subnet-builder/
------

### Convert the template to yaml file

```
python src/vpc.py
```

### Create Stack
```
aws cloudformation --profile ax-test create-stack --stack-name Troposphere-vpc --template-body file://vpc.yaml
``` 
 
### Update Stack
```
aws cloudformation --profile ax-test update-stack --stack-name Troposphere-vpc --template-body file://vpc.yaml
```

### Delete Stack
```
aws cloudformation --profile ax-test update-stack --stack-name Troposphere-vpc
```