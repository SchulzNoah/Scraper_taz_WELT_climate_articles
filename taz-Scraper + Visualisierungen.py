# -*- coding: utf-8 -*-
"""
Datum: 22. August 2024 

@author: Robin Saßmannshausen (taz-Scraper) + Phil Puschmann (Visualisierungen)
"""


######################################### 
########### Scraping der taz
#########################################


'''
Import der zum Scrapen notwendigen Bibliotheken
'''
import requests
from bs4 import BeautifulSoup
import pandas as pd


'''
Hier wird eine Funktion definiert, die, aufbauend auf der Standard-URL, 
weitere URLs erstellt. Dies ist nötig, um mehr als eine Seite von Artikeln
zu scrapen. Die Anzahl weiterer erstellter URLs kann manuell durch die 
Veränderung der Variable "anzahl_urls" angepasst werden.
'''
def urls_erstellen(base_url, anzahl_urls):
    urls = {}
    for i in range(anzahl_urls):
        new_url = base_url.format(i)
        urls[f'url_{i}'] = new_url
    return urls


#######################

'''
Hier wird eine Funktion definiert, die die Links aller einzelnen Artikel zu
einer Liste hinzufügt.
'''
def scrape_hrefs(urls):
    artikel_einzeln = []
    for name, url in urls.items():
        print(f"Scraping URL: {url}")
        # Speichern des Inhalts der Website 
        response = requests.get(url)
        if response.status_code == 200:
            # HTML-Parser wird auf response angewendet
            soup = BeautifulSoup(response.content, 'html.parser')
            # Finde alle href-Elemente, die mit "/Archiv-Suche" beginnen
            hrefs = [f"https://taz.de{a['href']}" for a in soup.find_all('a', href=True) if a['href'].startswith("/Archiv-Suche")]
            artikel_einzeln.extend(hrefs)
        else:
            print(f"Fehler beim Abrufen der URL: {url}")
    return artikel_einzeln


#######################

'''
Hier wird eine Funktion definiert, die die Informationen der einzelnen Artikel 
scraped. Diese Informationen sind der Titel, das Datum und der Text des 
Artikels. Gleichzeitg wird auch schon das Datum in ein einheitliches Format 
gebracht.
'''
def scrape_article(url):
    # Speichern des Inhalts der Website
    response = requests.get(url)

    # HTML-Parser wird auf response angewendet
    soup = BeautifulSoup(response.content, 'html.parser')

    # Titel der Artikel werden extrahiert
    title = soup.find('h1').get_text() if soup.find('h1') else "Kein Titel gefunden"
    # Datum der Artikel werden extrahiert
    datum = soup.find(class_="date").get_text() if soup.find(class_="date") else "Kein Datum gefunden"
    article_text = ''
       
    # Bei Archiv-Artikeln wird der Titelname zu "NA"
    title = title.replace('Archiv', 'NA')
         
    ''' Datum formatieren'''
    # "vom" wird wird entfernt
    datum = datum.replace('vom', '').strip()
    datum = datum.split(',')[0].replace(' ', '')
    # KeinDatumgefunden wird zu NA
    datum = datum.replace('KeinDatumgefunden', 'NA')

    # Suche nach dem <article> mit der Klasse "sectbody"
    sectbody = soup.find('article', class_='sectbody')
    if sectbody:
        # Finde alle <p>-Tags in "sectbody"
        paragraphs = sectbody.find_all('p')
        # Füge nur den Text nach dem ersten "|" zu article_text hinzu
        for p in paragraphs:
            # Ignoriere <p> tags in der "caption" class
            if 'caption' not in p.get('class', []):
               # Text nach dem ersten "|" extrahieren und Leerzeichen entfernen
                text = p.get_text().split('|', 1)[-1].strip()  
                article_text += text + ' '
    
    return title, datum, article_text.strip(), url # URL ebenfalls hinzufügen

##########
########## Durchführung des Scrapens
##########
'''
Zuerst wird die maximal mögliche (da sonst von der taz unterbunden) Anzahl
an URLs erstellt und in einem dictionary gespeichert
'''
# Definition der Basis-URL (Suchseite)
base_url = 'https://taz.de/!s=Klimawandel/?search_page={}'
# Festlegung, bis zu welcher Seite gescrapet wird
# 50 = Maximum = 1000 Artikel
anzahl_urls = 50
# Scraping der URLs
alle_urls = urls_erstellen(base_url, anzahl_urls)

