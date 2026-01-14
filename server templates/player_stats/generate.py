import json
import os
import glob
import math
from datetime import datetime

# ==========================================
# ⚙️ CONFIGURATION
# ==========================================

# Path settings - USING ABSOLUTE PATHS (Raw Strings)
WORLD_DIR = r"C:\Users\Server\Downloads\mcss_win-x86-64_v13.9.2\servers\server_season_2\world"
USERCACHE_PATH = r"C:\Users\Server\Downloads\mcss_win-x86-64_v13.9.2\servers\server_season_2\usercache.json"

STATS_DIR = os.path.join(WORLD_DIR, "stats")
OUTPUT_FILE = "stats_dashboard.html"
MIN_PLAYTIME_HOURS = 0.5

# ---------------------------------------------------------
# 1. LEADERBOARDS
# ---------------------------------------------------------
LEADERBOARDS = {
    "playtime": { "label": "Total Playtime (Hours)", "category": "minecraft:custom", "key": "minecraft:play_time", "unit": "ticks_to_hours", "color": "#76c710" }, # Green
    "deaths": { "label": "Total Deaths", "category": "minecraft:custom", "key": "minecraft:deaths", "color": "#c12c2c" }, # Red
    "mob_kills": { "label": "Mob Kills", "category": "minecraft:custom", "key": "minecraft:mob_kills", "color": "#d9a334" }, # Gold
    "player_kills": { "label": "Player Kills", "category": "minecraft:custom", "key": "minecraft:player_kills", "color": "#b83d3d" }, # Dark Red
    "blocks_mined": { "label": "Total Blocks Mined", "type": "sum", "category": "minecraft:mined", "color": "#7a7a7a" }, # Stone
    "items_crafted": { "label": "Items Crafted", "type": "sum", "category": "minecraft:crafted", "color": "#6d4e28" }, # Wood
    "items_used": { "label": "Items Used / Placed", "type": "sum", "category": "minecraft:used", "color": "#a88e63" }, # Sand
    "damage_dealt": { "label": "Damage Dealt", "category": "minecraft:custom", "key": "minecraft:damage_dealt", "unit": "deci_to_int", "color": "#d66c15" }, # Orange
    "distance_walked": { "label": "Distance Walked", "category": "minecraft:custom", "key": "minecraft:walk_one_cm", "unit": "cm_to_blocks", "color": "#5297d6" }, # Diamond
    "damage_taken": { "label": "Damage Taken", "category": "minecraft:custom", "key": "minecraft:damage_taken", "color": "#9e2b2b" } # Dark Red
}

# ---------------------------------------------------------
# 2. NOTABLE STATS
# ---------------------------------------------------------
NOTABLES = [
    {"label": "Distance Swum", "cat": "minecraft:custom", "key": "minecraft:swim_one_cm", "unit": "cm_to_blocks"},
    {"label": "Distance Flown", "cat": "minecraft:custom", "key": "minecraft:fly_one_cm", "unit": "cm_to_blocks"},
    {"label": "Distance Crouched", "cat": "minecraft:custom", "key": "minecraft:crouch_one_cm", "unit": "cm_to_blocks"},
    {"label": "Distance on Water", "cat": "minecraft:custom", "key": "minecraft:boat_one_cm", "unit": "cm_to_blocks"},
    {"label": "Distance by Elytra", "cat": "minecraft:custom", "key": "minecraft:aviate_one_cm", "unit": "cm_to_blocks"},
    {"label": "Jumps Made", "cat": "minecraft:custom", "key": "minecraft:jump"},
    {"label": "Chests Opened", "cat": "minecraft:custom", "key": "minecraft:open_chest"},
    {"label": "Workstations Used", "cat": "minecraft:custom", "key": "minecraft:interact_with_crafting_table"},
    {"label": "Beds Used", "cat": "minecraft:custom", "key": "minecraft:sleep_in_bed"},
    {"label": "Villager Trades", "cat": "minecraft:custom", "key": "minecraft:traded_with_villager"},
    {"label": "Damage Resisted", "cat": "minecraft:custom", "key": "minecraft:damage_resisted"},
    {"label": "Damage Absorbed", "cat": "minecraft:custom", "key": "minecraft:damage_absorbed"},
    {"label": "Fall Distance", "cat": "minecraft:custom", "key": "minecraft:fall_one_cm", "unit": "cm_to_blocks"}, 
    {"label": "Items Picked Up", "type": "sum", "cat": "minecraft:picked_up"},
    {"label": "Items Dropped", "type": "sum", "cat": "minecraft:dropped"},
    {"label": "Fish Caught", "cat": "minecraft:custom", "key": "minecraft:fish_caught"},
    {"label": "Animals Bred", "cat": "minecraft:custom", "key": "minecraft:animals_bred"},
    {"label": "Enchantments", "cat": "minecraft:custom", "key": "minecraft:enchant_item"},
    {"label": "Raids Won", "cat": "minecraft:custom", "key": "minecraft:raid_win"},
    {"label": "Bells Rung", "cat": "minecraft:custom", "key": "minecraft:bell_ring"},
]

