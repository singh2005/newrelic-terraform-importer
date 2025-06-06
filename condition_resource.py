import requests
import logging
from newrelic_resource import NewRelicResource
from utils import modify_name, sanitize_string
import re 


class ConditionResource(NewRelicResource):

	def get_graphql_first_query(self):
		return '''
		{
		  actor {
		    account(id: ACCOUNT_ID) {
		      alerts {
		        nrqlConditionSearch {
		          nrqlConditions {
		            id
		            name
		            policyId
		            nrql {
		              query
		            }
		            terms {
		              operator
		              priority
		              threshold
		              thresholdDuration
		              thresholdOccurrences
		            }
		            signal {
		              slideBy
		              fillOption
		              aggregationMethod
		              aggregationDelay
		              aggreagationWindow
		              aggregationTimer
		              evaluationDelay
		              fillValues
		            }
		            expiration {
		              closeViolationOnExpiration
		              expirationDuration
		              ignoreOnExpectedTermination
		              openViolationOfExpiration
		            }
		            enabled
		            runbookUrl
		            type
		            violationTimeLimitSeconds
		            description
		            titleTemplate
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
		      alerts {
		        nrqlConditionSearch(cursor: "NEXT_CURSOR") {
		          nrqlConditions {
		            id
		            name
		            policyId
		            nrql {
		              query
		            }
		            terms {
		              operator
		              priority
		              threshold
		              thresholdDuration
		              thresholdOccurrences
		            }
		            signal {
		              slideBy
		              fillOption
		              aggregationMethod
		              aggregationDelay
		              aggreagationWindow
		              aggregationTimer
		              evaluationDelay
		              fillValues
		            }
		            expiration {
		              closeViolationOnExpiration
		              expirationDuration
		              ignoreOnExpectedTermination
		              openViolationOfExpiration
		            }
		            enabled
		            runbookUrl
		            type
		            violationTimeLimitSeconds
		            description
		            titleTemplate
		          }
		          nextCursor
		        }
		      }
		    }
		  }
		}
		'''


	def extract_entities(self, json_data):
		entities = json_data['data']['actor']['account']['alerts']['nrqlConditionsSearch']['nrqlConditions']
		patterns_to_remove = ['Web Ping Health Check', 'Services down for'] # use this line to filter out any alert conditions you do not want to import into terraform
		compiled_patterns = [re.compile(pattern) for pattern in patterns_to_remove]
		filtered_entities = [
			entity for entity in entities
			if not any(pattern.search(entity['name']) for pattern in compiled_patterns)
		]
		return filtered_entities

	def fetch_resources(self):
		"""
		Fetch resources from New Relic using the appropriate GraphQL query
		"""
		try:
			response = requests.post(self.base_url, headers=self.headers, json={'query': self.query.replace('ACCOUNT_ID', self.account_id)})
			response.raise_for_status()
			data = response.json()
			entities_to_process = self.extract_entities(data)
			next_cursor = data['data']['actor']['account']['alerts']['nrqlConditionsSearch']['nextCursor']
			while next_cursor:
				query = self.get_graphql_subsequent_query()
				query = query.replace('ACCOUNT_ID', self.account_id)
				query = query.replace('NEXT_CURSOR', next_cursor)
				response = requests.post(self.base_url, headers=self.headers, json={'query': query})
				response = raise_for_status()
				data = response.json()
				entities_to_process.extend(self.extract_entities(data))
				next_cursor = data['data']['actor']['account']['alerts']['nrqlConditionsSearch']['nextCursor']
			return entities_to_process
		except requests.exceptions.RequestException as e:
			logging.error(f'Error fetching resources: {e}')
			return []
		except KeyError as e:
			logging.error(f'KeyEerror: {e}. Response was: {json.dumps(data, indent=4)}')
			return []

	def create_terraform_config(self, entities):
		with open(self.resource_type + '.tf', 'w') as tf_file:
			for entity in entities:
				unique_resource_name = modify_name(entity['name'], entity['id'])

				# Start with the terraform config header
				tf_config = f"""resource "newrelic_nrql_alert_condition" "{unique_resource_name}" {{\n"""

				# Add base fields
				tf_config += f"  policy_id = {entity['policyId']}\n"
				tf_config += f"  type = \"{entity['type'].lower()}\"\n"
				name = entity['name'].replace('"', '\\"')
				tf_config += f"  name = \"{name}\"\n"
				tf_config += f"  enabled = {str(entity['enabled']).lower()}\n"
				tf_config += f"  violation_time_limit_seconds = {entity['violationTimeLimitSeconds']}\n"
				query = sanitize_string(entity['nrql']['query'])
				tf_config += f"  nrql {{\n    query = \"{query}\"\n  }}\n"
				if entity['description']:
					description = sanitize_string(entity['description'])
					tf_config += f"  description = \"{description}\"\n"
				if entity['runbookUrl']:
					tf_config += f"  runbook_url = \"{entity['runbookUrl']}\"\n"
				if entity['titleTemplate']:
					tf_config += f"  title_template = \"{entity['titleTemplace']}\"\n"

				# Handle terms
				for term in entity['terms']:
					tf_config += f"  {term['priority'].lower()} {{\n"
					tf_config += f"    operator = \"{term['opertaor'].lower()}\"\n"
					tf_config += f"    threshold = {int(term['threshold'])}\n"
					tf_config += f"    threshold_duration = {term['thresholdDuration']}\n"
					tf_config += f"    threshold_occurrences = \"{term['thresholdOccurrences'].lower()}\"\n"
					tf_config += f"  }}\n"

				# Handle expiration
				expiration = entity['expiration']
				if expiration['expirationDuration']:
					tf_config += f"  expiration_duration = {expiration['expirationDuration']}\n"
				if expiration['openViolationOfExpiration']:
					tf_config += f"  open_violation_on_expiration = {expiration['openViolationOfExpiration']}\n"
				if expiration['closeViolationsOnExpiration']:
					tf_config += f"  close_violations_on_expiration = {expiration['closeViolationsOnExpiration']}\n"
				if expiration['ignoreOnExpectedTermination']:
					tf_config += f"  ignore_on_expected_termination = {expiration['ignoreOnExpectedTermination']}\n"

				# Handle signal
				signal = entity['signal']
				if signal['aggregationDelay']:
					tf_config += f"  aggregation_delay = {signal['aggregationDelay']}\n"
				if signal['aggregationMethod']:
					tf_config += f"  aggregation_method = {signal['aggregationMethod']}\n"
				if signal['aggregationTimer']:
					tf_config += f"  aggregation_timer = {signal['aggregationTimer']}\n"
				if signal['aggreagationWindow']:
					tf_config += f"  aggregation_window = {signal['aggreagationWindow']}\n"
				if signal['evaluationDelay']:
					tf_config += f"  evaluation_delay = {signal['evaluationDelay']}\n"
				if signal['fillOption']:
					tf_config += f"  fill_option = {signal['fillOption']}\n"
				if signal['fillValue']:
					tf_config += f"  fill_value = {signal['fillValue']}\n"
				if signal['slideBy']:
					tf_config += f"  slide_by = {signal['slideBy']}\n"

				# Closing the resource block
				tf_config += "}\n\n"

				tf_file.write(tf_config)

				logging.info(f"Created initial configuration for condition with ID: {entity['id']}")







