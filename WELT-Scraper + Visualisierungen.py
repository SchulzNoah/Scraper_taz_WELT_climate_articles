# -*- coding: utf-8 -*-
"""
Datum: 24. August 2024

@authors: Noah Schulz (Scraper) + Phil Puschmann (Visualisierungen)
"""

#################
########Scraping der WELT
################

'''
Zunächst werden die Packages, die für das Scrapen relevant sind, 
importiert. Selenium wird für das interaktive Scrapen verwendet, um die URLs 
der auf der Suchseite verlinkten Artikel zu scrapen.
BeautifulSoup und requests werden verwendet, um von den URLs jeweils das
Datum, den Textinhalt und den Titel zu extrahieren. Pandas wird benötigt,
um einen Dataframe zu erstellen, mit dem für die Abbildungen einfacher weiter
gearbeitet werden kann 
'''

# pip install selenium | # falls noch nicht installiert
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests
from bs4 import BeautifulSoup
import pandas as pd


'''In folgendem Code-Abschnitt werden mit Selenium die verlinkten URLs 
auf den Such-Seiten der Online-Zeitung WELT gescrapet. Hierfür muss unter
folgendem Link: https://googlechromelabs.github.io/chrome-for-testing/ 
der zum Betriebssystem passende Chromedriver installiert werden. Je nachdem,
wo der Chromedriver gespeichert wird, muss der Pfad hierzu festgelegt werden. 

Für den Rohentwurf des Scrapers, der die verlinkten URLs mithilfe von
Selenium scrapet, wurde ChatGPT verwendet. Der Prompt lautete:
    
"Hi, ich möchte die verlinkten URLs von WELT-Artikeln mit Selenium in Python 
scrapen. Dafür habe ich folgende Liste an URLs: urls = [
    "https://www.welt.de/suche?q=Klimawandel&type=article&section=all",
    "https://www.welt.de/suche?q=Klimawandel&type=article&section=wirtschaft",
    "https://www.welt.de/suche?q=Klimawandel&type=article&section=debatte",
    "https://www.welt.de/suche?q=Klimawandel&type=article&section=politik",
    "https://www.welt.de/suche?q=Klimawandel&type=article&section=vermischtes",
    "https://www.welt.de/suche?q=Klimawandel&type=article&section=kultur",
    "https://www.welt.de/suche?q=Klimawandel&type=article&section=sonderthemen"
].
Den Chromedriver habe ich bereits installiert. Das CSS-Element für den 
"mehr anzeigen-Button" lautet: .c-toggle-more--default. Das CSS-Element für 
den Headline Link ist folgender: .c-teaser__headline-link. Ich möchte zunächst
 eine Liste haben mit allen verlinkten URLs. Nenne mir den entsprechenden 
 Python-Code Ansatz. Wenn du mir bei der Aufgabe adäquat hilfst, 
 erhälst du 50$ Trinkgeld " 

Der Prompt wurde am 24. August 2024 ChatGPT um 18:37 Uhr gestellt. Weitere
Infos hierzu befinden sich im Anhang des Projektberichts.
'''
 
##### Erstellung des Scrapers für die verlinkten Artikel-URLs ###########


# WebDriver-Setup
chrome_options = Options()
## Optional: Chromedriver wird nicht geöffnet
# chrome_options.add_argument("--headless")  
# Pfad zum Chromedriver
service = Service("C:/Users/Noah/Desktop/chromedriver-win64/chromedriver.exe")
driver = webdriver.Chrome(service=service, options=chrome_options)

# Erstellung der Liste mit den URLs aller Ressorts

urls = [
    "https://www.welt.de/suche?q=Klimawandel&type=article&section=all",
    "https://www.welt.de/suche?q=Klimawandel&type=article&section=wirtschaft",
    "https://www.welt.de/suche?q=Klimawandel&type=article&section=debatte",
    "https://www.welt.de/suche?q=Klimawandel&type=article&section=politik",
    "https://www.welt.de/suche?q=Klimawandel&type=article&section=vermischtes",
    "https://www.welt.de/suche?q=Klimawandel&type=article&section=kultur",
    "https://www.welt.de/suche?q=Klimawandel&type=article&section=sonderthemen"
]


