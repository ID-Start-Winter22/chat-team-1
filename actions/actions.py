# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from sys import displayhook
from typing import Any, Text, Dict, List
from pyparsing import nestedExpr
from datetime import datetime

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from . import mvg
import json

# NOTE(Michael): We could use this action to store the name in
#                the TrackerStore (in memory database) or a persitent DB
#                such as MySQL. But we need to store a key-value pair 
#                to identify the user by id eg. (user_id, slotvalue)
class ActionStoreUserName(Action):

     def name(self):
         return "action_store_name"
         
     def run(self, dispatcher, tracker, domain):
        username = tracker.get_slot("username")
        print("Sender ID: ", tracker.sender_id)

        return []


class ActionUserName(Action):

     def name(self):
         return "action_get_name"

     def run(self, dispatcher, tracker, domain):
        username = tracker.get_slot("username")
        if not username :
            dispatcher.utter_message(" Du hast mir Deinen Namen nicht gesagt.")
        else:
            dispatcher.utter_message(' Du bist {}'.format(username))

        return []

class ActionMVG(Action):

     def name(self):
         return "action_get_travel_time"

     def run(self, dispatcher, tracker, domain):
        from_station = tracker.get_slot("from_station")
        to_station = tracker.get_slot("to_station")
        if not from_station or not to_station :
            dispatcher.utter_message("Diese Stationen habe ich nicht erkannt!")
        else:
            result = json.loads(mvg.handle_route(from_station, to_station))
            print(result)
            if "error" in result:
                print("FEHLER!!!!!!!!!!!!")
                dispatcher.utter_message("Sorry! Ich habe da mindestens eine Station nicht erkannt!")
            else:
                origin = result["from"]
                destination = result["to"]
                time_needed = result["time_needed"]
                dispatcher.utter_message("Du brauchst exakt: {} Minuten von {} nach {}. Gute Reise!".format(time_needed, origin, destination))

        return []

class ActionUserName(Action):

     def name(self):
         return "fächerauswahl_tag"

     def run(self, dispatcher, tracker, domain):
        wochentag = (tracker.get_slot("wochentag")).lower()
        fächerproTag = {'montag': ('Computatuional Thinking','8: 15- 9:45'), 'dienstag' : ('Computatuional Thinking', '10:00 - 11:30'), 'mittwoch': ('Grundlagen interface und Interactionsdesign', '16:30 - 18:00'), 'donnerstag': ('Grundlagen Gestaltung und Typographie', '13:00 - 16:15'), 'freitag': ('Projektmodul Start', '10:30 - 13:30')} 
        wochentage = ['montag', 'dienstag', 'mittwoch', 'donnerstag', 'freitag']
        today = datetime.today().weekday()
        tomorrow = datetime.today().weekday() + 1 
        dispatcher.utter_message(wochentag)
        if wochentag in fächerproTag: 
            dispatcher.utter_message(f'{fächerproTag[wochentag]}')

        if wochentag == 'heute': 
            
            today_name = wochentage[today]
            dispatcher.utter_message(fächerproTag[today_name])
        if wochentag =='morgen': 
            tomorrow_name = wochentage[tomorrow]
            dispatcher.utter_message(fächerproTag[tomorrow_name])

        


        return []