'''
Dann werden die URLs aller Artikel in einer Liste gespeichert
'''
artikel_einzeln = scrape_hrefs(alle_urls)


'''
Liste für die gesammelten Artikelinformationen wird erstellt
'''
artikel_infos = []

'''
Durchlaufe alle Artikel-URLs und scrape die Artikelinformationen: Titel, 
Datum, Text und füge sie zusammen mit der URL einer Liste hinzu
'''
for url in artikel_einzeln:
    title, datum, article_text, article_url = scrape_article(url)  
    if article_text:
        artikel_infos.append({'Titel': title, 'Datum': datum, 'Artikel': article_text, 'URL': article_url})
    else:
        print(f"Kein Text gefunden oder Fehler beim Scrapen der URL: {url}")

'''
DataFrame df_taz aus der Liste der Artikelinformationen erstellen
'''

df_taz = pd.DataFrame(artikel_infos)



#########
######### Visualisierungen TAZ
#########

'''In diesem Abschnitt werden die 3 Visualisierungen für die taz-Artikel
erstellt. Zum einen eine Wortwolke für die Titel, ein Säulendiagramm für
bestimmte Framing-Kategorien der taz-Artikel und zuletzt ein Boxplot mit
Sentiwerten der taz-Artikel.
'''

######### Wortwolke TAZ

'''
Installation der nötigen Packages für die Wortwolke, falls nicht bereits
installiert.

pip install wordcloud
pip install matplotlib
pip install pillow
'''


'''
Import der nötigen packages
'''

from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt


'''
 Eliminierung von irrelevanten Wörtern/Stoppwörtern
 '''

# Manuelles Entfernen weiterer Stoppwörter
uninteressant = "Die e und über der NA für auf Ein im mit Woche Podcast nicht von gegen bei aus Da zu den ist wie als wird zur Das au mehr nach Wir aus"
liste_unerw_wörter = uninteressant.split()
# Anwendung der Stoppwortliste
STOPWORDS.update(liste_unerw_wörter)

'''
Umwandlung aller Texte in der Spalte Titel zu einem String
'''
text = " ".join(df_taz['Titel'].astype(str).tolist())

''' 
Erstellung der Wortwolke
'''

# Erstellung der Wordcloud sowie Höhe, Breite und Hintergrundfarbe
wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
# Hinzufügen eines Titels
plt.title('Wortwolke für die Titel der taz-Artikel', fontsize=10, pad=10)
plt.imshow(wordcloud, interpolation='bilinear')
# keine Achsen werden dargestellt
plt.axis("off")
# Anzeigen des Plots
plt.show()



######################
############## Säulendiagramm TAZ

'''
Import der notwendigen Packages
'''

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re  

'''
Definition der Suchbegriffe bzw. Framinggruppen
'''

begriffsgruppen = {
    'Relativierendes Framing': ['Klimahysterie', 'Klimapanik', 'Klimafiktion', 
                                'Klimaterroristen', 'Klimakleber', 
                                'Klimaskepsis', 'Klimaskeptiker','Panikmache',
                                'Heizungshammer'],
    'Neutral': ['Klimawandel', 'Erderwärmung', 'Klimaerwärmung', 
                'Klimaforschung', 'CO2-Ausstoß', 'Klimaschutz', 'Umweltschutz',
                'Erneuerbare Energien', 'Verkehrswende'],
    'Hyperbolisches Framing': ['Klimakatastrophe', 'Klimakrise', 
                               'Klimanotstand', 'Klimabombe', 
                               'Klimaaktivisten', 'Klimaaktivist:innen',
                               'Artensterben', 'Umweltzerstörung', 
                               'Luftverschmutzung', 'Weltuntergang']
}

