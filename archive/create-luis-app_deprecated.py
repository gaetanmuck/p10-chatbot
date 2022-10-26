# This script is not needed anymore: Microsoft is removing LUIS, so it is impossible to create LUIS app anymore
# They introduced the CLU.
# I won't use this code anymore. 
# To train the model, I will use the GUI


# import json
# import os
# import pandas as pd
# import time
# import datetime
# from pprint import pprint

# from azure.cognitiveservices.language.luis.authoring import LUISAuthoringClient
# from msrest.authentication import CognitiveServicesCredentials


# from dotenv import load_dotenv
# load_dotenv()


# version_id = '0.1'

# def create_flight_reservation_app(subscription_key, version_id):
#     """This function creates a LUIS Flight Booking application, train and publish it."""
    
#     client = LUISAuthoringClient(
#         'https://westus.api.cognitive.microsoft.com',
#         CognitiveServicesCredentials(subscription_key),
#     )

#     try:
#         # Create a LUIS app
#         default_app_name = "FlyMeBot-{}".format(datetime.datetime.now())
#         print("Creating App {}, version {}".format(default_app_name, version_id))
#         app_id = client.apps.add({
#             'name': default_app_name,
#             'initial_version_id': version_id,
#             'description': "FlyMeBot application created by Python code",
#             'culture': 'en-us',
#         })
#         print("Created app {}".format(app_id))

#         # Add information into the model (parameters)
#         print("\nWe'll create 5 new entities.")
#         # Origin
#         print("The \"Origin\" simple entity will hold the departure.")
#         origin_name = "origin"
#         origin_id = client.model.add_entity(app_id, version_id, origin_name)
#         print(">> {} created with id {}".format(origin_name, origin_id))
#         # Destination
#         print("The \"Destination\" simple entity will hold the flight destination.")
#         destination_name = "destination"
#         destination_id = client.model.add_entity(app_id, version_id, destination_name)
#         print(">> {} created with id {}".format(destination_name, destination_id))
#         # Going date
#         print("The \"Go date\" datetime entity of the departure.")
#         go_date_name = "go_date"
#         go_date_id = client.model.add_entity(app_id, version_id, go_date_name)
#         print(">> {} created with id {}".format(go_date_name, go_date_id))
#         # Coming back date
#         print("The \"Back date\" datetime entity of the coming back.")
#         back_date_name = "back_date"
#         back_date_id = client.model.add_entity(app_id, version_id, back_date_name)
#         print(">> {} created with id {}".format(back_date_name, back_date_id))
#         # Budget
#         print("The \"Budget\" Currency entity for the total trip.")
#         total_price_name = "budget"
#         total_price_id = client.model.add_entity(app_id, version_id, total_price_name)
#         print(">> {} created with id {}".format(total_price_name, total_price_id))

#         # Add information into the model
#         print("\nWe'll now create the \"Flight\" composite entity including the fives entities.")
#         flight_name = "Flight"
#         flight_id = client.model.add_composite_entity(app_id, version_id, name=flight_name, children=[origin_name, origin_date_name, destination_name, destination_date_name, total_price_name])
#         print("{} composite entity created with id {}".format(flight_name, flight_id))


#         # Fetch utterances
#         utterances = pd.read_csv('../data/utterances.csv')
#         utterances = json.loads(utterances.to_json(orient='records'))

#         # Add intent to the model
#         utterances_result = client.examples.batch(app_id, version_id, utterances)
#         print("\nUtterances added to the {} intent".format('BookFlight'))

#         # Training the model
#         print("\nWe'll start training your app...")
#         async_training = client.train.train_version(app_id, version_id)

#         is_trained = async_training.status == "UpToDate"
#         trained_status = ["UpToDate", "Success"]
#         while not is_trained:
#             time.sleep(1)
#             status = client.train.get_status(app_id, version_id)
#             is_trained = all(m.details.status in trained_status for m in status)
#         print("Your app is trained. You can now go to the LUIS portal and test it!")

#         # Publish the app
#         print("\nWe'll start publishing your app...")
#         publish_result = client.apps.publish(app_id, {'version_id': version_id, 'is_staging': False, 'region': 'westus'})
#         endpoint = publish_result.endpoint_url + "?subscription-key=" + subscription_key + "&q="
#         print("Your app is published. You can now go to test it on\n{}".format(endpoint))

#     except Exception as err:
#         print("Encountered exception. {}".format(err))


# create_flight_reservation_app(os.environ.get("SUBSCRIPTION_KEY_ENV_NAME"), version_id)