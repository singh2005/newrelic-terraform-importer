import requests
import logging
from newrelic_resource import NewRelicResource
from utils import modify_name
impore re


class ChannelResource(NewRelicResource):

	def get_graphql_first_query(self):
		return '''
		{
		  actor {
		    account(id: ACCOUNT_ID) {
		      aiNotifications {
		        channels {
		          entities {
		            id
		            name
		            type
		            destinationId
		            product
		            properties {
		              key
		              label
		              value
		              displayValue
		            }
		            status
		          }
		          nextCursor
		        }
		      }
		    }
		  }
		}
		'''

	def get_graphql_subsequent_query(self):
		return '''
		{
		  actor {
		    account(id: ACCOUNT_ID) {
		      aiNotifications {
		        channels(cursor: "NEXT_CURSOR") {
		          entities {
		            id
		            name
		            type
		            destinationId
		            product
		            properties {
		              key
		              label
		              value
		              displayValue
		            }
		            status
		          }
		          nextCursor
		        }
		      }
		    }
		  }
		}
		'''

	def extract_entities(self, json_data):
		return json_data['data']['actor']['account']['aiNotifications']['channels']['entities']

	def fetch_resources(self):
		# Fetch resources from New Relic using appropriate graphQL query
		try:
			response = requests.post(self.base_url, headers=self.headers, json={'query': self.query.replace('ACCOUNT_ID', self.account_id)})
			response.raise_for_status()
			data = response.json()
			entities_to_process = self.extract_entities(data)
			next_cursor = data['data']['actor']['account']['aiNotifications']['channels']['nextCursor']
			while next_cursor:
				query = self.get_graphql_subsequent_query()
				query = query.replace('ACCOUNT_ID', self.account_id)
				query = query.replace('NEXT_CURSOR', next_cursor)
				response = requests.post(self.base_url, headers=self.headers, json={'query': query})
				response.raise_for_status()
				data = response.json()
				entities_to_process.extend(self.extract_entities(data))
				next_cursor = data['data']['actor']['account']['aiNotifications']['channels']['nextCursor']
			return entities_to_process
		except requests.exceptions.RequestException as e:
			logging.error(f'Error fetching resources: {e}')
			return []
		except KeyError as e:
			logging.error(f'KeyError: {e}. Response was: {json.dumps(data, indent=4)}')


	def create_terraform_config(self, entities):
		with open(self.resource_type + '.tf', 'w') as tf_file:
			for entity in entities:
				unique_resource_name = modify_name(entity['name'], entity['id'])
				
				# Terraform config header
				tf_config = f"""resource "newrelic_notification_channel" "{unique_resource_name}" {{\n"""
				tf_config += f"  name = \"{entity['name']}\"\n"				
				tf_config += f"  type = {entity['type']}\n"				
				tf_config += f"  destination_id = \"{entity['destinationId']}\"\n"				
				tf_config += f"  product = \"{entity['product']}\"\n"

				# Handle properties block
				for property in entity['properties']:
					tf_config += f"  property {{\n"
					tf_config += f"    key = \"{property['key']}\"\n"
					if '\n' in property['value']:
						formatted_value = f"<<EOT\n"
						formatted_value += property['value']
						formatted_value += "\nEOT\n"
						tf_config += f"    value = {formatted_value}\n"
					elif '"' in property['value']:
						escaped_value = property['value'].replace('"', '\\"')
						tf_config += f"    value = \"{escaped_value}\"\n"
					else:
						tf_config += f"    value = \"{property['value']}\"\n"
					tf_config += "  }\n\n"

				# Close the resource block
				tf_config += "}\n\n"

				tf_file.write(tf_config)
				logging.info(f"Created initial configuration for newrelic_notification_channel with ID: {entity['id']}")
