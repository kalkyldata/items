#!/usr/bin/env python3
"""
check_artikelnummer.py
=======================================================================
VAD GÖR DETTA SCRIPT?
-----------------------------------------------------------------------
Kontrollerar att alla artikelnummer som används i era "item-filer" (JSON)
faktiskt finns i grossistens masterprislista (CSV-export, t.ex. från
Ahlsell). Scriptet letar bara efter materialrader av typen "SV-ENR"
(styrbart, se nedan).

Resultatet blir en tydlig .txt-rapport som visar:
  - Hur många item-filer som kontrollerades
  - Hur många unika artikelnummer som används totalt
  - Hur många av dem som hittades i masterlistan (träffar)
  - Hur många som SAKNAS i masterlistan
  - För varje saknat artikelnummer: exakt i vilken/vilka item-filer
    (fullständig sökväg) och under vilken uppgift ("task") det används,
    så att du kan gå direkt dit och rätta.

Scriptet körs helt lokalt på din dator/server. Ingen uppkoppling mot
GitHub eller internet krävs eller används.


-----------------------------------------------------------------------
SÅ HÄR ANVÄNDER DU DET (enklaste sättet)
-----------------------------------------------------------------------
1. Lägg den här filen (check_artikelnummer.py) i ROTEN av mappen där du
   har klonat/laddat ner era item-filer (JSON) lokalt. Scriptet letar
   igenom ALLA undermappar, oavsett hur många nivåer djupt de ligger.

2. Lägg masterprislistan (en .csv-fil, t.ex. exporterad från Ahlsell) i
   en undermapp som heter "private-data" bredvid scriptet:

       repo-rot/
       ├── check_artikelnummer.py
       ├── .gitignore
       ├── private-data/
       │   └── Master_Price_List_Sv_Enr_Step_4.csv   <- läggs här
       └── ... era item-filer i mappar/undermappar ...

   Mappen "private-data" är avsedd för känsligt material (priser,
   rabattkoder m.m.) och ska ALDRIG laddas upp till GitHub - den
   gitignoras i sin helhet, se avsnittet om .gitignore nedan. Om
   filnamnet innehåller "master", "pris" eller "price" hittas den
   garanterat automatiskt; annars används den enda .csv-fil som finns
   i mappen. Mappen skapas automatiskt av scriptet om den saknas.

3. Öppna en terminal i repo-roten och kör:

       python check_artikelnummer.py

   Det är allt - inga argument behövs. Scriptet:
     - hittar automatiskt sin egen mapp och söker item-filer där
       (rekursivt, alla undermappar),
     - hittar automatiskt master-CSV:n i private-data/,
     - skriver rapporten i private-data/ med dagens datum och klockslag
       i filnamnet, t.ex. artikelnummer_rapport_2026-08-11_1432.txt,
       så gamla rapporter aldrig skrivs över av misstag OCH så att
       rapporten - som kan innehålla interna produktnamn - inte heller
       laddas upp till Git av misstag.

4. Öppna den skapade .txt-rapporten (i private-data/) och gå igenom
   listan över saknade artikelnummer. Varje rad talar om exakt vilken
   fil och uppgift numret hör hemma i.


-----------------------------------------------------------------------
AVANCERAD ANVÄNDNING (valfria flaggor)
-----------------------------------------------------------------------
Du behöver ALDRIG ange dessa - de finns bara om du vill styra något
manuellt, t.ex. om item-filerna och masterlistan ligger i olika mappar,
eller om du vill spara rapporten någon annanstans:

    --items-root SÖKVÄG
        Vilken mapp som ska sökas igenom (rekursivt) efter .json-filer.
        Standard: samma mapp som scriptet ligger i.

    --master SÖKVÄG
        Sökväg till en specifik masterprislista (CSV), om du inte vill
        att scriptet ska leta efter den automatiskt, eller om det finns
        flera CSV-filer i mappen och fel en hittas automatiskt.
        Standard: den .csv-fil som hittas i private-data/ (eller,
        bakåtkompatibelt, bredvid scriptet om private-data/ är tom).

    --output SÖKVÄG
        Var rapporten ska sparas, och under vilket filnamn.
        Standard: private-data/artikelnummer_rapport_ÅÅÅÅ-MM-DD_TTMM.txt

    --material-type TYP
        Vilken material_type som ska kontrolleras. Standard: SV-ENR.
        Ändra bara om ni börjar använda en annan materialtyp-kod.

Exempel med alla flaggor:

    python check_artikelnummer.py \\
        --items-root /home/anvandare/projekt/item-filer \\
        --master /home/anvandare/projekt/master/Ahlsell_prislista.csv \\
        --output /home/anvandare/projekt/rapporter/kontroll.txt \\
        --material-type SV-ENR


-----------------------------------------------------------------------
VILKA FORMAT PÅ MASTERLISTAN HANTERAS?
-----------------------------------------------------------------------
Scriptet läser masterprislistan RADVIS (aldrig hela filen i minnet på
en gång), så det fungerar utan problem även för mycket stora filer
(100+ MB, hundratusentals rader).

Två CSV-format hanteras automatiskt, utan att du behöver göra något:

  1. Vanlig CSV med kommatecken som avgränsare:
         material_type,material_number,material_name,...

  2. "Dubbel-inpackad" CSV, vilket är vanligt när stora Excel-ark
     exporteras till CSV. Där ser varje rad ut ungefär så här:
         "SV-ENR,0002602,""ACEFLEX RV-K 3G 1,5 R100"",M,52.5,...";;;;
     dvs hela raden ligger som ETT textfält, avgränsat med semikolon,
     med citattecken dubblerade inuti. Scriptet upptäcker och packar
     upp detta automatiskt.

Teckenkodning provas i turordning (utf-8-sig, utf-8, cp1252, latin-1)
tills en fungerar, så svenska tecken (å ä ö) hanteras korrekt oavsett
om filen exporterats från Excel på Windows eller Mac.

Tomma "utfyllnadsrader" i slutet av stora Excel-exporter (rader utan
faktiskt innehåll) hoppas automatiskt över och räknas inte som fel.

Dubbletter i masterlistan (t.ex. samma artikelnummer hos flera olika
grossister, en rad per grossist) är inget problem - scriptet räknar
bara unika artikelnummer vid jämförelsen.


-----------------------------------------------------------------------
VAD RÄKNAS SOM "ANVÄNT ARTIKELNUMMER" I EN ITEM-FIL?
-----------------------------------------------------------------------
I varje item-fil (JSON) letar scriptet i listan "itm_tasks". För varje
uppgift ("task") i den listan räknas artikelnumret som "använt" om:
  - "tsk_material_type" är exakt lika med den kontrollerade typen
    (standard: "SV-ENR"), OCH
  - "tsk_material_number" innehåller något (är inte tomt).

Artikelnummer normaliseras innan jämförelse (whitespace trimmas bort,
och rent numeriska nummer fylls ut till 7 siffror med inledande nollor)
så att t.ex. "2602" i en item-fil korrekt matchar "0002602" i
masterlistan.


-----------------------------------------------------------------------
FELHANTERING
-----------------------------------------------------------------------
Om en enskild item-fil inte går att tolka som giltig JSON avbryts INTE
hela körningen - filen hoppas över, loggas i rapporten under en egen
rubrik ("FILER SOM INTE KUNDE LÄSAS"), och kontrollen fortsätter med
resterande filer. På så sätt får du alltid en komplett rapport i ett
enda körningstillfälle, istället för att behöva rätta ett fel i taget.


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
# item-filerna ligger i samma mappstruktur (rekursivt) och att masterprislistan
# (en .csv-fil) ligger direkt bredvid scriptet. Inga argument behöver anges
# vid vanlig körning: "python check_artikelnummer.py"
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_ITEMS_ROOT = SCRIPT_DIR
DEFAULT_MATERIAL_TYPE = "SV-ENR"
PRIVATE_DIR_NAME = "private-data"


def get_or_create_private_dir():
    """
    Mappen 'private-data' bredvid scriptet är avsedd för känsligt material
    (masterprislistan och genererade rapporter) och ska gitignoras i sin
    helhet - se .gitignore. Skapas automatiskt om den saknas.
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


