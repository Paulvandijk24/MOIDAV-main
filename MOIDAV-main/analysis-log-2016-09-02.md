# Analyse chatdag 2016-09-02

## Vraag en scope

- Dataset: vriendengroepschat.
- Interesse: nagaan wat er op de drukke dag is besproken.
- Doelgroep: eigen gebruik.
- Gewenste analyse: gespreksonderwerpen, uitgesplitst naar auteur.
- De gebruiker noemde geen vooraf bekende gebeurtenissen of inhoudelijke hypothese.

## Databron en interpretatie

- Notebook: `notebooks/lesson3/03.3-events-in-your-chat.ipynb`.
- De actieve configuratie verwijst naar `data/processed/squad-vol.parq`.
- Een rij is een bericht; relevante velden zijn `timestamp`, `author` en `message`.
- De tijdstempels zijn UTC. De notebook telt dagen met `resample("D")` zonder tijdzoneconversie.
- Daardoor is 2016-09-02 de drukste UTC-dag (272 berichten). In de lokale tijdzone
  Europe/Amsterdam vallen 226 berichten op 2016-09-02; daar is 2016-09-10 drukker
  (271 berichten).
- De gebruiker bevestigt de UTC-daggrens, zodat de analyse overeenkomt met het notebook-label.
- Voor de inhoudsanalyse zijn `message` (tekst), `author` (auteur) en `timestamp` (dagfilter)
  de relevante velden. De auteurs zijn in de bron al gepseudonimiseerd.

## Verloop

### Vraag en data

- De vraag is wat er op de drukste dag werd besproken, samengevat per auteur.
- Geen vooraf bekende gebeurtenis of inhoudelijke verwachting is genoemd.
- Geobserveerde eenheid: een bericht; de analyse groepeert berichten binnen de gekozen UTC-dag
  en ordent de inhoud vervolgens per auteur.

### Nog uit te werken

- De gebruiker kiest ervoor verdelingscontroles over te slaan; aantallen per auteur mogen alleen
  kort als context dienen.
- De gebruiker kiest onderwerpen als hoofdstructuur, met bijdragen van verschillende auteurs
  onder elk onderwerp; geen grafiek gevraagd.
- Visuele kritiek is niet van toepassing op de gekozen tekstuele analyse.
- Controle: alle 272 berichten van de UTC-dag worden inhoudelijk doorgenomen, met auteurslabels
  gecontroleerd per onderwerp. De gebruiker vraagt om korte representatieve citaten.

## Afbakening

- De analyse beschrijft inhoud en bijdrage per auteur; berichtenaantallen op zichzelf zeggen
  niet waarover iemand sprak.
- De auteur- en themagroepen zijn categorieën; de tekstinhoud wordt kwalitatief gelezen. Er is
  geen numerieke verdelingsanalyse of grafiek nodig.
- De gekozen indeling is onderwerp-gedreven, met auteursbijdragen binnen elk thema.

## Resultaten: 2016-09-02 UTC

Er staan 272 berichten van 10 gepseudonimiseerde auteurs in dit UTC-dagvenster. De hoofdthema's:

1. **Zwemmen en het weer.** De groep bespreekt of ze bij de Vliet gaan zwemmen, of het weer
   daar geschikt voor is, en wie meegaat; een zwembad komt ook als alternatief langs.
   `dynamic-camel` trapt af met “Iemand vlietj?”, `opalescent-swallow` probeert mensen mee te
   krijgen (“Ik ga nu / Wie joint”), en `teasing-tapir` waarschuwt dat buiten zwemmen geen
   goed idee lijkt. `piebald-duck`, `laughing-chough`, `kaleidoscopic-yapok` en
   `carbonated-quetzal` doen mee in de discussie of geven aan of ze kunnen.
2. **Samen afspreken en de avond plannen.** Een groot deel van de berichten gaat over wie na
   werk, school of andere verplichtingen kan chillen, waar de groep is en hoe laat mensen
   aansluiten. `kaleidoscopic-yapok` vraagt “Gaan we nog chillen vanavond?”;
   `laughing-chough` peilt wie meegaat en helpt de afspraak organiseren. `dynamic-camel`
   vraagt herhaaldelijk waar de anderen zijn en wanneer ze er nog zijn. `breezy-bouncing`,
   `animated-chimpanzee`, `teasing-tapir`, `carbonated-quetzal` en anderen geven hun
   beschikbaarheid door.
