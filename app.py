from datetime import datetime
import pytz
from re import match
from flask import request, jsonify
from flask import Flask, render_template
from flask import request, redirect, session
from flask import Flask, render_template, request, redirect, session
from soupsieve import match
app = Flask(__name__)
from flask_compress import Compress
Compress(app)
import os
from werkzeug.utils import secure_filename
# =========================================
# EXACT DATA FOLDER → SQLITE CONVERTER
# =========================================

# 🔥 RESULT:
#
# data/
# ├── all_match/
# ├── NRR_calculation/
# ├── match_result/
# ├── teamlist/
# ├── current_match.txt
# ├── history.txt
# ├── most_runs.txt
# └── ...
#
# ⬇ EXACT SAME STRUCTURE INSIDE SQLITE
#
# TABLE: folders
# TABLE: files
#
# 🔥 FULL ORIGINAL CONTENT PRESERVED
# 🔥 NO DATA LOSS
# 🔥 SAME FOLDER STRUCTURE
# 🔥 SAME FILE CONTENT
# 🔥 FUTURE RESTORE POSSIBLE
#
# =========================================

import sqlite3
import os

DB_NAME = "data/cricket.db"


def get_db():

    conn = sqlite3.connect(DB_NAME)

    conn.row_factory = sqlite3.Row

    return conn


@app.route("/full-convert")
def full_convert():

    conn = get_db()

    c = conn.cursor()

    # =====================================
    # CREATE FOLDERS TABLE
    # =====================================

    c.execute("""

    CREATE TABLE IF NOT EXISTS folders (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        folder_name TEXT UNIQUE

    )

    """)

    # =====================================
    # CREATE FILES TABLE
    # =====================================

    c.execute("""

    CREATE TABLE IF NOT EXISTS files (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        folder_name TEXT,

        file_name TEXT,

        full_path TEXT,

        content TEXT

    )

    """)

    # =====================================
    # CLEAR OLD DATA
    # =====================================

    c.execute("DELETE FROM folders")
    c.execute("DELETE FROM files")

    # =====================================
    # ROOT DATA FOLDER
    # =====================================

    root = "data"

    # =====================================
    # WALK THROUGH EVERYTHING
    # =====================================

    for current_path, dirs, files in os.walk(root):

        # =================================
        # RELATIVE FOLDER NAME
        # =================================

        relative_folder = os.path.relpath(current_path, root)

        if relative_folder == ".":
            relative_folder = "root"

        # =================================
        # SAVE FOLDER
        # =================================

        c.execute("""

        INSERT OR IGNORE INTO folders (

            folder_name

        )

        VALUES (?)

        """, (

            relative_folder,

        ))

        # =================================
        # SAVE FILES
        # =================================

        for file in files:

            # 🔥 SKIP DB ITSELF
            if file == "cricket.db":
                continue

            full_path = os.path.join(current_path, file)

            try:

                with open(full_path, "r", encoding="utf-8") as f:

                    content = f.read()

            except:

                continue

            c.execute("""

            INSERT INTO files (

                folder_name,
                file_name,
                full_path,
                content

            )

            VALUES (?, ?, ?, ?)

            """, (

                relative_folder,
                file,
                full_path,
                content

            ))

    # =====================================
    # SAVE
    # =====================================

    conn.commit()

    conn.close()

    return "FULL EXACT DATA STRUCTURE CONVERTED"

def sync_db():

    import sqlite3
    import os

    conn = sqlite3.connect("data/cricket.db")

    c = conn.cursor()

    # =====================================
    # CREATE TABLE
    # =====================================

    c.execute("""

    CREATE TABLE IF NOT EXISTS files (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        folder_name TEXT,

        file_name TEXT,

        full_path TEXT,

        content TEXT

    )

    """)

    # =====================================
    # CLEAR OLD
    # =====================================

    c.execute("DELETE FROM files")

    root = "data"

    # =====================================
    # WALK THROUGH DATA
    # =====================================

    for current_path, dirs, files in os.walk(root):

        relative_folder = os.path.relpath(current_path, root)

        if relative_folder == ".":
            relative_folder = "root"

        for file in files:

            # 🔥 SKIP DB ITSELF
            if file == "cricket.db":
                continue

            full_path = os.path.join(current_path, file)

            try:

                with open(full_path, "r", encoding="utf-8") as f:

                    content = f.read()

                c.execute("""

                INSERT INTO files (

                    folder_name,
                    file_name,
                    full_path,
                    content

                )

                VALUES (?, ?, ?, ?)

                """, (

                    relative_folder,
                    file,
                    full_path,
                    content

                ))

            except:
                pass

    conn.commit()

    conn.close()
# 🔥 SAFE FILE WRITE
def safe_write(path, data):

    import os
    import uuid

    # 🔥 UNIQUE TEMP FILE
    temp_path = path + "." + str(uuid.uuid4()) + ".tmp"

    with open(temp_path, "w", encoding="utf-8") as f:

        for k, v in data.items():
            f.write(f"{k}={v}\n")

    os.replace(temp_path, path)
# 🔥 SAFE HISTORY APPEND
def append_history(line):

    temp = "data/history_temp.txt"

    old = ""

    if os.path.exists("data/history.txt"):

        with open("data/history.txt", "r") as f:
            old = f.read()

    old += line + "\n"

    with open(temp, "w") as f:
        f.write(old)

    os.replace(temp, "data/history.txt")
# 🔥 ensure folder exists
os.makedirs("data/all_match", exist_ok=True)

UPLOAD_FOLDER = "static/images/players"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
# 🔥 secret key (must)
app.secret_key = "cricket_live_super_secret_2026"
def load_teams():
    teams = []

    for file in os.listdir("data/teamlist"):
        if file.endswith(".txt"):
            team_name = file.replace(".txt", "")
            teams.append(team_name)

    return teams
# Fixture file theke data ana
def load_fixtures():
    fixtures = []
    with open("data/fixture.txt", "r") as f:
        for line in f:
            parts = line.strip().split("|")
            teams = parts[0].split("vs")

            if len(teams) == 2:
                fixtures.append({
                    "team1": teams[0].strip(),
                    "team2": teams[1].strip(),
                    "time": parts[1].strip() if len(parts) > 1 else "TBD",
                    "date": parts[2].strip() if len(parts) > 2 else ""
                })
    return fixtures

import random

@app.route("/")
def home():
    import os, random

    fixtures = load_fixtures()

    sponsors = []
    try:
        sponsors = os.listdir("static/images/uploads")
    except:
        pass

    banners = []
    try:
        banners = os.listdir("static/images/banner")
    except:
        pass

    banner = random.choice(banners) if banners else None

    live_match = None
    completed_match = None

    try:
        folder = "data/all_match"
        lock_file = "data/home_current.txt"

        files = sorted(os.listdir(folder), reverse=True)
        # 🔥 ONLY FIRST INNINGS FILE
        files = [f for f in files if f.endswith("_1st.txt")]
        # 🔥 LOCK LOAD (FIXED)
        if os.path.exists(lock_file):
            with open(lock_file) as f:
                locked = f.read().strip()

            if locked in files:
                files = [locked]

        for file in files:
            path = os.path.join(folder, file)

            with open(path) as f:
                content = f.read()

            # 🔥 LOAD FIRST INNINGS

            first = {}

            for line in content.splitlines():

                if "=" in line:
                    k, v = line.strip().split("=", 1)
                    first[k] = v

            # 🔥 LOAD SECOND INNINGS

            second = {}

            second_file = path.replace("_1st.txt", "_2nd.txt")

            if os.path.exists(second_file):

                with open(second_file) as sf:

                    for line in sf:

                        if "=" in line:
                            k, v = line.strip().split("=", 1)
                            second[k] = v

            innings_break = len(second) > 0

            team1 = first.get("batting")
            team2 = second.get("batting") or first.get("bowling")

            team2_score = second.get("score", "")
            team2_wickets = second.get("wickets", "")
            team2_over = f"{second.get('over','0')}.{second.get('ball','0')}"

            if second.get("over", "0") == "0" and second.get("ball", "0") == "0":
                if innings_break:
                    team2_score = "0"
                    team2_wickets = "0"
                    team2_over = "0.0"
                else:
                    team2_score = ""
                    team2_wickets = ""
                    team2_over = ""

            result_text = ""
            result_text = second.get("match_result", "")

            match_data = {
                "team1": team1,
                "team1_score": first.get("score", "0"),
                "team1_wickets": first.get("wickets", "0"),
                "team1_over": f"{first.get('over','0')}.{first.get('ball','0')}",

                "team2": team2,
                "team2_score": team2_score,
                "team2_wickets": team2_wickets,
                "team2_over": team2_over,

                "result": result_text,
                "need_text": second.get("need_text"),
                "toss": first.get("toss"),
                "opt": first.get("opt"),
                "innings_break": innings_break,
            }

            if not result_text and live_match is None:
                match_data["status"] = "LIVE"
                live_match = match_data

                # 🔥 NEW LIVE MATCH → LOCK UPDATE (ADD HERE)
                try:
                    if os.path.exists(lock_file):
                        with open(lock_file) as f:
                            locked = f.read().strip()

                        if locked != file:
                            with open(lock_file, "w") as f:
                                f.write(file)
                except:
                    pass

            

            if result_text and completed_match is None:
                match_data["status"] = "COMPLETED"
                completed_match = match_data

            # 🔥 LOCK SAVE (FIRST TIME ONLY)
            if not os.path.exists(lock_file):
                with open(lock_file, "w") as f:
                    f.write(file)

            if live_match and completed_match:
                break

        live_match = live_match  # শুধু live থাকলেই show হবে

    except:
        pass

    return render_template(
        "index.html",
        fixtures=fixtures,
        sponsors=sponsors,
        banner=banner,
        admin=session.get("admin"),
        live_match=live_match
    )
home_cache = {
    "data": "",
    "time": 0
}
@app.route("/home-live-data")
def home_live_data():

    import os
    import time

    if time.time() - home_cache["time"] < 2 and home_cache["data"]:

        return home_cache["data"]

    live_match = None
    completed_match = None

    try:

        folder = "data/all_match"

        lock_file = "data/home_current.txt"

        files = sorted(os.listdir(folder), reverse=True)

        # 🔥 ONLY FIRST INNINGS FILE
        files = [f for f in files if f.endswith("_1st.txt")]

        # 🔥 LOCK LOAD
        if os.path.exists(lock_file):

            with open(lock_file) as f:

                locked = f.read().strip()

            if locked in files:

                files = [locked]

        for file in files:

            path = os.path.join(folder, file)

            first = {}
            second = {}

            # =========================
            # 🔥 LOAD FIRST INNINGS
            # =========================

            try:

                with open(path) as f:

                    for line in f:

                        if "=" in line:

                            k, v = line.strip().split("=", 1)

                            first[k] = v

            except:
                continue

            # =========================
            # 🔥 LOAD SECOND INNINGS
            # =========================

            second_file = path.replace("_1st.txt", "_2nd.txt")

            if os.path.exists(second_file):

                try:

                    with open(second_file) as sf:

                        for line in sf:

                            if "=" in line:

                                k, v = line.strip().split("=", 1)

                                second[k] = v

                except:
                    pass

            # =========================
            # 🔥 MATCH INFO
            # =========================

            innings_break = len(second) > 0

            team1 = first.get("batting")

            team2 = second.get("batting") or first.get("bowling")

            team2_score = second.get("score", "")

            team2_wickets = second.get("wickets", "")

            team2_over = (
                f"{second.get('over','0')}."
                f"{second.get('ball','0')}"
            )

            if (
                second.get("over", "0") == "0"
                and second.get("ball", "0") == "0"
            ):

                if innings_break:

                    team2_score = "0"
                    team2_wickets = "0"
                    team2_over = "0.0"

                else:

                    team2_score = ""
                    team2_wickets = ""
                    team2_over = ""

            # =========================
            # 🔥 RESULT
            # =========================

            result_text = second.get("match_result", "")

            match_data = {

                "team1": team1,

                "team1_score": first.get("score", "0"),

                "team1_wickets": first.get("wickets", "0"),

                "team1_over":
                f"{first.get('over','0')}."
                f"{first.get('ball','0')}",

                "team2": team2,

                "team2_score": team2_score,

                "team2_wickets": team2_wickets,

                "team2_over": team2_over,

                "result": result_text,

                "need_text": second.get("need_text"),

                "toss": first.get("toss"),

                "opt": first.get("opt"),

                "innings_break": innings_break,
            }

            # =========================
            # 🔥 LIVE
            # =========================

            if not result_text and live_match is None:

                match_data["status"] = "LIVE"

                live_match = match_data

            # =========================
            # 🔥 COMPLETED
            # =========================

            if result_text and completed_match is None:

                match_data["status"] = "COMPLETED"

                completed_match = match_data

            if live_match and completed_match:
                break

        live_match = live_match

    except:
        pass

    response = render_template(
        "home_live_partial.html",
        live_match=live_match
    )

    home_cache["data"] = response

    home_cache["time"] = time.time()

    return response

