#!/usr/bin/env python3
"""
check_artikelnummer.py
=======================================================================
VAD GÖR DETTA SCRIPT?
-----------------------------------------------------------------------
Kontrollerar era "item-filer" (JSON) mot två listor:

  1. ARTIKELNUMMER (material): kontrollerar att alla artikelnummer som
     används (tsk_material_number, där tsk_material_type = "SV-ENR" som
     standard) faktiskt finns i grossistens masterprislista (CSV-export,
     t.ex. från Ahlsell).

  2. ARBETSKODER (arbetstid): kontrollerar att alla arbetskoder som
     används (tsk_work_code, där tsk_work_type = "SV-ATL" som standard)
     finns registrerade i en arbetskodslista (CSV, t.ex. work_types_rows.csv),
     och om de i så fall är AKTIVA eller UTGÅNGNA (styrs av kolumnen
     tsk_work_task_valid i den listan).

Båda kontrollerna görs i samma körning och sammanfattas i EN .txt-rapport.
Arbetskodskontrollen är valfri - saknas arbetskodslistan hoppas den delen
bara över och du får fortfarande en fullständig artikelnummer-rapport.

Resultatet blir en tydlig .txt-rapport som visar:
  - Hur många item-filer som kontrollerades
  - Hur många unika artikelnummer/arbetskoder som används totalt
  - Hur många av dem som hittades (träffar) respektive SAKNAS
  - För arbetskoder: hur många som är AKTIVA respektive UTGÅNGNA
  - För varje saknat/utgånget nummer eller kod: exakt i vilken/vilka
    item-filer (fullständig sökväg) och under vilken uppgift ("task")
    det används, så att du kan gå direkt dit och rätta.

Scriptet körs helt lokalt på din dator/server. Ingen uppkoppling mot
GitHub eller internet krävs eller används.


-----------------------------------------------------------------------
SÅ HÄR ANVÄNDER DU DET (enklaste sättet)
-----------------------------------------------------------------------
1. Lägg den här filen (check_artikelnummer.py) i ROTEN av mappen där du
   har klonat/laddat ner era item-filer (JSON) lokalt. Scriptet letar
   igenom ALLA undermappar, oavsett hur många nivåer djupt de ligger.

2. Lägg BÅDA CSV-filerna i en undermapp som heter "private-data" bredvid
   scriptet:

       repo-rot/
       ├── check_artikelnummer.py
       ├── .gitignore
       ├── private-data/
       │   ├── Master_Price_List_Sv_Enr_Step_4.csv   <- masterprislista
       │   └── work_types_rows.csv                    <- arbetskodslista
       └── ... era item-filer i mappar/undermappar ...

   Mappen "private-data" är avsedd för känsligt material (priser,
   rabattkoder, interna arbetskoder m.m.) och ska ALDRIG laddas upp till
   GitHub - den gitignoras i sin helhet, se avsnittet om .gitignore
   nedan. Mappen skapas automatiskt av scriptet om den saknas.

   Masterprislistan hittas automatiskt om filnamnet innehåller "master",
   "pris" eller "price". Arbetskodslistan hittas automatiskt om filnamnet
   innehåller "work_type", "worktype", "arbetstid" eller "arbetskod".
   Annars används den kvarvarande .csv-filen i mappen.

3. Öppna en terminal i repo-roten och kör:

       python check_artikelnummer.py

   Det är allt - inga argument behövs. Scriptet:
     - hittar automatiskt sin egen mapp och söker item-filer där
       (rekursivt, alla undermappar),
     - hittar automatiskt master-CSV:n och arbetskodslistan i
       private-data/,
     - skriver rapporten i private-data/ med dagens datum och klockslag
       i filnamnet, t.ex. artikelnummer_rapport_2026-08-11_1432.txt,
       så gamla rapporter aldrig skrivs över av misstag OCH så att
       rapporten - som kan innehålla interna produktnamn - inte heller
       laddas upp till Git av misstag.

4. Öppna den skapade .txt-rapporten (i private-data/) och gå igenom
   listorna över saknade artikelnummer och ej registrerade/utgångna
   arbetskoder. Varje rad talar om exakt vilken fil och uppgift det
   hör hemma i.


-----------------------------------------------------------------------
AVANCERAD ANVÄNDNING (valfria flaggor)
-----------------------------------------------------------------------
Du behöver ALDRIG ange dessa - de finns bara om du vill styra något
manuellt:

    --items-root SÖKVÄG
        Vilken mapp som ska sökas igenom (rekursivt) efter .json-filer.
        Standard: samma mapp som scriptet ligger i.

    --master SÖKVÄG
        Sökväg till en specifik masterprislista (CSV).
        Standard: den .csv-fil som hittas i private-data/ (eller,
        bakåtkompatibelt, bredvid scriptet om private-data/ är tom).

    --worktypes SÖKVÄG
        Sökväg till en specifik arbetskodslista (CSV).
        Standard: den .csv-fil som hittas i private-data/. Om ingen
        hittas hoppas arbetskodskontrollen helt enkelt över.

    --output SÖKVÄG
        Var rapporten ska sparas, och under vilket filnamn.
        Standard: private-data/artikelnummer_rapport_ÅÅÅÅ-MM-DD_TTMM.txt

    --material-type TYP
        Vilken tsk_material_type som ska kontrolleras. Standard: SV-ENR.

    --work-type TYP
        Vilken tsk_work_type som ska kontrolleras. Standard: SV-ATL.

    --skip-worktypes
        Hoppa över arbetskodskontrollen helt, även om en arbetskodslista
        skulle hittas automatiskt.

Exempel med alla flaggor:

    python check_artikelnummer.py \\
        --items-root /home/anvandare/projekt/item-filer \\
        --master /home/anvandare/projekt/master/Ahlsell_prislista.csv \\
        --worktypes /home/anvandare/projekt/master/work_types_rows.csv \\
        --output /home/anvandare/projekt/rapporter/kontroll.txt \\
        --material-type SV-ENR \\
        --work-type SV-ATL


-----------------------------------------------------------------------
VILKA FORMAT PÅ CSV-FILERNA HANTERAS?
-----------------------------------------------------------------------
Båda CSV-filerna läses RADVIS (aldrig hela filen i minnet på en gång),
så det fungerar utan problem även för mycket stora filer (100+ MB,
hundratusentals rader).

Två CSV-format hanteras automatiskt, utan att du behöver göra något,
och SAMMA parsningslogik används för båda filerna (masterprislistan och
arbetskodslistan), så du kan blanda fritt:

  1. Vanlig CSV med kommatecken som avgränsare:
         material_type,material_number,material_name,...
         id,tsk_work_type,tsk_work_code,...

  2. "Dubbel-inpackad" CSV, vilket är vanligt när stora Excel-ark
     exporteras till CSV. Där ser varje rad ut ungefär så här:
         "SV-ENR,0002602,""ACEFLEX RV-K 3G 1,5 R100"",M,52.5,...";;;;
     dvs hela raden ligger som ETT textfält, avgränsat med semikolon,
     med citattecken dubblerade inuti. Scriptet upptäcker och packar
     upp detta automatiskt, per fil.

Teckenkodning provas i turordning (utf-8-sig, utf-8, cp1252, latin-1)
tills en fungerar, så svenska tecken (å ä ö) hanteras korrekt oavsett
om filen exporterats från Excel på Windows eller Mac.

Tomma "utfyllnadsrader" i slutet av stora Excel-exporter (rader utan
faktiskt innehåll) hoppas automatiskt över och räknas inte som fel.

Dubbletter (t.ex. samma artikelnummer hos flera olika grossister, en rad
per grossist) är inget problem - scriptet räknar bara unika värden vid
jämförelsen.


-----------------------------------------------------------------------
VAD RÄKNAS SOM "ANVÄNT" I EN ITEM-FIL?
-----------------------------------------------------------------------
I varje item-fil (JSON) letar scriptet i listan "itm_tasks". För varje
uppgift ("task") i den listan:

  ARTIKELNUMMER räknas som "använt" om:
    - "tsk_material_type" är exakt lika med den kontrollerade typen
      (standard: "SV-ENR"), OCH
    - "tsk_material_number" innehåller något (är inte tomt).
    Normaliseras innan jämförelse: whitespace trimmas bort, och rent
    numeriska nummer fylls ut till 7 siffror med inledande nollor, så
    att t.ex. "2602" i en item-fil korrekt matchar "0002602" i
    masterlistan.

  ARBETSKOD räknas som "använd" om:
    - "tsk_work_type" är exakt lika med den kontrollerade typen
      (standard: "SV-ATL"), OCH
    - "tsk_work_code" innehåller något (är inte tomt).
    Normaliseras innan jämförelse: whitespace trimmas bort. Ingen
    nollutfyllnad görs här eftersom arbetskoder har varierande längd
    (9-10 siffror har setts i exempeldata) utan något etablerat
    fast format.


-----------------------------------------------------------------------
HUR TOLKAS GILTIGHETSFÄLTET FÖR ARBETSKODER?
-----------------------------------------------------------------------
Kolumnen "tsk_work_task_valid" i arbetskodslistan tolkas enligt den
faktiska kodbetydelsen:

    J = Gällande                                -> AKTIV
    T = Ny tillkommande prisrad för versionen    -> AKTIV (ny prisrad)
    U = Utgående prisrad (fasas ut, men gäller
        fortfarande just nu)                      -> UTGÅENDE
    N = Gammal prisrad som inte längre gäller    -> UTGÅNGEN
    (tomt värde)                                 -> okänt (flaggas separat)
    Allt annat                                   -> okänt värde (flaggas
                                                     separat, visar det
                                                     exakta värdet)

Rapporten särskiljer "UTGÅENDE" (U - på väg ut, men fortfarande giltig
just nu) från "UTGÅNGEN" (N - redan ogiltig), eftersom de kräver olika
grad av brådska att åtgärda.

Tolkningen styrs av en enda funktion i koden (interpret_valid_flag) om
den någon gång behöver justeras.


-----------------------------------------------------------------------
FELHANTERING
-----------------------------------------------------------------------
Om en enskild item-fil inte går att tolka som giltig JSON avbryts INTE
hela körningen - filen hoppas över, loggas i rapporten under en egen
rubrik ("FILER SOM INTE KUNDE LÄSAS"), och kontrollen fortsätter med
resterande filer. På så sätt får du alltid en komplett rapport i ett
enda körningstillfälle, istället för att behöva rätta ett fel i taget.

Om arbetskodslistan inte hittas alls hoppas HELA arbetskodskontrollen
över (rapporten säger tydligt varför), men artikelnummer-kontrollen
körs och rapporteras som vanligt.


-----------------------------------------------------------------------
KRAV
-----------------------------------------------------------------------
Endast Python 3 (standardbiblioteket) krävs - inga externa paket
behöver installeras.
=======================================================================
"""

