# Kandidatų atitikties vertinimo sistema

Kursinio darbo II dalis: veikiantis prototipas.

Sistema įvertina, kiek kandidatas atitinka darbo pozicijos reikalavimus: apskaičiuoja svorinį balą (0–100), priskiria rekomendaciją (TINKAMAS / NETINKAMAS / PERŽIŪRĖTI RANKINIU BŪDU) ir parodo, kiek prie balo prisidėjo kiekvienas kriterijus. Taisyklės aprašytos [I etapo dokumente](1-etapo-projektavimo-dokumentas.md) (3 skyrius).

## Reikalingi įrankiai

- Python 3.10 arba naujesnė versija (kurta ir tikrinta su Python 3.14)
- Bibliotekos surašytos `requirements.txt`: FastAPI 0.163.0, Uvicorn 0.54.0, pytest 9.2.0, httpx 0.28.1
- Duomenų bazė – SQLite, ji yra Python dalis, atskirai diegti nereikia

## Pradinis paruošimas

Komandos vykdomos projekto aplanke.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Paleidimas

```bash
uvicorn app.main:app
```

Naršyklėje atidaryti <http://localhost:8000>.

## Testai

```bash
pytest
```

- `tests/test_engine.py` – pagrindinio modulio (vertinimo variklio) testai: įprastas atvejis, ribinis atvejis ir du klaidos atvejai (netenkintas privalomas reikalavimas, neteisingi pozicijos svoriai).
- `tests/test_isolation.py` – klientų (organizacijų) duomenų izoliavimo testas.

## Konfigūracija

Papildomos konfigūracijos ir API raktų nereikia. Pirmo paleidimo metu projekto aplanke sukuriamas duomenų bazės failas `data.db` ir į jį įrašomi pavyzdiniai duomenys. Norint grąžinti pradinius duomenis, reikia sustabdyti programą, ištrinti `data.db` ir paleisti iš naujo.

## Pavyzdiniai duomenys

Įkeliami iš `app/sample_data.py`.

| Organizacija | Pozicija | Kandidatai |
|---|---|---|
| UAB Kodo Dirbtuvės | Python programuotojas | Ona Onaitė (60, PERŽIŪRĖTI RANKINIU BŪDU), Petras Petraitis (NETINKAMAS) |
| UAB Kodo Dirbtuvės | Testuotojas (klaidos pavyzdys: svoriai nesusumuoja į 1,0) | – |
| UAB Duomenų Namai | Duomenų analitikas | Rasa Rasaitė (76,36, TINKAMAS) |

Pozicijos „Testuotojas“ kriterijų svoriai tyčia sumuojasi į 0,9, kad būtų galima parodyti klaidos atvejį.

## Klientų atskyrimas

Klientas yra organizacija. Kiekviena pozicija ir kiekvienas kandidatas duomenų bazėje turi `organization_id`. Užklausa nurodo organizaciją antrašte `X-Organization` (puslapyje ją nustato pasirinkimas „Organizacija“), o visos duomenų bazės užklausos `app/storage.py` faile filtruoja pagal `organization_id`. Prisijungimo šiame etape nėra – jis numatytas III etapui.

## Demonstravimo žingsniai

1. **Pagrindinis scenarijus.** Organizacija „UAB Kodo Dirbtuvės“, pozicija „Python programuotojas“. Įvesti: vardas `Jonas Jonaitis`, Python `3`, SQL `2`, Docker `2`, patirtis `4`, atlyginimo lūkestis `2500`. Rezultatas: balas `90`, TINKAMAS, paaiškinimas `SQL: 67 %, Docker: 100 %, patirtis: 100 %, atlyginimas: 100 %`. Kandidatas atsiranda sąrašo viršuje.
2. **Ribinis atvejis.** Tie patys duomenys, tik SQL `1`, o Docker laukas paliktas tuščias. Rezultatas: balas `60`, PERŽIŪRĖTI RANKINIU BŪDU, `Docker: nežinoma`.
3. **Klaidos atvejis – netenkintas privalomas reikalavimas.** Python laukas paliktas tuščias. Rezultatas: NETINKAMAS, balas neskaičiuotas.
4. **Klaidos atvejis – neteisingi pozicijos svoriai.** Pasirinkti poziciją „Testuotojas (klaidos pavyzdys…)“ ir pateikti bet kokį kandidatą. Rezultatas: `Klaida: Neteisingi pozicijos svoriai`, kandidatas neišsaugomas.
5. **Klientų atskyrimas.** Pasirinkti organizaciją „UAB Duomenų Namai“ – matoma tik jos pozicija ir jos kandidatai. Tiesioginis bandymas pasiekti kitos organizacijos poziciją:

   ```bash
   curl -H "X-Organization: 2" http://localhost:8000/api/positions/1/candidates
   ```

   Atsakymas: `{"detail":"Pozicija nerasta"}`.
6. **Testai.** Sustabdyti programą (`Ctrl+C`) ir paleisti `pytest`.