def find_default_master_csv():
    """
    Letar efter masterprislistan i följande ordning:
      1. I private-data/ (rekommenderat - denna mapp är gitignorad).
      2. Direkt bredvid scriptet, för bakåtkompatibilitet med tidigare
         upplägg. Om filen hittas här varnas det att den bör flyttas till
         private-data/ eftersom mappen bredvid scriptet normalt spåras av Git.

    Föredrar filnamn som innehåller "master", "pris" eller "price".
    Returnerar (sökväg, hittad_i_privat_mapp: bool) eller (None, False).
    """
    private_dir = os.path.join(SCRIPT_DIR, PRIVATE_DIR_NAME)

    def _pick_csv(folder):
        try:
            entries = os.listdir(folder)
        except OSError:
            return None
        csv_files = [f for f in entries if f.lower().endswith(".csv")]
        if not csv_files:
            return None
        preferred = [
            f for f in csv_files
            if any(key in f.lower() for key in ("master", "pris", "price"))
        ]
        chosen = sorted(preferred)[0] if preferred else sorted(csv_files)[0]
        return os.path.join(folder, chosen)

    found_in_private = _pick_csv(private_dir)
    if found_in_private:
        return found_in_private, True

    found_in_script_dir = _pick_csv(SCRIPT_DIR)
    if found_in_script_dir:
        return found_in_script_dir, False

    return None, False

