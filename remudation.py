import boto3

def enable_managed_rule(rule_name):
    # Create AWS Config client
    config_client = boto3.client('config')

    # Enable managed rule
    try:
        response = config_client.put_organization_config_rule(
            OrganizationConfigRuleName=rule_name
        )
        print(f"Successfully enabled managed rule: {rule_name}")
        return response
    except config_client.exceptions.OrganizationAllFeaturesNotEnabledException:
        print("Error: AWS Organizations must have all features enabled.")
    except config_client.exceptions.NoSuchOrganizationConfigRuleException:
        print(f"Error: Managed rule '{rule_name}' does not exist.")
    except config_client.exceptions.OrganizationAccessDeniedException:
        print("Error: Access to AWS Organizations is denied.")

# Specify the name of the managed rule to enable
rule_name = "aws-service-access-iam-role"

# Enable the managed rule
enable_managed_rule(rule_name)