''' 
Funktion zum Extrahieren der verlinkten Artikel-URLs
'''

def extract_article_urls(url):
    driver.get(url)
    last_count = 0
    # Erstellung einer leeren Liste für URLs
    article_links = []


# mehr-Anzeigen-Button wird bis zum Ende einer Seite so oft wie möglich ge-
# drückt, währenddessen werden URLs gescrapet    
    while True:
        try:
            # CSS-Element des "Mehr anzeigen"-Buttons
            load_more_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".c-toggle-more--default"))
            )
            driver.execute_script("arguments[0].click();", load_more_button)
            # Wartezeit, um sicherzustellen, dass der Inhalt geladen wird
            time.sleep(5)  
            
            # CSS-Element des Headline Links (Verlinkte URL)           
            article_links = driver.find_elements(By.CSS_SELECTOR, ".c-teaser__headline-link")
            
            # Überprüfung, ob sich die Anzahl der Artikel-Links erhöht hat
            if len(article_links) > last_count:
                last_count = len(article_links)
            else:
                break  
            
        except Exception as e:
            # Kein "Mehr anzeigen"- Button mehr vorhanden oder nicht klickbar
            # bzw. Ende der Seite liegt vor
            print(f"Ende der Seite liegt vor: {e}")
            break  
    
    # Extraktion der Artikel-URLs
    urls = [link.get_attribute('href') for link in article_links]
    return urls

# Liste, um alle Artikel-URLs zu speichern
all_article_urls = []

# Gehe jede URL in der Liste durch und extrahiere die Artikel-URLs
for url in urls:
    article_urls = extract_article_urls(url)
    all_article_urls.extend(article_urls)

# Schließen des Chromedrivers
driver.quit()

# Optional: Ausgabe der extrahierten URLs
# for article_url in all_article_urls:
#    print(article_url)

# Überprüfung, ob alle 517 Artikel-URLs gescrapet wurden
print(f"{len(all_article_urls)} Artikel-URLs wurden gescrapet")

'''Mit dem set-Befehl werden Duplikate entfernt, da manche WELT-Artikel
mehreren Ressorts zugeordnet sind'''

# 33 Duplikate liegen vor, insgesamt also 484 Artikel
alle_welt_artikel = set(all_article_urls)


##############################################################################
### Funktion zum Scrapen der wichtigen Artikelinfos (Datum, Titel, Textinhalt)

'''In diesem Code-Abschnitt werden mit BeautifulSoup und requests die 
relevanten Artikelinfos (Datum, Titel und Text) der verlinkten URLs gescrapet
und mithilfe von Pandas als Dataframe gespeichert und aufbereitet.''' 

# Funktion zum Scrapen der Artikeldaten
def scrape_article(url):
    try:
        # Speichern des Inhalts der Website 
        page = requests.get(url) 
        # HTML-Parser wird auf Page angewendet
        soup = BeautifulSoup(page.content, 'html.parser')

        # Titel der Artikel werden extrahiert
        title = soup.find('h1').get_text() if soup.find('h1') else "Kein Titel gefunden"

        # Datum der Artikel werden extrahiert
        date = soup.find(class_='c-article-header__date')
        date = date.get_text() if date else "Kein Datum gefunden"

        # Textinhalt der Artikel wird extrahiert
        # CSS-Elemente wurden mit dem SelectorGadget von Chrome ermittelt
        elements = soup.select('h3, .c-rich-text-renderer--article p, .c-article-page__intro p')
        article_text = ' '.join([element.get_text() for element in elements])

        return title, date, article_text, url
    except Exception as e:
        print(f"Fehler beim Scrapen der URL {url}: {e}")
        return "Fehler", "Fehler", "Fehler", url


# Liste für die gesammelten Artikelinformationen
artikel_infos_welt = []

# Durchlaufen aller URLs und Scrapen der relevanten Infos
for url in alle_welt_artikel:
    # Titel, Datum, Text und URL werden zur Liste hinzugefügt
    title, date, article_text, article_url = scrape_article(url)
    artikel_infos_welt.append({'Titel': title, 'Datum': date, 'Artikel': article_text, 'URL': article_url})