@app.route("/match")
def match_page():

    import os, json, ast
    from flask import request

    data = {}

    # 🔵 current match
    try:
        with open("data/current_match.txt") as f:

            for line in f:

                if "=" in line:
                    k, v = line.strip().split("=", 1)
                    data[k] = v

    except:
        pass

    # 🔥 =========================
    # 🔥 GET FILE FROM URL
    # 🔥 =========================

    file = request.args.get("file")

    first = {}
    second = {}

    try:

        if file:

            path = os.path.join("data/all_match", file)

        else:

            folder = "data/all_match"

            files = sorted(
                [f for f in os.listdir(folder) if f.endswith("_1st.txt")],
                key=lambda x: os.path.getmtime(os.path.join(folder, x)),
                reverse=True
            )

            path = os.path.join(folder, files[0]) if files else None

        # 🔥 =========================
        # 🔥 LOAD FIRST INNINGS
        # 🔥 =========================

        if path and os.path.exists(path):

            with open(path) as f:

                for line in f:

                    if "=" in line:
                        k, v = line.strip().split("=", 1)
                        first[k] = v

            # 🔥 =========================
            # 🔥 LOAD SECOND INNINGS
            # 🔥 =========================

            second_file = path.replace("_1st.txt", "_2nd.txt")

            if os.path.exists(second_file):

                with open(second_file) as sf:

                    for line in sf:

                        if "=" in line:
                            k, v = line.strip().split("=", 1)
                            second[k] = v

    except:
        pass

    # 🔥 =========================
    # 🔥 SAFE JSON
    # 🔥 =========================

    def safe_json(text):

        try:
            return json.loads(text)

        except:

            try:
                return ast.literal_eval(text)

            except:
                return []

    # 🔥 wickets
    first["wickets_log"] = safe_json(first.get("wickets_log", "[]"))
    second["wickets_log"] = safe_json(second.get("wickets_log", "[]"))

    # 🔥 =========================
    # 🔥 DISMISSALS
    # 🔥 =========================

    def clean(n):

        return n.split('(')[0].strip().lower()

    def build_map(log):

        d = {}

        for w in log:

            key = clean(w.get("batsman", ""))

            t = (w.get("type") or "").lower()

            bowler = w.get("bowler", "")

            if t == "bowled":
                d[key] = f"b {bowler}"

            elif "catch" in t:
                d[key] = f"c b {bowler}"

            elif "run out" in t:
                d[key] = "run out"

            elif t == "lbw":
                d[key] = f"lbw b {bowler}"

            else:
                d[key] = w.get("type", "out")

        return d

    first["dismissals"] = build_map(first["wickets_log"])
    second["dismissals"] = build_map(second["wickets_log"])

    # 🔥 =========================
    # 🔥 SQUADS
    # 🔥 =========================

    def find_squad_key(data, team):

        team = team.lower()

        for k in data.keys():

            if k.lower() == team + "_squad":
                return k

        return team + "_squad"

    host = first.get("host", "")
    visitor = first.get("visitor", "")

    host_key = find_squad_key(first, host)
    visitor_key = find_squad_key(first, visitor)

    # 🔥 parse squads
    first[host_key] = safe_json(first.get(host_key, "[]"))
    first[visitor_key] = safe_json(first.get(visitor_key, "[]"))

    # 🔥 split squads
    def split_squad(squad):

        playing = []
        bench = []
        staff = []

        for p in squad:

            extra = p.get("extra", [])

            if "bench" in extra:
                bench.append(p)

            elif "stf" in extra:
                staff.append(p)

            else:
                playing.append(p)

        return playing, bench, staff

    t1_play, t1_bench, t1_staff = split_squad(first.get(host_key, []))
    t2_play, t2_bench, t2_staff = split_squad(first.get(visitor_key, []))

    # 🔥 =========================
    # 🔥 RETURN
    # 🔥 =========================

    return render_template(
        "match.html",

        data=data,

        first=first,
        second=second,

        t1_play=t1_play,
        t1_bench=t1_bench,
        t1_staff=t1_staff,

        t2_play=t2_play,
        t2_bench=t2_bench,
        t2_staff=t2_staff
    )

@app.route("/match-live-data")
def match_live_data():

    data = {}

    try:
        with open("data/current_match.txt") as f:
            for line in f:
                if "=" in line:
                    k, v = line.strip().split("=", 1)
                    data[k] = v
    except:
        pass

    return render_template("match_live_partial.html", data=data)

def load_fixtures():

    fixtures = []

    try:
        with open("data/fixture.txt", "r") as f:

            for line in f:

                line = line.strip()
                if not line:
                    continue

                parts = [p.strip() for p in line.split("|")]

                team1 = ""
                team2 = ""
                time = ""
                date = ""
                stage = "group"

                # 🔥 TEAM
                if "vs" in parts[0].lower():
                    t = parts[0].split("vs")
                    team1 = t[0].strip()
                    team2 = t[1].strip()

                # 🔥 OTHER
                if len(parts) > 1:
                    time = parts[1]

                if len(parts) > 2:
                    date = parts[2]

                if len(parts) > 3:
                    stage = parts[3].lower()

                # 🔥 NORMALIZE
                if "knock" in stage:
                    stage = "knockout"
                elif "final" in stage:
                    stage = "final"
                else:
                    stage = "group"

                fixtures.append({
                    "team1": team1,
                    "team2": team2,
                    "time": time,
                    "date": date,
                    "stage": stage
                })

    except:
        pass

    return fixtures

def get_final_teams():

    import os

    group_a = []
    group_b = []

    try:
        with open("data/teamnamePoints.txt") as f:
            for line in f:

                team, group = [x.strip() for x in line.split(",")]

                path = f"data/match_result/{team}.txt"

                matches = won = lost = 0

                if os.path.exists(path):
                    with open(path) as tf:
                        for l in tf:
                            k,v = l.strip().split("=")
                            if k == "matches": matches = int(v)
                            elif k == "won": won = int(v)
                            elif k == "lost": lost = int(v)

                # 🔥 NRR read
                nrr = 0
                nrr_file = f"data/NRR_calculation/{team}.txt"

                if os.path.exists(nrr_file):
                    with open(nrr_file) as nf:
                        data = {}
                        for l in nf:
                            if "=" in l:
                                k,v = l.strip().split("=")
                                data[k] = float(v)

                        try:
                            rr = data["total_runs_scored"] / data["total_overs_faced"]
                            rrc = data["total_runs_conceded"] / data["total_overs_bowled"]
                            nrr = rr - rrc
                        except:
                            nrr = 0

                obj = {
                    "team": team,
                    "pts": won * 2,
                    "w": won,
                    "nrr": nrr
                }

                if group.lower() == "a":
                    group_a.append(obj)
                else:
                    group_b.append(obj)

    except:
        pass

    # 🔥 SORT
    group_a.sort(key=lambda x: (x["pts"], x["nrr"]), reverse=True)
    group_b.sort(key=lambda x: (x["pts"], x["nrr"]), reverse=True)

    team_a = group_a[0]["team"] if group_a else None
    team_b = group_b[0]["team"] if group_b else None

    return team_a, team_b

@app.route("/fixture")
def fixture():

    fixtures = load_fixtures()

    final_a, final_b = get_final_teams()

    return render_template(
        "fixture.html",
        fixtures=fixtures,
        final_a=final_a,
        final_b=final_b
    )
@app.route("/team")
def team():
    teams = load_teams()
    return render_template("team.html", teams=teams)
@app.route("/team/<name>")
def team_details(name):

    players = []
    bench = []
    staff = []

    try:
        with open(f"data/teamlist/{name}.txt", "r") as f:
            for line in f:
                parts = [p.strip() for p in line.strip().split(",")]

                # 🔥 Supporting Staff
                if len(parts) == 3 and "stf" in parts[1].lower():
                    staff.append({
                        "name": parts[0],
                        "role": parts[2]
                    })

                # 🔥 Bench player
                elif len(parts) == 3 and parts[1].lower() == "bench":
                    bench.append({
                        "name": parts[0],
                        "role": parts[2]
                    })

                # 🔥 Normal player
                elif len(parts) == 2:
                    players.append({
                        "name": parts[0],
                        "role": parts[1]
                    })

    except Exception as e:
        print(e)

    return render_template(
        "team_details.html",
        team=name,
        players=players,
        bench=bench,
        staff=staff
    )

# 🔐 LOGIN ROUTE
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # 🔥 admin check
        if username == "admin" and password == "1234":
            session["admin"] = True   # 🔥 login success
            return redirect("/")      # 🔥 home e jabe

        else:
            return "Wrong username or password"

    return render_template("login.html")


# 🔓 LOGOUT ROUTE
@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect("/")

@app.route("/live")
def live():
    if not session.get("admin"):
        return redirect("/login")

    return render_template("live.html")

@app.route("/player-images")
def player_images():
    images = os.listdir(app.config["UPLOAD_FOLDER"])
    return render_template("player_images.html", images=images)

@app.route("/upload-player-image", methods=["POST"])
def upload_player_image():

    file = request.files["image"]

    if file:
        filename = file.filename   # 🔥 ORIGINAL NAME (no change)

        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

    return redirect("/player-images")
@app.route("/rename-image", methods=["POST"])
def rename_image():

    old_name = request.form.get("old")
    new_name = request.form.get("new")

    folder = app.config["UPLOAD_FOLDER"]

    old_path = os.path.join(folder, old_name)
    new_path = os.path.join(folder, new_name)

    # extension same rakha better
    if os.path.exists(old_path):
        os.rename(old_path, new_path)

    return "OK"

@app.route("/delete-multiple", methods=["POST"])
def delete_multiple():

    files = request.form.getlist("files")

    for file in files:
        path = os.path.join(app.config["UPLOAD_FOLDER"], file)
        if os.path.exists(path):
            os.remove(path)

    return redirect("/player-images")

@app.route("/squad")
def squad():

    if not session.get("admin"):
        return redirect("/login")

    teams = load_teams()

    return render_template("squad.html", teams=teams)

@app.route("/squad/<team>")
def squad_details(team):

    players = []

    try:
        with open(f"data/teamlist/{team}.txt", "r") as f:
            for line in f:
                line = line.strip()

                if not line:   # 🔥 empty line skip
                    continue

                parts = [p.strip() for p in line.split(",")]

                if len(parts) >= 2:
                    players.append({
                        "name": parts[0],
                        "role": ", ".join(parts[1:])
                    })

    except Exception as e:
        print("Error:", e)

    return render_template("squad_details.html", team=team, players=players)

@app.route("/add-player/<team>", methods=["POST"])
def add_player(team):

    player = request.form.get("player")

    if player:
        with open(f"data/teamlist/{team}.txt", "a") as f:
            f.write(player + "\n")

    return redirect(f"/squad/{team}")

@app.route("/delete-player/<team>/<int:index>")
def delete_player(team, index):

    path = f"data/teamlist/{team}.txt"

    with open(path, "r") as f:
        lines = f.readlines()

    if 0 <= index < len(lines):
        lines.pop(index)

    with open(path, "w") as f:
        f.writelines(lines)

    return redirect(f"/squad/{team}")

@app.route("/edit-player/<team>/<int:index>", methods=["POST"])
def edit_player(team, index):

    new_data = request.form.get("player")

    path = f"data/teamlist/{team}.txt"

    with open(path, "r") as f:
        lines = f.readlines()

    if 0 <= index < len(lines):
        lines[index] = new_data + "\n"

    with open(path, "w") as f:
        f.writelines(lines)

    return redirect(f"/squad/{team}")

@app.route("/manage-teams")
def manage_teams():

    if not session.get("admin"):
        return redirect("/login")

    teams = []

    for file in os.listdir("data/teamlist"):
        if file.endswith(".txt"):
            teams.append(file.replace(".txt", ""))

    return render_template("manage_teams.html", teams=teams)

@app.route("/add-team", methods=["POST"])
def add_team():

    team = request.form.get("team")

    if team:
        path = f"data/teamlist/{team}.txt"

        if not os.path.exists(path):
            with open(path, "w") as f:
                pass

    return redirect("/manage-teams")

@app.route("/delete-team/<team>")
def delete_team(team):

    path = f"data/teamlist/{team}.txt"

    if os.path.exists(path):
        os.remove(path)

    return redirect("/manage-teams")
@app.route("/edit-team/<old>", methods=["POST"])
def edit_team(old):

    new = request.form.get("team")

    old_path = f"data/teamlist/{old}.txt"
    new_path = f"data/teamlist/{new}.txt"

    if os.path.exists(old_path):
        os.rename(old_path, new_path)

    return redirect("/manage-teams")

@app.route("/team-logos")
def team_logos():

    images = os.listdir("static/images/teams")

    return render_template("team_logos.html", images=images)

@app.route("/upload-team-logo", methods=["POST"])
def upload_team_logo():

    file = request.files["image"]

    if file:
        filename = file.filename

        path = os.path.join("static/images/teams", filename)

        # duplicate avoid
        if os.path.exists(path):
            import time
            name, ext = os.path.splitext(filename)
            filename = f"{name}_{int(time.time())}{ext}"

        file.save(os.path.join("static/images/teams", filename))

    return redirect("/team-logos")
@app.route("/delete-team-logo", methods=["POST"])
def delete_team_logo():

    files = request.form.getlist("files")

    for file in files:
        path = os.path.join("static/images/teams", file)
        if os.path.exists(path):
            os.remove(path)

    return redirect("/team-logos")

@app.route("/rename-team-logo", methods=["POST"])
def rename_team_logo():

    old = request.form.get("old")
    new = request.form.get("new")

    folder = "static/images/teams"

    old_path = os.path.join(folder, old)
    new_path = os.path.join(folder, new)

    if os.path.exists(old_path):
        os.rename(old_path, new_path)

    return "OK"

@app.route("/group")
def group_page():

    teams = []

    try:
        with open("data/teamnamePoints.txt", "r") as f:
            for line in f:
                parts = [p.strip() for p in line.strip().split(",")]

                if len(parts) == 2:
                    teams.append({
                        "name": parts[0],
                        "group": parts[1]
                    })

    except:
        pass

    return render_template("group.html", teams=teams)

