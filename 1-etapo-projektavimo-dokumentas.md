# Kandidatų atitikties vertinimo sistema

Kursinio darbo I dalis: projektavimo dokumentas

## 1. Problema ir idėja

**Sistema vienu sakiniu:** Ši sistema automatiškai įvertina, kiek kandidatas atitinka konkrečios darbo pozicijos reikalavimus, priskiria atitikties balą ir rekomendaciją (ką su kandidato anketa daryti toliau).

**Problema ir dabartinis procesas:** HR specialistai vienai pozicijai gauna daug kanditatų anketų ir kiekvieną rankiniu būdu lygina su reikalavimais. Toks procesas lėtas ir subjektyvus – skirtingi vertintojai tą patį kandidatą gali įvertinti skirtingai, lengva per ilgai analizuoti akivaizdžiai netinkamą kandidatą arba praleisti tinkamą kandidatą, kai yra daug anketų.

**Nauda:** Sistema automatiškai apskaičiuoja kandidato atitikties balą ir pateikia aiškų paaiškinimą, leidžiantį greitai surikiuoti kandidatus. Akivaizdžius atvejus, kai kandidatas tinka arba netinka, sistema sprendžia pati, o neaiškius - perduoda žmogui patikrinti rankiniu būdu.

**Naudotojai:** HR darbuotojas - kuria pozicijos reikalavimus, peržiūri atitikties rezultatus ir priima galutinį sprendimą; kandidatas - pateikia savo duomenis forma.

**Prielaidos:** Darome prielaidą, kad pozicijos reikalavimai apibrėžiami struktūrizuotai (įgūdžių sąrašas, minimali patirtis, atlyginimo rėžiai, išsilavinimas), o ne laisvo teksto skelbimu. Darome prielaidą, kad kandidato duomenys pateikiami struktūrizuota forma, o ne laisvo teksto forma.

## 2. Apimtis

| Funkcija | Ką naudotojas galės atlikti | Pagrindinis modulis ar pagalbinė funkcija |
|---|---|---|
| Kandidato atitikties įvertinimas pozicijai | Kandidatas įveda pateikia savo duomenis pasirinktai pozicijai, o sistema apskaičiuoja atitikties balą ir rekomendaciją | Pagrindinis modulis |
| Kandidatų sąrašo rikiavimas pagal balą | HR mato visų pozicijai pateiktų kandidatų sąrašą, surikiuotą pagal atitikties balą | Pagrindinis modulis |
| Pozicijos reikalavimų valdymas | HR sukuria ir redaguoja pozicijos reikalavimus | Pagrindinis modulis |
| Kandidato balo detalizacija | HR mato, kaip balas paskirstytas pagal atskirus kriterijus | Pagalbinė funkcija |
| Kandidatūros būsenos keitimas | HR gali rankiniu būdu patvirtinti, atmesti arba pažymėti kandidatą tolesnei peržiūrai | Pagalbinė funkcija |

**Į kursinio darbo apimtį neįeina:** CV failo automatinis duomenų išgavimas naudojant DI, atlyginimo derybos, pranešimai el. paštu, integracija su trečiųjų šalių darbo portalais.

## 3. Pagrindinis modulis

**Pavadinimas ir atsakomybė:** Atitikties vertinimo variklis (Matching Score Engine). Gavęs kandidato duomenis ir pozicijos reikalavimus, apskaičiuoja svorinį atitikties balą ir priskiria rekomendaciją.

**Logika:** privalomų reikalavimų tikrinimas, svorinis kriterijų vertinimas atitinkamai pagal įgūdžius ir patirtis, ribinių atvejų, kai balas arti sprendimo ribos, žymėjimas rankinei peržiūrai.

