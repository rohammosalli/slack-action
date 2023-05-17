import os
import requests
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from datetime import datetime

SLACK_BOT_TOKEN = os.environ['SLACK_BOT_TOKEN']
SLACK_CHANNEL = os.environ['SLACK_CHANNEL']
GITHUB_TOKEN = os.environ['GITHUB_TOKEN']
REPO_OWNER = os.environ['REPO_OWNER']
REPO_NAME = os.environ['REPO_NAME']
RUN_ID = os.environ['RUN_ID']
SEND_SUCCESS_MESSAGE = os.environ['SEND_SUCCESS_MESSAGE'].lower() == 'true'

client = WebClient(token=SLACK_BOT_TOKEN)


def get_headers():
    return {
        'Authorization': f"Bearer {GITHUB_TOKEN}",
        'Accept': 'application/vnd.github+json'
    }


def get_workflow_run(run_id):
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/runs/{run_id}"
    response = requests.get(url, headers=get_headers())
    if response.status_code == 404:
        return None
    response.raise_for_status()
    return response.json()


def get_workflow_run_jobs(run_id):
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/runs/{run_id}/jobs"
    response = requests.get(url, headers=get_headers())
    response.raise_for_status()
    return response.json()['jobs']


def get_previous_workflow_run(repo_owner, repo_name, run_id, branch, headers):
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/actions/runs?per_page=2"
    if branch:
        url += f"&branch={branch}"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    runs = response.json()['workflow_runs']
    for run in runs:
        if run['id'] != int(run_id):
            return run
    return None


def get_previous_same_run_number_workflow_run_with_failure(workflow_id, current_run_number):
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/workflows/{workflow_id}/runs?status=completed"
    response = requests.get(url, headers=get_headers())
    response.raise_for_status()
    runs = response.json()['workflow_runs']
    for run in runs:
        if run['run_number'] == current_run_number and run['conclusion'] == 'failure':
            return run
    return None


def convert_duration(seconds):
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours}h {minutes}m {seconds}s"


def send_slack_notification(message):
    try:
        response = client.chat_postMessage(
            channel=SLACK_CHANNEL,
            text=message,
        )
        print(f"Notification sent to Slack channel {SLACK_CHANNEL}.")
    except SlackApiError as e:
        print(f"Error sending Slack notification: {e}")


current_workflow_run = get_workflow_run(RUN_ID)
current_jobs = get_workflow_run_jobs(RUN_ID)
workflow_name = current_workflow_run['name']
commit_sha = current_workflow_run['head_sha']
commit_url = f"https://github.com/{REPO_OWNER}/{REPO_NAME}/commit/{commit_sha}"
workflow_url = current_workflow_run['html_url']


branch = current_workflow_run['head_branch']
previous_workflow_run = get_previous_workflow_run(
    REPO_OWNER, REPO_NAME, RUN_ID, branch, get_headers())

workflow_id = current_workflow_run['workflow_id']
current_run_number = current_workflow_run['run_number']
previous_same_run_number_workflow_run_with_failure = get_previous_same_run_number_workflow_run_with_failure(
    workflow_id, current_run_number)


# Calculate the build duration
created_at = datetime.strptime(
    current_workflow_run['created_at'], "%Y-%m-%dT%H:%M:%SZ")
updated_at = datetime.strptime(
    current_workflow_run['updated_at'], "%Y-%m-%dT%H:%M:%SZ")
duration_seconds = int((updated_at - created_at).total_seconds())

# Convert the duration to a human-readable format
duration_str = convert_duration(duration_seconds)

if any(job['conclusion'] == 'failure' for job in current_jobs):
    send_slack_notification(
        f":x: Workflow '{workflow_name}' run {RUN_ID} has failed jobs in {REPO_OWNER}/{REPO_NAME}.\n"
        f"Commit: <{commit_url}|{commit_sha[:7]}>\n"
        f"Workflow: <{workflow_url}|Link>"
    )
elif SEND_SUCCESS_MESSAGE and not any(job['conclusion'] == 'failure' for job in current_jobs):
    if (previous_workflow_run and previous_workflow_run['conclusion'] == 'failure') or previous_same_run_number_workflow_run_with_failure:
        send_slack_notification(
            f":white_check_mark: Workflow '{workflow_name}' run {RUN_ID} has succeeded in {REPO_OWNER}/{REPO_NAME} after previous failure.\n"
            f"Commit: <{commit_url}|{commit_sha[:7]}>\n"
            f"Workflow: <{workflow_url}|Link>\n"
            f"Build Duration: {duration_str}"
        )