@app.route("/add-group-team", methods=["POST"])
def add_group_team():

    data = request.form.get("team")

    if data:
        with open("data/teamnamePoints.txt", "a") as f:
            f.write(data + "\n")

    return redirect("/group")

@app.route("/delete-group-team/<int:index>")
def delete_group_team(index):

    path = "data/teamnamePoints.txt"

    with open(path, "r") as f:
        lines = f.readlines()

    if 0 <= index < len(lines):
        lines.pop(index)

    with open(path, "w") as f:
        f.writelines(lines)

    return redirect("/group")

@app.route("/edit-group-team/<int:index>", methods=["POST"])
def edit_group_team(index):

    new = request.form.get("team")

    path = "data/teamnamePoints.txt"

    with open(path, "r") as f:
        lines = f.readlines()

    if 0 <= index < len(lines):
        lines[index] = new + "\n"

    with open(path, "w") as f:
        f.writelines(lines)

    return redirect("/group")

@app.route("/fixture-manage")
def fixture_manage():

    fixtures = []

    try:
        with open("data/fixture.txt", "r") as f:
            fixtures = [l.strip() for l in f if l.strip()]
    except:
        pass

    return render_template("fixture_manage.html", fixtures=fixtures)
@app.route("/add-fixture", methods=["POST"])
def add_fixture():

    data = request.form.get("fixture")

    if data:
        with open("data/fixture.txt", "a") as f:
            f.write(data + "\n")

    return redirect("/fixture-manage")

@app.route("/delete-fixture/<int:index>")
def delete_fixture(index):

    path = "data/fixture.txt"

    with open(path, "r") as f:
        lines = f.readlines()

    if 0 <= index < len(lines):
        lines.pop(index)

    with open(path, "w") as f:
        f.writelines(lines)

    return redirect("/fixture-manage")

@app.route("/edit-fixture/<int:index>", methods=["POST"])
def edit_fixture(index):

    new = request.form.get("fixture")

    path = "data/fixture.txt"

    with open(path, "r") as f:
        lines = f.readlines()

    if 0 <= index < len(lines):
        lines[index] = new + "\n"

    with open(path, "w") as f:
        f.writelines(lines)

    return redirect("/fixture-manage")
@app.route("/sponsor-images")
def sponsor_images():

    images = os.listdir("static/images/uploads")

    return render_template("sponsor_images.html", images=images)

@app.route("/upload-sponsor-image", methods=["POST"])
def upload_sponsor_image():

    file = request.files["image"]

    if file:
        filename = file.filename
        path = os.path.join("static/images/uploads", filename)

        # duplicate avoid
        if os.path.exists(path):
            import time
            name, ext = os.path.splitext(filename)
            filename = f"{name}_{int(time.time())}{ext}"

        file.save(os.path.join("static/images/uploads", filename))

    return redirect("/sponsor-images")

@app.route("/delete-sponsor-image", methods=["POST"])
def delete_sponsor_image():

    files = request.form.getlist("files")

    for file in files:
        path = os.path.join("static/images/uploads", file)
        if os.path.exists(path):
            os.remove(path)

    return redirect("/sponsor-images")

@app.route("/rename-sponsor-image", methods=["POST"])
def rename_sponsor_image():

    old = request.form.get("old")
    new = request.form.get("new")

    folder = "static/images/uploads"

    old_path = os.path.join(folder, old)
    new_path = os.path.join(folder, new)

    if os.path.exists(old_path):
        os.rename(old_path, new_path)

    return "OK"

@app.route("/banner-images")
def banner_images():

    images = []
    try:
        images = os.listdir("static/images/banner")
    except:
        pass

    return render_template("banner_images.html", images=images)

@app.route("/upload-banner", methods=["POST"])
def upload_banner():

    file = request.files["image"]

    if file:
        filename = file.filename
        path = os.path.join("static/images/banner", filename)

        if os.path.exists(path):
            import time
            name, ext = os.path.splitext(filename)
            filename = f"{name}_{int(time.time())}{ext}"

        file.save(os.path.join("static/images/banner", filename))

    return redirect("/banner-images")

@app.route("/delete-banner", methods=["POST"])
def delete_banner():

    files = request.form.getlist("files")

    for f in files:
        path = os.path.join("static/images/banner", f)
        if os.path.exists(path):
            os.remove(path)

    return redirect("/banner-images")

@app.route("/rename-banner", methods=["POST"])
def rename_banner():

    old = request.form.get("old")
    new = request.form.get("new")

    folder = "static/images/banner"

    old_path = os.path.join(folder, old)
    new_path = os.path.join(folder, new)

    if os.path.exists(old_path):
        os.rename(old_path, new_path)

    return "OK"

@app.route("/live-score")
def live_score():
    if not session.get("admin"):
        return redirect("/login")

    return render_template("score_update.html")   # 🔥 name change

@app.route("/new-match")
def new_match():
    if not session.get("admin"):
        return redirect("/login")

    files = os.listdir("data/teamlist")
    teams = [f.replace(".txt", "") for f in files if f.endswith(".txt")]
    return render_template("new_match.html", teams=teams)


@app.route("/opening-players")
def opening_players():
    if not session.get("admin"):
        return redirect("/login")

    # 🔥 read match data
    data = {}
    with open("data/current_match.txt") as f:
        for line in f:
            key, value = line.strip().split("=",1)
            data[key] = value

    batting_team = data["batting"]
    bowling_team = data["bowling"]   # 🔥 NEW

    # 🔥 batting players (clean name)
    with open(f"data/teamlist/{batting_team}.txt") as f:
        players = [line.strip().split(",")[0] for line in f]

    # 🔥 bowling players (clean name)
    with open(f"data/teamlist/{bowling_team}.txt") as f:
        bowlers = [line.strip().split(",")[0] for line in f]

    return render_template(
        "opening_players.html",
        players=players,        # 🔥 ager ta same
        bowlers=bowlers         # 🔥 NEW
    )

@app.route("/save-match")
def save_match():

    import os
    import json
    from datetime import datetime

    # 🔥 RESET HISTORY
    open("data/history.txt", "w").close()

    host = request.args.get("host")
    visitor = request.args.get("visitor")
    toss = request.args.get("toss")
    opt = request.args.get("opt")
    overs = request.args.get("overs")

    # 🔥 SAFE TOSS WINNER
    if toss == "host":
        toss_winner = host
    else:
        toss_winner = visitor

    # 🔥 SAFE BATTING / BOWLING
    if opt == "bat":

        batting = toss_winner

        if toss_winner == host:
            bowling = visitor
        else:
            bowling = host

    else:

        bowling = toss_winner

        if toss_winner == host:
            batting = visitor
        else:
            batting = host

    # 🔥 MATCH FILE
    # 🔥 MATCH FILES

    base_name = f"data/all_match/{host}_vs_{visitor}".replace(" ", "_")

    first_file = base_name + "_1st.txt"
    second_file = base_name + "_2nd.txt"

    open(first_file, "a").close()
    open(second_file, "a").close()

    # 🔥 MATCH TIME
    bd_time = datetime.now(pytz.timezone("Asia/Dhaka"))

    match_time = bd_time.strftime("%d %b %Y, %I:%M %p")

    # 🔥 LOAD TEAM
    def load_team(file):

        players = []

        try:

            with open(file) as f:

                for line in f:

                    line = line.strip()

                    if not line:
                        continue

                    parts = [x.strip() for x in line.split(",")]

                    name = parts[0]

                    role = parts[-1] if len(parts) > 1 else ""

                    extra = parts[1:-1] if len(parts) > 2 else []

                    players.append({
                        "name": name,
                        "role": role,
                        "extra": extra
                    })

        except:
            pass

        return players

    team1_list = load_team(f"data/teamlist/{host}.txt")
    team2_list = load_team(f"data/teamlist/{visitor}.txt")

    # 🔥 DYNAMIC SQUAD KEYS
    t1_key = host.replace(" ", "_") + "_squad"
    t2_key = visitor.replace(" ", "_") + "_squad"

    # 🔥 MATCH DATA
    match_data = {

        "host": host,
        "visitor": visitor,

        "toss": toss_winner,
        "opt": opt,

        "batting": batting,
        "bowling": bowling,

        "overs": overs,

        "score": "0",
        "wickets": "0",

        "over": "0",
        "ball": "0",

        "s_runs": "0",
        "s_balls": "0",
        "s_4": "0",
        "s_6": "0",
        "s_sr": "0",

        "ns_runs": "0",
        "ns_balls": "0",
        "ns_4": "0",
        "ns_6": "0",
        "ns_sr": "0",

        "b_runs": "0",
        "b_balls": "0",
        "b_maiden": "0",
        "b_wickets": "0",
        "b_er": "0",

        "batsman_log": "",
        "this_over": "",
        "over_log": "",

        "extra": "0,0LB,0B,0WD,0NB",

        "partnerships": "[]",

        "innings": "1",

        "first_match_file": first_file,
        "second_match_file": second_file,
        "match_time": match_time,

        "wickets_log": "[]",

        t1_key: json.dumps(team1_list),
        t2_key: json.dumps(team2_list)
    }

    # 🔥 SAFE SAVE
    safe_write("data/current_match.txt", match_data)

    # 🔥 RESET HOME LOCK
    try:
        os.remove("data/home_current.txt")
    except:
        pass

    return redirect("/opening-players")

@app.route("/save-opening")
def save_opening():

   
    striker = request.args.get("striker")
    non_striker = request.args.get("nonStriker")
    bowler = request.args.get("bowler")

    # 🔥 previous data read
    data = {}
    with open("data/current_match.txt") as f:
        for line in f:
            key, value = line.strip().split("=",1)
            data[key] = value

    # 🔥 update
    data["striker"] = striker
    data["non_striker"] = non_striker
    data["bowler"] = bowler

    # 🔥 NEW: INIT BATSMAN LOG (instant show)
    data["batsman_log"] = (
        f"{striker}=0,0,0,0,0.00|"
        f"{non_striker}=0,0,0,0,0.00"
    )
    # 🔵 INIT BOWLER LOG (opening instant show)
    data["bowler_log"] = f"{bowler}=0.0,0,0,0,0.00"
    # 🔥 rewrite file
    safe_write("data/current_match.txt", data)

    # 🔥 SAVE INITIAL STATE FOR UNDO
    line = ";;".join([f"{k}={v}" for k, v in data.items()])
    append_history(line)
    return redirect("/live-match")



