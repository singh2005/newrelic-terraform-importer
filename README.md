# newrelic-terraform-importer

**🚧 Work in Progress — Scripts coming soon!**

`newrelic-terraform-importer` is a community-driven utility to help you **automatically import existing New Relic resources into Terraform**, bridging a major gap in observability-as-code workflows.

## 💡 Why This Exists

Managing New Relic infrastructure using Terraform is powerful — but importing existing alert policies, conditions, synthetic monitors, notification channels, and workflows into code is *painfully manual and incomplete*.

Official tools like [Terraformer](https://github.com/GoogleCloudPlatform/terraformer) offer limited support and often require significant cleanup and custom scripting.

This project was born out of that frustration — and aims to:

- ✅ Reduce the manual effort of importing existing New Relic resources
- ✅ Generate Terraform-compatible `.tf` and `.tfstate` files
- ✅ Make observability infrastructure truly reproducible
- ✅ Save teams weeks of tedious migration work

## 📦 What This Project Will Include

> The initial release is in progress and will include the following components:

- 🔧 Python scripts for fetching and translating New Relic resources
- 📄 Auto-generation of Terraform config files (`.tf`)
- 📂 Optional generation of Terraform state files (`terraform import` ready)
- 📘 Examples and documentation for:
  - Alert policies
  - Alert conditions
  - Synthetic monitors
  - Notification channels
  - Workflows

## 📅 Status

- ✅ Project initialized
- 🛠️ Python scripts being written (ETA: few days)
- 📚 Documentation and usage examples will follow shortly

## 📬 Stay in the Loop

If you're interested in using or contributing to this tool:

- ⭐ Star the repo to follow updates
- 🐛 File an issue if you’d like to request a feature or share your New Relic import pain points
- 🤝 PRs and suggestions welcome once the initial version is live!

---

## 🚀 Goal

Empower SREs, DevOps, and Observability engineers to bring their **existing New Relic setup under Terraform control** — without starting from scratch.

---

## 📜 License

MIT License — use freely, contribute openly.
