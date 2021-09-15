
```
aws cloudformation --profile ax-test create-stack --stack-name troposphere-vpc --template-body file://vpc.yaml 
 
aws cloudformation --profile ax-test update-stack --stack-name troposphere-vpc --template-body file://vpc.yaml
```