import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up authentication headers
headers = {
    "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}",
    "Accept": "application/vnd.github.v3+json"
}

# Get existing open issues with label "Vulnerability" and severity, and create a set of existing alert IDs
existing_alert_ids = set()
url = f"https://api.github.com/repos/{os.getenv('GITHUB_OWNER')}/{os.getenv('GITHUB_REPO')}/issues"
params = {
    "state": "open",
    "labels": "Vulnerability"
}
response = requests.get(url, headers=headers, params=params)
issues = response.json()
for issue in issues:
    if "severity" in issue:
        existing_alert_ids.add(issue["severity"]["id"])

# Get top 5 contributors of the repository
contributors = {}
url = f"https://api.github.com/repos/{os.getenv('GITHUB_OWNER')}/{os.getenv('GITHUB_REPO')}/stats/contributors"
response = requests.get(url, headers=headers)
stats = response.json()
for stat in stats:
    contributors[stat["author"]["login"]] = stat["total"]
top_contributors = sorted(contributors, key=contributors.get, reverse=True)[:5]

# Get code scanning results and create issues if they don't already exist
url = f"https://api.github.com/repos/{os.getenv('GITHUB_OWNER')}/{os.getenv('GITHUB_REPO')}/code-scanning/alerts"
response = requests.get(url, headers=headers)
alerts = response.json()
for alert in alerts["alerts"]:
    if alert["id"] not in existing_alert_ids:
        # Create issue
        url = f"https://api.github.com/repos/{os.getenv('GITHUB_OWNER')}/{os.getenv('GITHUB_REPO')}/issues"
        payload = {
            "title": f"Security vulnerability (Severity: {alert['severity']['id']})",
            "body": f"Description: {alert['rule_description']}\n\nRecommendation: {alert['recommendation']}\n\nLocation: {alert['location']['path']}:{alert['location']['start_line']}\n\n",
            "labels": "Vulnerability",
            "assignees": top_contributors
        }
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 201:
            print(f"Created issue for alert {alert['id']}")
        else:
            print(f"Failed to create issue for alert {alert['id']}")