@app.route("/live-match")
def live_match():

    if not session.get("admin"):
        return redirect("/login")

    data = {}

    # 🔥 1. file load
    with open("data/current_match.txt") as f:
        for line in f:
           if "=" in line:
            k, v = line.strip().split("=", 1)
            data[k] = v

    # 🔥 INIT BOWLER DATA (FIX PC ISSUE)
    if "b_balls" not in data:
        data["b_balls"] = "0"

    if "b_runs" not in data:
        data["b_runs"] = "0"

    if "b_wickets" not in data:
        data["b_wickets"] = "0"

    if "b_maiden" not in data:
        data["b_maiden"] = "0"

    if "b_er" not in data:
        data["b_er"] = "0"
    # 🔥 SAVE STATE WHEN PAGE LOAD (UNDO FIX)
    if not request.args:   # only first load (no button click)

        try:
            with open("data/history.txt", "r") as f:
                lines = f.readlines()
        except:
            lines = []

        current_line = ";;".join([f"{k}={data[k]}" for k in data])

        if not lines or lines[-1].strip() != current_line:
            append_history(current_line)
    # 🔥 2. URL data
    score = request.args.get("score")
    wickets = request.args.get("wickets")
    over = request.args.get("over")
    ball = request.args.get("ball")
    new_player = request.args.get("new")
    over_ended = request.args.get("overEnded")
    wicket_type = request.args.get("type")
    # 🔥 FINAL FIX: COUNT WICKET BEFORE NEW BOWLER
    if new_player and wicket_type:

        if not wicket_type.startswith("Run out"):

            bw = data.get("b_wickets")
            prev_bw = int(bw) if str(bw).isdigit() else 0

            data["b_wickets"] = str(prev_bw + 1)
    # 🔥 NEW ADD (BOWLER UPDATE)
    # 🔥 BOWLER UPDATE + SAVE
    new_bowler = request.args.get("bowler")
    

    if new_bowler:

        old_bowler = data.get("bowler")

        # 🔥 1. SAVE OLD BOWLER (REPLACE, NO ADD)
        if old_bowler:

            runs = int(data.get("b_runs", 0))
            balls = int(data.get("b_balls", 0))
            bw = data.get("b_wickets")
            b_wickets_val = int(bw) if str(bw).isdigit() else 0
            maiden = int(data.get("b_maiden", 0))

            # balls → overs
            overs = balls // 6
            rem = balls % 6
            over_text = f"{overs}.{rem}"

            er = round((runs / (balls/6)) if balls else 0, 2)

            log = data.get("bowler_log", "")
            new_log_list = []
            found_old = False

            if log:
                entries = log.split("|")

                for entry in entries:
                    name, stats = entry.split("=")

                    if name == old_bowler:
                        # 🔥 REPLACE (NOT ADD)
                        new_log_list.append(
                           f"{name}={over_text},{runs},{maiden},{b_wickets_val},{er}"
                        )
                        found_old = True
                    else:
                        new_log_list.append(entry)

                if not found_old:
                    new_log_list.append(
                        f"{old_bowler}={over_text},{runs},{maiden},{b_wickets_val},{er}"
                    )

                data["bowler_log"] = "|".join(new_log_list)

            else:
                data["bowler_log"] = f"{old_bowler}={over_text},{runs},{maiden},{b_wickets_val},{er}"

        # 🔥 2. SET NEW BOWLER
        data["bowler"] = new_bowler
        # 🔥 NEW BOWLER INSTANT SHOW (LIKE BATSMAN)

        def add_bowler_if_not_exists(log, name):
            if not name:
                return log

            entries = log.split("|") if log else []

            for e in entries:
                if e.split("=")[0] == name:
                    return log  # already আছে

            # default stats (same format as তোমার system)
            new_entry = f"{name}=0.0,0,0,0,0.00"

            if log:
                return log + "|" + new_entry
            else:
                return new_entry


        data["bowler_log"] = add_bowler_if_not_exists(
            data.get("bowler_log", ""),
            data.get("bowler")
        )

        # 🔥 3. LOAD FOR FRONTEND (ONLY SHOW)
        log = data.get("bowler_log", "")
        found = False

        if log:
            entries = log.split("|")

            for entry in entries:
                name, stats = entry.split("=")

                if name == new_bowler:
                    found = True

                    o, r, m, w, e = stats.split(",")

                    # overs → balls
                    ov, ob = map(int, o.split("."))
                    total_balls = ov * 6 + ob

                    data["b_runs"] = r
                    data["b_balls"] = str(total_balls)
                    data["b_maiden"] = m
                    data["b_wickets"] = w  
                    data["b_er"] = e
                    break

        # 🔥 4. IF NEW → RESET
        if not found:
            data["b_runs"] = "0"
            data["b_balls"] = "0"
            data["b_maiden"] = "0"
            data["b_wickets"] = "0" 
            data["b_er"] = "0"    

    # 🔥 3. score update
    if score:
        data["score"] = score

    # 🔥 ONLY update if URL has wickets (important)
    if request.args.get("wickets") is not None:
        data["wickets"] = request.args.get("wickets")
    if over:
        data["over"] = over
    if ball:
        data["ball"] = ball

    # 🔥 BOWLER WICKET CONTROL (FINAL FIX)

   # 🔥 FINAL: ONLY COUNT WICKET AFTER FOW DONE
    
    # 🔥 4. NEW BATSMAN + WICKET LOGIC
    if new_player:

        # 🔥 =========================
        # 🔵 NEW BATSMAN POSITION LOGIC
        # 🔥 =========================

        striker_new = data.get("striker", "")
        non_striker_new = data.get("non_striker", "")

        if wicket_type in ["Bowled", "Catch out", "LBW", "Stumping", "Hit wicket"]:
            striker_new = new_player

        elif wicket_type == "Run out striker":
            striker_new = new_player

        elif wicket_type == "Run out striker non-striker side":

            # 🔥 temp old non-striker stats
            temp_runs = data["ns_runs"]
            temp_balls = data["ns_balls"]
            temp_4 = data["ns_4"]
            temp_6 = data["ns_6"]
            temp_sr = data["ns_sr"]

            # 🔥 old non-striker → striker
            striker_new = data["non_striker"]

            data["s_runs"] = temp_runs
            data["s_balls"] = temp_balls
            data["s_4"] = temp_4
            data["s_6"] = temp_6
            data["s_sr"] = temp_sr

            # 🔥 new batsman → non-striker
            non_striker_new = new_player

            data["ns_runs"] = "0"
            data["ns_balls"] = "0"
            data["ns_4"] = "0"
            data["ns_6"] = "0"
            data["ns_sr"] = "0"

        elif wicket_type == "Run out non-striker":
            non_striker_new = new_player

        elif wicket_type == "Run out non-striker striker side":

            # 🔥 temp old striker stats
            temp_runs = data["s_runs"]
            temp_balls = data["s_balls"]
            temp_4 = data["s_4"]
            temp_6 = data["s_6"]
            temp_sr = data["s_sr"]

            # 🔥 old striker → non-striker
            non_striker_new = data["striker"]

            data["ns_runs"] = temp_runs
            data["ns_balls"] = temp_balls
            data["ns_4"] = temp_4
            data["ns_6"] = temp_6
            data["ns_sr"] = temp_sr

            # 🔥 new batsman → striker
            striker_new = new_player

            data["s_runs"] = "0"
            data["s_balls"] = "0"
            data["s_4"] = "0"
            data["s_6"] = "0"
            data["s_sr"] = "0"

        else:
            striker_new = new_player

        # 🔥 assign
        data["striker"] = striker_new
        data["non_striker"] = non_striker_new
        # 🔥 NEW BATSMAN INSTANT SHOW (NO BALL NEEDED)

        def add_if_not_exists(log, name):
            if not name:
                return log

            entries = log.split("|") if log else []

            for e in entries:
                if e.split("=")[0] == name:
                    return log  # already আছে

            new_entry = f"{name}=0,0,0,0,0.00"

            if log:
                return log + "|" + new_entry
            else:
                return new_entry


        data["batsman_log"] = add_if_not_exists(
            data.get("batsman_log", ""),
            data.get("striker")
        )

        data["batsman_log"] = add_if_not_exists(
            data.get("batsman_log", ""),
            data.get("non_striker")
        )

        # 🔥 reset ONLY new batsman
        if data["striker"] == new_player:
            data["s_runs"] = "0"
            data["s_balls"] = "0"
            data["s_4"] = "0"
            data["s_6"] = "0"
            data["s_sr"] = "0"
        else:
            data["ns_runs"] = "0"
            data["ns_balls"] = "0"
            data["ns_4"] = "0"
            data["ns_6"] = "0"
            data["ns_sr"] = "0"

        # 🔥 =========================
        # 🟡 LAST BALL SWAP (PERFECT)
        # 🔥 =========================
        if over_ended == "true":

            # name swap
            temp = data["striker"]
            data["striker"] = data["non_striker"]
            data["non_striker"] = temp

            # stats swap
            temp_runs = data.get("s_runs", "0")
            temp_balls = data.get("s_balls", "0")
            temp_4 = data.get("s_4", "0")
            temp_6 = data.get("s_6", "0")
            temp_sr = data.get("s_sr", "0")

            data["s_runs"] = data.get("ns_runs", "0")
            data["s_balls"] = data.get("ns_balls", "0")
            data["s_4"] = data.get("ns_4", "0")
            data["s_6"] = data.get("ns_6", "0")
            data["s_sr"] = data.get("ns_sr", "0")

            data["ns_runs"] = temp_runs
            data["ns_balls"] = temp_balls
            data["ns_4"] = temp_4
            data["ns_6"] = temp_6
            data["ns_sr"] = temp_sr
        
        # 🔥 =========================
        # 🔥 INSTANT MATCH FILE UPDATE (NEW BATSMAN FIX)
        # 🔥 =========================

        

    # 🔥 5. save
    safe_write("data/current_match.txt", data)

    # 🔥 LOAD PLAYERS FROM ADVANCED SETTINGS
    try:
        with open("data/advanced_settings.txt") as f:
            for line in f:
                if line.startswith("players="):
                    data["players"] = line.strip().split("=")[1]
    except:
        data["players"] = "11"

    
    # 🔥 6. render
    return render_template("live_match.html", data=data)


@app.route("/update-score", methods=["POST"])
def update_score():

    import os

    data = request.json

    match = {}

    # 🔥 LOAD CURRENT MATCH
    with open("data/current_match.txt") as f:
        for line in f:
            if "=" in line:
                k, v = line.strip().split("=", 1)
                match[k] = v

    # 🔥 SCORE
    match["score"] = str(data["score"])
    match["wickets"] = str(data["wickets"])
    match["over"] = str(data["over"])
    match["ball"] = str(data["ball"])

    match["striker"] = data.get("striker", match.get("striker"))
    match["non_striker"] = data.get("non_striker", match.get("non_striker"))

    # 🔥 BATSMAN
    match["s_runs"] = str(data.get("s_runs", 0))
    match["s_balls"] = str(data.get("s_balls", 0))
    match["s_4"] = str(data.get("s_4", 0))
    match["s_6"] = str(data.get("s_6", 0))
    match["s_sr"] = str(data.get("s_sr", 0))

    match["ns_runs"] = str(data.get("ns_runs", 0))
    match["ns_balls"] = str(data.get("ns_balls", 0))
    match["ns_4"] = str(data.get("ns_4", 0))
    match["ns_6"] = str(data.get("ns_6", 0))
    match["ns_sr"] = str(data.get("ns_sr", 0))

    # 🔥 BOWLER
    match["b_runs"] = str(data.get("b_runs", 0))
    match["b_balls"] = str(data.get("b_balls", 0))
    match["b_maiden"] = str(data.get("b_maiden", 0))
    match["b_er"] = str(data.get("b_er", 0))
    match["b_wickets"] = str(data.get("b_wickets", match.get("b_wickets", 0)))

    # 🔥 THIS OVER
    if data.get("this_over") is not None:
        match["this_over"] = data.get("this_over")

    # 🔥 FINISHED OVER
    if data.get("finished_over"):

        old = match.get("over_log", "")

        if old:
            match["over_log"] = old + "|" + data.get("finished_over")
        else:
            match["over_log"] = data.get("finished_over")

        match["this_over"] = ""

    # 🔥 EXTRA
    extra = data.get("extra", "")
    if extra:
        match["extra"] = extra

    # 🔥 PARTNERSHIP
    p = data.get("partnerships")
    if p and p.strip() not in ["", "[]", "null"]:
        match["partnerships"] = p

    # 🔥 FORCE SAVE LAST BOWLER
    total_overs = int(match.get("overs", 0))
    current_over = int(match.get("over", 0))
    current_ball = int(match.get("ball", 0))

    if current_over == total_overs and current_ball == 0:

        bowler = match.get("bowler")

        if bowler:

            runs = int(match.get("b_runs", 0))
            balls = int(match.get("b_balls", 0))
            wickets = int(match.get("b_wickets", 0))
            maiden = int(match.get("b_maiden", 0))

            overs_done = balls // 6
            rem = balls % 6
            over_text = f"{overs_done}.{rem}"

            er = round((runs / (balls / 6)) if balls else 0, 2)

            log = match.get("bowler_log", "")
            new_log = []
            found = False

            if log:

                for entry in log.split("|"):

                    name, stats = entry.split("=")

                    if name == bowler:
                        new_log.append(f"{name}={over_text},{runs},{maiden},{wickets},{er}")
                        found = True
                    else:
                        new_log.append(entry)

                if not found:
                    new_log.append(f"{bowler}={over_text},{runs},{maiden},{wickets},{er}")

                match["bowler_log"] = "|".join(new_log)

            else:
                match["bowler_log"] = f"{bowler}={over_text},{runs},{maiden},{wickets},{er}"

    # 🔥 BATSMAN LOG
    def update_batsman_log(match, name, runs, balls, fours, sixes, sr):

        if not name:
            return match

        name = name.strip()

        new_entry = f"{name}={runs},{balls},{fours},{sixes},{sr}"

        log = match.get("batsman_log", "")
        new_log = []
        found = False

        if log:

            for entry in log.split("|"):

                n = entry.split("=")[0].strip()

                if n == name:
                    new_log.append(new_entry)
                    found = True
                else:
                    new_log.append(entry)

            if not found:
                new_log.append(new_entry)

            match["batsman_log"] = "|".join(new_log)

        else:
            match["batsman_log"] = new_entry

        return match

    # 🔴 STRIKER
    match = update_batsman_log(
        match,
        match.get("striker"),
        match.get("s_runs"),
        match.get("s_balls"),
        match.get("s_4"),
        match.get("s_6"),
        match.get("s_sr")
    )

    # 🔵 NON STRIKER
    match = update_batsman_log(
        match,
        match.get("non_striker"),
        match.get("ns_runs"),
        match.get("ns_balls"),
        match.get("ns_4"),
        match.get("ns_6"),
        match.get("ns_sr")
    )

    # 🔵 BOWLER LOG
    def update_bowler_log(match, name, runs, balls, maiden, wickets, er):

        if not name:
            return match

        overs_done = int(balls) // 6
        rem = int(balls) % 6
        over_text = f"{overs_done}.{rem}"

        new_entry = f"{name}={over_text},{runs},{maiden},{wickets},{er}"

        log = match.get("bowler_log", "")
        new_log = []
        found = False

        if log:

            for entry in log.split("|"):

                n = entry.split("=")[0]

                if n == name:
                    new_log.append(new_entry)
                    found = True
                else:
                    new_log.append(entry)

            if not found:
                new_log.append(new_entry)

            match["bowler_log"] = "|".join(new_log)

        else:
            match["bowler_log"] = new_entry

        return match

    match = update_bowler_log(
        match,
        match.get("bowler"),
        match.get("b_runs"),
        match.get("b_balls"),
        match.get("b_maiden"),
        match.get("b_wickets"),
        match.get("b_er")
    )

    # 🔥 NEED CALCULATION
    if str(match.get("innings")) == "2":

        target = int(match.get("target", 0) or 0)
        score = int(match.get("score", 0) or 0)

        total_overs = int(match.get("overs", 0) or 0)
        over = int(match.get("over", 0) or 0)
        ball = int(match.get("ball", 0) or 0)

        total_balls = total_overs * 6
        played_balls = over * 6 + ball

        balls_left = total_balls - played_balls
        runs_needed = target - score

        if runs_needed < 0:
            runs_needed = 0

        if balls_left < 0:
            balls_left = 0

        match["need_runs"] = str(runs_needed)
        match["need_balls"] = str(balls_left)

        batting_team = match.get("batting", "")

        match["need_text"] = f"{batting_team} need {runs_needed} runs in {balls_left} balls"

    # 🔥 MATCH FILE SAVE
    if match.get("innings") == "1":
        match_file = match.get("first_match_file")
    else:
        match_file = match.get("second_match_file")

    if match_file:

        # 🔥 SAFE FIRST INNINGS
        if str(match.get("innings", "1")).strip() == "1":

            safe_write(match_file, match)

        # 🔥 SAFE SECOND INNINGS
        temp_match = match_file + ".tmp"

        with open(temp_match, "w") as f:

            for k, v in match.items():
                f.write(f"{k}={v}\n")

        os.replace(temp_match, match_file)

    # 🔥 SAFE HISTORY
    safe_match = {}

    for k, v in match.items():

        if isinstance(v, str):
            v = v.replace("\n", "").replace(";;", "")

        safe_match[k] = v

    line = ";;".join([f"{k}={safe_match[k]}" for k in safe_match])
    append_history(line)

    # 🔥 SAVE CURRENT MATCH
    safe_write("data/current_match.txt", match)

    return jsonify({"status": "ok"})



    
