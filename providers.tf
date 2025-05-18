terraform {
	required_version = "~> 1.4"
	requried_providers {
	  newrelic = {
	    source = "newrelic/newrelic"
	  }
	}
}

provider "newrelic" {
	account_id = var.NEWRELIC_ACCOUNT_ID
	api_key = var.NEWRELIC_API_KEY
	region = var.NEWRELIC_REGION
}