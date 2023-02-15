#!/usr/bin/env python
import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load the .env file
dotenv_path = Path('../.env')
load_dotenv(dotenv_path=dotenv_path)

# Set repository and owner
owner = os.environ.get('GITHUB_REPO_OWNER')
repo = os.environ.get('GITHUB_REPO_NAME')

# Set headers and access token
headers = {
    "Authorization": f"Bearer {os.environ['GITHUB_ACCESS_TOKEN']}",
    "Accept": "application/vnd.github.v3+json"
}

# Get existing issues in the repository
url = f"https://api.github.com/repos/{owner}/{repo}/issues"
params = {"state": "open", "labels": "Secret Exposed"}
response = requests.get(url, headers=headers, params=params)

# Create a set of existing alert IDs
existing_alerts = set()
if response.status_code == 200:
    issues = response.json()
    for issue in issues:
        alert_id = issue.get("title").split()[0][1:]
        existing_alerts.add(alert_id)

# Get top 5 contributors of the repository
url = f"https://api.github.com/repos/{owner}/{repo}/stats/contributors"
response = requests.get(url, headers=headers)

top_contributors = set()
if response.status_code == 200:
    contributors = response.json()
    contributors_sorted = sorted(contributors, key=lambda x: x['total'], reverse=True)
    for contributor in contributors_sorted[:5]:
        top_contributors.add(contributor['author']['login'])

# Get secret scanning results
url = f"https://api.github.com/repos/{owner}/{repo}/secret-scanning/alerts"
response = requests.get(url, headers=headers)

# Loop through each secret scanning result and create an issue if it doesn't already exist
scans = response.json()
for scan in scans:

    # Create issue only for open state
    if scan["state"] != "open":
        continue

    # Extract number and description from scan result
    alert_id        = scan["number"]
    html_url        = scan["html_url"]
    alert_summary   = scan["secret_type_display_name"]
    created_at_str  = scan["created_at"]

    # Calculate time difference between current time and created_at
    created_at = datetime.strptime(created_at_str, '%Y-%m-%dT%H:%M:%SZ')
    now = datetime.utcnow()
    delta = now - created_at
    days = delta.days
    hours = delta.seconds // 3600
    minutes = (delta.seconds // 60) % 60
    seconds = delta.seconds % 60

    # Set issue title and body
    if days > 0:
        time_str = f"{days} day{'s' if days > 1 else ''}"
    elif hours > 0:
        time_str = f"{hours} hour{'s' if hours > 1 else ''}"
    elif minutes > 0:
        time_str = f"{minutes} minute{'s' if minutes > 1 else ''}"
    else:
        time_str = f"{seconds} second{'s' if seconds > 1 else ''}"

    title = f"#{alert_id} Secret Scanning {alert_summary} exposed"
    body = f"### Description\nGitHub detected a secret {time_str} ago that is compromised. Anyone with Read access can discover secrets exposed in this repository, potentially resulting in unauthorized access to your services.\n\n### Recommendation\nRotate and Revoke the secret to avoid any irreversible damage.\n\n### URL\n{html_url}\n\n"

    # Check if issue already exists with same title
    issue_exists = False
    issues_url = f"https://api.github.com/repos/{owner}/{repo}/issues"
    response = requests.get(issues_url, headers=headers)
    issues = response.json()

    for issue in issues:
        if issue['title'] == title:
            issue_exists = True
            break

    if issue_exists:
        print(f"{title} - Issue already exists")
    else:
        # Assign the issue to the top five contributors of the repository
        contributors_url = f"https://api.github.com/repos/{owner}/{repo}/contributors"
        contributors_response = requests.get(contributors_url, headers=headers)
        contributors = contributors_response.json()

        # Sort contributors by number of contributions
        contributors_sorted = sorted(contributors, key=lambda c: c['contributions'], reverse=True)

        # Create issue using GitHub API
        url = f"https://api.github.com/repos/{owner}/{repo}/issues"
        data = {
            "title": title,
            "body": body,
            "labels": ["Secret Exposed"]
        }

        response = requests.post(url, headers=headers, data=json.dumps(data))

        # Check for errors
        if response.status_code != 201:
            print(f"Error creating issue: {response.text}")
        else:
            issue_url = response.json()['html_url']
            print(f"{title} - {issue_url}")

        # Assign issue to top five contributors
        for i, contributor in enumerate(contributors_sorted[:5]):
            assignee = contributor['login']
            assign_url = f"https://api.github.com/repos/{owner}/{repo}/issues/{response.json()['number']}/assignees"
            assignees = {'assignees': [assignee]}
            response = requests.post(assign_url, headers=headers, data=json.dumps(assignees))

            # if response.status_code == 201:
            #     print(f"{title} - Issue assigned to {assignee}")
            # else:
            #     print(f"Error assigning issue to {assignee}: {response.text}")