@app.route("/advanced-settings")
def advanced_settings():
    if not session.get("admin"):
        return redirect("/login")

    data = {}

    try:
        with open("data/advanced_settings.txt") as f:
            for line in f:
                key, value = line.strip().split("=")
                data[key] = value
    except:
        pass

    return render_template("advanced_settings.html", data=data)

@app.route("/save-settings")
def save_settings():

    players = request.args.get("players")
    noball = request.args.get("noball")
    noball_reball = request.args.get("noball_reball")
    noball_run = request.args.get("noball_run")

    wide = request.args.get("wide")
    wide_reball = request.args.get("wide_reball")
    wide_run = request.args.get("wide_run")

    # 🔥 file save
    with open("data/advanced_settings.txt", "w") as f:
        f.write(f"players={players}\n")
        f.write(f"noball={noball}\n")
        f.write(f"noball_reball={noball_reball}\n")
        f.write(f"noball_run={noball_run}\n")
        f.write(f"wide={wide}\n")
        f.write(f"wide_reball={wide_reball}\n")
        f.write(f"wide_run={wide_run}\n")

    return redirect("/advanced-settings")
@app.route("/fall-of-wicket")
def fall_wicket():

    data = {}
    with open("data/current_match.txt") as f:
        for line in f:
            k, v = line.strip().split("=", 1)
            data[k] = v

    batting = data["batting"]

    with open(f"data/teamlist/{batting}.txt") as f:
        players = [line.strip().split(",")[0] for line in f]

    return render_template("fall_of_wicket.html", players=players)

@app.route("/choose-bowler")
def choose_bowler():

    # 🔥 current match data load
    data = {}
    with open("data/current_match.txt") as f:
        for line in f:
            k, v = line.strip().split("=",1)
            data[k] = v

    bowling_team = data.get("bowling")

    if not bowling_team:
        return "Bowling team missing"

    # 🔥 SAME AS opening page
    with open(f"data/teamlist/{bowling_team}.txt") as f:
        bowlers = [line.strip().split(",")[0] for line in f]

    return render_template("choose_bowler.html", bowlers=bowlers)

@app.route("/undo")
def undo():

    import os

    try:

        # 🔥 READ HISTORY
        with open("data/history.txt", "r") as f:
            lines = f.readlines()

        if len(lines) < 2:
            return redirect("/live-match")

        # 🔥 REMOVE LAST STATE
        lines = lines[:-1]

        # 🔥 SAFE SAVE HISTORY
        temp_history = "data/history_temp.txt"

        with open(temp_history, "w") as f:
            f.writelines(lines)

        os.replace(temp_history, "data/history.txt")

        # 🔥 GET PREVIOUS STATE
        last = lines[-1].strip()

        new_data = {}

        # 🔥 SAFE SPLIT
        items = last.split(";;")

        for item in items:

            if "=" in item:
                k, v = item.split("=", 1)
                new_data[k] = v

        # 🔥 SAVE CURRENT MATCH
        safe_write("data/current_match.txt", new_data)

        # =====================================
        # 🔥 UPDATE MATCH FILE (DUAL FILE FIX)
        # =====================================

        if new_data.get("innings") == "1":

            match_file = new_data.get("first_match_file")

        else:

            match_file = new_data.get("second_match_file")

        if match_file:

            safe_write(match_file, new_data)

    except Exception as e:

        print("UNDO ERROR:", e)

    return redirect("/live-match")


@app.route("/start-second")
def start_second():

    data = {}

    with open("data/current_match.txt") as f:
        for line in f:
            if "=" in line:
                k, v = line.strip().split("=", 1)
                data[k] = v

    match_file = data.get("first_match_file")

    # 🔥 SAFE SAVE 1ST INNINGS (ATOMIC)
    # 🔥 SAVE FIRST INNINGS FILE

    if match_file:

        safe_write(match_file, data)

    data["target"] = str(int(data.get("score", 0)) + 1)

    # 🔥 swap
    data["batting"], data["bowling"] = data["bowling"], data["batting"]

    # 🔥 reset
    data["score"] = "0"
    data["wickets"] = "0"
    data["over"] = "0"
    data["ball"] = "0"

    data["this_over"] = ""
    data["over_log"] = ""
    data["batsman_log"] = ""
    data["partnerships"] = "[]"
    data["extra"] = "0,0LB,0B,0WD,0NB"

    data["s_runs"] = "0"
    data["s_balls"] = "0"
    data["s_4"] = "0"
    data["s_6"] = "0"
    data["s_sr"] = "0"

    data["ns_runs"] = "0"
    data["ns_balls"] = "0"
    data["ns_4"] = "0"
    data["ns_6"] = "0"
    data["ns_sr"] = "0"

    data["b_runs"] = "0"
    data["b_balls"] = "0"
    data["b_wickets"] = "0"
    data["b_maiden"] = "0"
    data["b_er"] = "0"

    data["bowler_log"] = ""
    data["wickets_log"] = "[]"
    data["Man_of_the_Match"] = ""

    data["innings"] = "2"

    # 🔥 SAFE SAVE CURRENT MATCH
    safe_write("data/current_match.txt", data)

    return redirect("/opening-players")


@app.route("/save-result", methods=["POST"])
def save_result():

    data_json = request.json

    result = data_json.get("result", "")

    print("RESULT RECEIVED:", result)

    match = {}

    # 🔥 LOAD CURRENT MATCH
    with open("data/current_match.txt") as f:

        for line in f:

            if "=" in line:
                k, v = line.strip().split("=", 1)
                match[k] = v

    # 🔥 SAVE RESULT
    match["match_result"] = result

    # 🔥 SAVE CURRENT MATCH
    safe_write("data/current_match.txt", match)

    # 🔥 SAVE SECOND INNINGS FILE
    match_file = match.get("second_match_file")

    if match_file:

        safe_write(match_file, match)

    return "OK"
@app.route("/history")
def history():

    import os

    folder = "data/all_match"
    matches = []

    # 🔥 ONLY FIRST INNINGS FILE
    files = [f for f in os.listdir(folder) if f.endswith("_1st.txt")]

    for file in files:

        path = os.path.join(folder, file)

        # 🔥 LOAD FIRST INNINGS
        first = {}

        with open(path) as f:

            for line in f:

                if "=" in line:
                    k, v = line.strip().split("=", 1)
                    first[k] = v

        # 🔥 LOAD SECOND INNINGS
        second = {}

        second_file = path.replace("_1st.txt", "_2nd.txt")

        if os.path.exists(second_file):

            with open(second_file) as sf:

                for line in sf:

                    if "=" in line:
                        k, v = line.strip().split("=", 1)
                        second[k] = v

        # 🔥 MATCH TIME
        match_time = first.get("match_time", "")

        # 🔥 RESULT
        result_text = second.get("match_result", "")

        innings_break = len(second) > 0

        # 🔥 TEAM ORDER
        team1 = first.get("batting", "")
        team2 = second.get("batting", "")
        if not team2:
            team2 = first.get("bowling")

        # 🔥 TEAM2 SCORE
        team2_score = second.get("score", "")
        team2_wickets = second.get("wickets", "")
        team2_over = f"{second.get('over','0')}.{second.get('ball','0')}"

        if second.get("over", "0") == "0" and second.get("ball", "0") == "0":

            if innings_break:
                team2_score = "0"
                team2_wickets = "0"
                team2_over = "0.0"

            else:
                team2_score = ""
                team2_wickets = ""
                team2_over = ""

        # 🔥 STATUS
        status = "COMPLETED" if result_text else "LIVE"

        match_info = {

            "team1": team1,
            "team1_score": first.get("score", "0"),
            "team1_wickets": first.get("wickets", "0"),
            "team1_over": f"{first.get('over','0')}.{first.get('ball','0')}",

            "team2": team2,
            "team2_score": team2_score,
            "team2_wickets": team2_wickets,
            "team2_over": team2_over,

            "result": result_text,
            "need_text": second.get("need_text"),

            "toss": first.get("toss"),
            "opt": first.get("opt"),

            "status": status,

            "innings_break": innings_break,

            "date": match_time,

            # 🔥 IMPORTANT
            "file": file
        }

        matches.append(match_info)

    from datetime import datetime

    def parse_time(m):

        try:
            return datetime.strptime(m["date"], "%d %b %Y, %I:%M %p")

        except:
            return datetime.min

    matches.sort(key=parse_time, reverse=True)

    return render_template(
        "history.html",
        matches=matches,
        hide_delete=False
    )


@app.route("/history-data")
def history_data():

    import os

    folder = "data/all_match"
    matches = []

    # 🔥 ONLY FIRST INNINGS FILE
    files = [f for f in os.listdir(folder) if f.endswith("_1st.txt")]

    for file in files:

        path = os.path.join(folder, file)

        # 🔥 LOAD FIRST INNINGS
        first = {}

        with open(path) as f:

            for line in f:

                if "=" in line:
                    k, v = line.strip().split("=", 1)
                    first[k] = v

        # 🔥 LOAD SECOND INNINGS
        second = {}

        second_file = path.replace("_1st.txt", "_2nd.txt")

        if os.path.exists(second_file):

            with open(second_file) as sf:

                for line in sf:

                    if "=" in line:
                        k, v = line.strip().split("=", 1)
                        second[k] = v

        # 🔥 MATCH TIME
        match_time = first.get("match_time", "")

        # 🔥 RESULT
        result_text = second.get("match_result", "")

        innings_break = len(second) > 0

        # 🔥 TEAM ORDER
        team1 = first.get("batting", "")

        team2 = second.get("batting", "")

        if not team2:
            team2 = first.get("bowling")

        # 🔥 TEAM2 SCORE
        team2_score = second.get("score", "")
        team2_wickets = second.get("wickets", "")
        team2_over = f"{second.get('over','0')}.{second.get('ball','0')}"

        if second.get("over", "0") == "0" and second.get("ball", "0") == "0":

            if innings_break:
                team2_score = "0"
                team2_wickets = "0"
                team2_over = "0.0"

            else:
                team2_score = ""
                team2_wickets = ""
                team2_over = ""

        # 🔥 STATUS
        status = "COMPLETED" if result_text else "LIVE"

        match_info = {

            "team1": team1,
            "team1_score": first.get("score", "0"),
            "team1_wickets": first.get("wickets", "0"),
            "team1_over": f"{first.get('over','0')}.{first.get('ball','0')}",

            "team2": team2,
            "team2_score": team2_score,
            "team2_wickets": team2_wickets,
            "team2_over": team2_over,

            "result": result_text,
            "need_text": second.get("need_text"),

            "toss": first.get("toss"),
            "opt": first.get("opt"),

            "status": status,

            "innings_break": innings_break,

            "date": match_time,

            # 🔥 IMPORTANT
            "file": file
        }

        matches.append(match_info)

    from datetime import datetime

    def parse_time(m):

        try:
            return datetime.strptime(m["date"], "%d %b %Y, %I:%M %p")

        except:
            return datetime.min

    matches.sort(key=parse_time, reverse=True)

    return render_template(
        "history_partial.html",
        matches=matches,
        hide_delete=False
    )

@app.route("/delete-match/<filename>")
def delete_match(filename):

    import os

    first_file = os.path.join(
        "data/all_match",
        filename + "_1st.txt"
    )

    second_file = os.path.join(
        "data/all_match",
        filename + "_2nd.txt"
    )

    # 🔥 DELETE FIRST INNINGS
    if os.path.exists(first_file):
        os.remove(first_file)

    # 🔥 DELETE SECOND INNINGS
    if os.path.exists(second_file):
        os.remove(second_file)

    return redirect("/history")

@app.route("/resume-match/<file>")
def resume_match(file):

    import shutil
    import os

    first_file = f"data/all_match/{file}_1st.txt"
    second_file = f"data/all_match/{file}_2nd.txt"

    target = "data/current_match.txt"

    try:

        data = {}

        # 🔥 LOAD FIRST INNINGS
        if os.path.exists(first_file):

            with open(first_file) as f:

                for line in f:

                    if "=" in line:
                        k, v = line.strip().split("=", 1)
                        data[k] = v

        # 🔥 LOAD SECOND INNINGS
        if os.path.exists(second_file):

            with open(second_file) as f:

                for line in f:

                    if "=" in line:
                        k, v = line.strip().split("=", 1)
                        data[k] = v

        # 🔥 SAVE CURRENT MATCH
        safe_write(target, data)

    except Exception as e:

        print("RESUME ERROR:", e)

        return "Resume failed"

    return redirect("/live-match")

