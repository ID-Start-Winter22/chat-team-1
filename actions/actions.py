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

class ActionFächerauswahlTag(Action):

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
                    ort =  (dict[i][1] )
                    veranstaltungszeit = str(i)  
                    ort = str(ort)
                    dispatcher.utter_message(f' {veranstaltung} um {veranstaltungszeit[11:-3:]} im Raum {ort} ' )
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

class ActionWannWo(Action):
    
     def name(self):
        return "Wann_Wo"

     def run(self, dispatcher, tracker, domain):

        def fächerdict(datum) : 
    
            fächer_am_tag = []
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
                    ort =  (dict[i][1] )
                    veranstaltungszeit = str(i)  
                    ort = str(ort)
                    fach_info = []
                    fach_info.append(veranstaltung)
                    fach_info.append(veranstaltungszeit)
                    fach_info.append(ort)
                    fächer_am_tag.append(tuple(fach_info) )
                    fächercount.append(str(i)) 
            if len(fächercount) == 0 : 
                    dispatcher.utter_message('Mhh ich sehe grade, dass du an dem gefragten Tag gar keine Vorlesung hast')

            return fächer_am_tag


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
            fächer_am_tag = fächerdict(datum)
            
            return fächer_am_tag



        def fach_select(fächer_am_tag, fach) : #Filter Funktion für Fachauswahl für die Vorlesung keine gute Rechtschreibung kein PrOPlem es reicht wenn man Anfangsbuchtstabe der Fächer nimmt. Co Pr = Computational Thinking Prakitkum
            selectionlist= 'Eintrag nicht gefunden'  #hat mich Nerven gekostet, dass auch ja das richtige Fach rauskommt, auch wenn sich Namen überschneiden. Montag CT VL und CT Praktikum
                                                    #nur Praktikum wenn danach gefragt wird ! 
            
            zwischencounter = 0
            for eintrag in fächer_am_tag: 
                truecounter = 0 
                for wort in fach: 
                    if wort in eintrag[0].lower(): 
                        truecounter += 1 

                if truecounter > zwischencounter: 
                    selectionlist = eintrag
                zwischencounter = truecounter
                
            return selectionlist



        def tag_selection(fächer_am_tag, fach) : 
            selectionlist= 'Eintrag nicht gefunden'
                                                    
            
            zwischencounter = 0
            for eintrag in fächer_am_tag: 
                truecounter = 0 
                for wort in fach: 
                    if wort in eintrag.lower(): 
                        truecounter += 1 

                if truecounter > zwischencounter: 
                    selectionlist = eintrag
                zwischencounter = truecounter
                
            return selectionlist



        


        try: 
            wochentag = tracker.get_slot('wochentag')
            if wochentag == None: 
                wochentag = 'heute'
            fach = tracker.get_slot('Fach')
            wochentage = ('montag', 'dienstag', 'mittwoch', 'donnerstag', 'freitag', 'samstag', 'sonntag')
            anfrage = tracker.get_slot('Anfrage')
            anfrage=anfrage.lower() 
            dispatcher.utter_message(f'a = {wochentag}, b= {fach}, c = {anfrage}')
            if wochentag == 'samstag' or wochentag == 'sonntag': 
                dispatcher.utter_message('UHUUU da ist Wochenende. Da hat man doch keine Vorlesung sondern Freizeit. Genieß es und nimm dir auch mal etwas Zeit für dich selber. Ich gehe zum Beispiel sehr gerne Mäuse fangen an den Wochenenden!')
            else: 
                

                if wochentag== 'heute' or wochentag== 'morgen': 
                    
                    fächer_am_tag = tagesauswahl(wochentag)
                    selectionlist = fach_select(fächer_am_tag, fach)
                    dispatcher.utter_message(f'Die gefragte Vorlesung: {selectionlist[0]}, findet {wochentag} im Raum {selectionlist[2]} statt')

                    


                else: 
                    wochentag = wochentag.split() 
                    wochentag_richtig = tag_selection(wochentage, wochentag)
                    
                    wochentag_richtig_groß = wochentag_richtig[0].upper() + wochentag_richtig[1::]
                    
                    fächer_am_tag = tagesauswahl(wochentag_richtig)
                    
                    fach = fach.lower().split()
                    selectionlist = fach_select(fächer_am_tag, fach)

                    if len(fach)!= 0 and selectionlist!= 'Eintrag nicht gefunden': 
                        

                        if anfrage == 'wo': 
                            dispatcher.utter_message(f'Die gefragte Vorlesung: {selectionlist[0]}, findet am {wochentag_richtig_groß} im Raum {selectionlist[2]} statt')
                        if anfrage == 'wann': 
                            dispatcher.utter_message(f'Die gefragte Vorlesung: {selectionlist[0]}, findet am {wochentag_richtig_groß} um {selectionlist[1][11:-3]} statt')
                    
                    elif selectionlist == 'Eintrag nicht gefunden': 
                        dispatcher.utter_custom_message('Du hast das Fach gar nicht an diesem Tag. Du kannst auch Fragen: welche Fächer habe ich (Wochentag) um eine allgemeine Übersicht zu erhalten')

                    else: dispatcher.utter_message('UHUUU da ist wohl irgendwas schief gegangen. Du kannst auch Fragen: welche Fächer habe ich (Wochentag) um eine allgemeine Übersicht zu erhalten')
        except: 

            dispatcher.utter_message('UHUUU das habe ich leider nicht genau verstanden. Um diese Funktion zu verwenden musst du mindestens den Anfang des Wochentages und der gewünschten Vorlesung sagen. ')
            dispatcher.utter_message( 'Du kannst auch Fragen: welche Fächer habe ich (Wochentag) um eine allgemeine Übersicht zu erhalten')
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

