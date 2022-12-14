# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"
from rasa_sdk.events import AllSlotsReset
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
        dispatcher.utter_message("Sender ID: ", tracker.sender_id)

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
            dispatcher.utter_message(result)
            if "error" in result:
                dispatcher.utter_message("FEHLER!!!!!!!!!!!!")
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


        wochentag= tracker.get_slot("wochentag")
        if wochentag : wochentag = wochentag.lower()
        fächerproTag = {'montag': ('Computational Thinking','8: 15- 9:45'), 'dienstag' : ('Computational Thinking', '10:00 - 11:30'), 'mittwoch': ('Grundlagen Interface und Interactionsdesign', '16:30 - 18:00'), 'donnerstag': ('Grundlagen Gestaltung und Typographie', '13:00 - 16:15'), 'freitag': ('Projektmodul Start', '10:30 - 13:30'), 'samstag': 'Es ist Wochenende. Da hat man keine Vorlesung sondern Freizeit. Lass es dir auch mal etwas gut gehen ', 'sonntag': ' Es ist Wochenende. Da hat man keine Vorlesung sondern Freizeit. Lass es dir auch mal etwas gut gehen'} 
        wochenliste = ['montag', 'dienstag', 'mittwoch', 'donnerstag', 'freitag','samstag', 'sonntag']

        today = datetime.today().weekday()

        today= wochenliste[today]
        today= fächerproTag[today]


        if not wochentag: 
            dispatcher.utter_message('Das habe ich entweder nicht verstanden oder du hast was vercheckt und du frägst mich gerade ernsthaft ob du am Wochenende eine Vorlesung hast :)')

        elif wochentag in fächerproTag: 
            dispatcher.utter_message(f'Du hast am {wochentag} die Fächer {fächerproTag[wochentag][0]} um {fächerproTag[wochentag][1]}')

        elif wochentag == 'heute' : 
            dispatcher.utter_message(f'Du hast heute das Fach {today[0]} um {today[1]} ')

        elif wochentag == 'morgen': 
            tomorrow = datetime.today().weekday()
            tomorrow += 1 
            tomorrow %= len(wochenliste)
            wochenendcount = tomorrow
            tomorrow = wochenliste[tomorrow]
            
            if wochenendcount <= 4: 
                tomorrow = fächerproTag[tomorrow]
                dispatcher.utter_message(f'Du hast morgen das Fach {tomorrow[0]} um  {tomorrow[1]} ')
            else: 
                dispatcher.utter_message('Es ist Wochenende. Da hat man keine Vorlesung sondern Freizeit. Lass es dir auch mal etwas gut gehen  ')
            del wochentag 

        else: 
            if wochentag== 'samstag' or wochentag == 'sonntag' : 
                dispatcher.utter_message('Es ist wochenende. Da hat man keine Vorlesung sondern Freizeit. Lass es dir auch mal etwas gut gehen ')
            else: dispatcher.utter_message('Das hab ich jetzt nicht verstanden. Frag doch bitte nochmal genuaer wenn es um deinen Stundenplan ging.')


        return[AllSlotsReset()]

class ActionUserName(Action):

    def name(self):
        return "frage_nach_funktionen"

    def run(self, dispatcher, tracker, domain):
        antwort= ("Ich helfe dir bei der Organisation deines Unialltags und kann dir beispielsweise bei folgenden Fragen weiterhelfen: \n - Was habe ich heute für Fächer? \n - Wann beginnt die Vorlesung? \n - Wo findet die Voresung statt? \n - Was steht heute alles an? \n - Dich aufheitern, wenn es mal nicht so läuft \n - Dir einen Lageplan schicken Und noch einiges mehr. Probiers doch einfach mal aus :). ")

        dispatcher.utter_message(antwort)

        return[]

