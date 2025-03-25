# Director Deployment

This is an example of how to deploy a Sandgarden director pool
into your private infrastructure.

It assumes you have a private VPC already set up where your director pool will live.

## Usage

```bash
cp terraform.tfvars.example terraform.tfvars
# Set the variables as needed

tofu init
tofu apply


# Your CLI expects this value to be set to the NLB of your director pool
export SAND_BACKEND_URL="https://$(tofu output -raw nlb_dns)"
sand health # Health check?
```

## Inputs

* namespace ("sandgarden" by default)
* vpc_id
* include_sample_database=true

## Outputs

* director_secret_arn
* lambda_role_arn
* nlb_dns

## Resources created

* ASG for directors
* Role/Instance Profile for directors to assume
* Basic example role for lambda workflows to run as
* The ECR repo acting as a passthrough for director images

## Private Cloud Director Notes

### Questions
* Will customers be able to fetch the AMI we have specified?

### TODO

* [ ] Make lambda policy customizable
