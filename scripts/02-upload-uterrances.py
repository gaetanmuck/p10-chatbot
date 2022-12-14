import os, json, requests, time
import dotenv; dotenv.load_dotenv()

# Get environment variables
print('[UPLOAD-UTTERANCES]: Load variables...')

utterances_path = os.environ.get('PATH_UTTERANCES')
endpoint = os.environ.get('CLU_ENDPOINT')
project_name = os.environ.get('CLU_PROJECT_NAME')
clu_api_version_upload = os.environ.get('CLU_API_VERSION_UPLOAD')
resource_key = os.environ.get('CLU_RESOURCE_KEY')
language_code = os.environ.get('CLU_LANGUAGE_CODE')

if not utterances_path: raise SystemExit('> Environment variable [PATH_UTTERANCES] is missing')
if not endpoint: raise SystemExit('> Environment variable [CLU_ENDPOINT] is missing')
if not project_name: raise SystemExit('> Environment variable [CLU_PROJECT_NAME] is missing')
if not clu_api_version_upload: raise SystemExit('> Environment variable [CLU_API_VERSION_UPLOAD] is missing')
if not resource_key: raise SystemExit('> Environment variable [CLU_RESOURCE_KEY] is missing')
if not language_code: raise SystemExit('> Environment variable [CLU_LANGUAGE_CODE] is missing')


# Read utterances
print('[UPLOAD-UTTERANCES]: Read utterances...')
file = open(utterances_path)
utterances = json.load(file)
file.close()


print('[UPLOAD-UTTERANCES]: Prepare the API call...')

# Create the URL
url = f"{endpoint}language/authoring/analyze-conversations/projects/{project_name}/:import?api-version={clu_api_version_upload}"


# Create headers
headers = {
    "Ocp-Apim-Subscription-Key": resource_key
}


# Create the body
body = {
    "projectFileVersion": clu_api_version_upload,
    "stringIndexType": "Utf16CodeUnit",
    "metadata": {
        "projectKind": "Conversation",
        "settings": {"confidenceThreshold": 0.7},
        "projectName": project_name,
        "multilingual": True,
        "description": "Trying out CLU",
        "language": language_code
    },
    "assets": {
        "projectKind": "Conversation",
        "intents": [{"category": "BookFlight"}],
        "entities": [
            {"category": "destination"},
            {"category": "origin"},
            {"category": "go_date"},
            {"category": "back_date"},
            {"category": "budget"}
        ],
        "utterances": utterances
    }
}

# Make the API call
print('[UPLOAD-UTTERANCES]: Making the API call...')
response = requests.post(url, headers=headers, json=body)
check_url = response.headers['operation-location']

# Check status
print('[UPLOAD-UTTERANCES]: Waiting on Job status success...')
print('', end='')

while True:
    time.sleep(1)
    response = requests.get(check_url, headers=headers)
    if response.json()['status'] == "succeeded": break
