import re


def modify_name(name, id):
	# Modifies resource names to fit Terraform naming convention
	special_characters_to_remove = ['-', '+', '/', '<', '>', '@', '.', '(', ')', ' ', '&', ':', '=', '%', "'", '"', ',']
	for char in special_characters_to_remove:
		name = name.replace(char, '_')
	modified_name = 'terraform_' + name + '_' + id
	while '__' in modified_name:
		modified_name = modified_name.replace('__', '_')
	return modified_name.lower()

def sanitize_string(input_string):
	query = input_string.strip()
	query = query.replace('\r\n', ' ')
	query = query.replace('\n', ' ')
	if '"' in query:
		query = query.replace('"', '\\"')
	elif '\\' in query:
		query = query.replace('\\', '\\\\')
	return query