**Įvestis:** kandidato duomenys (įgūdžių sąrašas su lygiu skalėje 1–5, kur 1 = pradedantysis, 5 = ekspertas; patirties metai; atlyginimo lūkestis) ir pozicijos reikalavimai: privalomi įgūdžiai (tik taip/ne patikrinimas) ir svoriniai kriterijai – įgūdžiai su reikalaujamu lygiu, patirtis ir atlyginimas, kiekvienas su savo svoriu (visi kartu sumuojasi į 1,0).
Pavyzdys:
```
{
  kandidatas: {igudziai: {"Python": 3, "SQL": 2, "Docker": 2}, patirtis_metais: 4, atlyginimo_lukestis: 2500},
  pozicija: {
    privalomi: ["Python"],
    kriterijai: {
      "SQL": {reikalaujamas_lygis: 3, svoris: 0.3},
      "Docker": {reikalaujamas_lygis: 2, svoris: 0.2},
      "patirtis": {min: 3, svoris: 0.3},
      "atlyginimas": {intervalas: [2000, 2800], svoris: 0.2}
    }
  }
}
```

**Išvestis:** trys dalys:
- **balas** (0–100) – bendras svorinis atitikties balas, apskaičiuojamas kaip kriterijų balų svorinė suma: `balas = Σ (kriterijaus_balas × jo_svoris)`.
- **rekomendacija** (TINKAMAS / NETINKAMAS / PERŽIŪRĖTI RANKINIU BŪDU) – galutinis sprendimas pagal 3. skyriaus taisykles.
- **paaiškinimas** – kiekvieno kriterijaus (įgūdžių, patirties, atlyginimo) atskiras procentinis balas, kad HR matytų, *kodėl* gautas būtent toks bendras rezultatas, o ne tik galutinį skaičių.

Pavyzdys: `{balas: 90, rekomendacija: "TINKAMAS", paaiskinimas: {SQL: 67, Docker: 100, patirtis: 100, atlyginimas: 100}}`
Paaiškinimas: SQL kriterijus pasiekė tik 67 % savo galimo indėlio (kandidato lygis 2 žemesnis už reikalaujamą 3), o visi kiti kriterijai – 100 %. Bendras svorinis balas (67%×0,3 + 100%×0,2 + 100%×0,3 + 100%×0,2 ≈ 90) viršija ribinę 50–65 zoną ir visi privalomi reikalavimai tenkinti, todėl galutinė rekomendacija – TINKAMAS.

**Veikimo eiga:**
1. Validuoti, kad pozicijos kriterijų svoriai sumuojasi į 1,0.
2. Patikrinti privalomus reikalavimus – jei netenkintas bent vienas, iškart NETINKAMAS, tolesni žingsniai nevykdomi.
3. Apskaičiuoti kiekvieno svorinio kriterijaus (įgūdžiai, patirtis, atlyginimas) balą.
4. Sudėti bendrą svorinį balą.
5. Jei balas patenka į ribinę zoną arba trūksta duomenų – pažymėti "PERŽIŪRĖTI RANKINIU BŪDU".
6. Grąžinti balą, rekomendaciją ir detalų paaiškinimą.

### Taisyklės arba sprendimo žingsniai

1. Jei kandidatas neatitinka bent vieno privalomo reikalavimo, galutinis rezultatas yra NETINKAMAS, nepriklausomai nuo kitų kriterijų balų.
2. Įgūdžio kriterijaus balas = min(kandidato_lygis / reikalaujamas_lygis, 1,0) × 100 %. Pvz. kandidato SQL lygis 2 prie reikalaujamo 3 duoda 67 % atitiktį, o ne 0 % ar 100 %.
3. Patirties kriterijaus balas = min(kandidato_patirtis / min_patirtis, 1,0) × 100 %.
4. Atlyginimo kriterijaus balas lyginant kandidato lūkestį `L` su pozicijos intervalu `[min; max]`:
   - `L < min` (lūkestis žemiau intervalo) – 100 %, nes pigesnis kandidatas darbdavio biudžeto neviršija; kandidatas dėl to nenubaudžiamas;
   - `min ≤ L ≤ max` – 100 %;
   - `max < L ≤ 1,1 × max` – balas = `(1 − (L − max) / (0,1 × max)) × 100 %`, t. y. mažėja tiesiškai nuo 100 % (ties `max`) iki 0 % (ties `1,1 × max`). Pvz. intervalas 2000–2800, `L` = 2940 → (1 − 140/280) × 100 = 50 %;
   - `L > 1,1 × max` – 0 %.
