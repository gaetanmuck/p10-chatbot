
import os, json
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.conversations import ConversationAnalysisClient
from dotenv import load_dotenv; load_dotenv()

def ask_clu(text):
    clu_endpoint = os.environ["AZURE_CONVERSATIONS_ENDPOINT"]
    clu_key = os.environ["AZURE_CONVERSATIONS_KEY"]
    project_name = os.environ["AZURE_CONVERSATIONS_PROJECT_NAME"]
    deployment_name = os.environ["AZURE_CONVERSATIONS_DEPLOYMENT_NAME"]

    client = ConversationAnalysisClient(clu_endpoint, AzureKeyCredential(clu_key))
    result = client.analyze_conversation(
        task={
            "kind": "Conversation",
            "analysisInput": {
                "conversationItem": {
                    "participantId": "1",
                    "id": "1",
                    "modality": "text",
                    "language": "en",
                    "text": text
                },
                "isLoggingEnabled": False
            },
            "parameters": {
                "projectName": project_name,
                "deploymentName": deployment_name,
                "verbose": True
            }
        }
    )

    entities = result['result']['prediction']['entities']
    toreturn = []
    for ent in entities:
        toreturn.append({'key': ent['category'], 'value': ent['text']})

    return toreturn