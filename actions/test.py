
from datetime import datetime

fächerproTag = {'montag': ('Computational Thinking CT','8: 15- 9:45', 'R0.058'), 'dienstag' : ('computational thinking ct', '10:00 - 11:30', 'E0.103'), 'mittwoch': ('grundlagen interface und interactionsdesign ui ux', '16:30 - 18:00', 'X1.018'), 'donnerstag': ('grundlagen gestaltung und typographie ggt', '13:00 - 16:15', 'X1.018'), 'freitag': ('projektmodul start pm', '10:30 - 13:30', 'Pavillion X - Gebäude'), 'samstag': 'Es ist Wochenende. Da hat man keine Vorlesung sondern Freizeit. Lass es dir auch mal etwas gut gehen ', 'sonntag': ' Es ist Wochenende. Da hat man keine Vorlesung sondern Freizeit. Lass es dir auch mal etwas gut gehen'} 
wochenliste = ['montag', 'dienstag', 'mittwoch', 'donnerstag', 'freitag','samstag', 'sonntag']
today = datetime.today().weekday()
today= wochenliste[today]
today= fächerproTag[today]
print(today)