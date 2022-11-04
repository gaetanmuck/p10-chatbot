import os, json, requests, time
import dotenv; dotenv.load_dotenv()

# Get environment variables
print('[TRAIN-MODEL]: Load variables...')
endpoint = os.environ.get('CLU_ENDPOINT')
if not endpoint: raise SystemExit('> Environment variable [CLU_ENDPOINT] is missing')
project_name = os.environ.get('CLU_PROJECT_NAME')
if not project_name: raise SystemExit('> Environment variable [CLU_PROJECT_NAME] is missing')
clu_api_version = os.environ.get('CLU_API_VERSION')
if not clu_api_version: raise SystemExit('> Environment variable [CLU_API_VERSION] is missing')
clu_model_version = os.environ.get('CLU_MODEL_VERSION')
if not clu_model_version: raise SystemExit('> Environment variable [CLU_MODEL_VERSION] is missing')
resource_key = os.environ.get('CLU_RESOURCE_KEY')
if not resource_key: raise SystemExit('> Environment variable [CLU_RESOURCE_KEY] is missing')
model_name = os.environ.get('CLU_MODEL_NAME')
if not model_name: raise SystemExit('> Environment variable [CLU_MODEL_NAME] is missing')


print('[TRAIN-MODEL]: Prepare the API call...')

# Create the URL
url = f"{endpoint}/language/authoring/analyze-conversations/projects/{project_name}/:train?api-version={clu_api_version}"


# Create headers
headers = {
    "Ocp-Apim-Subscription-Key": resource_key
}


# Create the body
body = {
    "modelLabel": model_name,
    "trainingConfigVersion": clu_model_version,
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
print(response.headers)
# print(json.dumps(response.json(), indent=2))
check_url = response.headers['operation-location']


# Check status
print('[TRAIN-MODEL]: Waiting on Job status success...')
print('', end='')

while True:
    time.sleep(3)
    response = requests.get(check_url, headers=headers)
    body = response.json()
    print('[TRAIN-MODEL]: Training:', body['result']['trainingStatus']['percentComplete'], '% - Evaluation:', body['result']['evaluationStatus']['percentComplete'], '%')
    if body['status'] == "succeeded": break
