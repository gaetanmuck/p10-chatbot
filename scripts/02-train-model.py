import os, json, requests, time
import dotenv; dotenv.load_dotenv()

# Get environment variables
print('[TRAIN-MODEL]: Load variables...')
endpoint = os.environ.get('CLU_ENDPOINT')
project_name = os.environ.get('CLU_PROJECT_NAME')
clu_api_version_upload = os.environ.get('CLU_API_VERSION_UPLOAD')
clu_api_version_train = os.environ.get('CLU_API_VERSION_TRAIN')
resource_key = os.environ.get('CLU_RESOURCE_KEY')
model_name = os.environ.get('CLU_MODEL_NAME')

if not endpoint: raise SystemExit('> Environment variable [CLU_ENDPOINT] is missing')
if not project_name: raise SystemExit('> Environment variable [CLU_PROJECT_NAME] is missing')
if not clu_api_version_upload: raise SystemExit('> Environment variable [CLU_API_VERSION_UPLOAD] is missing')
if not clu_api_version_train: raise SystemExit('> Environment variable [CLU_API_VERSION_TRAIN] is missing')
if not resource_key: raise SystemExit('> Environment variable [CLU_RESOURCE_KEY] is missing')
if not model_name: raise SystemExit('> Environment variable [CLU_MODEL_NAME] is missing')


print('[TRAIN-MODEL]: Prepare the API call...')

# Create the URL
url = f"{endpoint}/language/authoring/analyze-conversations/projects/{project_name}/:train?api-version={clu_api_version_upload}"


# Create headers
headers = {
    "Ocp-Apim-Subscription-Key": resource_key
}


# Create the body
body = {
    "modelLabel": model_name,
    "trainingConfigVersion": clu_api_version_train,
    "trainingMode": 'standard',
    "evaluationOptions": {
        "kind": "percentage",
        "testingSplitPercentage": 20,
        "trainingSplitPercentage": 80
    }
}


# Make the API call
print('[TRAIN-MODEL]: Making the API call...')
response = requests.post(url, headers=headers, json=body)
check_url = response.headers['operation-location']


# Check status
print('[TRAIN-MODEL]: Waiting on Job status success...')

while True:
    time.sleep(3)
    response = requests.get(check_url, headers=headers)
    body = response.json()
    print('[TRAIN-MODEL]: Training:', body['result']['trainingStatus']['percentComplete'], '% - Evaluation:', body['result']['evaluationStatus']['percentComplete'], '%')
    if body['status'] == "succeeded": break