5. Bendras balas = Σ (kriterijaus balas × jo svoris). Visų kriterijų (įgūdžių, patirties, atlyginimo) svoriai turi sumuotis iki 1,0; jei nesusumuoja, sistema prieš skaičiavimą grąžina klaidą, o ne klaidingą balą.
6. Trūkstami duomenys. Kriterijaus duomuo laikomas **nežinomu**, jei jis nenurodytas (įgūdis nepateiktas kandidato sąraše, nėra patirties ar atlyginimo lūkesčio). Nežinomas kriterijus **neturi procentinio balo**, bet į bendrą sumą įneša 0 taškų (konservatyvus sprendimas: nežinomas duomuo nepakelia balo). Paaiškinime jis rodomas kaip „nežinoma“, o ne kaip 0 %. Tai skiriasi nuo žinomo, bet žemo rezultato: pvz. kandidato lūkestis, viršijantis `1,1 × max`, yra **0 %** (žinomas blogas atitikimas). Be to, nežinomas kriterijus visada įjungia rankinės peržiūros požymį (7 taisyklė). Privalomo reikalavimo nežinomumas (įgūdis nenurodytas) laikomas netenkintu → NETINKAMAS (1 taisyklė).
7. Sprendimo tvarka: (a) netenkintas privalomas reikalavimas → NETINKAMAS; (b) kitu atveju, jei bent vienas svorinis kriterijus nežinomas **arba** bendras balas yra intervale **50 ≤ balas ≤ 65** (imtinai abi ribos) → PERŽIŪRĖTI RANKINIU BŪDU; (c) kitu atveju balas > 65 → TINKAMAS, balas < 50 → NETINKAMAS. Nežinomi duomenys todėl nuleidžia net aukštą balą į rankinę peržiūrą.

### Scenarijai būsimiems testams

| Scenarijus | Pradinės sąlygos ir konkreti įvestis | Veiksmas | Tikslus laukiamas rezultatas |
|---|---|---|---|
| Įprastas atvejis | Pozicija: privalomas Python; kriterijai – SQL (reikalaujamas lygis 3, svoris 0,3), Docker (reikalaujamas lygis 2, svoris 0,2), patirtis (min 3 m., svoris 0,3), atlyginimas (2000–2800, svoris 0,2) | Kandidatas: Python 3, SQL 2, Docker 2, patirtis 4 m., lūkestis 2500 | TINKAMAS, balas ≈90 (SQL atitiktis tik 67 %, nes kandidato lygis žemesnis už reikalaujamą, bet kiti kriterijai kompensuoja) |
| Ribinis atvejis arba konfliktas | Ta pati pozicija (privalomas Python; SQL – lygis 3, svoris 0,3; Docker – lygis 2, svoris 0,2; patirtis – min 3 m., svoris 0,3; atlyginimas 2000–2800, svoris 0,2) | Kandidatas: Python 3, SQL 1, **Docker nenurodytas (nežinomas)**, patirtis 4 m., lūkestis 2500 | Kriterijų balai: SQL = min(1/3; 1) × 100 = 33,3 % → 33,3 % × 0,3 = **10**; Docker = **nežinoma** (ne 0 %) → įneša **0** taškų; patirtis = 100 % × 0,3 = **30**; atlyginimas = 100 % (2500 patenka į 2000–2800) × 0,2 = **20**. Bendras balas = 10 + 0 + 30 + 20 = **60**. 60 patenka į 50–65 zoną ir Docker nežinomas → PERŽIŪRĖTI RANKINIU BŪDU; paaiškinime: `{SQL: 33, Docker: "nežinoma", patirtis: 100, atlyginimas: 100}`, silpniausi kriterijai – SQL (33 %) ir Docker (nežinoma, trūksta duomenų) |
| Klaida arba neįmanomas rezultatas | Ta pati pozicija | Kandidatas neturi Python įgūdžio (privalomas reikalavimas) | NETINKAMAS iškart, be tolesnio balo skaičiavimo. Papildomas atvejis: pozicijos kriterijų svoriai sumuojasi į 0,9 (ne 1,0) → sistema grąžina klaidą „Neteisingi pozicijos svoriai“, balas neskaičiuojamas |

