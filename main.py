import os
import requests
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

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

if any(job['conclusion'] == 'failure' for job in current_jobs):
    send_slack_notification(
        f":x: Workflow '{workflow_name}' run {RUN_ID} has failed jobs in {REPO_OWNER}/{REPO_NAME}.\n"
        f"Commit: <{commit_url}|{commit_sha[:7]}>\n"
        f"Workflow: <{workflow_url}|Link>"
    )
elif SEND_SUCCESS_MESSAGE and not any(job['conclusion'] == 'failure' for job in current_jobs):
    send_slack_notification(
        f":white_check_mark: Workflow '{workflow_name}' run {RUN_ID} has succeeded in {REPO_OWNER}/{REPO_NAME}.\n"
        f"Commit: <{commit_url}|{commit_sha[:7]}>\n"
        f"Workflow: <{workflow_url}|Link>"
    )
