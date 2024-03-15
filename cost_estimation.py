import subprocess
import re
import boto3

def parse_terraform_plan(output):
    # Regular expression pattern to extract resource information
    resources = []

    # Split the output into lines and iterate through each line
    lines = output.split('\n')
    for i, line in enumerate(lines):
        # Check if the line contains resource information
        if 'resource' in line and ('+' in line or '-' in line or '#' in line):
            # Extract resource type and name from the line
            parts = line.split('"')
            if len(parts) >= 2:
                resource_type = parts[1]
                resource_name = parts[3]
                resources.append((resource_type, resource_name))
    
    return resources
def get_resource_service(resource_type):
    # Mapping from resource type to AWS service name
    service_map = {
        'aws_instance': 'AmazonEC2',
        'aws_s3_bucket': 'AmazonS3',
        'aws_db_instance': 'AmazonRDS',
        'aws_iam_user': 'IAM',
        'aws_lambda_function': 'Lambda',
        'aws_dynamodb_table': 'DynamoDB',
        'aws_api_gateway_rest_api': 'APIGateway',
        'aws_sqs_queue': 'AmazonSQS',
        'aws_sns_topic': 'AmazonSNS',
        'aws_glue_catalog_database': 'Glue',
        # Add more mappings as needed for other resource types
    }
    return service_map.get(resource_type)
def get_estimated_cost(resources,region,startDate,endDate):
    # Create a Cost Explorer client
    client = boto3.client('ce', region_name=region)

    # Prepare the filter for Cost Explorer
    filters = []
    for resource_type, resource_name in resources:
        service = get_resource_service(resource_type)
        print(f"Resource Type: {resource_type}, Resource Name: {resource_name}, Service: {service}")
        if service:
            filters.append(service)
            filters.append(resource_name)   

    # Retrieve cost and usage data between startDate and endDate                
    if not filters:
        print("Error: No valid filters found. Unable to retrieve cost and usage data.")
        return None
    # Get cost and usage data
    response = client.get_cost_and_usage(
        TimePeriod={
            'Start': startDate,  # Specify the start date (adjust as needed)
            'End': endDate  # Specify the end date (adjust as needed)
        },
        Granularity='MONTHLY',
        Filter={
            'Dimensions': {
                'Key': 'SERVICE',
                'Values': filters
            }
        },
        Metrics=['UnblendedCost'],  # You can adjust the metrics as needed
    )

    # Extract the estimated cost
    estimated_cost = float(response['ResultsByTime'][0]['Total']['UnblendedCost']['Amount'])
    return estimated_cost

def estimation():
    region = input("Enter AWS region: ")
    startDate= input("Enter the Start Date")
    endDate=input("Enter the End Date")
    # Run terraform plan command and capture its output
    try:
        plan_output = subprocess.check_output(['terraform', 'plan'], stderr=subprocess.STDOUT, text=True)
    except subprocess.CalledProcessError as e:
        print("Error running terraform plan:", e.output)
        return
    print(plan_output)
    # Parse terraform plan output to extract resource information
    resources = parse_terraform_plan(plan_output)
    print(resources)
    # Get estimated cost based on AWS Cost Explorer data
    estimated_cost = get_estimated_cost(resources,region,startDate,endDate)

    print("Estimated cost of resources:")
    print("${:.2f}".format(estimated_cost))