import argparse
import csv
import json
import os
import sys
from collections import defaultdict
from datetime import datetime

# ---------------------------------------------------------------------------
# Standardvärden - scriptet hittar automatiskt sin egen mapp och antar att
# item-filerna ligger i samma mappstruktur (rekursivt) och att CSV-filerna
# (masterprislista + arbetskodslista) ligger i private-data/ bredvid
# scriptet. Inga argument behöver anges vid vanlig körning:
#   python check_artikelnummer.py
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_ITEMS_ROOT = SCRIPT_DIR
DEFAULT_MATERIAL_TYPE = "SV-ENR"
DEFAULT_WORK_TYPE = "SV-ATL"
PRIVATE_DIR_NAME = "private-data"

MASTER_KEYWORDS = ("master", "pris", "price")
WORKTYPE_KEYWORDS = ("work_type", "worktype", "work-type", "arbetstid", "arbetskod")

csv.field_size_limit(sys.maxsize)


# ---------------------------------------------------------------------------
# Sökvägshjälpare
# ---------------------------------------------------------------------------

def get_or_create_private_dir():
    """
    Mappen 'private-data' bredvid scriptet är avsedd för känsligt material
    (masterprislista, arbetskodslista och genererade rapporter) och ska
    gitignoras i sin helhet - se .gitignore. Skapas automatiskt om den
    saknas.
    """
    private_dir = os.path.join(SCRIPT_DIR, PRIVATE_DIR_NAME)
    os.makedirs(private_dir, exist_ok=True)
    return private_dir