# CSV-inställningar för masterfilen
csv.field_size_limit(sys.maxsize)


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


def find_item_files(root_dir):
    """Rekursiv sökning efter .json-filer under root_dir."""
    json_files = []
    for dirpath, _dirnames, filenames in os.walk(root_dir):
        for fname in filenames:
            if fname.lower().endswith(".json"):
                json_files.append(os.path.join(dirpath, fname))
    return sorted(json_files)


def collect_used_numbers(item_files, material_type):
    """
    Läser item-filerna och samlar använda artikelnummer.

    Returnerar:
      used_numbers: set av normaliserade artikelnummer
      usage_map: dict {normaliserat_nummer: [(item_fil, materialnamn, tsk_name), ...]}
      checked_count: antal item-filer som kunde läsas
      skipped_files: lista med (fil, felmeddelande) för filer som inte kunde tolkas
    """
    used_numbers = set()
    usage_map = defaultdict(list)
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
            t_type = (task.get("tsk_material_type") or "").strip()
            t_number_raw = task.get("tsk_material_number")
            t_number = normalize_number(t_number_raw)

            if t_type != material_type:
                continue
            if not t_number:
                continue

            used_numbers.add(t_number)
            usage_map[t_number].append(
                (
                    path,
                    task.get("tsk_material_name", "").strip(),
                    task.get("tsk_name", "").strip(),
                )
            )

    return used_numbers, usage_map, checked_count, skipped_files


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


def _detect_double_wrapped_csv(first_data_line):
    """
    Vissa Excel-exporter (t.ex. 'CSV UTF-8' från stora kalkylark) skriver varje
    rad som ETT enda textfält, omslutet av citattecken, separerat med ';' och
    med tomma extra-kolumner på slutet, typ:

        "SV-ENR,0000220,""NAMN, MED KOMMA"",M,173,...";;;;

    Detta upptäcker det mönstret genom att kolla om raden (efter att BOM/whitespace
    trimmats) börjar med ett citattecken och slutar med ett eller flera ';'.
    """
    line = first_data_line.rstrip("\r\n")
    return line.startswith('"') and line.rstrip(";").endswith('"') and ";" in line[-6:]


