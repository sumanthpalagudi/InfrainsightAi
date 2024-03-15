from openai import OpenAI
import re
from automate import run_terraform_script

resource_variables = {
    "ec2": ["instance_tag","ami", "instance_type", "subnet_id", "security_group_id", "key_pair_name", "access_key", "secret_key","region"],
    "s3_bucket": ["bucket_name", "region", "access_key", "secret_key"],
    "rds_instance": ["db_engine", "db_name", "db_username", "db_password", "instance_type", "subnet_id", "access_key", "secret_key"],
    "iam_user": ["username", "password", "access_key", "secret_key"],
    "vpc": ["vpc_cidr_block", "vpc_name", "access_key", "secret_key"],
    "route_table": ["vpc_id", "route_table_name", "route_destination_cidr", "route_destination_target", "access_key", "secret_key"],
    "nat_gateway": ["subnet_id", "elastic_ip_id", "access_key", "secret_key"],
    "glue_job": ["job_name", "glue_script_location", "role_arn", "access_key", "secret_key"],
    "sagemaker_endpoint": ["endpoint_name", "model_name", "instance_type", "instance_count", "access_key", "secret_key"],
    "lambda_function": ["function_name", "runtime", "handler", "source_code", "role_arn", "access_key", "secret_key"],
    # Add more resources and their required variables as needed
}

def generate_script(resource_type, more_info):
    client = OpenAI()
    # Construct the user message with provided variables
    

    # Prompt the user for variables required for the specified resource type
    variable_values = {}
    for variable in resource_variables.get(resource_type, []):
        variable_values[variable] = input(f"Enter value for '{variable}': ")
    
    # Convert variable values to Terraform variable assignments
    variable_assignments = "\n".join([f'variable "{key}" {{\n  default = "{value}"\n}}' for key, value in variable_values.items()])
    with open('variables.tf','a') as f:
        f.write(variable_assignments)
    print("variables have been added to  'variables.tf'")
    user_message = f"create a terraform script for {resource_type} with following specifications: {more_info}and also add this variables to the script and use them{variable_assignments}"
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a devops engineer, skilled in writing terraform scripts,you follow the best practices,you don't allow the public ips and ports,don't pass secrets directly,and also don't add and extra text while creating the script"},
            {"role": "user", "content": user_message}
        ]
    )
    output = completion.choices[0].message.content
    matches = re.search(r'```(.*?)```', output, re.DOTALL)
    if matches:
        extracted_content = matches.group(1).strip()
        # Remove "terraform" or "hcl" at the beginning of the extracted content
        extracted_content = re.sub(r'^\s*(?:terraform|hcl)\s*', '', extracted_content, flags=re.IGNORECASE)
    else:
        extracted_content = "No content found between triple backquotes."

    
    with open('main.tf', 'a') as f:
        f.write(extracted_content)
    print("Terraform code has been stored in the main.tf file for further use.")
if __name__ == "__main__":
    num_resources=input("how  many resources do you want to create?: ")
    for i in range(int(num_resources)):
        resource_type=input("Enter the type of AWS resource you want to create  (e.g., ec2 ,s3 ,vpc, nat_gateway, glue_job): ")
        more_info = input("give me some more info about the resource: ")
        generate_script(resource_type, more_info)
    run_terraform_script("main.tf")