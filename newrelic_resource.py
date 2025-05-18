import logging
import subprocess
from utils import modify_name


class NewRelicResource:
	def __init__(self, resource_type, account_id, api_key):
		self.resource_type = resource_type
		self.account_id = account_id
		self.base_url = 'https://api.newrelic.com/graphql'
		self.headers = {
			'Contents-Type': 'application/json',
			'API-Key': api_key
		}
		self.query = self.get_graphql_first_query()

	def get_graphql_first_query(self):
		"""
		Returns the GraphQL query string based on the resource type.
		First query to fetch the next request's cursor value.
		Override this method in child classes to provide the query for specific resource type.
		"""
		raise NotImplementedError

	def get_graphql_subsequent_query(self):
		"""
		Returns the GraphQL query string based on the resource type.
		Subsequent requests to make as long as we get back a nextCursor value.
		Override this method in child classes to provide the query for specific resource type.
		"""
		raise NotImplementedError

	def fetch_resources(self):
		"""
		Fetch resources from NewRelic using the appropriate GraphQL query.
		Override this method in child classes to provide the query for specific resource type.
		"""
		raise NotImplementedError

	def extract_entities(self):
		"""
		Extract resource entities from the graphQL response.
		Override this method in child classes to provide the query for specific resource type.
		"""
		raise NotImplementedError

	def create_terraform_config(self):
		"""
		Create the Terraform configuration for the fetched resource.
		Override this method in child classes to provide the query for specific resource type.
		"""
		raise NotImplementedError

	def import_to_terraform(self, resources):
		"""
		Import resrouces into Terraform
		"""
		for resource in resources:
			if self.resource_type == 'newrelic_nrql_alert_condition':
				resource_id = resource['policyId'] + ':' + resource['id']
			else:
				resource_id = resource['id']
			unique_resource_name = modify_name(resource['name'], resource['id'])
			logging.info(f"Importing {self.resource_type} with ID: {resource_id}")
			try:
				subprocess.run(['terraform', 'import', f'{self.resource_type}.{unique_resource_name}', resource_id], check=True)
			except subprocess.CalledProcessError as e:
				logging.error(f"Error importing resource ID {resource_id}: {e}")