def collect_master_numbers(master_csv, material_type):
    """
    Läser masterprislistan radvis (streamat, hela filen laddas aldrig i minnet)
    och samlar alla artikelnummer med angiven material_type.

    Hanterar automatiskt två format:
      1. Vanlig CSV: material_type,material_number,...  (delimiter ',')
      2. "Dubbel-inpackad" CSV (vanligt från stora Excel-exporter):
         varje rad är ett enda citerat textfält separerat med ';' och tomma
         extra-kolumner, där det citerade fältet i sin tur är den riktiga
         kommaseparerade raden med dubblerade citattecken.

    Returnerar:
      master_numbers: set av normaliserade artikelnummer
      total_rows: antal inlästa (icke-tomma) datarader
      matching_rows: antal rader som matchade material_type
      used_encoding: vilken teckenkodning som användes
    """
    master_numbers = set()
    total_rows = 0
    matching_rows = 0

    fh, used_encoding = _open_with_fallback_encoding(master_csv)

    try:
        outer_reader = csv.reader(fh, delimiter=";", quotechar='"')
        try:
            header_outer = next(outer_reader)
        except StopIteration:
            raise RuntimeError("Masterfilen verkar vara tom.")

        # Kolla om formatet är dubbel-inpackat genom att titta på headerraden:
        # om headern efter kommasplit inte innehåller "material_type" som första
        # kolumn, eller om outer-split gav flera fält där bara första är fylld,
        # tolkar vi det som dubbel-inpackat och kommasplit-parsar fält 0 igen.
        is_wrapped = len(header_outer) > 1 and header_outer[0].strip().split(",")[0].strip(' "') == "material_type"

        if is_wrapped:
            fieldnames = [fn.strip() for fn in next(csv.reader([header_outer[0]], delimiter=",", quotechar='"'))]
        else:
            # Vanligt format: header_outer var redan hela raden kommaseparerad
            # (dvs vi läste med fel delimiter ovan) - läs om filen med ','.
            fh.close()
            fh, used_encoding = _open_with_fallback_encoding(master_csv)
            reader = csv.DictReader(fh)
            fieldnames = [fn.strip() for fn in reader.fieldnames] if reader.fieldnames else []
            reader.fieldnames = fieldnames

            if "material_type" not in fieldnames or "material_number" not in fieldnames:
                raise RuntimeError(
                    "Masterfilen saknar förväntade kolumner 'material_type' och/eller "
                    f"'material_number'. Hittade kolumner: {fieldnames}"
                )

            for row in reader:
                total_rows += 1
                m_type = (row.get("material_type") or "").strip()
                if m_type != material_type:
                    continue
                matching_rows += 1
                m_number = normalize_number(row.get("material_number"))
                if m_number:
                    master_numbers.add(m_number)

            fh.close()
            return master_numbers, total_rows, matching_rows, used_encoding

        if "material_type" not in fieldnames or "material_number" not in fieldnames:
            raise RuntimeError(
                "Masterfilen saknar förväntade kolumner 'material_type' och/eller "
                f"'material_number'. Hittade kolumner: {fieldnames}"
            )

        type_idx = fieldnames.index("material_type")
        number_idx = fieldnames.index("material_number")

        for row in outer_reader:
            if not row or not row[0].strip():
                # Tom "utfyllnadsrad" från Excel-exporten - hoppa över.
                continue
            try:
                inner = next(csv.reader([row[0]], delimiter=",", quotechar='"'))
            except Exception:
                continue
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
    finally:
        fh.close()

    return master_numbers, total_rows, matching_rows, used_encoding