class ActionUserName(Action):

     def name(self):
        return "Wann_Wo"

     def run(self, dispatcher, tracker, domain):

        try: 
            fächerproTag = {'montag': ('computational thinking ct','8: 15- 9:45', 'R0.058'), 'dienstag' : ('computational thinking ct', '10:00 - 11:30', 'E0.103'), 'mittwoch': ('grundlagen interface und interactionsdesign ui ux', '16:30 - 18:00', 'X1.018'), 'donnerstag': ('grundlagen gestaltung und typographie ggt', '13:00 - 16:15', 'X1.018'), 'freitag': ('projektmodul start pm', '10:30 - 13:30', 'Pavillion X - Gebäude'), 'samstag': 'Es ist Wochenende. Da hat man keine Vorlesung sondern Freizeit. Lass es dir auch mal etwas gut gehen ', 'sonntag': ' Es ist Wochenende. Da hat man keine Vorlesung sondern Freizeit. Lass es dir auch mal etwas gut gehen'} 
            wochenliste = ['montag', 'dienstag', 'mittwoch', 'donnerstag', 'freitag','samstag', 'sonntag']


            today = datetime.today().weekday()
            today= wochenliste[today]
            today= fächerproTag[today]

            frage = tracker.get_slot("Anfrage")
            if frage : frage=frage.lower()
            fach = tracker.get_slot("Fach") 
            if fach : fach = fach.lower()
            wochentag = tracker.get_slot("wochentag")
            if wochentag : wochentag = wochentag.lower() 

            
            if wochentag: 
                if fach and fach in fächerproTag[wochentag][0]: 

                    if frage == 'wann': 
                        dispatcher.utter_message(f'Du hast das Fach {fächerproTag[wochentag][0]} am {wochentag}  um {fächerproTag[wochentag][1]} ') 

                    if frage == 'wo': 
                        dispatcher.utter_message(f'Du hast das Fach {fächerproTag[wochentag][0]} am {wochentag}  im {fächerproTag[wochentag][2]} ')
                        #Lageplan


                if not fach or fach not in fächerproTag[wochentag][0]: 
                    dispatcher.utter_message(f'UHUUUUU! Ich glaube du hast das Fach am {wochentag} gar nicht. Aber du hast an diesem Tag: ')

                    if frage =='wann':
                        dispatcher.utter_message(f'Das Fach {fächerproTag[wochentag][0]} um {fächerproTag[wochentag][1]} ')
                    if frage =='wo':
                        dispatcher.utter_message(f'Das Fach {fächerproTag[wochentag][0]} im Raum {fächerproTag[wochentag][2]} ')

            if not wochentag or wochentag == 'heute': 
                wochentag= 'heute'

                if fach and fach in today[0]: 

                    if frage == 'wann': 
                        dispatcher.utter_message(f'Du hast heute das Fach {today[0]} um {today[1]}') 
                    if frage == 'wo': 
                        dispatcher.utter_message(f'Du hast heute das Fach {today[0]} im Raum: {today[2]}')
                        #Lageplan einfügen 

                if not fach or fach not in today[0]: 
                    dispatcher.utter_message('Ich glaube du hast das Fach heute gar nicht. Aber du hast heute: ')

                    if frage =='wann':
                        dispatcher.utter_message(f'Das Fach {today[0]} um {today[1]} ')
                    if frage =='wo':
                        dispatcher.utter_message(f'Das Fach {today[0]} im Raum {today[1]} ')
        except: 
            dispatcher.utter_message(f'Tut mir leid das verstehe ich noch nicht genau. um diese Funktion zu verwenden musst du mir genau den Tag und das Modul sagen. Und die Schlagwörter wo und wann verwenden. ')


        return[AllSlotsReset()]

# class ActionUserName(Action):

#      def name(self):
#          return "Organisations_Hauptfunktion"

#      def run(self, dispatcher, tracker, domain):
#         #slots holen und strings anpassen 
#         frage = tracker.get_slot("Anfrage")
#         if frage : frage=frage.lower()
#         fach = tracker.get_slot("Fach") 
#         if fach : fach = fach.lower()
#         wochentag = tracker.get_slot("wochentag")
#         if wochentag : wochentag = wochentag.lower() 

#         #dictionaries mit informationen holen 
#         fächerproTag = {'montag': ('Computational Thinking CT','8: 15- 9:45', 'R0.058'), 'dienstag' : ('computational thinking ct', '10:00 - 11:30', 'E0.103'), 'mittwoch': ('grundlagen interface und interactionsdesign ui ux', '16:30 - 18:00', 'X1.018'), 'donnerstag': ('grundlagen gestaltung und typographie ggt', '13:00 - 16:15', 'X1.018'), 'freitag': ('projektmodul start pm', '10:30 - 13:30', 'Pavillion X - Gebäude'), 'samstag': 'Es ist Wochenende. Da hat man keine Vorlesung sondern Freizeit. Lass es dir auch mal etwas gut gehen ', 'sonntag': ' Es ist Wochenende. Da hat man keine Vorlesung sondern Freizeit. Lass es dir auch mal etwas gut gehen'} 
#         wochenliste = ['montag', 'dienstag', 'mittwoch', 'donnerstag', 'freitag','samstag', 'sonntag']
#         today = datetime.today().weekday()
#         today= wochenliste[today]
        
#         #fehler wenn frage nach wochenende
#         if wochentag =='samstag' or wochentag== "sonntag" or today == 'samstag' or today == 'sonntag': 
#             dispatcher.utter_message(fächerproTag('samstag'))

#         # dictionary öffenen mit tag 
#         elif wochentag and wochentag in fächerproTag: 
#             value_tag = fächerproTag[wochentag] #dict. ist jetzt offen inhalt in value_tag gespeichert 
            
#             # suche nach Fach welches ich auslesen möchte 
#             fach = fach.split()
#             if fach: 
#                 for i in fach: 
#                     if i in value_tag[0].lower(): 
#                         fach_ausgabe = value_tag[0] 
#                         break 
#                     if i not in fach: 
#                         fach_ausgabe = 'UHUU da hab ich das Fach leider nicht gefunden . Könntest du deine frage noch einmal stellen?'

#             if fach_ausgabe != 'UHUU da hab ich das Fach leider nicht gefunden. Könntest du deine frage noch einmal stellen?':
#                 if frage == 'was':
#                     dispatcher.utter_message(f'Du hast am {wochentag} die Fächer: {value_tag[0]} ')
#                 elif frage =="wo": 
#                     dispatcher.utter_message(f'Du hast das {fach_ausgabe} im Raum: {value_tag[2]}')
#                 elif frage == "wann": 
#                     dispatcher.utter_message(f'Du hast das {fach_ausgabe} um {value_tag[1]}')
#                 else: 
#                     dispatcher.utter_message(f"mhhh ich weiß leider nicht was du genau von mir wolltest... kannst du dene Frage bitte noch einmal wiederholen?")


                    
#             # fehler wenn kein fach oder falsches fach 
#             else : dispatcher.utter_message('UHUU da hab ich das Fach leider nicht gefunden. Könntest du deine frage noch einmal stellen? Vielleicht hast ud das Fach an einem anderen Tag')

#         return[AllSlotsReset()]