'''
Funktion zum Zählen der Begriffe in einer Textgruppe (ChatGPT)

ChatGPT wurde am 27. August 2024 um 16:24 Uhr folgender Prompt gegeben:

"Ich möchte ein Säulendiagramm basierend auf einer Frequenzanalyse mit Python
Spyder un dem seaborn package erstellen. Hierfür möchte ich in einem Text
string zum Thema Klimawandel nach einzelnen Begriffen suchen, die verschiedenen
Gruppen zugeordnet sind (z.B. 1. Positive  Begriffe: Klimaschutz, Umweltschutz;
2. Neutrale Begriffe: Klimawandel,...; 3. Klimakrise). Die Begriffe der jewei-
ligen Gruppe sollen dann im string gezählt und schließlich in dem Diagramm
dargestellt werden."

Weitere Infos zum Code-Entwurf von ChatGPT befinden sich im Anhang des Projekt-
berichts    
'''

def count_group_terms(text, term_groups):
    text = text.lower()  
    group_counts = {}
    for group_name, terms in term_groups.items():
        count = 0
        for term in terms:
            term_lower = term.lower()
            count += len(re.findall(r'\b' + re.escape(term_lower) + r'\b', text))
        group_counts[group_name] = count
    return group_counts



# Umwandlung aller Texte in der Spalte Artikel in einen String
all_text = ' '.join(df_taz['Artikel'].astype(str).tolist())


# Durchführung der Frequenzanalyse
group_counts = count_group_terms(all_text, begriffsgruppen)


#Erzeugung eines Dataframes mit den Ergebnissen
df_counts = pd.DataFrame(list(group_counts.items()), columns=['Begriffsgruppe', 'Häufigkeit'])

'''
Erstellung und Konfiguration des Säulendiagrammes
'''
# Größe der Abbildung
plt.figure(figsize=(10, 6))

# Erstellen des Säulendiagramms
sns.barplot(x='Begriffsgruppe', y='Häufigkeit', data=df_counts, palette='pastel')

# x-Achsen-Beschriftung
plt.xlabel('Begriffsgruppen')

# y-Achsen-Beschriftung
plt.ylabel('Häufigkeit')

# Titel
plt.title('Framing in taz-Artikeln')

# Rotieren der x-Achsenbeschriftung um 45 Grad
plt.xticks(rotation=45, ha='right')

# Hinzufügen des tight-layouts
plt.tight_layout()

# Anzeigen des Plots
plt.show()


##################
###### Sentimentanalyse Boxplot TAZ


# Installation und Import aller notwendigen packages


# pip install nltk # Installation von nltk, falls noch nicht geschehen
import pandas as pd
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import matplotlib.pyplot as plt
import seaborn as sns


# Download des VADER Lexikons aus dem nltk-Package
nltk.download('vader_lexicon')


# Aufstellen des Sentiment Analyzers
sia = SentimentIntensityAnalyzer()

'''
Durchführung der Sentimentanalyse und Anzeigen des Ergebnisses
'''

def analyze_sentiment(text):
    sentiment = sia.polarity_scores(text)
    return sentiment['compound']  # Compound-Wert als Gesamtsentiment
df_taz['Sentiment'] = df_taz['Artikel'].apply(analyze_sentiment)
print(df_taz)


''' 
Erstellung und Konfiguration des Boxplots
'''

# Festlegen der Plot-Größe
plt.figure(figsize=(10, 6))
# Erstellung des Boxplots und der Farbpalette
sns.boxplot(y=df_taz['Sentiment'], palette='pastel')

# Definition des Minimums und Maximums
max_sentiment = df_taz['Sentiment'].max()
min_sentiment = df_taz['Sentiment'].min()

# Anzeigen des Minimums und Maximums
plt.scatter(1, max_sentiment, color='green', s=100, label='Positivster Artikel (Max)')
plt.scatter(1, min_sentiment, color='red', s=100, label='Negativster Artikel (Min)')

# Hinzufügen des Titels
plt.title('Sentimentverteilung der taz-Artikel')
# Änderung der y-Achsen-Beschriftung
plt.ylabel('Sentiment Score')
# Hinzufügen der Legende
plt.legend()
# Anzeigen des Plots
plt.show()


'''
Die Dokumentation darüber, wie zwei Boxplots in einer Abbildung erstellt
wurden, befindet sich im anderen Script: "WELT-Scraper + Visualisierungen"
'''