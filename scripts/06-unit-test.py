import os, json, requests, time
import dotenv; dotenv.load_dotenv()

# Get environment variables
print('[UNIT-TEST]: Load variables...')

endpoint = os.environ.get('CLU_ENDPOINT')
resource_key = os.environ.get('CLU_RESOURCE_KEY')
project_name = os.environ.get('CLU_PROJECT_NAME')
deployment_name = os.environ.get('CLU_DEPLOYMENT_NAME')
model_name = os.environ.get('CLU_MODEL_NAME')
clu_api_version_test = os.environ.get('CLU_API_VERSION_TEST')

if not endpoint: raise SystemExit('> Environment variable [CLU_ENDPOINT] is missing')
if not resource_key: raise SystemExit('> Environment variable [CLU_RESOURCE_KEY] is missing')
if not project_name: raise SystemExit('> Environment variable [CLU_PROJECT_NAME] is missing')
if not deployment_name: raise SystemExit('> Environment variable [CLU_DEPLOYMENT_NAME] is missing')
if not clu_api_version_test: raise SystemExit('> Environment variable [CLU_API_VERSION_TEST] is missing')


print('[UNIT-TEST]: Prepare the API call...')

# Create the URL
url = f"{endpoint}language/:analyze-conversations?api-version={clu_api_version_test}"


# Create headers
headers = {
    "Ocp-Apim-Subscription-Key": resource_key
}

# Create the body
body = {
  "kind": "Conversation",
  "analysisInput": {
    "conversationItem": {
      "id": "1",
      "participantId": "1",
      "text": "I would like to book a flight from Paris to New York on the 1st of december."
    }
  },
  "parameters": {
    "projectName": project_name,
    "deploymentName": deployment_name,
    "stringIndexType": "TextElement_V8"
  }
}


# Make the API call
print('[UNIT-TEST]: Making the API call...')
response = requests.post(url, headers=headers, json=body).json()

# INTENT
assert response['result']['prediction']['topIntent'] == 'BookFlight'

# ENTITIES
entities = response['result']['prediction']['entities']
for ent in entities:
    if ent['category'] == 'origin': assert ent['text'] == 'Paris'
    if ent['category'] == 'destination': assert ent['text'] == 'New York'
    if ent['category'] == 'go_date': assert ent['text'] == '1st of december'

print('[UNIT-TEST]: All unit tests passed')