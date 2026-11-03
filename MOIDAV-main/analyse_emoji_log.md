# Analyseplan: emoji-gebruik per auteur

## GOAD-stage 1 — vraag en verwachting

**Onderzoeksvraag**  
Verschilt het emoji-gebruik tussen de auteurs in `data/processed/squad-vol.parq`?

**Verwachting**  
De auteurs verschillen van elkaar. Het interessante contrast is het verschil tussen de
auteur met het hoogste en de auteur met het laagste emoji-gebruik, nadat auteurs met te
weinig berichten zijn uitgesloten.

**Eenheid van observatie**  
Een bericht.

## Vooraf vastgelegde keuzes

- Vergelijk alle auteurs met minstens **100 berichten**.
- Primaire maatstaf: **gemiddeld aantal emoji's per bericht**.
- Gebruik daarnaast het aandeel berichten met minstens één emoji en het aandeel
  uitsluitend-emoji-berichten als aanvullende maten.
- Gebruik `p < 0,05` als vooraf gekozen significantiegrens.
- Dataset: `data/processed/squad-vol.parq`.

## Nog vast te leggen in GOAD-stage 2

- Emoji's worden geteld als afzonderlijke emoji-tekens.
- Eerste visualisatie: een puntenplot met een samenvatting per auteur.
- Rapporteer naast het gemiddelde ook de mediaan.
- Druk de praktische grootte uit als relatief percentageverschil.
- Praktisch relevant verschil: minimaal 25% relatief verschil.
- Primaire inferentie: verschillen tussen alle auteurs.
- Analyseenheid voor de primaire toets: auteur-samenvatting.
- Nulhypothese: de auteurs verschillen niet in emoji-gebruik.
- Ondersteuning voor de verwachting: `p < 0,05` én minstens 25% relatief verschil.
- Secundaire tijdscope: emoji-gebruik per auteur-maand.
- Een patroon noemen we terugkerend als het in minstens drie afzonderlijke maanden zichtbaar is.
- Secundaire feature: auteursaandeel per auteur-maand.
- Verwachting voor auteursaandeel: geen stabiel verschil tussen auteurs.
- Referentie voor auteursaandeel: het groepsgemiddelde in dezelfde maand.
- Een auteur wijkt praktisch relevant af bij minstens 5 procentpunt verschil,
  zichtbaar in minstens 6 afzonderlijke maanden.
- Welke onzekerheid of toets past bij berichten die binnen auteurs gegroepeerd zijn.
- Of de conclusie stabiel blijft wanneer we de periode of minimumdrempel variëren.


## GOAD-stage 1 — uitbreiding berichtlengte en vervolgactiviteit

- Vraag 1: verschillen auteurs in gemiddelde berichtlengte? Primaire maat: tekens per bericht; mediaan en woorden per bericht als aanvullende maten.
- Vraag 2: hangen onderwerpen samen met meer activiteit in de volgende zes uur en op de volgende kalenderdag?
- Verwachting: een interessant onderwerp kan een gesprek starten of verlengen; daarom verwachten we mogelijk hogere vervolgactiviteit, maar de analyse is associatief en niet causaal.
- Onderwerp-categorieën: vakantie, vakantie naar Frankrijk, bordspellen spelen, feest en overlijden. De categorieën zijn vooraf gekozen trefwoordfilters en mogen overlappen.
- Activiteitseenheid: onderwerp-startmomenten met minimaal zes uur tussen opeenvolgende starts van hetzelfde onderwerp.
- Baseline: topicloze startmomenten; uitkomsten worden descriptief geïnterpreteerd en gecontroleerd op aantal starts en mogelijke confounding door tijdstip/weekdag.
- Plan staat in `notebooks/notebooks/analyse-emoji-auteurs.ipynb`; dit log bewaart de keuzes buiten de notebook.