# Erstellung eines Dataframes df_welt
df_welt = pd.DataFrame(artikel_infos_welt)

#######################
''' Weitere Datenaufbereitung/Datacleaning des Dataframes''' 

# "Veröffentlicht am" wird in der Variable Datum entfernt
df_welt['Datum'] = df_welt['Datum'].str.replace("Veröffentlicht am", "")

# "Stand:" wird ebenfalls in der Variable Datum entfernt
df_welt['Datum'] = df_welt['Datum'].str.replace("Stand:", "")

'''Da einige Artikel keine Datumsangabe haben, sondern nur eine Uhrzeit 
angegeben wird, werden mit folgendem Code diese Artikel für die Variable Datum
mit NA versehen'''
 
df_welt['Datum'] = df_welt['Datum'].replace(to_replace=r'.*Uhr.*', value= "NA", regex = True)


''' Außerdem soll berechnet werden, wie viele der gescrapten Artikel aus
dem Jahr 2024 stammen'''


# Anzahl der WELT-Artikel aus dem Jahr 2024 
anzahl_welt_2024 = df_welt['Datum'].str.contains("2024").sum()

# 378 der Artikel wurden im Jahr 2024 veröffentlicht 
print("Anzahl der Artikel aus dem Jahr 2024:", anzahl_welt_2024)


''' Berechnung der Anzahl an WELT+-Artikeln, da diese nicht vollständig
gescrapet werden können, sondern nur der erste Absatz'''


# Anzahl WELTplus-Artikel
anzahl_weltplus = len(df_welt[df_welt['URL'].str.contains('/plus')])
# Insgesamt 179 WELT+ Artikel
print(f"Anzahl der WELTplus-Artikel: {anzahl_weltplus}")

'''Der finale Dataframe kann optional als Excel-Datei gespeichert werden,
damit die Gruppenmitglieder nicht warten müssen, bis das Scraping 
abgeschlossen wurde bzw. der Code durchgelaufen ist.

df_welt.to_excel('df_welt.xlsx', index=False)
'''


#######################
############ Visualisierungen WELT

'''In diesem Abschnitt werden die 3 Visualisierungen für die WELT-Artikel
erstellt. Zum einen eine Wortwolke für die Titel, ein Säulendiagramm für
bestimmte Framing-Kategorien der WELT-Artikel und zuletzt ein Boxplot mit
Sentiwerten der WELT-Artikel.
'''

######################
################ Wortwolke WELT

'''
Falls noch nicht geschehen, können die Packages 
für die Wordcloud mit folgenden Codezeilen installiert werden

pip install wordcloud
pip install matplotlib
pip install pillow
'''

# Import der nötigen Packages
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt


# Umwandlung aller Texte in der Spalte Titel zu einem String
text = " ".join(df_welt['Titel'].astype(str).tolist())


''' Eliminierung von uninteressanten Wörtern/Stoppwörtern'''

# Manuelle Entfernung weiterer Stoppwörter
stopwords = "dem Sie sich aus sind noch haben zum Ich des us um dass vor ein die der und bei Das wird nach neue im von mit auf den es"
liste_unerw_wörter = stopwords.split()
# Anwendung der Stoppwortliste
STOPWORDS.update(liste_unerw_wörter)

'''Erstellung der Wortwolke'''


# Wordclouderstellung sowie Festlegung der Höhe, Breite und Hintergrundfarbe
wordcloud = WordCloud(width=800, height=400, background_color='white', stopwords= STOPWORDS).generate(text)
# Hinzufügen eines Titels
plt.title('Wortwolke für die Titel der WELT-Artikel', fontsize=10, pad=10)
plt.imshow(wordcloud, interpolation='bilinear')
# keine Darstellung von Achsen
plt.axis("off")
# Anzeigen des Plots
plt.show()


################### 
############ Säulendiagramm WELT


''' Import der notwendigen packages'''

import matplotlib.pyplot as plt
import seaborn as sns
import re  


# Definition der Suchbegriffe/Framing-Kategorien
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

# Aufstellen der Zählfunktion
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
all_text = ' '.join(df_welt['Artikel'].astype(str).tolist())


