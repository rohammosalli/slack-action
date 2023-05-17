# Custom GitHub Action for Slack Notification:

Custom GitHub Action for Slack Notification: Sends Slack notifications when failed build jobs become green again
 
 ### features
1. Connects to the GitHub API to fetch information about workflow runs and jobs.
2. Sends Slack notifications using a Slack bot token for authentication.
3. Notifies about failed jobs in a workflow run, with relevant information and links.
4. Optionally sends notifications for successful workflow runs based on the SEND_SUCCESS_NOTIFICATIONS environment variable.
5. Send a success message if the last build failed but the current build was successful.
6. Send a success message if the current build is successful after retrying the same workflow run with previously failed jobs.
7. Send a message if there was a failed build.
8. Added build duration in a successful build
### How use it in Github action 

```yaml
slack_notification:
    needs: [first-job, second-job]
    if: always()
    runs-on: ubuntu-latest
    steps:
      - name: Checkout codee
        uses: actions/checkout@v3
      - name: Run Slack Notification
        uses: rohammosalli/slack-action@master
        env:
          SLACK_BOT_TOKEN: ${{ secrets.MY_SLACK_TOKEN }}
          SLACK_CHANNEL: "Your Channel"
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          GITHUB_RUN_ID: ${{ github.run_id }}
          REPO_OWNER: ${{ github.repository_owner }}
          REPO_NAME: ${{ github.event.repository.name }}
          RUN_ID: ${{ github.run_id }}
          SEND_SUCCESS_MESSAGE: "true"
```

To disable the sending of Slack messages upon successful completion, simply set the environment variable SEND_SUCCESS_MESSAGE to 'false'. 


### Slack config
##### To create a Slack bot for your workspace and integrate it with this code, follow these steps:

1. Go to https://api.slack.com/apps and sign in to your Slack account.
2. Click the "Create New App" button.
3. Choose a name for your app and select the workspace where you want the app to be developed, then click "Create App".
4. From the "Add features and functionality" section, click on "Bots".
5. Click the "Add a Bot User" button to add a bot user to your app. Fill in the required details and click "Add Bot User".
6. Go to the "OAuth & Permissions" page in the sidebar menu.
7. Scroll down to the "Scopes" section and add the necessary bot token scopes. For this code, you will need to add the chat:write scope.
8. Scroll back up and click "Install App to Workspace". You will be prompted to authorize the app in your workspace. Click "Allow".
9. Once the app is installed, you will see the "Bot User OAuth Token" under the "OAuth & Permissions" page. Copy this token and set it as the SLACK_BOT_TOKEN environment variable in your code.
10. Invite the bot to the desired channel in your Slack workspace by typing @bot_username and selecting the bot from the list. Click "Invite".

### Github Token 
##### To create a GitHub token, follow these steps:

1. Sign in to your GitHub account and go to your account settings by clicking on your profile picture in the top-right corner.
2. In the settings sidebar, click on "Developer settings".
3. In the "Developer settings" sidebar, click on "Personal access tokens".
4. Click the "Generate new token" button.
5. Give your token a descriptive name in the "Note" field, so you can remember its purpose later.
6. Select the necessary scopes for your token. For the provided code, you need to grant the repo scope, which allows the token to access repositories and perform various actions.
7. Click the "Generate token" button at the bottom of the page.
8. After generating the token, copy the token value. Important: This is the only time you will be able to see the token value, so make sure you copy it now.
10. Set the copied token value as the GITHUB_TOKEN environment variable in your code.

