import os, json, requests, time
import dotenv; dotenv.load_dotenv()

# Get environment variables
print('[DEPLOY-MODEL]: Load variables...')

endpoint = os.environ.get('CLU_ENDPOINT')
resource_key = os.environ.get('CLU_RESOURCE_KEY')
project_name = os.environ.get('CLU_PROJECT_NAME')
deployment_name = os.environ.get('CLU_DEPLOYMENT_NAME')
model_name = os.environ.get('CLU_MODEL_NAME')
clu_api_version_deploy = os.environ.get('CLU_API_VERSION_DEPLOY')

if not endpoint: raise SystemExit('> Environment variable [CLU_ENDPOINT] is missing')
if not resource_key: raise SystemExit('> Environment variable [CLU_RESOURCE_KEY] is missing')
if not project_name: raise SystemExit('> Environment variable [CLU_PROJECT_NAME] is missing')
if not deployment_name: raise SystemExit('> Environment variable [CLU_DEPLOYMENT_NAME] is missing')
if not model_name: raise SystemExit('> Environment variable [CLU_MODEL_NAME] is missing')
if not clu_api_version_deploy: raise SystemExit('> Environment variable [CLU_API_VERSION_DEPLOY] is missing')


print('[DEPLOY-MODEL]: Prepare the API call...')

# Create the URL
url = f"{endpoint}language/authoring/analyze-conversations/projects/{project_name}/deployments/{deployment_name}?api-version={clu_api_version_deploy}"


# Create headers
headers = {
    "Ocp-Apim-Subscription-Key": resource_key
}

# Create the body
body = {
    "trainedModelLabel": model_name
}


# Make the API call
print('[DEPLOY-MODEL]: Making the API call...')
response = requests.put(url, headers=headers, json=body)
check_url = response.headers['operation-location']


# Check status
print('[DEPLOY-MODEL]: Waiting on Job status success...')

while True:
    time.sleep(3)
    response = requests.get(check_url, headers=headers)
    body = response.json()
    if body['status'] == "succeeded": break