# Durchführung der Frequenzanalyse 
group_counts = count_group_terms(all_text, begriffsgruppen)


# Erstellung eines Dataframes mit den Ergebnissen
df_counts = pd.DataFrame(list(group_counts.items()), columns=['Begriffsgruppe', 'Häufigkeit'])


'''
Erstellung des Säulendiagramms
'''

# Festlegung der Plotgröße
plt.figure(figsize=(10, 6))

# Erstellung des Säulendiagramms
sns.barplot(x='Begriffsgruppe', y='Häufigkeit', data=df_counts, palette='pastel')

# x-Achsen-Beschriftung
plt.xlabel('Begriffsgruppen')

# y-Achsen-Beschriftung
plt.ylabel('Häufigkeit')

# Hinzufügen eines Titels
plt.title('Framing in WELT-Artikeln')

# Drehen der x-Achsenbeschriftung um 45 Grad
plt.xticks(rotation=45, ha='right')

# tight Layout
plt.tight_layout()

# Anzeigen des Plots
plt.show()


##########################
################## Sentimentanalyse Boxplot WELT


''' 
Installation und Import aller notwendigen Packages
'''

#pip install nltk # falls noch nicht installiert
import pandas as pd
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import matplotlib.pyplot as plt
import seaborn as sns


# Download des VADER Lexikons aus dem nltk-Package
nltk.download('vader_lexicon')


# Initialisierung des Sentiment Analyzers
sia = SentimentIntensityAnalyzer()


'''
Durchführung der Sentimentanalyse und Anzeigen des Ergebnisses
'''

def analyze_sentiment(text):
    sentiment = sia.polarity_scores(text)
    return sentiment['compound']  # Compound-Wert als Gesamtsentiment
df_welt['Sentiment'] = df_welt['Artikel'].apply(analyze_sentiment)
print(df_welt)


'''
Erstellung und Konfiguration des Boxplots
'''

# Festlegen Plot-Größe
plt.figure(figsize=(10, 6))
# Erstellung des Boxplots
sns.boxplot(y=df_welt['Sentiment'], palette='pastel')

# Definition des Minimums und Maximums
max_sentiment = df_welt['Sentiment'].max()
min_sentiment = df_welt['Sentiment'].min()

# Anzeigen des Minimums und Maximums im Plot
plt.scatter(1, max_sentiment, color='green', s=100, label='Positivster Artikel (Max)')
plt.scatter(1, min_sentiment, color='red', s=100, label='Negativster Artikel (Min)')

# Hinzufügen eines Titels
plt.title('Sentimentverteilung der WELT-Artikel')
# Hinzufügen der y-Achsen-Beschriftung
plt.ylabel('Sentiment Score')
# Hinzufügen einer Legende
plt.legend()
# Anzeigen des Plots
plt.show()


''' Abbildung mit beiden Boxplots

# In dem Projektbericht wurde eine Abbildung mit 2 Boxplots erstellt.
# Dies ist der dazugehörige Code. Jedoch müsste der taz-Scraper in dieses
# Python-Script integriert werden, damit die Abbildung erstellt werden kann.
# Aus Gründen der Übersichtlichkeit wurden jedoch 2 Python-Scripte (separiert
# nach taz und WELT) erstellt.


# Data Frame mit den Sentimentwerten aller Artikel beider Medien erstellen

df_senti = pd.DataFrame({
    'Wert': df_taz['Sentiment'].tolist() + df_welt['Sentiment'].tolist(),
    'Gruppe': ['taz (n = 997)'] * len(df_taz) + ['Welt (n = 484)'] * len(df_welt)
})



# Abbildung mit zwei Boxplots erstellen

# Festlegen der Plot-Größe
plt.figure(figsize=(10, 6))
# Erstellung der Boxplots
sns.boxplot(x='Gruppe', y='Wert', data=df_senti, palette='pastel')
# Hinzufügen eines Titels
plt.title('Vergleich der Sentimentwerte zwischen taz und WELT', fontsize=16)
# x-Achsen-Beschriftung
plt.xlabel('Medium')
# y-Achsen-Beschriftung
plt.ylabel('Gesamtsentimentwerte')
# Anzeigen des Plots
plt.show()'''