3. **Uitgaan en roken.** Later bespreekt `opalescent-swallow` een uitstapje na een verjaardag;
   de anderen overleggen of en wanneer ze aansluiten. Er is ook expliciet verschil in voorkeur
   over roken: `breezy-bouncing` zegt “Alleen no smoke for me”, waarop `laughing-chough`
   begripvol reageert. De chat maakt niet precies duidelijk wat iedereen uiteindelijk doet.
4. **Verjaardag en auto.** `dynamic-camel` vraagt naar een verjaardag de volgende dag;
   `carbonated-quetzal` antwoordt dat die thuis gevierd wordt. `carbonated-quetzal` vertelt
   eerder ook: “met n beetje geluk heb ik zaterdag mn auto”. Later komt een auto-/ophaalafspraak
   opnieuw langs, maar uit de berichten is niet zeker of dat om dezelfde auto gaat.
5. **Kleine zijgesprekken en plagerijen.** Er is een kort gesprek over petten, een gedeelde
   meme/link, woordgrappen en plagerige opmerkingen. Dit zijn losse tussendoortjes naast de
   plannen, geen lang inhoudelijk gesprek.

### Aantal berichten per auteur

| Gepseudonimiseerde auteur | Berichten |
|---|---:|
| dynamic-camel | 85 |
| laughing-chough | 47 |
| carbonated-quetzal | 30 |
| kaleidoscopic-yapok | 27 |
| teasing-tapir | 26 |
| breezy-bouncing | 18 |
| opalescent-swallow | 16 |
| animated-chimpanzee | 11 |
| piebald-duck | 8 |
| uproarious-gnat | 4 |

De gesprekstoon is informeel en plagerig. `dynamic-camel` is de meest actieve stem en stuurt
vaak de vragen en afstemming aan; `laughing-chough` reageert veel en helpt afspraken maken.
De overige auteurs leveren vooral bijdragen aan specifieke plannen of laten weten of ze
kunnen aansluiten. Dit beschrijft alleen de berichten op die ene dag; het zegt niet wie in de
groep doorgaans de meeste invloed heeft.

### Interpretatiebeperking

- De themaclusters zijn kwalitatieve groeperingen van korte berichten; sommige losse reacties
  zijn zonder de volledige chatcontext dubbelzinnig.
- Tijdstip en berichtenaantallen volgen UTC zoals de notebook. Bij lokale kalenderdagen
  verandert de dagindeling.
- Straatadres, kaartcoördinaten en niet-geanonimiseerde namen zijn niet opgenomen.

## Andere dagen met meer dan 150 berichten

Dezelfde inhoudelijke lezing is toegepast op alle UTC-dagen met strikt meer dan 150 berichten.
De auteurs hieronder zijn de meest zichtbare stemmen in de genoemde onderwerpen; namen zijn
de pseudoniemen uit de bron.