def write_report(
    output_path,
    material_type,
    items_root,
    master_csv,
    checked_count,
    skipped_files,
    used_numbers,
    usage_map,
    master_numbers,
    total_master_rows,
    matching_master_rows,
    master_encoding,
):
    missing = sorted(used_numbers - master_numbers)
    found = used_numbers & master_numbers

    with open(output_path, "w", encoding="utf-8") as out:
        out.write("ARTIKELNUMMER-KONTROLL MOT MASTERPRISLISTA\n")
        out.write("=" * 60 + "\n\n")
        out.write(f"Kontroll körd:            {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        out.write(f"Materialtyp kontrollerad: {material_type}\n")
        out.write(f"Item-filer sökta i:       {items_root}\n")
        out.write(f"Masterprislista:          {master_csv}\n")
        out.write(f"Masterfil inläst med kodning: {master_encoding}\n\n")

        out.write("SAMMANFATTNING\n")
        out.write("-" * 60 + "\n")
        out.write(f"Item-filer kontrollerade:              {checked_count}\n")
        out.write(f"Item-filer som ej kunde läsas:         {len(skipped_files)}\n")
        out.write(f"Rader i masterfilen (totalt):           {total_master_rows}\n")
        out.write(f"Rader i masterfilen ({material_type}):  {matching_master_rows}\n")
        out.write(f"Unika använda artikelnummer ({material_type}): {len(used_numbers)}\n")
        out.write(f"Träffar (finns i masterlistan):        {len(found)}\n")
        out.write(f"SAKNADE (finns EJ i masterlistan):     {len(missing)}\n\n")

        if skipped_files:
            out.write("FILER SOM INTE KUNDE LÄSAS\n")
            out.write("-" * 60 + "\n")
            for path, err in skipped_files:
                out.write(f"- {path}\n    Fel: {err}\n")
            out.write("\n")

        out.write("SAKNADE ARTIKELNUMMER - DETALJER\n")
        out.write("-" * 60 + "\n")
        if not missing:
            out.write("Inga saknade artikelnummer. Allt stämmer mot masterlistan.\n\n")
        else:
            for number in missing:
                out.write(f"\nArtikelnummer: {number}\n")
                for path, mat_name, tsk_name in usage_map[number]:
                    out.write(
                        f"  - Fil: {path}\n"
                        f"    Materialnamn i item-fil: {mat_name or '(saknas)'}\n"
                        f"    Task: {tsk_name or '(saknas)'}\n"
                    )
            out.write("\n")

        out.write("=" * 60 + "\n")
        out.write("Slut på rapport.\n")


def main():
    parser = argparse.ArgumentParser(
        description="Kontrollerar att artikelnummer i item-filer finns i grossistens masterprislista."
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
             "Standard: den .csv-fil som ligger bredvid scriptet.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Sökväg dit textrapporten skrivs. "
             "Standard: artikelnummer_rapport.txt bredvid scriptet.",
    )
    parser.add_argument(
        "--material-type",
        default=DEFAULT_MATERIAL_TYPE,
        help="Vilken material_type som ska kontrolleras (standard: SV-ENR).",
    )
    args = parser.parse_args()

    if args.items_root is None:
        args.items_root = DEFAULT_ITEMS_ROOT
        print(f"Ingen --items-root angiven, använder scriptets mapp: {args.items_root}")

    if args.output is None:
        args.output = default_output_path()

    if args.master is None:
        auto_master, found_in_private = find_default_master_csv()
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
                f"Flytta den dit så skyddas den av .gitignore och laddas inte upp till Git av misstag."
            )

    if not os.path.isdir(args.items_root):
        print(f"FEL: items-root-mappen finns inte: {args.items_root}", file=sys.stderr)
        sys.exit(1)
    if not os.path.isfile(args.master):
        print(f"FEL: masterfilen finns inte: {args.master}", file=sys.stderr)
        sys.exit(1)

    print(f"Söker item-filer i: {args.items_root} ...")
    item_files = find_item_files(args.items_root)
    print(f"Hittade {len(item_files)} .json-filer.")

    print("Läser item-filer och samlar använda artikelnummer...")
    used_numbers, usage_map, checked_count, skipped_files = collect_used_numbers(
        item_files, args.material_type
    )
    print(f"  Kontrollerade {checked_count} item-filer.")
    print(f"  Hittade {len(used_numbers)} unika artikelnummer ({args.material_type}).")
    if skipped_files:
        print(f"  OBS: {len(skipped_files)} filer kunde inte läsas (se rapporten för detaljer).")

    print(f"Läser masterprislista (kan ta en stund för stora filer): {args.master} ...")
    master_numbers, total_rows, matching_rows, master_encoding = collect_master_numbers(
        args.master, args.material_type
    )
    print(f"  Läste {total_rows} rader totalt, {matching_rows} matchade material_type={args.material_type}.")
    print(f"  Kodning som användes: {master_encoding}")

    missing_count = len(used_numbers - master_numbers)
    print(f"\nSaknade artikelnummer: {missing_count} av {len(used_numbers)}")

    write_report(
        args.output,
        args.material_type,
        args.items_root,
        args.master,
        checked_count,
        skipped_files,
        used_numbers,
        usage_map,
        master_numbers,
        total_rows,
        matching_rows,
        master_encoding,
    )
    print(f"\nRapport skriven till: {args.output}")


if __name__ == "__main__":
    main()