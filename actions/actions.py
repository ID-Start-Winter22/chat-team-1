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

import icalendar
from datetime import datetime, timedelta

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


        def fächerdict(datum) : 
            fächercount = []
            dict = {}
            # Kalender file öffnen
            with open('nine.ics', 'rb') as f:
                #Kalender file auslesen
                calendar = icalendar.Calendar.from_ical(f.read())
                

            # Durch die Events durchlaufen
            for component in calendar.walk():
                if component.name == "VEVENT":
                    vdt =  component.get('dtstart')
                    decode= str(icalendar.vDDDTypes.from_ical(vdt))
                    veranstaltung = str(component.get('summary'))
                    ort = component.get('location')
                    dict[decode]= veranstaltung, ort
            for i in dict: 
                if datum in i: 
                    veranstaltung =  (dict[i][0] )
                    dispatcher.utter_message(veranstaltung)
                    ort =  (dict[i][1] )
                    print(ort)
                    veranstaltungszeit = str(i)  
                    dispatcher.utter_message(veranstaltungszeit[11:-3:])
                    fächercount.append(str(i)) 
            if len(fächercount  ) == 0 : 
                    dispatcher.utter_message('Mhh ich sehe grade, dass du an dem gefragten Tag gar keine Vorlesung hast')
                
        def next_weekday(weekday: int) -> str : 
            # Get today's date and find the next weekday
            today = datetime.now()
            days_ahead = weekday - today.weekday()
            if days_ahead <= 0:  # Target day already happened this week
                days_ahead += 7
            datum = str(today + timedelta(days_ahead))
            datum_sort = datum[0:11]
            return datum_sort

        def tagesauswahl(wochentag) : 
            wochentage = ('montag', 'dienstag', 'mittwoch', 'donnerstag', 'freitag', 'samstag', 'sonntag')
            if wochentag == 'heute': 
                heute = str(datetime.today())
                datum = heute[0:11]
            if wochentag == 'morgen': 
                morgen = (int(datetime.today().weekday() +1 ))
                datum = next_weekday(morgen)
            if wochentag in wochentage: 
                tag_nummer =  wochentage.index(wochentag)
                datum = next_weekday(tag_nummer)
            fach = fächerdict(datum)
        try: 
            wochentag = tracker.get_slot('wochentag')
            
            wochentag = wochentag.lower() 
            if wochentag == 'samstag' or wochentag == 'sonntag': 
                dispatcher.utter_message('UHUUU da ist Wochenende. Da hat man doch keine Vorlesung sondern Freizeit. Genieß es und nimm dir auch mal etwas Zeit für dich selber. Ich gehe zum Beispiel sehr gerne Mäuse fangen an den Wochenenden!')
            else: 
                wochentag_richtig= wochentag[0].upper() + wochentag[1::]
                if wochentag== 'heute' or wochentag== 'morgen': 
                    dispatcher.utter_message(f'Du hast {wochentag} die Veranstaltungen:')
                    tagesauswahl(wochentag)
                else: 
                    dispatcher.utter_message(f'Du hast am {wochentag_richtig} die Veranstaltungen:')
                    tagesauswahl(wochentag)
        except: 
            dispatcher.utter_message('Das habe ich leider nicht Verstanden. Du hast wohl nach deinen Veranstaltungen gefragt. Bitte stelle sicher, dass du den Wochentag richtig schreibst. Ich versteh außerdem auch, wenn du mich frägst: \"Welches Fach habe ich heute/ morgen ?\" ')
        return[AllSlotsReset()]

class ActionUserName(Action):

    def name(self):
        return "frage_nach_funktionen"

    def run(self, dispatcher, tracker, domain):

        def antwort():
            antwort= ("Ich helfe dir bei der Organisation deines Unialltags und kann dir beispielsweise bei folgenden Fragen weiterhelfen: \n - Was habe ich heute für Fächer? \n - Wann beginnt die Vorlesung? \n - Wo findet die Voresung statt? \n - Was steht heute alles an? \n - Dich aufheitern, wenn es mal nicht so läuft \n - Dir einen Lageplan schicken Und noch einiges mehr. Probiers doch einfach mal aus :). ")

            dispatcher.utter_message(antwort)
        antwort() 

        return[]

class ActionUserName(Action):

     def name(self):
        return "Wann_Wo"

     def run(self, dispatcher, tracker, domain):

        try: 
            fächerproTag = {'montag': ('computational thinking ct','8: 15- 9:45', 'R0.058'), 'dienstag' : ('computational thinking ct', '10:00 - 11:30', 'E0.103'), 'mittwoch': ('grundlagen interface und interactionsdesign ui ux', '16:30 - 18:00', 'X1.018'), 'donnerstag': ('grundlagen gestaltung und typographie ggt', '13:00 - 16:15', 'X1.018'), 'freitag': ('projektmodul start pm', '10:30 - 13:30', 'Pavillion X - Gebäude')} 
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
                        dispatcher.utter_message(f'Das Fach {today[0]} im Raum {today[2]} ')
        except: 
            dispatcher.utter_message(f'Tut mir leid das verstehe ich noch nicht genau. um diese Funktion zu verwenden musst du mir genau den Tag und das Modul sagen. Und die Schlagwörter wo und wann verwenden. ')


        return[AllSlotsReset()]

class ActionUserName(Action):

     def name(self):
        return "zoom_link_antwort"
        

     def run(self, dispatcher, tracker, domain):
        fach = tracker.get_slot("Fach") 
        if fach : fach = fach.lower()
        try: 
            

            zoom_links = {'Computational Thinking CT':'https://bbb.cs.hm.edu/b/tho-ajk-ffr-bev' ,'Grundlagen Gestaltung und Typographie GGT':'https://hm-edu.zoom.us/my/karin.fischnaller?pwd=S252WnRzakNRSXZsS2VUT2tDeFhZdz09' , 'Grundlagen wissenschaftlichen arbeitens GWA':'https://hm-edu.zoom.us/j/5550698639?pwd=SlpQQ0hIbGoxMG54QllacUlDTWFOUT09'}
            
            for key in zoom_links:
                if fach in key.lower() : 
                    fach = key
                    link = zoom_links[key] 
                    break
            dispatcher.utter_message(f'Der Zoom link für das Fach {fach} lautet : {link}')
        except: dispatcher.utter_message('Für dieses Fach habe ich leider keinen Link gefunden')

        return[]

