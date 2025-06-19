# newrelic-terraform-importer

`newrelic-terraform-importer` is a community-driven utility to help you **automatically import existing New Relic resources into Terraform**, bridging a major gap in observability-as-code workflows.

## 💡 Why This Exists

Managing New Relic infrastructure using Terraform is powerful — but importing existing alert policies, conditions, synthetic monitors, notification channels, and workflows into code is *painfully manual and incomplete*.

Official tools like [Terraformer](https://github.com/GoogleCloudPlatform/terraformer) offer limited support and often require significant cleanup and custom scripting.

This project was born out of that frustration — and aims to:

- ✅ Reduce the manual effort of importing existing New Relic resources  
- ✅ Generate Terraform-compatible `.tf` files  
- ✅ Enable `terraform import` automation  
- ✅ Make observability infrastructure truly reproducible  
- ✅ Save teams weeks of tedious migration work

## ✅ Currently Supported Resources

> You can import the following New Relic resources today:

- **Notification Destinations**
- **Notification Channels**
- **NRQL-Based Alert Conditions**

More resource types will be added over time based on community feedback. 

## 🚀 Getting Started

### 1. Clone and install

- `git clone https://github.com/singh2005/newrelic-terraform-importer.git`
- `cd newrelic-terraform-importer`
- `pip install -r requirements.txt`

### 2. Set up your `.env`

- `cp .env.example .env`

Then edit .env to populate your new relic API key and account id.


### 3. Initialize Terraform

- `terraform init`


### 4. Run an import

To import all resources of a given type:

- `python main.py newrelic_notification_destination`

To import only a specific number of resources (e.g 5 notification destinations):

- `python main.py newrelic_notification_destination 5`

## 📬 Stay in the Loop

If you're interested in using or contributing to this tool:

- ⭐ Star the repo to follow updates  
- 🐛 File an issue if you’d like to request a feature or share your New Relic import pain points  
- 🤝 PRs and suggestions welcome!

---

## 🚀 Goal

Empower SREs, DevOps, and Observability engineers to bring their **existing New Relic setup under Terraform control** — without starting from scratch.

---

## 📜 License

MIT License — use freely, contribute openly.



