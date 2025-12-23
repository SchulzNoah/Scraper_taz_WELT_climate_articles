# Scraping der taz


# Import der zum Scrapen notwendigen Bibliotheken
import requests
from bs4 import BeautifulSoup
import pandas as pd


# URLS erstellen/zählen
def urls_erstellen(base_url, anzahl_urls):
    urls = {}
    for i in range(anzahl_urls):
        new_url = base_url.format(i)
        urls[f'url_{i}'] = new_url
    return urls


# Hier wird eine Funktion definiert, die die Links aller einzelnen Artikel zu
# einer Liste hinzufügt.

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


# Scraping der Inhalte
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
         
    # Datum formatieren
    # "vom" wird entfernt
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

# Durchführen des Scrapings

# Definition der Basis-URL (Suchseite)
base_url = 'https://taz.de/!s=Klimawandel/?search_page={}'
# Festlegung, bis zu welcher Seite gescrapet wird
# 50 = Maximum = 1000 Artikel
anzahl_urls = 50
# Scraping der URLs
alle_urls = urls_erstellen(base_url, anzahl_urls)

artikel_einzeln = scrape_hrefs(alle_urls)
artikel_infos = []


for url in artikel_einzeln:
    title, datum, article_text, article_url = scrape_article(url)  
    if article_text:
        artikel_infos.append({'Titel': title, 'Datum': datum, 'Artikel': article_text, 'URL': article_url})
    else:
        print(f"Kein Text gefunden oder Fehler beim Scrapen der URL: {url}")


# Speichern in Dataframe
df_taz = pd.DataFrame(artikel_infos)



# Visualisierungen TAZ
# Wortwolke TAZ


# Import der nötigen Pakete

from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt


# Eliminierung irrelevanter Stoppwörter

# Manuelles Entfernen weiterer Stoppwörter
uninteressant = "Die e und über der NA für auf Ein im mit Woche Podcast nicht von gegen bei aus Da zu den ist wie als wird zur Das au mehr nach Wir aus"
liste_unerw_wörter = uninteressant.split()
# Anwendung der Stoppwortliste
STOPWORDS.update(liste_unerw_wörter)

# Umwandlung aller Texte in der Spalte Titel zu einem String

text = " ".join(df_taz['Titel'].astype(str).tolist())


# Erstellung der Wortwolke

# Erstellung der Wordcloud sowie Höhe, Breite und Hintergrundfarbe
wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
# Hinzufügen eines Titels
plt.title('Wortwolke für die Titel der taz-Artikel', fontsize=10, pad=10)
plt.imshow(wordcloud, interpolation='bilinear')
# keine Achsen werden dargestellt
plt.axis("off")
# Anzeigen des Plots
plt.show()


# Säulendiagramm TAZ

# Import der notwendigen Packages


import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re  


# Definition der Suchbegriffe bzw. Framinggruppen


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


# Zählfunktion
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


# Erstellen Säulendiagramm

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


# Sentimentanalyse Boxplot TAZ

import pandas as pd
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import matplotlib.pyplot as plt
import seaborn as sns


# Download des VADER Lexikons aus dem nltk-Package
nltk.download('vader_lexicon')


# Aufstellen des Sentiment Analyzers
sia = SentimentIntensityAnalyzer()

# Durchführung der Sentimentanalyse und Anzeigen des Ergebnisses

def analyze_sentiment(text):
    sentiment = sia.polarity_scores(text)
    return sentiment['compound']  # Compound-Wert als Gesamtsentiment
df_taz['Sentiment'] = df_taz['Artikel'].apply(analyze_sentiment)
print(df_taz)

 
# Erstellung und Konfiguration des Boxplots


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