**Jei modulis naudoja AI:** Netaikoma.

## 4. Kokybės atributas

**Pasirinktas atributas:** Palaikomumas (angl. maintainability).

**Kodėl svarbus šiai sistemai:** Skirtingos pozicijos ir organizacijos norės skirtingų vertinimo kriterijų (pvz. sertifikatai, kalbų mokėjimas). Naujus kriterijus turi būti galima pridėti nerizikuojant sugadinti esamos balo skaičiavimo logikos.

**Tikrinimo scenarijus ir sąlygos:** Pridedamas naujas kriterijus „sertifikatai“ su savo svoriu, nekeičiant esamų kriterijų (įgūdžiai, patirtis, atlyginimas) skaičiavimo kodo.

**Sėkmės kriterijus:** Naujas kriterijus įgyvendinamas kaip atskiras objektas, atitinkantis bendrą sąsają, ir užregistruojamas kriterijų sąraše; esamos klasės lieka nepakeistos; visi anksčiau parašyti testai lieka žali (100 %).

**Numatytas projektavimo sprendimas:** Kiekvienas kriterijus – atskiras objektas, įgyvendinantis bendrą sąsają. Sistema iteruoja per registruotų kriterijų sąrašą ir sudeda svorinį balą.

**Kaip patikrinsiu vėlesniame etape:** Kiekvienam kriterijui – atskiras unit testas, visai sistemai – integracinis. Pridėjus naują kriterijų, paleisiu visą testų rinkinį ir patikrinsiu, kad senieji testai liko žali ir kodo pakeitimai apsiriboja vienu nauju failu.

**Sprendimo kaina:** Daugiau integracijos nei tiesioginis skaičiavimas, bet tai atsiperka, kai skirtingoms pozicijoms ar organizacijoms reikės skirtingų kriterijų rinkinių.

## 5. Pradinė sistemos struktūra

### Paprasta schema

```
[Naudotojo sąsaja (Web UI)]
        |
        v  HTTP užklausa (vertinimo prašymas)
[API / valdiklio sluoksnis]
        |
        v  kviečia domeno logiką
[Atitikties vertinimo variklis (domeno logika, kriterijų sąrašas)]
        |
        v  skaito / rašo
[Duomenų saugykla (pozicijos, kandidatai, vertinimų rezultatai)]
```

| Sistemos dalis | Atsakomybė |
|---|---|
| Naudotojo sąsaja (Web UI) | Priima pozicijos reikalavimus ir kandidato duomenis, rodo balą, rekomendaciją ir kandidatų sąrašą |
| API / valdiklio sluoksnis | Priima HTTP užklausas, validuoja formatą, perduoda domeno logikai, grąžina atsakymą |
| Atitikties vertinimo variklis | Kriterijų vertinimas, svorinio balo skaičiavimas, rekomendacijos priskyrimas |
| Duomenų saugykla | Saugo pozicijas, kandidatus ir vertinimų rezultatus |

**Planuojamos technologijos ir pasirinkimo priežastys:** Python + FastAPI – greitas prototipavimas, aiškus domeno logikos atskyrimas nuo web sluoksnio, geras testų palaikymas (pytest). SQLite pradiniam prototipui – nereikia atskiro serverio. Pirmai iteracijai – paprastas HTML/JS priekinis sluoksnis.

## 6. AI panaudojimas

### AI rengiant šį dokumentą

