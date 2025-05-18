import sys
import os
import logging
import time
import json
from condition_resource import ConditionResource
from dotenv import load_dotenv


load_dotenv() # Load environment variables from the .env file
logging.basicConfig(level=logging.INFO)

def main(resource_type, num_resources, account_id, api_key):
	# Create the appropriate resource handler
	resource_classes = {
		'newrelic_nrql_alert_condition': ConditionResource
	}

	if resource_type not in resource_classes:
		logging.error(f"Unsupported resource type: {resource_type}")
		return

	resource_class = resource_classes[resource_type]
	resource_handler = resource_class(resource_type, account_id, api_key)

	resources = resource_handler.fetch_resources()

	if num_resources == 'all':
		resources_to_process = resources
	else:
		try:
			num_resources = int(num_resources)
			resources_to_process = resources[:num_resources]
		except ValueError:
			logging.error("Invalid number of resources specified. Please provide an integer or 'all'.")
			return

	filename = resource_type + "before_change.json"
	with open(filename, 'w') as f:
		json.dump(resources_to_process, f, indent=4)

	if resources_to_process:
		logging.info(f'Importing {len(resouces_to_process)} resources of type {resource_type}.')
		resource_handler.create_terraform_config(resources_to_process)
		resource_handler.import_to_terraform(resources_to_process)
	else:
		logging.info(f'No resources found for type {resource_type}.')

if __name__ == "__main__":
	if len(sys.argv) < 2:
		logging.error("Usage: python import_resources.py [resource_type] [num_of_resources]")
		sys.exit(1)

	resource_type = sys.argv[1]
	num_resources = sys.argv[2] if len(sys.argv) > 2 else 'all'

	# Get the environment variables
	account_id = os.getenv('ACCOUNT_ID')
	api_key = os.getenv('API_KEY')

	if not account_id or not api_key:
		raise ValueError("ACCOUNT_ID and API_KEY must be set in environment variables")

	start_time = time.time()
	main(resource_type, num_resources, account_id, api_key)
	end_time = time.time()
	duration = end_time - start_time
	print(f"Duration: {duration: .4f} seconds")