| UTC-datum | Berichten | Categorie | Besproken onderwerpen en auteursbijdragen |
|---|---:|---|---|
| 2015-04-03 | 170 | Sociale afspraken & groepsactiviteiten | Een avond samen plannen en bier/drank regelen: `kaleidoscopic-yapok` coördineert geld, aankoop en aankomst; `animated-chimpanzee` en `teasing-tapir` stemmen vervoer en school/werk af. |
| 2015-06-11 | 167 | School & examens | Examenuitslagen, zakken/herkansen en of de groep dat gaat vieren; `breezy-bouncing` en `teasing-tapir` vertellen over herkansingen, `animated-chimpanzee` stelt plannen voor en `opalescent-swallow` probeert de groep bij elkaar te krijgen. |
| 2015-07-24 | 168 | Reis & vakantie | Voorbereiding op een trip naar Terschelling: trein/boot, vertrektijd, spullen en inkopen; daarnaast grappen en overleg over wat men die avond doet. `bold-monkey` en `breezy-bouncing` bespreken de reislogistiek, `animated-chimpanzee` vraagt naar plannen. |
| 2015-08-12 | 175 | Reis & vakantie | Verdere Terschelling-planning: route via Harlingen/Leeuwarden, bagage, slaapspullen en kaarten; later losse avondplannen. `kaleidoscopic-yapok` en `teasing-tapir` organiseren spullen en afspraken; `dynamic-camel` vergelijkt treinroutes. |
| 2016-09-02 | 272 | Sociale afspraken & groepsactiviteiten | Zwemmen bij de Vliet en het weer; wie 's avonds gaat chillen of uitgaan; verjaardag en auto; losse petten-/memegrappen. `dynamic-camel` stuurt veel afstemming, `opalescent-swallow` probeert zwemmers te verzamelen en `laughing-chough` helpt met avondplannen. |
| 2016-09-09 | 224 | Sociale afspraken & groepsactiviteiten | Uitgaan de vorige nacht, zwemmen bij de Vliet, een feest in Rijswijk en avondplannen; ook komt een pijnlijke knie ter sprake. `dynamic-camel` en `teasing-tapir` mobiliseren mensen voor de Vliet/het feest; `laughing-chough` organiseert de avond en biedt steun rond de knie. |
| 2016-09-10 | 231 | Sociale afspraken & groepsactiviteiten | Een nachtelijke chill-afspraak loopt door; overdag plannen voor het Strandwalfestival, eten en later uitgaan. Een aantal nachtelijke berichten is onbegrijpelijk doordat de auteurs woordenvoorspelling/spraakinput lijken te gebruiken. `kaleidoscopic-yapok` en `laughing-chough` stemmen af; `dynamic-camel` en `uproarious-gnat` bespreken het festival. |
| 2016-09-16 | 188 | Sociale afspraken & groepsactiviteiten | De groep probeert chill-afspraken te maken rond werk, weer, vervoer en geld; later wordt een plek en tijd afgestemd. `dynamic-camel` en `opalescent-swallow` trekken de planning, `laughing-chough` sluit na werk aan en `carbonated-quetzal` meldt werkverplichtingen. |
| 2016-09-17 | 175 | Sociale afspraken & groepsactiviteiten | Kijken naar een voetbalwedstrijd van `kaleidoscopic-yapok`, daarna plannen om uit te gaan/chillen; er is plagerige voetbalcommentaar en overleg over werk/geld. `kaleidoscopic-yapok` nodigt uit, `breezy-bouncing` moedigt anderen aan om mee te gaan en `dynamic-camel` peilt wie aansluit. |
| 2016-09-21 | 242 | School & opleiding | `breezy-bouncing` vertelt over een relatiebreuk en bespreekt met de groep dat die beter zo is; `dynamic-camel` vraagt advies over stoppen met de huidige opleiding en overstappen naar koksopleiding. `breezy-bouncing` geeft concreet advies; later regelen ze mogelijk samen een voetbalwedstrijd bijwonen. |
| 2016-10-16 | 152 | Dagelijks leven & vrije tijd | Grappen over een fietsongeval na het uitgaan, videogames en avondplannen; er volgt een verjaardagsuitnodiging. `carbonated-quetzal` vertelt over de val, `breezy-bouncing` en `piebald-duck` praten over games en `silky-lion` nodigt uit. |
| 2016-11-28 | 181 | Sociale afspraken & groepsactiviteiten | Een paintballuitje wordt gepland (datum, vervoer, kosten); daarnaast wordt een eerdere avond uit besproken en een nieuwe vriendin aan de groep gekoppeld. `kaleidoscopic-yapok` start met paintball, `teasing-tapir` bespreekt beschikbaarheid en `carbonated-quetzal` haalt herinneringen aan het weekend op. |
| 2017-01-11 | 191 | Sociale afspraken & groepsactiviteiten | Afscheidsfeest en een grotere squad-bijeenkomst met groepsfoto, gasten en drank worden georganiseerd. `kaleidoscopic-yapok` neemt de planning op zich; `laughing-chough` en `dynamic-camel` reageren en bevestigen deelname. |
| 2017-03-08 | 196 | Sociale afspraken & groepsactiviteiten | De groep merkt dat een Netflix-wachtwoord is veranderd en probeert het terug te regelen; daarna plannen ze een bowlingavond inclusief tijd, baan en prijs. `kaleidoscopic-yapok` en `dynamic-camel` coördineren, `laughing-chough` bespreekt of die na werk mee kan. |
| 2017-06-22 | 162 | Sociale afspraken & groepsactiviteiten | Praktische coördinatie voor paintball: deelnemers, verzamelplek, vervoer en vertraging door treinproblemen. `piebald-duck` beheert de reservering en verzamelt bevestigingen; `breezy-bouncing` meldt dat de trein de aankomst in gevaar brengt. |
| 2018-01-25 | 170 | Dagelijks leven & vrije tijd | Plagerige discussie over een huisgenoot die kaas at; verder studeren/werken, gamen, auto's en wie gaat chillen. `teasing-tapir` begint het kaasgesprek, `breezy-bouncing` en `nutty-pelican` reageren; `nutty-pelican` vertelt over een bedrijfseconomiestudie. |
| 2020-03-15 | 178 | Corona & actualiteit | Reacties op coronamaatregelen en sluitingen, werk en leverings-/schaarsteberichten in supermarkten; de groep maakt ook grappen over inslaan en hoe ze thuis de tijd gaan doorbrengen. `kaleidoscopic-hyena` meldt sluitingen, `silky-lion` deelt informatie over bevoorrading en `breezy-bouncing` en `laughing-chough` praten over werk en thuisactiviteiten. |
| 2020-09-01 | 202 | Geld & gezamenlijke kosten | Afrekening na een groepsreis naar Frankrijk: boodschappen, benzine en andere gezamenlijke kosten via een verdeelapp/Tikkies; daarnaast wordt een coronatestuitslag gevierd en is er reis-/etenbanter. `opalescent-swallow` jaagt de afrekening aan, `silky-lion` en `nutty-pelican` helpen de app uitzoeken. |
| 2021-12-12 | 162 | Sport & live wedstrijden | Live reacties op de spannende Formule 1-finale waarin Verstappen kampioen wordt, met discussie over beslissingen, strategie en Perez; later kort vervoer/overnachtspullen regelen. `nutty-pelican`, `laughing-chough` en `silky-lion` geven doorlopend commentaar; `opalescent-swallow` reageert op de race. |
| 2022-08-01 | 167 | Geld & gezamenlijke kosten | Afrekening en herinneringen aan de groepsvakantie: boodschappen, maaltijden, kanoën en wie nog moet betalen; gedeelde foto's en grappen over eten. `silky-lion` probeert de gezamenlijke kosten te verrekenen, `opalescent-swallow` en `nutty-pelican` helpen de app en afspraken te verduidelijken. |
| 2023-06-24 | 156 | Entertainment & media | De groep probeert voorwerpen op een afbeelding aan films te koppelen; een quiz-achtig gesprek met veel gezamenlijke gokjes en correcties. `breezy-bouncing` houdt een filmlijst bij, `nutty-pelican` controleert antwoorden en `laughing-chough` en `silky-lion` vullen aan. |
| 2024-06-21 | 154 | Sport & live wedstrijden | Praktische afspraken over een verjaardag en vervoer; 's avonds live commentaar op Nederland–Frankrijk op het EK voetbal. `nutty-pelican` leidt de meeste voetbaldiscussie, `laughing-chough` en `silky-lion` reageren op spelers en scheidsrechter; `breezy-bouncing` bespreekt vervoer. |

