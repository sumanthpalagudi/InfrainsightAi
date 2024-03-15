import subprocess
from cost_estimation import estimation
def run_terraform_script(script_file):
    # Run Terraform commands from the script file
    try:
        subprocess.run(["terraform", "init"], check=True)
        subprocess.run(["terraform", "validate"], check=True)
        subprocess.run(["terraform", "plan"], check=True)
        estimation()
        proceed=input("Do you want to apply these changes? (yes/no): ")
        if proceed == 'yes':
            subprocess.run(["terraform", "apply", "-auto-approve"], check=True)
        else:
            print('No changes applied')
    except subprocess.CalledProcessError as e:
        print("Error running Terraform command:", e)