@app.route("/save-wicket", methods=["POST"])
def save_wicket():

    import json

    data = request.json

    # 🔥 LOAD MATCH
    match = {}
    with open("data/current_match.txt") as f:
        for line in f:
            if "=" in line:
                k, v = line.strip().split("=", 1)
                match[k] = v

    wicket_type = data.get("wicket_type")
    out_player = data.get("out_player")
    bowler = match.get("bowler")

    if wicket_type and out_player:

        try:
            log = json.loads(match.get("wickets_log", "[]"))
        except:
            log = []

        log.append({
            "batsman": out_player,
            "type": wicket_type,
            "bowler": bowler
        })
        # 🔥 ADD THIS
        match["last_wicket_player"] = out_player
        match["last_wicket_type"] = wicket_type

        match["wickets_log"] = json.dumps(log)

    # 🔥 SAVE BACK
    safe_write("data/current_match.txt", match)

    return {"status": "ok"}


@app.route("/match-details")
def match_details():

    import os, json
    from flask import request, render_template

    file = request.args.get("file")

    path = os.path.join("data/all_match", file)

    first = {}
    second = {}

    result = ""
    pom = ""

    try:

        # =====================
        # 🔥 LOAD FIRST INNINGS
        # =====================
        with open(path) as f:

            for line in f:

                if "=" in line:
                    k, v = line.strip().split("=", 1)
                    first[k] = v

        # =====================
        # 🔥 LOAD SECOND INNINGS
        # =====================
        second_file = path.replace("_1st.txt", "_2nd.txt")

        if os.path.exists(second_file):

            with open(second_file) as sf:

                for line in sf:

                    if "=" in line:
                        k, v = line.strip().split("=", 1)
                        second[k] = v

        # =====================
        # 🏁 RESULT
        # =====================
        result = second.get("match_result", "")

        # =====================
        # 🔥 PLAYER OF MATCH
        # =====================
        pom = second.get("Man_of_the_Match", "")

    except:
        pass

    # =====================
    # 🔥 SAFE JSON
    # =====================
    def safe_json(text):

        try:
            return json.loads(text)

        except:
            return []

    # =====================
    # 🔥 WICKETS
    # =====================
    first["wickets_log"] = safe_json(first.get("wickets_log", "[]"))
    second["wickets_log"] = safe_json(second.get("wickets_log", "[]"))

    # =====================
    # 🔥 DISMISSALS
    # =====================
    def clean(n):

        return n.split('(')[0].strip().lower()

    def build_map(log):

        d = {}

        for w in log:

            key = clean(w.get("batsman", ""))

            t = (w.get("type") or "").lower()

            bowler = w.get("bowler", "")

            if t == "bowled":
                d[key] = f"b {bowler}"

            elif "catch" in t:
                d[key] = f"c b {bowler}"

            elif "run out" in t:
                d[key] = "run out"

            elif t == "lbw":
                d[key] = f"lbw b {bowler}"

            else:
                d[key] = w.get("type", "out")

        return d

    first["dismissals"] = build_map(first["wickets_log"])
    second["dismissals"] = build_map(second["wickets_log"])

    # =====================
    # 🔥 SQUAD FIND
    # =====================
    def find_squad_key(data, team):

        team_clean = team.lower().replace(" ", "").replace("-", "").replace("_", "")

        for k in data.keys():

            key_clean = k.lower().replace("_", "").replace("-", "")

            if team_clean in key_clean:
                return k

        return team.lower() + "_squad"

    host = first.get("host", "")
    visitor = first.get("visitor", "")

    host_key = find_squad_key(first, host)
    visitor_key = find_squad_key(first, visitor)

    first[host_key] = safe_json(first.get(host_key, "[]"))
    first[visitor_key] = safe_json(first.get(visitor_key, "[]"))

    # =====================
    # 🔥 SPLIT SQUAD
    # =====================
    def split_squad(squad):

        playing = []
        bench = []
        staff = []

        for p in squad:

            extra = p.get("extra", [])

            if "bench" in extra:
                bench.append(p)

            elif "stf" in extra:
                staff.append(p)

            else:
                playing.append(p)

        return playing, bench, staff

    t1_play, t1_bench, t1_staff = split_squad(first.get(host_key, []))
    t2_play, t2_bench, t2_staff = split_squad(first.get(visitor_key, []))

    # =====================
    # 🔥 RETURN
    # =====================
    return render_template(
        "match_details.html",

        first=first,
        second=second,

        result=result,
        pom=pom,

        t1_play=t1_play,
        t1_bench=t1_bench,
        t1_staff=t1_staff,

        t2_play=t2_play,
        t2_bench=t2_bench,
        t2_staff=t2_staff
    )
@app.route("/latest-history")
def latest_history():

    import os

    folder = "data/all_match"

    matches = []

    # 🔥 ONLY FIRST INNINGS FILE
    files = [f for f in os.listdir(folder) if f.endswith("_1st.txt")]

    for file in files:

        first = {}
        second = {}

        path = os.path.join(folder, file)

        # =========================
        # 🔥 LOAD FIRST INNINGS
        # =========================

        try:

            with open(path) as f:

                for line in f:

                    if "=" in line:

                        k, v = line.strip().split("=", 1)

                        first[k] = v

        except:
            continue

        # =========================
        # 🔥 LOAD SECOND INNINGS
        # =========================

        second_file = path.replace("_1st.txt", "_2nd.txt")

        if os.path.exists(second_file):

            try:

                with open(second_file) as sf:

                    for line in sf:

                        if "=" in line:

                            k, v = line.strip().split("=", 1)

                            second[k] = v

            except:
                pass

        # =========================
        # 🔥 COMPLETED ONLY
        # =========================

        result = second.get("match_result", "")

        if not result:
            continue

        # =========================
        # 🔥 TEAM INFO
        # =========================

        team1 = first.get("batting")

        team2 = second.get("batting")

        if not team2:

            team2 = first.get("bowling")

        # =========================
        # 🔥 APPEND
        # =========================

        matches.append({

            "team1": team1,

            "team2": team2,

            "team1_score": first.get("score", "0"),

            "team1_wickets": first.get("wickets", "0"),

            "team1_over":
            f"{first.get('over','0')}."
            f"{first.get('ball','0')}",

            "team2_score": second.get("score", "0"),

            "team2_wickets": second.get("wickets", "0"),

            "team2_over":
            f"{second.get('over','0')}."
            f"{second.get('ball','0')}",

            "date": first.get("match_time"),

            "result": result,

            "status": "COMPLETED",

            "file": file
        })

    # =========================
    # 🔥 SORT
    # =========================

    from datetime import datetime

    def parse_time(m):

        try:

            return datetime.strptime(
                m.get("date", ""),
                "%d %b %Y, %I:%M %p"
            )

        except:

            return datetime.min

    matches.sort(key=parse_time, reverse=True)

    return render_template(
        "history_partial.html",
        matches=matches[:10],
        hide_delete=True
    )

@app.route("/history-scorecard-data")
def history_scorecard_data():

    import os
    import json

    file = request.args.get("file")

    path = os.path.join("data/all_match", file)

    first = {}
    second = {}

    # =========================
    # 🔥 LOAD FIRST INNINGS
    # =========================

    try:

        with open(path) as f:

            for line in f:

                if "=" in line:

                    k, v = line.strip().split("=", 1)

                    first[k] = v

    except:
        pass

    # =========================
    # 🔥 LOAD SECOND INNINGS
    # =========================

    second_file = path.replace("_1st.txt", "_2nd.txt")

    if os.path.exists(second_file):

        try:

            with open(second_file) as sf:

                for line in sf:

                    if "=" in line:

                        k, v = line.strip().split("=", 1)

                        second[k] = v

        except:
            pass

    # =========================
    # 🔥 SAFE JSON
    # =========================

    def safe_json(text):

        try:

            return json.loads(text)

        except:

            return []

    first["wickets_log"] = safe_json(
        first.get("wickets_log", "[]")
    )

    second["wickets_log"] = safe_json(
        second.get("wickets_log", "[]")
    )

    # =========================
    # 🔥 DISMISSALS
    # =========================

    def clean(n):

        return n.split('(')[0].strip().lower()

    def build_map(log):

        d = {}

        for w in log:

            key = clean(w.get("batsman", ""))

            t = (w.get("type") or "").lower()

            bowler = w.get("bowler", "")

            if t == "bowled":

                d[key] = f"b {bowler}"

            elif "catch" in t:

                d[key] = f"c b {bowler}"

            elif "run out" in t:

                d[key] = "run out"

            elif t == "lbw":

                d[key] = f"lbw b {bowler}"

            else:

                d[key] = w.get("type", "out")

        return d

    first["dismissals"] = build_map(
        first["wickets_log"]
    )

    second["dismissals"] = build_map(
        second["wickets_log"]
    )

    return render_template(
        "partials/history_scorecard.html",
        first=first,
        second=second
    )

@app.route("/all-match-files")
def all_match_files_page():

    import os

    folder = "data/all_match"

    matches = []

    # 🔥 ONLY FIRST INNINGS FILES
    files = sorted(
        [f for f in os.listdir(folder) if f.endswith("_1st.txt")],
        reverse=True
    )

    for file in files:

        path = os.path.join(folder, file)

        first = {}

        try:

            with open(path) as f:

                for line in f:

                    if "=" in line:

                        k, v = line.strip().split("=", 1)

                        first[k] = v

        except:
            continue

        team1 = first.get("host", "team")

        team2 = first.get("visitor", "team")

        matches.append({

            "file": file,

            "team1": team1,

            "team2": team2
        })

    return render_template(
        "all_match_files.html",
        matches=matches
    )

@app.route("/update-match", methods=["POST"])
def update_match():

    import os

    from flask import request, redirect

    file = request.form.get("file")

    path = os.path.join("data/all_match", file)

    second_file = path.replace("_1st.txt", "_2nd.txt")

    first = {}
    second = {}

    # =========================
    # 🔥 LOAD FIRST INNINGS
    # =========================

    if os.path.exists(path):

        with open(path) as f:

            for line in f:

                if "=" in line:

                    k, v = line.strip().split("=", 1)

                    first[k] = v

    # =========================
    # 🔥 LOAD SECOND INNINGS
    # =========================

    if os.path.exists(second_file):

        with open(second_file) as sf:

            for line in sf:

                if "=" in line:

                    k, v = line.strip().split("=", 1)

                    second[k] = v

    # =========================
    # 🔥 UPDATE FIRST
    # =========================

    first["wickets_log"] = request.form.get(
        "wickets_log_1",
        first.get("wickets_log", "")
    )

    first["bowler_log"] = request.form.get(
        "bowler_log_1",
        first.get("bowler_log", "")
    )

    # =========================
    # 🔥 UPDATE SECOND
    # =========================

    second["wickets_log"] = request.form.get(
        "wickets_log_2",
        second.get("wickets_log", "")
    )

    second["bowler_log"] = request.form.get(
        "bowler_log_2",
        second.get("bowler_log", "")
    )

    # =========================
    # 🏆 PLAYER OF MATCH
    # =========================

    pom = request.form.get("man_of_match", "").strip()

    if pom:

        second["Man_of_the_Match"] = pom

    # =========================
    # 🏁 MATCH RESULT
    # =========================

    match_result = request.form.get("match_result", "").strip()

    if match_result:

        second["match_result"] = match_result

    # =========================
    # 🔥 SAVE FIRST INNINGS
    # =========================

    safe_write(path, first)

    # =========================
    # 🔥 SAVE SECOND INNINGS
    # =========================

    if second:

        safe_write(second_file, second)

    # =========================
    # 🔥 AUTO TEAM STATS UPDATE
    # =========================

    try:

        rebuild_stats_logic()

        update_nrr_stats()

    except:
        pass

    return redirect(
        f"/match-editor?file={file}"
    )

@app.route("/match-editor")
def match_editor():

    import os
    from flask import request

    file = request.args.get("file")

    first = {}
    second = {}

    pom = ""

    result = ""

    team1 = ""
    team2 = ""

    if file:

        path = os.path.join("data/all_match", file)

        # =========================
        # 🔥 LOAD FIRST INNINGS
        # =========================

        if os.path.exists(path):

            try:

                with open(path) as f:

                    for line in f:

                        if "=" in line:

                            k, v = line.strip().split("=", 1)

                            if k in ["wickets_log", "bowler_log"]:

                                first[k] = v

                            # 🔥 TEAM1
                            if k == "batting":
                                team1 = v

                            # 🔥 fallback TEAM2
                            if k == "bowling" and not team2:
                                team2 = v

                            # 🔥 SAVE
                            first[k] = v

            except:
                pass

        # =========================
        # 🔥 LOAD SECOND INNINGS
        # =========================

        second_file = path.replace("_1st.txt", "_2nd.txt")

        if os.path.exists(second_file):

            try:

                with open(second_file) as sf:

                    for line in sf:

                        if "=" in line:

                            k, v = line.strip().split("=", 1)

                            if k in ["wickets_log", "bowler_log"]:

                                second[k] = v

                            # 🔥 TEAM2 priority
                            if k == "batting":
                                team2 = v

                            # 🔥 RESULT
                            if k == "match_result":
                                result = v

                            # 🔥 POM
                            if k == "Man_of_the_Match":
                                pom = v

                            # 🔥 SAVE
                            second[k] = v

            except:
                pass

    return render_template(

        "match_editor.html",

        first=first,
        second=second,

        pom=pom,

        result=result,

        file=file,

        team1=team1,
        team2=team2
    )

import os, json
from flask import request, render_template, jsonify

# =========================
# 🔥 LOAD TEAM STATS
# =========================
def load_stats(team):
    path = os.path.join("data/match_result", f"{team}.txt")

    stats = {"matches": "0", "won": "0", "lost": "0"}

    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                if "=" in line:
                    k, v = line.strip().split("=")
                    stats[k] = v

    return stats
