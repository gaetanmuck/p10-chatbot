import os, json, requests
from IPython.display import display
import pandas as pd
import dotenv; dotenv.load_dotenv()

# Get environment variables
print('[GET-EVALUATION]: Load variables...')

endpoint = os.environ.get('CLU_ENDPOINT')
project_name = os.environ.get('CLU_PROJECT_NAME')
clu_api_version_eval = os.environ.get('CLU_API_VERSION_EVAL')
resource_key = os.environ.get('CLU_RESOURCE_KEY')
model_name = os.environ.get('CLU_MODEL_NAME')

if not endpoint: raise SystemExit('> Environment variable [CLU_ENDPOINT] is missing')
if not project_name: raise SystemExit('> Environment variable [CLU_PROJECT_NAME] is missing')
if not clu_api_version_eval: raise SystemExit('> Environment variable [CLU_API_VERSION_EVAL] is missing')
if not resource_key: raise SystemExit('> Environment variable [CLU_RESOURCE_KEY] is missing')
if not model_name: raise SystemExit('> Environment variable [CLU_MODEL_NAME] is missing')


print('[GET-EVALUATION]: Prepare the API call...')

# Create the URL
url = f"{endpoint}/language/authoring/analyze-conversations/projects/{project_name}/models/{model_name}/evaluation/summary-result?api-version={clu_api_version_eval}"


# Create headers
headers = {
    "Ocp-Apim-Subscription-Key": resource_key
}


# Make the API call
print('[GET-EVALUATION]: Making the API call...')
response = requests.get(url, headers=headers)
body = response.json()

# temp
# print(response.headers)
# print(json.dumps(body, indent=2))

# Display evaluation report
print(' ===== Evaluation report ===== ')
print('> Entities confusion (ordered confusion rate, 0% confusions are not displayed)')

conf_mat = body['entitiesEvaluation']['confusionMatrix']
entities = ['$none', 'origin', 'destination', 'budget', 'go_date', 'back_date']

confusions = []
for label in entities:
    for predict in entities:
        if label not in conf_mat: continue
        if predict not in conf_mat[label]: continue
        if label == predict: continue
        confusions.append({'label': label, 'predict': predict, 'rate': conf_mat[label][predict]['normalizedValue']})

confusions.sort(key=lambda x:x['rate'])

for conf in confusions:
    print(f'>  {round(conf["rate"], 2)}% of the time [{conf["label"]}] have been confused as [{conf["predict"]}]')