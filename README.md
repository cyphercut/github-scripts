# OpenIssue

OpenIssue is a Python script that uses the GitHub API to automate the management of code and secret scanning issues in a repository. It is designed to help teams quickly identify and respond to vulnerabilities and secret exposures, while also leveraging the collective expertise of the repository's top contributors.

## Code Scanning:

The code scanning module of OpenIssue uses the following process to manage vulnerabilities:

1. Load the environment variables from a .env file.
2. Use the GitHub API to get the existing open issues in the repository with the label "Vulnerability" and the severity (available in GitHub API) and creates a set of existing alert IDs.
3. Use the GitHub API to get the top 5 contributors of the repository.
4. Use the GitHub API to get the code scanning results and loops through each result to create an issue if it doesn't already exist.
5. Assign the issue to the top 5 contributors of the repository using the GitHub API.

### Required Python Libraries
The following Python libraries are required to run the code scanning module of OpenIssue:

- os to access environment variables.
- json: to parse JSON responses from the GitHub API.
- requests: to make HTTP requests to the GitHub API.
- datetime: to calculate the time difference between the current time and the time the vulnerability was detected.
- dotenv: to load environment variables from a .env file.

## Secret Scanning:

The secret scanning module of OpenIssue uses the following process to manage secret exposures:

1. Load the environment variables from a .env file.
2. Use the GitHub API to get the existing open issues in the repository with the label "Secret Exposed" and creates a set of existing alert IDs.
3. Use the GitHub API to get the top 5 contributors of the repository.
4. Use the GitHub API to get the secret scanning results and loops through each result to create an issue if it doesn't already exist.
5. Assign the issue to the top 5 contributors of the repository using the GitHub API.

### Required Python Libraries
The following Python libraries are required to run the secret scanning module of OpenIssue:

- os: to access environment variables.
- json: to parse JSON responses from the GitHub API.
- requests: to make HTTP requests to the GitHub API.
- datetime: to calculate the time difference between the current time and the time the secret was exposed.
- dotenv: to load environment variables from a .env file.

### Running the Script
To run the secret scanning module of OpenIssue, you need to have the required environment variables set up, and the script assumes that the .env file is located one level above the directory where the script is located.