# =========================
# 🔥 AUTO UPDATE FROM MATCH
# =========================
def update_team_stats_from_match(content, first, second):

    import os

    result_block = content.split("===== MATCH RESULT =====")[-1].strip()
    result = result_block.splitlines()[0] if result_block else ""

    if not result:
        return

    team1 = first.get("batting")
    team2 = second.get("batting") or first.get("bowling")

    if not team1 or not team2:
        return

    r = result.lower()

    # 🔥 DRAW SUPPORT (ONLY ADD)
    if "draw" in r or "tie" in r:

        def update(team):

            path = os.path.join("data/match_result", f"{team}.txt")

            matches = 0
            won = 0
            lost = 0

            if os.path.exists(path):
                with open(path) as f:
                    for line in f:
                        if "=" in line:
                            k, v = line.strip().split("=")
                            if k == "matches": matches = int(v)
                            if k == "won": won = int(v)
                            if k == "lost": lost = int(v)

            matches += 1

            with open(path, "w") as f:
                f.write(f"matches={matches}\n")
                f.write(f"won={won}\n")
                f.write(f"lost={lost}\n")

        update(team1)
        update(team2)
        return  # 🔥 stop here (no win/loss)


    # 🔥 ORIGINAL LOGIC SAME
    winner = None
    if team1.lower() in r:
        winner = team1
        loser = team2
    elif team2.lower() in r:
        winner = team2
        loser = team1
    else:
        return

    def update(team, win=False, lose=False):

        path = os.path.join("data/match_result", f"{team}.txt")

        matches = 0
        won = 0
        lost = 0

        if os.path.exists(path):
            with open(path) as f:
                for line in f:
                    if "=" in line:
                        k, v = line.strip().split("=")
                        if k == "matches": matches = int(v)
                        if k == "won": won = int(v)
                        if k == "lost": lost = int(v)

        matches += 1
        if win: won += 1
        if lose: lost += 1

        with open(path, "w") as f:
            f.write(f"matches={matches}\n")
            f.write(f"won={won}\n")
            f.write(f"lost={lost}\n")

    update(winner, win=True)
    update(loser, lose=True)

# =========================
# 🔥 TEAM MANAGER PAGE
# =========================
@app.route("/team-manager")
def team_manager():

    import os

    # 🔥 NRR UPDATE
    try:

        update_nrr_stats()

    except:
        pass
    try:

        rebuild_stats_logic()

    except:
        pass

    folder = "data/teamlist"

    teams = []

    for file in os.listdir(folder):

        if file.endswith(".txt"):

            team_name = file.replace(".txt", "")

            s = load_stats(team_name)

            teams.append({

                "name": team_name,

                "matches": s["matches"],

                "won": s["won"],

                "lost": s["lost"]
            })

    return render_template(
        "team_manager.html",
        teams=teams
    )

# =========================
# 🔥 UPDATE STATS (SAVE)
# =========================
@app.route("/update-team-stats", methods=["POST"])
def update_team_stats():

    team = request.form.get("team")
    matches = request.form.get("matches","0")
    won = request.form.get("won","0")
    lost = request.form.get("lost","0")

    folder = "data/match_result"
    os.makedirs(folder, exist_ok=True)

    path = os.path.join(folder, f"{team}.txt")

    # 🔥 overwrite (no duplicate)
    with open(path, "w") as f:
        f.write(f"matches={matches}\n")
        f.write(f"won={won}\n")
        f.write(f"lost={lost}\n")

    return jsonify({"status":"ok"})

@app.route("/delete-team-manager")
def delete_team_manager():

    import os
    from flask import request, redirect

    team = request.args.get("team")
    path = os.path.join("data/teamlist", team + ".txt")

    if os.path.exists(path):
        os.remove(path)

    return redirect("/team-manager")

def rebuild_stats_logic():

    import os

    match_folder = "data/all_match"

    result_folder = "data/match_result"

    os.makedirs(result_folder, exist_ok=True)

    stats = {}

    # 🔥 ONLY FIRST INNINGS FILE
    files = [f for f in os.listdir(match_folder) if f.endswith("_1st.txt")]

    for file in files:

        first = {}
        second = {}

        path = os.path.join(match_folder, file)

        # =========================
        # 🔥 LOAD FIRST INNINGS
        # =========================

        try:

            with open(path) as f:

                for line in f:

                    if "=" in line:

                        k, v = line.strip().split("=", 1)

                        first[k] = v

        except:
            continue

        # =========================
        # 🔥 LOAD SECOND INNINGS
        # =========================

        second_file = path.replace("_1st.txt", "_2nd.txt")

        if os.path.exists(second_file):

            try:

                with open(second_file) as sf:

                    for line in sf:

                        if "=" in line:

                            k, v = line.strip().split("=", 1)

                            second[k] = v

            except:
                pass

        # =========================
        # 🔥 RESULT
        # =========================

        result = second.get("match_result", "")

        if not result:
            continue

        # =========================
        # 🔥 TEAM INFO
        # =========================

        team1 = first.get("batting")

        team2 = second.get("batting") or first.get("bowling")

        if not team1 or not team2:
            continue

        r = result.lower()

        # =========================
        # 🔥 INIT
        # =========================

        for t in [team1, team2]:

            if t not in stats:

                stats[t] = {
                    "matches": 0,
                    "won": 0,
                    "lost": 0
                }

        # =========================
        # 🔥 DRAW / TIE
        # =========================

        if "draw" in r or "tie" in r:

            stats[team1]["matches"] += 1
            stats[team2]["matches"] += 1

            # 🔥 running super over
            if "running super over" in r:
                continue

            # 🔥 super over winner
            if "won the super over" in r:

                if team1.lower() in r:

                    winner = team1
                    loser = team2

                elif team2.lower() in r:

                    winner = team2
                    loser = team1

                else:
                    continue

                stats[winner]["won"] += 1
                stats[loser]["lost"] += 1

                continue

            # 🔥 normal draw
            continue

        # =========================
        # 🔥 NORMAL RESULT
        # =========================

        if team1.lower() in r:

            winner = team1
            loser = team2

        elif team2.lower() in r:

            winner = team2
            loser = team1

        else:
            continue

        stats[team1]["matches"] += 1
        stats[team2]["matches"] += 1

        stats[winner]["won"] += 1
        stats[loser]["lost"] += 1

    # =========================
    # 🔥 SAVE
    # =========================

    for t, s in stats.items():

        with open(
            os.path.join(result_folder, f"{t}.txt"),
            "w"
        ) as f:

            f.write(f"matches={s['matches']}\n")

            f.write(f"won={s['won']}\n")

            f.write(f"lost={s['lost']}\n")

@app.route("/rebuild-team-stats")
def rebuild_team_stats():
    rebuild_stats_logic()
    return "✅ Done"

@app.route("/points")
def points():

    import os
     # 🔥 TEAM STATS
    try:
        rebuild_stats_logic()
    except:
        pass

    # 🔥 NRR UPDATE (ADD THIS)
    try:
        update_nrr_stats()
    except:
        pass
    try:
        sync_db()
    except:
        pass
    group_a = []
    group_b = []

    try:
        with open("data/teamnamePoints.txt", "r") as f:
            for line in f:
                parts = [p.strip() for p in line.strip().split(",")]

                if len(parts) == 2:
                    team = parts[0]
                    group = parts[1].lower()

                    # 🔥 default values
                    matches = 0
                    won = 0
                    lost = 0

                    # 🔥 read from match_result
                    path = os.path.join("data/match_result", f"{team}.txt")

                    if os.path.exists(path):
                        with open(path) as tf:
                            for l in tf:
                                if "=" in l:
                                    k, v = l.strip().split("=")
                                    if k == "matches":
                                        matches = int(v)
                                    elif k == "won":
                                        won = int(v)
                                    elif k == "lost":
                                        lost = int(v)

                    # =========================
                    # 🔥 NRR CALCULATION (ADD)
                    # =========================
                    nrr_value = 0.00

                    nrr_path = os.path.join("data/NRR_calculation", f"{team}.txt")

                    if os.path.exists(nrr_path):

                        runs_scored = 0
                        overs_faced = 0
                        runs_conceded = 0
                        overs_bowled = 0

                        with open(nrr_path) as nf:
                            for l in nf:
                                if "=" in l:
                                    k, v = l.strip().split("=")

                                    if k == "total_runs_scored":
                                        runs_scored = float(v)
                                    elif k == "total_overs_faced":
                                        overs_faced = float(v)
                                    elif k == "total_runs_conceded":
                                        runs_conceded = float(v)
                                    elif k == "total_overs_bowled":
                                        overs_bowled = float(v)

                        # 🔥 SAFE DIVISION
                        if overs_faced > 0 and overs_bowled > 0:
                            nrr_value = (runs_scored / overs_faced) - (runs_conceded / overs_bowled)

                    # 🔥 build data
                    data = {
                        "team": team,
                        "p": matches,
                        "w": won,
                        "l": lost,
                        "nr": 0,
                        "pts": won * 2,
                        "nrr": f"{nrr_value:+.2f}"
                    }

                    # 🔥 assign group
                    if group == "a":
                        group_a.append(data)

                    elif group == "b":
                        group_b.append(data)

    except Exception as e:
        print("Error:", e)

    # 🔥 SORT INSIDE GROUP
    group_a.sort(key=lambda x: (x["pts"], float(x["nrr"])), reverse=True)
    group_b.sort(key=lambda x: (x["pts"], float(x["nrr"])), reverse=True)

    # 🔥 mark top 2
    for i, t in enumerate(group_a):
        t["top"] = True if i < 2 else False

    for i, t in enumerate(group_b):
        t["top"] = True if i < 2 else False

    return render_template(
        "points.html",
        group_a=group_a,
        group_b=group_b
    )

#nrr file create
def ensure_nrr_files():

    import os

    team_folder = "data/teamlist"
    nrr_folder = "data/NRR_calculation"

    os.makedirs(nrr_folder, exist_ok=True)

    for file in os.listdir(team_folder):

        if not file.endswith(".txt"):
            continue

        team_name = file.replace(".txt", "")

        path = os.path.join(nrr_folder, f"{team_name}.txt")

        # 🔥 create if not exists
        if not os.path.exists(path):

            with open(path, "w") as f:

                f.write("total_runs_scored=0\n")
                f.write("total_overs_faced=0\n")
                f.write("total_runs_conceded=0\n")
                f.write("total_overs_bowled=0\n")


@app.route("/create-nrr")
def create_nrr():

    ensure_nrr_files()

    return "NRR files created"


def update_nrr_stats():

    import os

    match_folder = "data/all_match"

    nrr_folder = "data/NRR_calculation"

    # 🔥 total players
    total_players = 11

    try:

        with open("data/advanced_setting.txt") as f:

            for line in f:

                if line.startswith("players="):

                    total_players = int(line.split("=")[1])

    except:
        pass

    all_out_wickets = total_players - 1

    # 🔥 init
    stats = {}

    # 🔥 ONLY FIRST INNINGS FILE
    files = [f for f in os.listdir(match_folder) if f.endswith("_1st.txt")]

    for file in files:

        first = {}
        second = {}

        path = os.path.join(match_folder, file)

        # =========================
        # 🔥 LOAD FIRST INNINGS
        # =========================

        try:

            with open(path) as f:

                for line in f:

                    if "=" in line:

                        k, v = line.strip().split("=", 1)

                        first[k] = v

        except:
            continue

        # =========================
        # 🔥 LOAD SECOND INNINGS
        # =========================

        second_file = path.replace("_1st.txt", "_2nd.txt")

        if os.path.exists(second_file):

            try:

                with open(second_file) as sf:

                    for line in sf:

                        if "=" in line:

                            k, v = line.strip().split("=", 1)

                            second[k] = v

            except:
                pass

        # =========================
        # 🔥 TEAM INFO
        # =========================

        team1 = first.get("batting")

        team2 = second.get("batting") or first.get("bowling")

        if not team1 or not team2:
            continue

        # =========================
        # 🔥 SCORE DATA
        # =========================

        def get_data(d):

            runs = int(d.get("score", "0"))

            wickets = int(d.get("wickets", "0"))

            over = int(d.get("over", "0"))

            ball = int(d.get("ball", "0"))

            overs = over + (ball / 6)

            # 🔥 all out
            if wickets >= all_out_wickets:

                try:

                    overs = int(d.get("overs", "20"))

                except:

                    overs = 20

            return runs, overs

        t1_runs, t1_overs = get_data(first)

        t2_runs, t2_overs = get_data(second)

        # =========================
        # 🔥 INIT
        # =========================

        for t in [team1, team2]:

            if t not in stats:

                stats[t] = {
                    "runs_scored": 0,
                    "overs_faced": 0,
                    "runs_conceded": 0,
                    "overs_bowled": 0
                }

        # =========================
        # 🔥 UPDATE
        # =========================

        stats[team1]["runs_scored"] += t1_runs
        stats[team1]["overs_faced"] += t1_overs
        stats[team1]["runs_conceded"] += t2_runs
        stats[team1]["overs_bowled"] += t2_overs

        stats[team2]["runs_scored"] += t2_runs
        stats[team2]["overs_faced"] += t2_overs
        stats[team2]["runs_conceded"] += t1_runs
        stats[team2]["overs_bowled"] += t1_overs

    # =========================
    # 🔥 SAVE
    # =========================

    for team, s in stats.items():

        path = os.path.join(nrr_folder, f"{team}.txt")

        with open(path, "w") as f:

            f.write(f"total_runs_scored={s['runs_scored']}\n")

            f.write(
                f"total_overs_faced={round(s['overs_faced'],2)}\n"
            )

            f.write(
                f"total_runs_conceded={s['runs_conceded']}\n"
            )

            f.write(
                f"total_overs_bowled={round(s['overs_bowled'],2)}\n"
            )