### Categorieën die terugkomen

- **Sociale afspraken & groepsactiviteiten** is de duidelijkste terugkerende categorie
  (10 dagen): 2015-04-03, 2016-09-02, 2016-09-09, 2016-09-10, 2016-09-16,
  2016-09-17, 2016-11-28, 2017-01-11, 2017-03-08 en 2017-06-22.
- **Reis & vakantie** komt terug op 2015-07-24 en 2015-08-12; beide dagen draaien om
  de voorbereiding van de Terschelling-reis.
- **School & examens/opleiding** komt voor op 2015-06-11 en 2016-09-21. In de eerste
  gaat het om uitslagen en herkansingen; in de tweede vooral om een opleidingskeuze.
- **Geld & gezamenlijke kosten** komt terug op 2020-09-01 en 2022-08-01, beide rond het
  verrekenen van kosten van een groepsvakantie.
- **Sport & live wedstrijden** komt terug op 2021-12-12 en 2024-06-21, als live
  groepscommentaar op sportwedstrijden.
- **Dagelijks leven & vrije tijd** komt terug op 2016-10-16 en 2018-01-25, met losse
  persoonlijke onderwerpen, grappen en vrijetijdsgesprekken.
- **Corona & actualiteit** en **Entertainment & media** komen elk één keer voor in deze
  selectie.

De berichtenaantallen duiden op volume, niet op belang of representativiteit van de thema's.
Op sommige dagen is een deel van de context afhankelijk van ontbrekende media of voorafgaande
berichten. De 2020-09-01-dag bevatte bank-/betaalgegevens in de bron; die zijn bewust niet in
deze samenvatting opgenomen.