def default_output_path():
    """
    Bygger ett rapportnamn med dagens datum och klockslag, t.ex.
    artikelnummer_rapport_2026-08-11_1432.txt, och sparar det i
    private-data/ så rapporten aldrig hamnar i Git av misstag.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    return os.path.join(get_or_create_private_dir(), f"artikelnummer_rapport_{timestamp}.txt")


def _pick_csv_by_keywords(folder, keywords, exclude_basenames=None):
    try:
        entries = os.listdir(folder)
    except OSError:
        return None
    csv_files = [f for f in entries if f.lower().endswith(".csv")]
    if exclude_basenames:
        csv_files = [f for f in csv_files if f not in exclude_basenames]
    if not csv_files:
        return None
    preferred = [f for f in csv_files if any(k in f.lower() for k in keywords)]
    chosen = sorted(preferred)[0] if preferred else sorted(csv_files)[0]
    return os.path.join(folder, chosen)


def find_default_csv(keywords, exclude_basenames=None):
    """
    Generisk sökning efter en CSV-fil:
      1. I private-data/ (rekommenderat - denna mapp är gitignorad).
      2. Direkt bredvid scriptet, för bakåtkompatibilitet. Om filen hittas
         här varnas det att den bör flyttas till private-data/.

    Returnerar (sökväg, hittad_i_privat_mapp: bool) eller (None, False).
    """
    private_dir = os.path.join(SCRIPT_DIR, PRIVATE_DIR_NAME)

    found = _pick_csv_by_keywords(private_dir, keywords, exclude_basenames)
    if found:
        return found, True

    found = _pick_csv_by_keywords(SCRIPT_DIR, keywords, exclude_basenames)
    if found:
        return found, False

    return None, False


def find_item_files(root_dir):
    """Rekursiv sökning efter .json-filer under root_dir."""
    json_files = []
    for dirpath, _dirnames, filenames in os.walk(root_dir):
        for fname in filenames:
            if fname.lower().endswith(".json"):
                json_files.append(os.path.join(dirpath, fname))
    return sorted(json_files)


# ---------------------------------------------------------------------------
# Normalisering
# ---------------------------------------------------------------------------

def normalize_number(raw):
    """
    Normaliserar ett artikelnummer för jämförelse.
    - Tar bort whitespace
    - Om numeriskt: fyller ut till 7 siffror med inledande nollor
      (masterlistan använder 7-siffrigt format t.ex. 0002602, medan
      item-filerna ibland saknar inledande nollor, t.ex. 5002124/2989459).
    - Om icke-numeriskt: returneras oförändrat (trimmat).
    """
    if raw is None:
        return None
    s = str(raw).strip()
    if not s:
        return None
    if s.isdigit():
        return s.zfill(7)
    return s


def normalize_code(raw):
    """
    Normaliserar en arbetskod för jämförelse. Bara whitespace trimmas -
    ingen nollutfyllnad, eftersom arbetskoder har varierande längd utan
    något etablerat fast format (till skillnad från artikelnummer).
    """
    if raw is None:
        return None
    s = str(raw).strip()
    return s if s else None


def interpret_valid_flag(raw):
    """
    Tolkar värdet i kolumnen tsk_work_task_valid enligt den faktiska
    kodbetydelsen (bekräftad):
        J = Gällande                              -> AKTIV
        T = Ny tillkommande prisrad för versionen  -> AKTIV (ny prisrad)
        U = Utgående prisrad (fasas ut, men gäller
            fortfarande just nu)                   -> UTGÅENDE
        N = Gammal prisrad som inte längre gäller  -> UTGÅNGEN

    Extra ordformer (JA/NEJ/Y/N osv) hanteras också ifall fältet någon
    gång matas in på annat sätt än enbokstavskoden.
    """
    val = (raw or "").strip().upper()

    if val == "J":
        return "AKTIV"
    if val == "T":
        return "AKTIV (ny prisrad)"
    if val == "U":
        return "UTGÅENDE"
    if val == "N":
        return "UTGÅNGEN"

    # Extra ordformer, för säkerhets skull
    active_words = {"JA", "Y", "YES", "1", "TRUE", "AKTIV", "GÄLLANDE"}
    expiring_words = {"UTGÅENDE", "UTGAENDE", "FASAS UT"}
    expired_words = {"NEJ", "NO", "0", "FALSE", "UTGÅNGEN", "UTGANGEN", "INAKTIV"}

    if val in active_words:
        return "AKTIV"
    if val in expiring_words:
        return "UTGÅENDE"
    if val in expired_words:
        return "UTGÅNGEN"
    if val == "":
        return "OKÄNT (tomt värde)"
    return f"OKÄNT VÄRDE ({raw!r})"


def status_bucket(status):
    """
    Grupperar ett status-resultat (från interpret_valid_flag) i en av de
    fyra rapportkategorierna: 'aktiv', 'utgaende', 'utgangen' eller 'okant'.
    """
    if status.startswith("AKTIV"):
        return "aktiv"
    if status.startswith("UTGÅENDE"):
        return "utgaende"
    if status == "UTGÅNGEN":
        return "utgangen"
    return "okant"


# ---------------------------------------------------------------------------
# Läsning av item-filer (JSON)
# ---------------------------------------------------------------------------

def collect_item_file_data(item_files, material_type, work_type):
    """
    Läser item-filerna EN gång och samlar både använda artikelnummer och
    använda arbetskoder samtidigt.

    Returnerar:
      used_numbers: set av normaliserade artikelnummer (material_type-match)
      material_usage_map: dict {nummer: [(fil, materialnamn, tsk_name), ...]}
      used_work_codes: set av normaliserade arbetskoder (work_type-match)
      work_usage_map: dict {kod: [(fil, arbetsbeskrivning, tsk_name), ...]}
      checked_count: antal item-filer som kunde läsas
      skipped_files: lista med (fil, felmeddelande) för filer som inte
                     kunde tolkas som giltig JSON
    """
    used_numbers = set()
    material_usage_map = defaultdict(list)
    used_work_codes = set()
    work_usage_map = defaultdict(list)
    checked_count = 0
    skipped_files = []

    for path in item_files:
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            skipped_files.append((path, f"Kunde inte läsas som JSON: {e}"))
            continue

        checked_count += 1
        tasks = data.get("itm_tasks", [])
        if not isinstance(tasks, list):
            continue

        for task in tasks:
            if not isinstance(task, dict):
                continue

            # --- Artikelnummer (material) ---
            t_type = (task.get("tsk_material_type") or "").strip()
            t_number = normalize_number(task.get("tsk_material_number"))
            if t_type == material_type and t_number:
                used_numbers.add(t_number)
                material_usage_map[t_number].append(
                    (
                        path,
                        (task.get("tsk_material_name") or "").strip(),
                        (task.get("tsk_name") or "").strip(),
                    )
                )

            # --- Arbetskod (arbetstid) ---
            w_type = (task.get("tsk_work_type") or "").strip()
            w_code = normalize_code(task.get("tsk_work_code"))
            if w_type == work_type and w_code:
                used_work_codes.add(w_code)
                work_usage_map[w_code].append(
                    (
                        path,
                        (task.get("tsk_work_description") or "").strip(),
                        (task.get("tsk_name") or "").strip(),
                    )
                )

    return (
        used_numbers,
        material_usage_map,
        used_work_codes,
        work_usage_map,
        checked_count,
        skipped_files,
    )


# ---------------------------------------------------------------------------
# Flexibel CSV-läsning (delas mellan masterprislista och arbetskodslista)
# ---------------------------------------------------------------------------

def _open_with_fallback_encoding(path):
    """
    Öppnar en textfil och provar flera kodningar tills en fungerar.
    Returnerar (filhandtag, kodning_som_användes).
    """
    encodings_to_try = ["utf-8-sig", "utf-8", "cp1252", "latin-1"]
    last_error = None
    for enc in encodings_to_try:
        try:
            fh = open(path, "r", encoding=enc, newline="")
            fh.readline()  # trigga ev. UnicodeDecodeError direkt
            fh.seek(0)
            return fh, enc
        except UnicodeDecodeError as e:
            last_error = e
            continue
    raise RuntimeError(
        f"Kunde inte läsa filen med någon av kodningarna {encodings_to_try}: {last_error}"
    )


def open_flexible_csv_rows(path):
    """
    Läser en CSV-fil radvis och hanterar automatiskt BÅDA kända format
    (vanlig CSV och "dubbel-inpackad" CSV från stora Excel-exporter, se
    dokumentationen högst upp i filen) med samma kod.

    Metod: varje rad läses först med ';' som yttre avgränsare.
      - Är raden "dubbel-inpackad" (hela raden ligger som ETT citerat
        textfält) blir resultatet ett enda fält: den uppackade,
        korrekta kommaseparerade raden (citattecken korrekt avkodade).
      - Är raden i vanligt format (inga semikolon i raden) blir
        resultatet OCKSÅ ett enda fält: hela raden oförändrad.
    I båda fallen parsas sedan det fältet om med ',' som avgränsare för
    att få ut de riktiga kolumnvärdena. Tomma utfyllnadsrader (vanligt i
    stora Excel-exporter) hoppas automatiskt över.

    Returnerar (fieldnames, used_encoding, rows_generator).
    OBS: rows_generator måste itereras helt (t.ex. i en for-loop) för att
    filhandtaget ska stängas korrekt.
    """
    fh, used_encoding = _open_with_fallback_encoding(path)
    outer_reader = csv.reader(fh, delimiter=";", quotechar='"')

    try:
        header_outer = next(outer_reader)
    except StopIteration:
        fh.close()
        raise RuntimeError(f"Filen verkar vara tom: {path}")

    if not header_outer or not header_outer[0].strip():
        fh.close()
        raise RuntimeError(f"Filen verkar sakna en giltig header-rad: {path}")

    fieldnames = [
        f.strip()
        for f in next(csv.reader([header_outer[0]], delimiter=",", quotechar='"'))
    ]

    def rows_generator():
        try:
            for row in outer_reader:
                if not row or not row[0].strip():
                    continue  # tom utfyllnadsrad
                try:
                    inner = next(csv.reader([row[0]], delimiter=",", quotechar='"'))
                except Exception:
                    continue
                yield inner
        finally:
            fh.close()

    return fieldnames, used_encoding, rows_generator()


def collect_master_numbers(master_csv, material_type):
    """
    Samlar alla artikelnummer i masterprislistan med angiven material_type.

    Returnerar:
      master_numbers: set av normaliserade artikelnummer
      total_rows: antal inlästa (icke-tomma) datarader
      matching_rows: antal rader som matchade material_type
      used_encoding: vilken teckenkodning som användes
    """
    fieldnames, used_encoding, rows = open_flexible_csv_rows(master_csv)

    if "material_type" not in fieldnames or "material_number" not in fieldnames:
        raise RuntimeError(
            "Masterfilen saknar förväntade kolumner 'material_type' och/eller "
            f"'material_number'. Hittade kolumner: {fieldnames}"
        )

    type_idx = fieldnames.index("material_type")
    number_idx = fieldnames.index("material_number")

    master_numbers = set()
    total_rows = 0
    matching_rows = 0

    for inner in rows:
        if len(inner) <= max(type_idx, number_idx):
            continue
        total_rows += 1
        m_type = (inner[type_idx] or "").strip()
        if m_type != material_type:
            continue
        matching_rows += 1
        m_number = normalize_number(inner[number_idx])
        if m_number:
            master_numbers.add(m_number)

    return master_numbers, total_rows, matching_rows, used_encoding


def collect_work_type_records(worktypes_csv, work_type):
    """
    Samlar arbetskoder i arbetskodslistan med angiven tsk_work_type, samt
    om varje kod är AKTIV eller UTGÅNGEN (se interpret_valid_flag).

    Returnerar:
      records: dict {kod: {"id", "description", "valid_raw", "status",
                            "resource_type"}}
      total_rows: antal inlästa (icke-tomma) datarader
      matching_rows: antal rader som matchade work_type
      used_encoding: vilken teckenkodning som användes
    """
    fieldnames, used_encoding, rows = open_flexible_csv_rows(worktypes_csv)

    required_cols = ("tsk_work_type", "tsk_work_code", "tsk_work_task_valid")
    missing_cols = [c for c in required_cols if c not in fieldnames]
    if missing_cols:
        raise RuntimeError(
            "Arbetskodslistan saknar förväntade kolumner: "
            f"{missing_cols}. Hittade kolumner: {fieldnames}"
        )

    col_idx = {name: fieldnames.index(name) for name in fieldnames}

    def get(inner, col):
        i = col_idx.get(col)
        if i is None or i >= len(inner):
            return ""
        return (inner[i] or "").strip()

    records = {}
    total_rows = 0
    matching_rows = 0

    for inner in rows:
        total_rows += 1
        w_type = get(inner, "tsk_work_type")
        if w_type != work_type:
            continue
        matching_rows += 1
        w_code = normalize_code(get(inner, "tsk_work_code"))
        if not w_code:
            continue
        valid_raw = get(inner, "tsk_work_task_valid")
        records[w_code] = {
            "id": get(inner, "id"),
            "description": get(inner, "tsk_work_description"),
            "valid_raw": valid_raw,
            "status": interpret_valid_flag(valid_raw),
            "resource_type": get(inner, "tsk_resource_type"),
        }

    return records, total_rows, matching_rows, used_encoding


# ---------------------------------------------------------------------------
# Rapport
# ---------------------------------------------------------------------------

def write_report(
    output_path,
    # allmänt
    items_root,
    checked_count,
    skipped_files,
    # material
    material_type,
    master_csv,
    used_numbers,
    material_usage_map,
    master_numbers,
    total_master_rows,
    matching_master_rows,
    master_encoding,
    # arbetskoder (kan vara None om avsnittet hoppades över)
    work_type,
    worktypes_csv,
    used_work_codes,
    work_usage_map,
    work_records,
    total_wt_rows,
    matching_wt_rows,
    wt_encoding,
):
    missing_numbers = sorted(used_numbers - master_numbers)
    found_numbers = used_numbers & master_numbers

    with open(output_path, "w", encoding="utf-8") as out:
        out.write("KONTROLLRAPPORT: ARTIKELNUMMER OCH ARBETSKODER\n")
        out.write("=" * 60 + "\n\n")
        out.write(f"Kontroll körd:      {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        out.write(f"Item-filer sökta i: {items_root}\n")
        out.write(f"Item-filer kontrollerade:      {checked_count}\n")
        out.write(f"Item-filer som ej kunde läsas: {len(skipped_files)}\n\n")

        if skipped_files:
            out.write("FILER SOM INTE KUNDE LÄSAS\n")
            out.write("-" * 60 + "\n")
            for path, err in skipped_files:
                out.write(f"- {path}\n    Fel: {err}\n")
            out.write("\n")

        # ============================= DEL 1: ARTIKELNUMMER =============================
        out.write("=" * 60 + "\n")
        out.write("DEL 1: ARTIKELNUMMER MOT MASTERPRISLISTA\n")
        out.write("=" * 60 + "\n\n")
        out.write(f"Materialtyp kontrollerad:     {material_type}\n")
        out.write(f"Masterprislista:               {master_csv}\n")
        out.write(f"Masterfil inläst med kodning:  {master_encoding}\n\n")

        out.write("SAMMANFATTNING - ARTIKELNUMMER\n")
        out.write("-" * 60 + "\n")
        out.write(f"Rader i masterfilen (totalt):           {total_master_rows}\n")
        out.write(f"Rader i masterfilen ({material_type}):  {matching_master_rows}\n")
        out.write(f"Unika använda artikelnummer ({material_type}): {len(used_numbers)}\n")
        out.write(f"Träffar (finns i masterlistan):        {len(found_numbers)}\n")
        out.write(f"SAKNADE (finns EJ i masterlistan):     {len(missing_numbers)}\n\n")

        out.write("SAKNADE ARTIKELNUMMER - DETALJER\n")
        out.write("-" * 60 + "\n")
        if not missing_numbers:
            out.write("Inga saknade artikelnummer. Allt stämmer mot masterlistan.\n\n")
        else:
            for number in missing_numbers:
                out.write(f"\nArtikelnummer: {number}\n")
                for path, mat_name, tsk_name in material_usage_map[number]:
                    out.write(
                        f"  - Fil: {path}\n"
                        f"    Materialnamn i item-fil: {mat_name or '(saknas)'}\n"
                        f"    Task: {tsk_name or '(saknas)'}\n"
                    )
            out.write("\n")

        # ============================= DEL 2: ARBETSKODER ==============================
        out.write("=" * 60 + "\n")
        out.write("DEL 2: ARBETSKODER (ARBETSTID) MOT ARBETSKODSLISTA\n")
        out.write("=" * 60 + "\n\n")

        if worktypes_csv is None:
            out.write(
                "Ingen arbetskodslista hittades - detta avsnitt hoppades över.\n"
                "Lägg en CSV-fil (t.ex. work_types_rows.csv) i private-data/ för\n"
                "att aktivera denna kontroll vid nästa körning.\n\n"
            )
        else:
            out.write(f"Arbetstyp kontrollerad:        {work_type}\n")
            out.write(f"Arbetskodslista:                {worktypes_csv}\n")
            out.write(f"Fil inläst med kodning:         {wt_encoding}\n")
            out.write(
                "OBS: giltighetsfältet 'tsk_work_task_valid' tolkas enligt:\n"
                "     J = Gällande                          -> AKTIV\n"
                "     T = Ny tillkommande prisrad            -> AKTIV (ny prisrad)\n"
                "     U = Utgående prisrad (fasas ut)        -> UTGÅENDE\n"
                "     N = Gammal prisrad som ej längre gäller -> UTGÅNGEN\n\n"
            )

            found_codes = used_work_codes & set(work_records.keys())
            missing_codes = sorted(used_work_codes - set(work_records.keys()))

            buckets = defaultdict(list)
            for c in found_codes:
                buckets[status_bucket(work_records[c]["status"])].append(c)
            active_codes = sorted(buckets["aktiv"])
            expiring_codes = sorted(buckets["utgaende"])
            expired_codes = sorted(buckets["utgangen"])
            unknown_codes = sorted(buckets["okant"])

            out.write("SAMMANFATTNING - ARBETSKODER\n")
            out.write("-" * 60 + "\n")
            out.write(f"Rader i arbetskodslistan (totalt):         {total_wt_rows}\n")
            out.write(f"Rader i arbetskodslistan ({work_type}):    {matching_wt_rows}\n")
            out.write(f"Unika använda arbetskoder ({work_type}):   {len(used_work_codes)}\n")
            out.write(f"  - Aktiva (J/T):                          {len(active_codes)}\n")
            out.write(f"  - Utgående (U, fasas ut):                {len(expiring_codes)}\n")
            out.write(f"  - Utgångna (N):                          {len(expired_codes)}\n")
            out.write(f"  - Okänt värde i giltighetsfältet:        {len(unknown_codes)}\n")
            out.write(f"  - EJ REGISTRERADE (finns ej i listan):   {len(missing_codes)}\n\n")

            out.write("EJ REGISTRERADE ARBETSKODER - DETALJER\n")
            out.write("-" * 60 + "\n")
            if not missing_codes:
                out.write("Inga oregistrerade arbetskoder. Allt finns i arbetskodslistan.\n\n")
            else:
                for code in missing_codes:
                    out.write(f"\nArbetskod: {code}\n")
                    for path, desc, tsk_name in work_usage_map[code]:
                        out.write(
                            f"  - Fil: {path}\n"
                            f"    Arbetsbeskrivning i item-fil: {desc or '(saknas)'}\n"
                            f"    Task: {tsk_name or '(saknas)'}\n"
                        )
                out.write("\n")

            out.write("UTGÅNGNA ARBETSKODER (N) - DETALJER\n")
            out.write("-" * 60 + "\n")
            if not expired_codes:
                out.write("Inga utgångna arbetskoder används.\n\n")
            else:
                for code in expired_codes:
                    rec = work_records[code]
                    out.write(
                        f"\nArbetskod: {code}  "
                        f"(id {rec['id'] or '(saknas)'}, giltighetsfält='{rec['valid_raw']}')\n"
                    )
                    out.write(f"  Beskrivning i arbetskodslistan: {rec['description'] or '(saknas)'}\n")
                    for path, desc, tsk_name in work_usage_map[code]:
                        out.write(f"  - Fil: {path}\n    Task: {tsk_name or '(saknas)'}\n")
                out.write("\n")

            out.write("UTGÅENDE ARBETSKODER (U, fasas ut) - DETALJER\n")
            out.write("-" * 60 + "\n")
            if not expiring_codes:
                out.write("Inga utgående (snart utfasade) arbetskoder används.\n\n")
            else:
                for code in expiring_codes:
                    rec = work_records[code]
                    out.write(
                        f"\nArbetskod: {code}  "
                        f"(id {rec['id'] or '(saknas)'}, giltighetsfält='{rec['valid_raw']}')\n"
                    )
                    out.write(f"  Beskrivning i arbetskodslistan: {rec['description'] or '(saknas)'}\n")
                    for path, desc, tsk_name in work_usage_map[code]:
                        out.write(f"  - Fil: {path}\n    Task: {tsk_name or '(saknas)'}\n")
                out.write("\n")

            if unknown_codes:
                out.write("ARBETSKODER MED OKÄNT VÄRDE I GILTIGHETSFÄLTET\n")
                out.write("-" * 60 + "\n")
                for code in unknown_codes:
                    rec = work_records[code]
                    out.write(
                        f"Arbetskod: {code}  giltighetsfält='{rec['valid_raw']}'  "
                        f"(id {rec['id'] or '(saknas)'})\n"
                    )
                out.write("\n")

        out.write("=" * 60 + "\n")
        out.write("Slut på rapport.\n")


# ---------------------------------------------------------------------------
# Huvudprogram
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description=(
            "Kontrollerar att artikelnummer och arbetskoder i item-filer finns "
            "registrerade (och är aktiva) i grossistens masterprislista respektive "
            "arbetskodslista."
        )
    )
    parser.add_argument(
        "--items-root",
        default=None,
        help="Rotmapp som söks igenom rekursivt efter .json item-filer. "
             "Standard: samma mapp som scriptet ligger i.",
    )
    parser.add_argument(
        "--master",
        default=None,
        help="Sökväg till masterprislistan (CSV). "
             "Standard: den .csv-fil som hittas i private-data/.",
    )
    parser.add_argument(
        "--worktypes",
        default=None,
        help="Sökväg till arbetskodslistan (CSV). "
             "Standard: den .csv-fil som hittas i private-data/. "
             "Hittas ingen hoppas arbetskodskontrollen över.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Sökväg dit textrapporten skrivs. "
             "Standard: private-data/artikelnummer_rapport_ÅÅÅÅ-MM-DD_TTMM.txt",
    )
    parser.add_argument(
        "--material-type",
        default=DEFAULT_MATERIAL_TYPE,
        help="Vilken tsk_material_type som ska kontrolleras (standard: SV-ENR).",
    )
    parser.add_argument(
        "--work-type",
        default=DEFAULT_WORK_TYPE,
        help="Vilken tsk_work_type som ska kontrolleras (standard: SV-ATL).",
    )
    parser.add_argument(
        "--skip-worktypes",
        action="store_true",
        help="Hoppa över arbetskodskontrollen helt.",
    )
    args = parser.parse_args()

    if args.items_root is None:
        args.items_root = DEFAULT_ITEMS_ROOT
        print(f"Ingen --items-root angiven, använder scriptets mapp: {args.items_root}")

    if args.output is None:
        args.output = default_output_path()

    # --- Masterprislista (obligatorisk) ---
    if args.master is None:
        auto_master, found_in_private = find_default_csv(MASTER_KEYWORDS)
        if auto_master is None:
            private_dir = get_or_create_private_dir()
            print(
                "FEL: Ingen --master angavs och ingen .csv-fil hittades i "
                f"'{PRIVATE_DIR_NAME}/' eller bredvid scriptet ({SCRIPT_DIR}).\n"
                f"Lägg masterprislistan (.csv) i mappen: {private_dir}\n"
                "(den mappen skapades nu automatiskt och är gitignorad),\n"
                "eller ange --master /sökväg/till/fil.csv.",
                file=sys.stderr,
            )
            sys.exit(1)
        args.master = auto_master
        if found_in_private:
            print(f"Ingen --master angiven, använder fil i {PRIVATE_DIR_NAME}/: {args.master}")
        else:
            print(f"Ingen --master angiven, använder hittad fil: {args.master}")
            print(
                f"OBS: Denna fil ligger direkt i repo-mappen, inte i '{PRIVATE_DIR_NAME}/'. "
                "Flytta den dit så skyddas den av .gitignore."
            )

    if not os.path.isdir(args.items_root):
        print(f"FEL: items-root-mappen finns inte: {args.items_root}", file=sys.stderr)
        sys.exit(1)
    if not os.path.isfile(args.master):
        print(f"FEL: masterfilen finns inte: {args.master}", file=sys.stderr)
        sys.exit(1)

    # --- Arbetskodslista (valfri) ---
    if args.skip_worktypes:
        args.worktypes = None
        print("Arbetskodskontroll avstängd (--skip-worktypes).")
    elif args.worktypes is None:
        master_basename = os.path.basename(args.master)
        auto_wt, wt_found_in_private = find_default_csv(
            WORKTYPE_KEYWORDS, exclude_basenames={master_basename}
        )
        if auto_wt is None:
            print(
                f"Ingen arbetskodslista hittades i '{PRIVATE_DIR_NAME}/' - "
                "hoppar över arbetskodskontrollen. Lägg en CSV-fil (t.ex. "
                "work_types_rows.csv) där för att aktivera den."
            )
        else:
            args.worktypes = auto_wt
            location = f"i {PRIVATE_DIR_NAME}/" if wt_found_in_private else "bredvid scriptet"
            print(f"Ingen --worktypes angiven, använder fil {location}: {args.worktypes}")
            if not wt_found_in_private:
                print(
                    f"OBS: Denna fil ligger direkt i repo-mappen, inte i '{PRIVATE_DIR_NAME}/'. "
                    "Flytta den dit så skyddas den av .gitignore."
                )
    elif not os.path.isfile(args.worktypes):
        print(f"FEL: arbetskodsfilen finns inte: {args.worktypes}", file=sys.stderr)
        sys.exit(1)

    # --- Läs item-filer ---
    print(f"Söker item-filer i: {args.items_root} ...")
    item_files = find_item_files(args.items_root)
    print(f"Hittade {len(item_files)} .json-filer.")

    print("Läser item-filer och samlar använda artikelnummer och arbetskoder...")
    (
        used_numbers,
        material_usage_map,
        used_work_codes,
        work_usage_map,
        checked_count,
        skipped_files,
    ) = collect_item_file_data(item_files, args.material_type, args.work_type)
    print(f"  Kontrollerade {checked_count} item-filer.")
    print(f"  Hittade {len(used_numbers)} unika artikelnummer ({args.material_type}).")
    print(f"  Hittade {len(used_work_codes)} unika arbetskoder ({args.work_type}).")
    if skipped_files:
        print(f"  OBS: {len(skipped_files)} filer kunde inte läsas (se rapporten för detaljer).")

    # --- Läs masterprislista ---
    print(f"Läser masterprislista (kan ta en stund för stora filer): {args.master} ...")
    master_numbers, total_master_rows, matching_master_rows, master_encoding = collect_master_numbers(
        args.master, args.material_type
    )
    print(
        f"  Läste {total_master_rows} rader totalt, {matching_master_rows} "
        f"matchade material_type={args.material_type}."
    )
    print(f"  Kodning som användes: {master_encoding}")
    missing_count = len(used_numbers - master_numbers)
    print(f"  Saknade artikelnummer: {missing_count} av {len(used_numbers)}")

    # --- Läs arbetskodslista (om angiven/hittad) ---
    work_records = {}
    total_wt_rows = 0
    matching_wt_rows = 0
    wt_encoding = None
    if args.worktypes:
        print(f"Läser arbetskodslista: {args.worktypes} ...")
        work_records, total_wt_rows, matching_wt_rows, wt_encoding = collect_work_type_records(
            args.worktypes, args.work_type
        )
        print(
            f"  Läste {total_wt_rows} rader totalt, {matching_wt_rows} "
            f"matchade work_type={args.work_type}."
        )
        print(f"  Kodning som användes: {wt_encoding}")
        found_work_codes = used_work_codes & set(work_records.keys())
        missing_work_count = len(used_work_codes - set(work_records.keys()))
        bucket_counts = defaultdict(int)
        for c in found_work_codes:
            bucket_counts[status_bucket(work_records[c]["status"])] += 1
        print(
            f"  Arbetskoder: {bucket_counts['aktiv']} aktiva, "
            f"{bucket_counts['utgaende']} utgående (fasas ut), "
            f"{bucket_counts['utgangen']} utgångna, "
            f"{bucket_counts['okant']} okänt värde, "
            f"{missing_work_count} ej registrerade (av {len(used_work_codes)} unika)"
        )

    # --- Skriv rapport ---
    write_report(
        args.output,
        args.items_root,
        checked_count,
        skipped_files,
        args.material_type,
        args.master,
        used_numbers,
        material_usage_map,
        master_numbers,
        total_master_rows,
        matching_master_rows,
        master_encoding,
        args.work_type,
        args.worktypes,
        used_work_codes,
        work_usage_map,
        work_records,
        total_wt_rows,
        matching_wt_rows,
        wt_encoding,
    )
    print(f"\nRapport skriven till: {args.output}")


if __name__ == "__main__":
    main()