# ==========================================
# 🛠️ HELPER FUNCTIONS
# ==========================================

def load_usercache():
    cache = {}
    if os.path.exists(USERCACHE_PATH):
        try:
            with open(USERCACHE_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for entry in data:
                    raw_uuid = entry.get('uuid', '').replace('-', '').lower()
                    cache[raw_uuid] = entry.get('name', 'Unknown')
        except Exception as e:
            print(f"Warning: Could not read usercache.json: {e}")
    return cache

def convert_unit(value, unit_type):
    if value is None: return 0
    if unit_type == "ticks_to_hours": return round(value / 20 / 3600, 2)
    elif unit_type == "cm_to_blocks": return int(value / 100)
    elif unit_type == "deci_to_int": return int(value / 10)
    return value

def extract_stat_value(stats_json, category, key=None, agg_type="stat"):
    stats_root = stats_json.get('stats', {}) or stats_json
    cat_data = stats_root.get(category, {})
    if agg_type == "sum": return sum(cat_data.values())
    return cat_data.get(key, 0)

# ==========================================
# 🚀 DATA PROCESSING
# ==========================================

def process_data():
    print("Reading User Cache...")
    uuid_map = load_usercache()
    print(f"Scanning stats in {STATS_DIR}...")
    
    player_data = []
    files = glob.glob(os.path.join(STATS_DIR, "*.json"))
    
    for filepath in files:
        filename = os.path.basename(filepath)
        u_uuid = filename.replace('.json', '').replace('-', '').lower()
        name = uuid_map.get(u_uuid, u_uuid[:8]) 
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except:
            continue

        playtime_ticks = extract_stat_value(data, "minecraft:custom", "minecraft:play_time")
        if playtime_ticks == 0:
             playtime_ticks = extract_stat_value(data, "minecraft:custom", "minecraft:play_one_minute")

        playtime_hours = convert_unit(playtime_ticks, "ticks_to_hours")
        
        if playtime_hours < MIN_PLAYTIME_HOURS:
            continue

        p_obj = { "name": name, "uuid": u_uuid, "playtime": playtime_hours }

        for lb_id, lb_conf in LEADERBOARDS.items():
            if lb_id == 'playtime': continue 
            val = extract_stat_value(data, lb_conf['category'], lb_conf.get('key'), lb_conf.get('type', 'stat'))
            if 'unit' in lb_conf: val = convert_unit(val, lb_conf['unit'])
            p_obj[lb_id] = val

        p_obj['notables'] = {}
        for note in NOTABLES:
            val = extract_stat_value(data, note.get('cat'), note.get('key'), note.get('type', 'stat'))
            if 'unit' in note: val = convert_unit(val, note['unit'])
            p_obj['notables'][note['label']] = val

        player_data.append(p_obj)
        
    print(f"Processed {len(player_data)} players.")
    return player_data

# ==========================================
# 🎨 HTML GENERATION (THEMED)
# ==========================================

def generate_html(players):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # 1. Generate JS for Charts
    charts_js = ""
    for lb_id, lb_conf in LEADERBOARDS.items():
        sorted_players = sorted(players, key=lambda x: x.get(lb_id, 0), reverse=True)[:10]
        labels = [p['name'] for p in sorted_players]
        data_vals = [p[lb_id] for p in sorted_players]
        color = lb_conf.get('color', '#36a2eb')
        
        charts_js += f"""
        new Chart(document.getElementById('{lb_id}'), {{
            type: 'bar',
            data: {{
                labels: {json.dumps(labels)},
                datasets: [{{
                    label: '{lb_conf['label']}',
                    data: {json.dumps(data_vals)},
                    backgroundColor: '{color}',
                    borderColor: '#000',
                    borderWidth: 2,
                    hoverBackgroundColor: '#fff'
                }}]
            }},
            options: {{
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{ legend: {{ display: false }} }},
                scales: {{ 
                    x: {{ grid: {{ color: '#555' }}, ticks: {{ color: '#fff', font: {{ family: "'VT323', monospace", size: 16 }} }} }}, 
                    y: {{ grid: {{ display: false }}, ticks: {{ color: '#fff', font: {{ family: "'VT323', monospace", size: 16 }} }} }} 
                }}
            }}
        }});
        """

    # 2. Generate Notables HTML
    notables_html = ""
    for note in NOTABLES:
        top_5 = sorted(players, key=lambda x: x['notables'].get(note['label'], 0), reverse=True)[:5]
        rows = ""
        for i, p in enumerate(top_5):
            val = p['notables'].get(note['label'], 0)
            medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"{i+1}."
            rows += f"<tr><td><span class='rank'>{medal}</span> {p['name']}</td><td class='text-right'>{val:,}</td></tr>"
            
        notables_html += f"""
        <div class="mc-window">
            <div class="mc-title">{note['label']}</div>
            <div class="mc-content">
                <table>{rows}</table>
            </div>
        </div>
        """

    # 3. Full HTML Template with Minecraft CSS
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Minecraft Server Stats</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=VT323&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {{
            --bg-color: #1a1a1a;
            --mc-grey: #c6c6c6;
            --mc-dark-grey: #8b8b8b;
            --mc-dark: #373737;
            --mc-border-light: #ffffff;
            --mc-border-dark: #555555;
            --text-color: #e0e0e0;
        }}
        body {{
            background-color: #121212;
            background-image: linear-gradient(30deg, #181818 12%, transparent 12.5%, transparent 87%, #181818 87.5%, #181818),
            linear-gradient(150deg, #181818 12%, transparent 12.5%, transparent 87%, #181818 87.5%, #181818),
            linear-gradient(30deg, #181818 12%, transparent 12.5%, transparent 87%, #181818 87.5%, #181818),
            linear-gradient(150deg, #181818 12%, transparent 12.5%, transparent 87%, #181818 87.5%, #181818),
            linear-gradient(60deg, #222 25%, transparent 25.5%, transparent 75%, #222 75%, #222),
            linear-gradient(60deg, #222 25%, transparent 25.5%, transparent 75%, #222 75%, #222);
            background-size: 40px 70px;
            background-position: 0 0, 0 0, 20px 35px, 20px 35px, 0 0, 20px 35px;
            font-family: 'VT323', monospace;
            color: var(--text-color);
            margin: 0;
            padding: 20px;
        }}
        h1 {{ 
            text-align: center; 
            font-size: 4rem; 
            margin: 20px 0 5px 0; 
            text-shadow: 4px 4px 0px #000; 
            color: #fff;
            letter-spacing: 2px;
        }}
        h2 {{ 
            text-align: center; 
            font-size: 2.5rem; 
            margin-top: 50px; 
            text-shadow: 2px 2px 0px #000; 
            color: #fce803; /* Gold */
        }}
        .timestamp {{ text-align: center; font-size: 1.2rem; color: #aaa; margin-bottom: 40px; text-shadow: 1px 1px 0 #000; }}

        /* Minecraft Window Style Container */
        .mc-window {{
            background: #212121;
            border: 4px solid #000;
            box-shadow: inset 4px 4px 0px #444, inset -4px -4px 0px #111;
            padding: 4px;
            position: relative;
        }}
        .mc-title {{
            background: #333;
            color: #ddd;
            padding: 5px 10px;
            font-size: 1.5rem;
            text-align: center;
            border-bottom: 2px solid #555;
            margin-bottom: 10px;
            text-shadow: 1px 1px 0 #000;
        }}

        /* Chart Grid */
        .chart-grid {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(450px, 1fr)); 
            gap: 25px; 
            max-width: 1400px;
            margin: 0 auto 50px auto;
        }}
        .chart-container {{
            background: rgba(0,0,0,0.6);
            border: 3px solid #888;
            padding: 15px;
            height: 320px;
        }}
        .chart-header {{ font-size: 1.8rem; text-align: center; margin-bottom: 10px; color: #fff; text-shadow: 2px 2px 0 #000; }}

        /* Notables Grid */
        .notables-grid {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); 
            gap: 20px; 
            max-width: 1400px;
            margin: 0 auto;
        }}
        .mc-content {{ padding: 10px; }}
        
        table {{ width: 100%; border-collapse: collapse; font-size: 1.4rem; }}
        td {{ padding: 6px 4px; border-bottom: 2px solid #333; }}
        tr:last-child td {{ border-bottom: none; }}
        .text-right {{ text-align: right; color: #76c710; }}
        .rank {{ color: #d9a334; width: 20px; display: inline-block; }}
    </style>
</head>
<body>
    <h1>SERVER STATISTICS</h1>
    <div class="timestamp">Last Updated: {timestamp}</div>

    <h2>🏆 LEADERBOARDS</h2>
    <div class="chart-grid">
        {''.join([f'<div class="mc-window"><div class="chart-header">{cfg["label"]}</div><div class="chart-container"><canvas id="{lid}"></canvas></div></div>' for lid, cfg in LEADERBOARDS.items()])}
    </div>

    <h2>⭐ HALL OF FAME</h2>
    <div class="notables-grid">
        {notables_html}
    </div>

    <script>
        Chart.defaults.font.family = "'VT323', monospace";
        Chart.defaults.color = '#ddd';
        {charts_js}
    </script>
</body>
</html>
    """
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Successfully generated {OUTPUT_FILE}")

# ==========================================
# 🏁 MAIN EXECUTION
# ==========================================

if __name__ == "__main__":
    if not os.path.exists(STATS_DIR):
        print(f"ERROR: Stats directory not found at {STATS_DIR}")
    else:
        data = process_data()
        if data:
            generate_html(data)
        else:
            print("No player data found or all players below playtime threshold.")
