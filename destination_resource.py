import requests
import logging
from newrelic_resource import NewRelicResource
from utils import modify_name
import re


class DestinationResource(NewRelicResource):

	def get_graphql_first_query(self):
		return '''
		{
		  actor {
		    account_id(id: ACCOUNT_ID) {
		      aiNotifications {
		        destinations(cursor: "") {
		          entities {
		            id
		            name
		            type
		            properties {
		              key
		              value
		              displayValue
		            }
		            auth {
		              ... on AiNotificationsTokenAuth {
		                authType
		                prefix
		              }
		            }
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
		    account_id(id: ACCOUNT_ID) {
		      aiNotifications {
		        destinations(cursor: "NEXT_CURSOR") {
		          entities {
		            id
		            name
		            type
		            properties {
		              key
		              value
		              displayValue
		            }
		            auth {
		              ... on AiNotificationsTokenAuth {
		                authType
		                prefix
		              }
		            }
		          }
		          nextCursor
		        }
		      }
		    }
		  }
		}
		'''

	def extract_entities(self, json_data):
		entities = json_data['data']['actor']['account']['aiNotifications']['destinations']['entities']
		filtered_entities = []
		for entity in entities:
			if not entity.get('auth'):
				filtered_entities.append(entity)
		return filtered_entities

	def fetch_resources(self):
		# Fetch resources from NewRelic using appropriate GraphQL query
		try:
			response = requests.post(self.base_url, headers=self.headers, json={'query': self.query.replace('ACCOUNT_ID', self.account_id)})
			response.raise_for_status()
			data = response.json()
			entities_to_process = self.extract_entities(data)
			next_cursor = data['data']['actor']['account']['aiNotifications']['destinations']['nextCursor']
			while next_cursor:
				query = self.get_graphql_subsequent_query()
				query = query.replace('ACCOUNT_ID', self.account_id)
				query = query.replace('NEXT_CURSOR', next_cursor)
				response = requests.post(self.base_url, headers=self.headers, json={'query': query})
				response.raise_for_status()
				data = response.json()
				entities_to_process.extend(self.extract_entities(data))
				next_cursor = data['data']['actor']['account']['aiNotifications']['destinations']['nextCursor']
			return entities_to_process
		except requests.exceptions.RequestException as e:
			logging.error(f'Error fetching resources: {e}')
			return []
		except KeyError as e:
			logging.error(f'KeyError: {e}. Response was: {json.dumps(data, indent=4)}')
			return []

	def create_terraform_config(self, entities):
		with open(self.resource_type + '.tf', 'w') as tf_file:
			for entity in entities:
				unique_resource_name = modify_name(entity['name'], entity['id'])
				tf_config = f"""resource "newrelic_notification_destination" "{unique_resource_name}" {{\n"""
				tf_config += f"  name = \"{entity['name']}\"\n"
				tf_config += f"  name = \"{entity['type']}\"\n"

				# Handle auth block
				if entity['auth']:
					tf_config += f' auth_token {{\n    prefix = "{entity["auth"]["prefix"]}"\n  }}\n'

				# Handle properties block
				properties = []
				if entity['properties']:
					for property in entity['properties']:
						if property['displayValue']:
							block = f'  property {{\n    display_value = "{property["displayValue"]}"\n    key = "{property["key"]}"\n    value = "{property["value"]}"\n  }}\n'
						else:
							block = f'  property {{\n    key = "{property["key"]}"\n    value = "{property["value"]}"\n  }}\n'
						properties.append(block)
				else:
					default_property_block = '  property {\n    key = "migrated_tf"\n    value = "terraform_tf"\n  }\n'
					properties.append(default_property_block)
				for block in properties:
					tf_config += block

				# Closing the resource block
				tf_config += "}\n\n"

				tf_file.write(tf_config)
				logging.info(f"Created initial configuration for destination with ID: (entity['id'])")