| Priemonė ir užduotis | Ką panaudojau | Ką atmečiau arba perrašiau ir kodėl | Kaip patikrinau |
|---|---|---|---|
| Claude – temos išsigryninimas | Padėjo suprasti problemą, apsispręsti, kuo sistema būtų naudinga, ir sugalvoti, kokias papildomas funkcijas galėčiau integruoti | Iš kelių AI pasiūlytų temų pasirinkau kandidatų atitikties vertinimo sistemą, nes ji man pasirodė aiškiausia | Palyginau pasiūlymą su tuo, ką pats norėjau daryti, ir pasirinkau artimiausią savo supratimui |
| Claude – Markdown formatavimas | Kadangi anksčiau niekada nedirbau su .md failais, naudojau Claude, kad tekstas būtų tvarkingai suformatuotas (antraštės, lentelės, paryškinimai) | Formatavimą palikau beveik be pakeitimų, nes tai tik techninė failo išvaizda, ne turinys | Patikrinau, kad dokumentas tvarkingai atsivaizduoja GitHub'e |
| ChatGPT – teksto juodraščio rašymas | Pradinį teksto variantą atskiriems skyriams | Vėliau perrašiau savais žodžiais, kaip pats būčiau pasakęs ir parašęs, kad tikrai suprasčiau ir galėčiau paaiškinti kiekvieną teiginį | Perskaičiau ir palyginau kiekvieną skyrių su užduoties reikalavimais punktas po punkto |

### Planuojamas AI naudojimas kuriant sistemą

**Kur ir kam naudosiu AI:** AI kodo generavimo pagalbai; pagrindinę domeno logiką rašysiu ir testuosiu pats.

**Kaip tikrinsiu pasiūlymus ir sugeneruotą kodą:** Unit testais kiekvienam pakeitimui ir rankine kodo peržiūra, lyginant su 3 skyriaus taisyklėmis.

**Ar AI bus funkcionalumo dalis:** Ne.

## 7. Tolesnių darbų planas

| Darbas | Apčiuopiamas rezultatas | Planuojama darbų seka |
|---|---|---|
| Duomenų modelio ir saugyklos įgyvendinimas | Veikianti duomenų bazės schema (pozicijos, kandidatai) su testiniais duomenimis | 1 |
| Vertinimo variklio (kriterijų) įgyvendinimas | Praeinantys unit testai visoms taisyklėms ir 3 skyriaus scenarijams | 2 |
| API sluoksnio sukūrimas | Veikiantys endpoint'ai: reikalavimų kūrimas, kandidato vertinimas, sąrašo gavimas | 3 |
| Paprastas UI reikalavimams įvesti ir kandidatų sąrašui peržiūrėti | Naudotojas gali pereiti nuo įvesties iki rezultato naršyklėje | 4 |
| Kandidatūros būsenos valdymo funkcija | HR gali rankiniu būdu pakeisti rekomendaciją | 5 |

**Būsimo prototipo veikimo scenarijus:** HR sukuria poziciją „Python programuotojas“ su reikalavimais (privalomas Python, pageidaujami SQL ir Docker, min. 3 metų patirtis, atlyginimas 2000–2800). Kandidatas įveda duomenis. Sistema iš karto parodo balą, rekomendaciją ir paaiškinimą, kodėl toks balas gautas.

| Rizika arba neaiškumas | Kaip patikrinsiu arba sumažinsiu |
|---|---|
| Neaišku, kaip tiksliai nustatyti ribinės zonos (50–65) ribas skirtingoms pozicijoms | Testuosiu su keliais realistiniais pavyzdžiais ir koreguosiu ribas pagal rezultatus |
| Kriterijų svorių balansavimas gali būti subjektyvus | HR pats galės nustatyti svorius vietoj fiksuotų reikšmių; dokumentuosiu numatytąsias reikšmes |
| Trūkstami kandidato duomenys gali iškraipyti balą | Trūkstamus duomenis aiškiai žymėsiu ir tokius atvejus automatiškai siųsiu į PERŽIŪRĖTI RANKINIU BŪDU |

## Šaltiniai, jei naudojote

Nenaudojau