@app.route("/update-nrr")
def update_nrr():

    update_nrr_stats()

    return "NRR updated"

@app.route("/current-squad")
def current_squad():

    import os

    path = "data/current_match.txt"

    t1_play, t2_play = [], []
    t1_bench, t2_bench = [], []
    t1_staff, t2_staff = [], []

    first = {"host": "", "visitor": ""}

    if os.path.exists(path):

        with open(path) as f:
            content = f.read()

        data = {}
        for line in content.splitlines():
            if "=" in line:
                k, v = line.split("=", 1)
                data[k.strip()] = v.strip()

        # 🔥 team names
        first["host"] = data.get("team1", "")
        first["visitor"] = data.get("team2", "")

        # 🔥 helper
        def parse_players(text):
            players = []
            for item in text.split("|"):
                if item.strip():
                    if "," in item:
                        name, role = item.split(",",1)
                    else:
                        name, role = item, ""
                    players.append({
                        "name": name.strip(),
                        "role": role.strip()
                    })
            return players

        # 🔥 load all
        t1_play = parse_players(data.get("t1_play",""))
        t2_play = parse_players(data.get("t2_play",""))

        t1_bench = parse_players(data.get("t1_bench",""))
        t2_bench = parse_players(data.get("t2_bench",""))

        t1_staff = parse_players(data.get("t1_staff",""))
        t2_staff = parse_players(data.get("t2_staff",""))

    return render_template(
        "current_squad.html",
        first=first,
        t1_play=t1_play,
        t2_play=t2_play,
        t1_bench=t1_bench,
        t2_bench=t2_bench,
        t1_staff=t1_staff,
        t2_staff=t2_staff
    )


@app.route("/stats")
def stats_page():
    return render_template("stats.html")

@app.route("/most-runs")
def most_runs():

    import os
    try:
         build_most_runs()
    except:
        pass
    data = []

    path = "data/most_runs.txt"

    if os.path.exists(path):

        with open(path) as f:
            lines = f.readlines()[1:]  # skip header

            for line in lines:

                parts = line.strip().split("|")

                if len(parts) == 7:

                    data.append({
                        "player": parts[0],
                        "match": int(parts[1]),
                        "inns": int(parts[2]),
                        "runs": int(parts[3]),
                        "sr": parts[4],
                        "fours": parts[5],
                        "sixes": parts[6]
                    })

    # 🔥 SORT (RUNS DESC)
    data.sort(key=lambda x: x["runs"], reverse=True)

    return render_template("most_runs.html", players=data)

@app.route("/build-most-runs")
def build_runs():

    build_most_runs()

    return "✅ Most Runs Updated"


def build_most_runs():

    import os, json

    folder = "data/all_match"

    save_path = "data/most_runs.txt"

    players = {}

    for file in os.listdir(folder):

        # 🔥 ONLY FIRST INNINGS FILE
        if not file.endswith("_1st.txt"):
            continue

        path = os.path.join(folder, file)

        innings_parts = []

        # =========================
        # 🔥 FIRST INNINGS
        # =========================

        try:

            with open(path) as f:
                innings_parts.append(f.read())

        except:
            continue

        # =========================
        # 🔥 SECOND INNINGS
        # =========================

        second_file = path.replace("_1st.txt", "_2nd.txt")

        if os.path.exists(second_file):

            try:

                with open(second_file) as sf:
                    innings_parts.append(sf.read())

            except:
                pass

        # 🔥 match count safe
        match_players = set()

        for inn in innings_parts:

            lines = inn.splitlines()

            # =========================
            # 🔥 SQUAD
            # =========================

            for line in lines:

                if "_squad=" in line:

                    try:

                        data = json.loads(line.split("=", 1)[1])

                        for p in data:

                            name = p["name"].strip()

                            match_players.add(name)

                    except:
                        pass

        # =========================
        # 🔥 MATCH ++
        # =========================

        for name in match_players:

            if name not in players:

                players[name] = {
                    "match": 0,
                    "inns": 0,
                    "runs": 0,
                    "balls": 0,
                    "4s": 0,
                    "6s": 0
                }

            players[name]["match"] += 1

        # =========================
        # 🔥 BATTING LOG
        # =========================

        for inn in innings_parts:

            lines = inn.splitlines()

            for line in lines:

                if line.startswith("batsman_log="):

                    log = line.split("=", 1)[1]

                    if not log.strip():
                        continue

                    entries = log.split("|")

                    for e in entries:

                        try:

                            name, stats = e.split("=")

                            vals = stats.split(",")

                            runs = int(vals[0])

                            balls = int(vals[1])

                            fours = int(vals[2])

                            sixes = int(vals[3])

                            name = name.strip()

                            if name not in players:

                                players[name] = {
                                    "match": 0,
                                    "inns": 0,
                                    "runs": 0,
                                    "balls": 0,
                                    "4s": 0,
                                    "6s": 0
                                }

                            # 🔥 INNS++
                            players[name]["inns"] += 1

                            # 🔥 STATS
                            players[name]["runs"] += runs
                            players[name]["balls"] += balls
                            players[name]["4s"] += fours
                            players[name]["6s"] += sixes

                        except:
                            continue

    # =========================
    # 🔥 SAVE FILE
    # =========================

    with open(save_path, "w") as f:

        f.write("Player|Match|Inns|Runs|SR|4s|6s\n")

        for name, s in players.items():

            sr = (s["runs"] / s["balls"] * 100) if s["balls"] > 0 else 0

            line = (
                f"{name}|{s['match']}|{s['inns']}|"
                f"{s['runs']}|{sr:.2f}|{s['4s']}|{s['6s']}\n"
            )

            f.write(line)

@app.route("/build-most-wicket")
def build_most_wicket_route():

    try:

        build_most_wickets()

        return "✅ Most Wicket Data Updated"

    except Exception as e:

        return f"❌ Error: {e}"


def build_most_wickets():

    import os
    import json

    match_folder = "data/all_match"

    save_path = "data/most_wicket.txt"

    players = {}

    for file in os.listdir(match_folder):

        # 🔥 ONLY FIRST INNINGS FILE
        if not file.endswith("_1st.txt"):
            continue

        path = os.path.join(match_folder, file)

        innings_list = []

        # =========================
        # 🔥 FIRST INNINGS
        # =========================

        try:

            with open(path, encoding="utf-8") as f:

                innings_list.append(f.read())

        except:
            continue

        # =========================
        # 🔥 SECOND INNINGS
        # =========================

        second_file = path.replace("_1st.txt", "_2nd.txt")

        if os.path.exists(second_file):

            try:

                with open(second_file, encoding="utf-8") as sf:

                    innings_list.append(sf.read())

            except:
                pass

        # =========================
        # 🔥 MATCH COUNT
        # =========================

        all_data = "\n".join(innings_list)

        data_map = {}

        for line in all_data.splitlines():

            if "=" in line:

                k, v = line.split("=", 1)

                data_map[k.strip()] = v.strip()

        counted_players = set()

        for key in data_map:

            if key.endswith("_squad"):

                try:

                    squad = json.loads(data_map[key])

                except:
                    continue

                for p in squad:

                    name = p["name"]

                    # 🔥 already counted
                    if name in counted_players:
                        continue

                    counted_players.add(name)

                    if name not in players:

                        players[name] = {
                            "match": 0,
                            "balls": 0,
                            "wickets": 0,
                            "runs": 0
                        }

                    # 🔥 MATCH ++
                    players[name]["match"] += 1

        # =========================
        # 🔥 BOWLER LOG
        # =========================

        for inning in innings_list:

            data = {}

            for line in inning.splitlines():

                if "=" in line:

                    k, v = line.split("=", 1)

                    data[k.strip()] = v.strip()

            bowler_log = data.get("bowler_log", "")

            if not bowler_log:
                continue

            entries = bowler_log.split("|")

            for e in entries:

                if "=" not in e:
                    continue

                name, stats = e.split("=")

                name = name.strip()

                vals = stats.split(",")

                if len(vals) < 5:
                    continue

                over_str = vals[0]

                runs = int(vals[1])

                wickets = int(vals[3])

                # 🔥 overs → balls
                if "." in over_str:

                    o, b = over_str.split(".")

                    balls = int(o) * 6 + int(b)

                else:

                    balls = int(over_str) * 6

                if name not in players:

                    players[name] = {
                        "match": 0,
                        "balls": 0,
                        "wickets": 0,
                        "runs": 0
                    }

                players[name]["balls"] += balls

                players[name]["wickets"] += wickets

                players[name]["runs"] += runs

    # =========================
    # 🔥 SAVE FILE
    # =========================

    with open(save_path, "w", encoding="utf-8") as f:

        for name, d in players.items():

            balls = d["balls"]

            overs = f"{balls//6}.{balls%6}"

            wickets = d["wickets"]

            runs = d["runs"]

            avg = round(balls / wickets, 2) if wickets > 0 else 0

            f.write(
                f"{name}|{d['match']}|{overs}|"
                f"{balls}|{wickets}|{avg}|{runs}\n"
            )
@app.route("/most-wicket")
def most_wicket():

    try:
        build_most_wickets()   # 🔥 auto update
    except:
        pass

    import os

    players = []
    path = "data/most_wicket.txt"

    if os.path.exists(path):

        with open(path, encoding="utf-8") as f:

            for line in f:

                parts = line.strip().split("|")

                if len(parts) == 7:

                    players.append({
                        "player": parts[0],
                        "match": int(parts[1]),
                        "overs": parts[2],
                        "balls": int(parts[3]),
                        "wickets": int(parts[4]),
                        "avg": float(parts[5]),
                        "runs": int(parts[6])
                    })

    players.sort(key=lambda x: (-x["wickets"], x["avg"], x["runs"]))

    return render_template("most_wicket.html", players=players)

@app.route("/all-match")
def all_match():

    import os

    folder = "data/all_match"

    matches = []

    # 🔥 ONLY FIRST INNINGS FILE
    files = [f for f in os.listdir(folder) if f.endswith("_1st.txt")]

    for file in files:

        path = os.path.join(folder, file)

        first = {}
        second = {}

        # 🔥 =========================
        # 🔥 LOAD FIRST INNINGS
        # 🔥 =========================

        with open(path) as f:

            for line in f:

                if "=" in line:
                    k, v = line.strip().split("=", 1)
                    first[k] = v

        # 🔥 =========================
        # 🔥 LOAD SECOND INNINGS
        # 🔥 =========================

        second_file = path.replace("_1st.txt", "_2nd.txt")

        if os.path.exists(second_file):

            with open(second_file) as sf:

                for line in sf:

                    if "=" in line:
                        k, v = line.strip().split("=", 1)
                        second[k] = v

        # 🔥 =========================
        # 🔥 MATCH TIME
        # 🔥 =========================

        match_time = first.get("match_time", "")

        # 🔥 innings break
        innings_break = len(second) > 0

        # 🔥 RESULT
        result_text = second.get("match_result", "")

        # 🔥 TEAMS
        team1 = first.get("batting")
        team2 = second.get("batting") or first.get("bowling")

        # 🔥 SECOND SCORE
        team2_score = second.get("score", "")
        team2_wickets = second.get("wickets", "")
        team2_over = f"{second.get('over','0')}.{second.get('ball','0')}"

        if second.get("over", "0") == "0" and second.get("ball", "0") == "0":

            if innings_break:

                team2_score = "0"
                team2_wickets = "0"
                team2_over = "0.0"

            else:

                team2_score = ""
                team2_wickets = ""
                team2_over = ""

        # 🔥 STATUS
        status = "COMPLETED" if result_text else "LIVE"

        matches.append({

            "team1": team1,

            "team1_score": first.get("score", "0"),
            "team1_wickets": first.get("wickets", "0"),
            "team1_over": f"{first.get('over','0')}.{first.get('ball','0')}",

            "team2": team2,

            "team2_score": team2_score,
            "team2_wickets": team2_wickets,
            "team2_over": team2_over,

            "result": result_text,

            "need_text": second.get("need_text"),

            "toss": first.get("toss"),
            "opt": first.get("opt"),

            "status": status,

            "innings_break": innings_break,

            "date": match_time,

            "file": file
        })

    from datetime import datetime

    matches.sort(
        key=lambda m:
        datetime.strptime(m["date"], "%d %b %Y, %I:%M %p")
        if m["date"] else datetime.min,
        reverse=True
    )

    return render_template(
        "all_match.html",
        matches=matches
    )



@app.route("/current-squad-data")
def current_squad_data():

    import json

    path = "data/current_match.txt"

    t1 = []
    t2 = []
    team1 = ""
    team2 = ""

    try:
        with open(path) as f:
            content = f.read()

        for line in content.splitlines():

            if line.startswith("host="):
                team1 = line.split("=",1)[1]

            elif line.startswith("visitor="):
                team2 = line.split("=",1)[1]

            elif "_squad=" in line:

                key, val = line.split("=",1)

                try:
                    squad = json.loads(val)
                except:
                    squad = []

                if key.startswith(team1):
                    t1 = squad
                elif key.startswith(team2):
                    t2 = squad

    except:
        pass

    return render_template(
        "partials/current_squad_partial.html",
        team1=team1,
        team2=team2,
        t1=t1,
        t2=t2
    )

if __name__ == "__main__":
    import os

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )