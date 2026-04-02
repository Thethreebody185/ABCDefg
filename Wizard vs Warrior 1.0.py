# -*- coding: utf-8 -*-
# --- Wizard Game Full (Chinese UI + Inventory/Equip System + Styled Buttons) ---

import tkinter as tk
from tkinter import ttk # For better Treeview in inventory
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk
import os
import json
import random

# --- Configuration ---
USERS_FILE = "users.json"
SCORES_FILE = "scores.txt"
AVATAR_FOLDER = "avatars"
DEFAULT_AVATAR = "default.png"
BOSS_LEVEL_INTERVAL = 10

# --- Equipment Slot Limits (for equipping, not owning) ---
MAX_WEAPONS_EQUIPPED = 1
MAX_ARMOR_EQUIPPED = 1
MAX_ACCESSORIES_EQUIPPED = 5

# --- Ensure Avatar Folder Exists ---
if not os.path.exists(AVATAR_FOLDER):
    os.makedirs(AVATAR_FOLDER)
    print(f"已创建 '{AVATAR_FOLDER}' 文件夹。请添加一些 .png 或 .jpg 图片作为头像。")
    try:
        default_path = os.path.join(AVATAR_FOLDER, DEFAULT_AVATAR)
        if not os.path.exists(default_path):
            img = Image.new('RGB', (60, 60), color = 'grey')
            img.save(default_path)
            print(f"已创建占位头像 '{DEFAULT_AVATAR}'。")
    except Exception as e:
        print(f"无法创建占位头像：{e}")


# --- Game Data (Global State) ---
game_data = {
    "current_user": None,
    "users": {},
    "player_stats": {
        "score": 0,
        "level": 1,
        "avatar": os.path.join(AVATAR_FOLDER, DEFAULT_AVATAR),
        "inventory": {}, # item_id: {"level": X}
        "equipped_items": { 
            "weapon": None, 
            "armor": None,  
            "accessories": [] 
        },
        "max_hp": 50,
        "current_hp": 50,
        "high_score": 0,
        "defeated_bosses": []
    }
}

# --- Shop Item Definitions (with Chinese names/descriptions) ---
SHOP_ITEMS = {
    "wooden_sword": {
        "name": "木剑", "type": "weapon", "description": "基础剑。+伤害", "stat_type": "damage",
        "base_cost": 20, "upgrade_multiplier": 1.2,
        "base_stat": 2, "stat_growth": 1
    },
    "iron_sword": {
        "name": "铁剑", "type": "weapon", "description": "更坚固的剑。+伤害", "stat_type": "damage",
        "base_cost": 100, "upgrade_multiplier": 1.5,
        "base_stat": 5, "stat_growth": 2
    },
    "steel_sword": {
        "name": "钢剑", "type": "weapon", "description": "锋利的钢剑。+伤害", "stat_type": "damage",
        "base_cost": 250, "upgrade_multiplier": 1.6,
        "base_stat": 8, "stat_growth": 3
    },
    "basic_wand": {
        "name": "基础魔杖", "type": "weapon", "description": "引导微弱的魔法。+伤害", "stat_type": "damage",
        "base_cost": 50, "upgrade_multiplier": 1.3,
        "base_stat": 3, "stat_growth": 1.5
    },
    "leather_armor": {
        "name": "皮甲", "type": "armor", "description": "简单的保护。+防御", "stat_type": "defense",
        "base_cost": 30, "upgrade_multiplier": 1.2,
        "base_stat": 1, "stat_growth": 0.5
    },
    "chainmail_armor": {
        "name": "锁子甲", "type": "armor", "description": "更好的保护。+防御", "stat_type": "defense",
        "base_cost": 150, "upgrade_multiplier": 1.6,
        "base_stat": 3, "stat_growth": 1
    },
    "plate_armor": {
        "name": "板甲", "type": "armor", "description": "坚固的板甲。+防御", "stat_type": "defense",
        "base_cost": 300, "upgrade_multiplier": 1.7,
        "base_stat": 5, "stat_growth": 1.5
    },
     "health_amulet": {
        "name": "生命护符", "type": "accessory", "description": "增加最大生命值。+最大HP", "stat_type": "max_hp",
        "base_cost": 80, "upgrade_multiplier": 1.4,
        "base_stat": 10, "stat_growth": 5
    },
    "mana_ring": {
        "name": "法力戒指", "type": "accessory", "description": "微量增加法术伤害 (概念性)。+微量伤害", "stat_type": "damage",
        "base_cost": 120, "upgrade_multiplier": 1.5,
        "base_stat": 1, "stat_growth": 0.5
    },
    "swiftness_boots": {
        "name": "迅捷之靴", "type": "accessory", "description": "略微提升闪避 (概念性)。+微量闪避", "stat_type": "evasion",
        "base_cost": 100, "upgrade_multiplier": 1.3,
        "base_stat": 1, "stat_growth": 0.2
    }
}

# --- Enemy Definitions (with Chinese names) ---
REGULAR_ENEMY_TYPES = {
    "Goblin": {"name_cn": "哥布林", "hp": 15, "attack": 3, "defense": 0, "xp": 10, "score": 15},
    "Orc": {"name_cn": "兽人", "hp": 40, "attack": 6, "defense": 1, "xp": 25, "score": 30},
    "Skeleton": {"name_cn": "骷髅", "hp": 25, "attack": 4, "defense": 2, "xp": 18, "score": 25},
    "Slime": {"name_cn": "史莱姆", "hp": 50, "attack": 2, "defense": 0, "xp": 15, "score": 20},
    "Wolf": {"name_cn": "狼", "hp": 20, "attack": 5, "defense": 0, "xp": 12, "score": 18},
    "Giant Spider": {"name_cn": "巨型蜘蛛", "hp": 30, "attack": 5, "defense": 1, "xp": 20, "score": 22},
}

# --- Boss Definitions (with Chinese names) ---
BOSS_TYPES = {
    10: {"name": "哥布林王 格鲁克", "hp": 200, "attack": 15, "defense": 5, "score_reward": 250},
    20: {"name": "兽人督军 沃哥斯", "hp": 450, "attack": 25, "defense": 10, "score_reward": 600},
    30: {"name": "死灵法师 萨瑟斯", "hp": 400, "attack": 35, "defense": 8, "score_reward": 1000},
}


# --- Data Handling Functions ---
def load_users():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                users = json.load(f)
                for username, data in users.items(): 
                    data.setdefault("defeated_bosses", [])
                    data.setdefault("max_hp", 50)
                    data.setdefault("inventory", {})
                    data.setdefault("high_score", data.get("score", 0))
                    data.setdefault("equipped_items", {"weapon": None, "armor": None, "accessories": []})
                    if not isinstance(data["equipped_items"].get("accessories"), list):
                        data["equipped_items"]["accessories"] = []
                return users
        except (json.JSONDecodeError, FileNotFoundError, TypeError) as e:
            print(f"警告：无法加载或解码 {USERS_FILE}。错误：{e}。将重新开始。")
            return {}
    return {}

def save_users():
    try:
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(game_data["users"], f, indent=4, ensure_ascii=False)
    except IOError as e:
        messagebox.showerror("保存错误", f"无法保存用户数据：{e}")
    except Exception as e:
        print(f"保存用户时发生意外错误：{e}")

def load_scores():
    scores = {}
    if os.path.exists(SCORES_FILE):
        try:
            with open(SCORES_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    parts = line.strip().split("|")
                    if len(parts) == 2:
                        user, score_str = parts
                        try:
                            score = int(score_str)
                            scores[user] = max(score, scores.get(user, 0))
                        except ValueError:
                            print(f"跳过无效积分行：{line.strip()}")
        except Exception as e:
             print(f"加载积分文件时出错：{e}")
    return scores

def save_score(user, score):
    needs_user_save = False
    if user in game_data["users"]:
         if score > game_data["users"][user].get("high_score", 0):
             game_data["users"][user]["high_score"] = score
             game_data["player_stats"]["high_score"] = score
             needs_user_save = True

    current_scores = load_scores()
    current_scores[user] = max(score, current_scores.get(user, 0))
    try:
        with open(SCORES_FILE, "w", encoding="utf-8") as f:
            for u, s in current_scores.items():
                f.write(f"{u}|{s}\n")
    except IOError as e:
        messagebox.showerror("保存错误", f"无法保存积分：{e}")
    return needs_user_save

# --- UI Helper Functions ---
def clear_frame(frame=None):
    target_frame = frame or main_frame
    widgets_to_destroy = target_frame.winfo_children()
    for widget in widgets_to_destroy:
        widget.destroy()

def display_avatar(path, size=(100, 100)):
    try:
        if not path or not os.path.exists(path):
            path = os.path.join(AVATAR_FOLDER, DEFAULT_AVATAR)
            if not os.path.exists(path):
                 print(f"错误：在 '{AVATAR_FOLDER}' 中找不到默认头像 '{DEFAULT_AVATAR}'。")
                 return None
        img = Image.open(path)
        img = img.resize(size, Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(img)
    except Exception as e:
        print(f"加载图片 {path} 时出错：{e}")
        try:
            default_path = os.path.join(AVATAR_FOLDER, DEFAULT_AVATAR)
            if not os.path.exists(default_path): return None
            img = Image.open(default_path)
            img = img.resize(size, Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(img)
        except Exception as e_default:
             print(f"错误：加载默认头像 '{DEFAULT_AVATAR}' 时也出错：{e_default}")
             return None

# --- Player Stat Calculation ---
def calculate_player_stats():
    equipped = game_data["player_stats"]["equipped_items"]
    inventory = game_data["player_stats"]["inventory"] 
    total_damage = 0; total_defense = 0; added_max_hp_from_items = 0
    if equipped["weapon"] and equipped["weapon"] in inventory:
        item_id = equipped["weapon"]
        if item_id in SHOP_ITEMS: 
            item_def = SHOP_ITEMS[item_id]
            level = max(1, inventory[item_id].get("level", 1))
            total_damage += item_def["base_stat"] + (item_def["stat_growth"] * (level - 1))
    if equipped["armor"] and equipped["armor"] in inventory:
        item_id = equipped["armor"]
        if item_id in SHOP_ITEMS: 
            item_def = SHOP_ITEMS[item_id]
            level = max(1, inventory[item_id].get("level", 1))
            total_defense += item_def["base_stat"] + (item_def["stat_growth"] * (level - 1))
    for item_id in equipped["accessories"]:
        if item_id in inventory and item_id in SHOP_ITEMS: 
            item_def = SHOP_ITEMS[item_id]
            level = max(1, inventory[item_id].get("level", 1))
            stat_value = item_def["base_stat"] + (item_def["stat_growth"] * (level - 1))
            if item_def["stat_type"] == "max_hp": added_max_hp_from_items += stat_value
            elif item_def["stat_type"] == "damage": total_damage += stat_value
    base_damage = 1; base_defense = 0 
    current_max_hp_base = game_data["player_stats"].get("max_hp", 50)
    final_max_hp = current_max_hp_base + added_max_hp_from_items
    game_data["player_stats"]["calculated_damage"] = base_damage + total_damage
    game_data["player_stats"]["calculated_defense"] = base_defense + total_defense
    game_data["player_stats"]["final_max_hp"] = final_max_hp
    game_data["player_stats"]["current_hp"] = min(game_data["player_stats"]["current_hp"], final_max_hp)
    return game_data["player_stats"]["calculated_damage"], game_data["player_stats"]["calculated_defense"]


# --- UI Screens ---
def login_screen():
    clear_frame(); game_data["current_user"] = None; game_data["users"] = load_users()
    tk.Label(main_frame, text="巫师冒险", font=("SimHei", 24, "bold"), fg="#FFD700", bg="#111111").pack(pady=20)
    tk.Button(main_frame, text="登录", font=("SimHei", 14, "bold"), command=login_ui, width=20, bg="#4CAF50", fg="white", relief=tk.FLAT, padx=10, pady=5, bd=0, activebackground="#45a049", activeforeground="white").pack(pady=10)
    tk.Button(main_frame, text="注册", font=("SimHei", 14, "bold"), command=register_ui, width=20, bg="#2196F3", fg="white", relief=tk.FLAT, padx=10, pady=5, bd=0, activebackground="#1e88e5", activeforeground="white").pack(pady=10)
    tk.Button(main_frame, text="退出", font=("SimHei", 12, "bold"), command=root.quit, width=15, bg="#f44336", fg="white", relief=tk.FLAT, padx=10, pady=5, bd=0, activebackground="#e53935", activeforeground="white").pack(pady=20)

def login_ui():
    clear_frame()
    tk.Label(main_frame, text="登录", font=("SimHei", 18), fg="white", bg="#111111").pack(pady=10)
    tk.Label(main_frame, text="用户名：", font=("SimHei", 12), bg="#111111", fg="white").pack()
    name_entry = tk.Entry(main_frame, width=30, bg="#333333", fg="white", insertbackground="white", font=("SimHei", 11))
    name_entry.pack(pady=5)
    tk.Label(main_frame, text="密码：", font=("SimHei", 12), bg="#111111", fg="white").pack()
    pass_entry = tk.Entry(main_frame, show="*", width=30, bg="#333333", fg="white", insertbackground="white", font=("SimHei", 11))
    pass_entry.pack(pady=5)
    def attempt_login():
        name = name_entry.get(); pwd = pass_entry.get(); users = game_data["users"]
        if name in users and users[name].get("password") == pwd:
            game_data["current_user"] = name; player_data = users[name]
            game_data["player_stats"]["score"] = player_data.get("score", 0)
            game_data["player_stats"]["level"] = player_data.get("level", 1)
            game_data["player_stats"]["avatar"] = player_data.get("avatar", os.path.join(AVATAR_FOLDER, DEFAULT_AVATAR))
            game_data["player_stats"]["inventory"] = player_data.get("inventory", {})
            equipped_data = player_data.get("equipped_items", {"weapon": None, "armor": None, "accessories": []})
            if not isinstance(equipped_data.get("accessories"), list): equipped_data["accessories"] = []
            game_data["player_stats"]["equipped_items"] = equipped_data
            game_data["player_stats"]["high_score"] = player_data.get("high_score", 0)
            game_data["player_stats"]["max_hp"] = player_data.get("max_hp", 50)
            game_data["player_stats"]["defeated_bosses"] = player_data.get("defeated_bosses", [])
            calculate_player_stats(); game_data["player_stats"]["current_hp"] = game_data["player_stats"]["final_max_hp"]
            user_home()
        else: messagebox.showerror("登录失败", "无效的用户名或密码。")
    tk.Button(main_frame, text="登录", command=attempt_login, bg="#4CAF50", fg="white", font=("SimHei", 12, "bold"), relief=tk.FLAT, padx=10, pady=3, bd=0, activebackground="#45a049", activeforeground="white").pack(pady=15)
    tk.Button(main_frame, text="返回", command=login_screen, bg="#555555", fg="white", font=("SimHei", 10, "bold"), relief=tk.FLAT, padx=10, pady=3, bd=0, activebackground="#444444", activeforeground="white").pack(pady=5)

def register_ui():
    clear_frame()
    tk.Label(main_frame, text="注册", font=("SimHei", 18), fg="white", bg="#111111").pack(pady=10)
    tk.Label(main_frame, text="用户名：", font=("SimHei", 12), bg="#111111", fg="white").pack()
    name_entry = tk.Entry(main_frame, width=30, bg="#333333", fg="white", insertbackground="white", font=("SimHei", 11))
    name_entry.pack(pady=5)
    tk.Label(main_frame, text="密码：", font=("SimHei", 12), bg="#111111", fg="white").pack()
    pass_entry = tk.Entry(main_frame, show="*", width=30, bg="#333333", fg="white", insertbackground="white", font=("SimHei", 11))
    pass_entry.pack(pady=5)
    selected_avatar_path = [os.path.join(AVATAR_FOLDER, DEFAULT_AVATAR)]
    avatar_preview_label = tk.Label(main_frame, text="已选头像：", font=("SimHei", 12), bg="#111111", fg="white")
    avatar_preview_label.pack(pady=(10, 0))
    avatar_img_label = tk.Label(main_frame, bg="#111111"); avatar_img_label.pack()
    def update_avatar_preview(path):
        selected_avatar_path[0] = path; img = display_avatar(path, (64, 64))
        if img: avatar_img_label.config(image=img); avatar_img_label.image = img
        else: avatar_img_label.config(image='')
    update_avatar_preview(selected_avatar_path[0])
    tk.Label(main_frame, text="选择头像：", font=("SimHei", 12), bg="#111111", fg="white").pack(pady=(10, 5))
    avatar_frame = tk.Frame(main_frame, bg="#222222", bd=1, relief=tk.SUNKEN); avatar_frame.pack(pady=5)
    avatar_canvas = tk.Canvas(avatar_frame, bg="#222222", height=80, width=400, highlightthickness=0)
    scrollbar = tk.Scrollbar(avatar_frame, orient="horizontal", command=avatar_canvas.xview)
    scrollable_frame = tk.Frame(avatar_canvas, bg="#222222")
    scrollable_frame.bind("<Configure>", lambda e: avatar_canvas.configure(scrollregion=avatar_canvas.bbox("all")))
    avatar_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    avatar_canvas.configure(xscrollcommand=scrollbar.set)
    avatar_canvas.pack(side="top", fill="x", expand=True); scrollbar.pack(side="bottom", fill="x")
    col = 0; available_avatars = False
    try: avatar_files = sorted(os.listdir(AVATAR_FOLDER))
    except FileNotFoundError: avatar_files = []; print(f"错误：注册时未找到头像文件夹 '{AVATAR_FOLDER}'。")
    for file in avatar_files:
        if file.lower().endswith((".png", ".jpg", ".jpeg")):
            available_avatars = True; path = os.path.join(AVATAR_FOLDER, file)
            img = display_avatar(path, (50, 50))
            if img:
                btn = tk.Button(scrollable_frame, image=img, command=lambda p=path: update_avatar_preview(p), bg="#444444", bd=1, relief=tk.RAISED, width=50, height=50)
                btn.image = img; btn.grid(row=0, column=col, padx=5, pady=5); col += 1
    if not available_avatars: tk.Label(scrollable_frame, text="在 'avatars' 文件夹中未找到头像。", font=("SimHei", 10), fg="orange", bg="#222222").pack()
    def attempt_register():
        name = name_entry.get().strip(); pwd = pass_entry.get(); avatar = selected_avatar_path[0]
        if not name or not pwd: messagebox.showerror("错误", "用户名和密码不能为空。"); return
        if '|' in name or '|' in pwd: messagebox.showerror("错误", "用户名或密码不能包含 '|' 字符。"); return
        if name in game_data["users"]: messagebox.showerror("错误", "用户名已存在。"); return
        game_data["users"][name] = {"password": pwd, "avatar": avatar, "score": 0, "level": 1, "high_score": 0, "max_hp": 50, "inventory": {"wooden_sword": {"level": 1}, "leather_armor": {"level": 1}}, "equipped_items": {"weapon": "wooden_sword", "armor": "leather_armor", "accessories": []}, "defeated_bosses": []}
        save_users(); messagebox.showinfo("成功", "注册成功！请登录。"); login_screen()
    tk.Button(main_frame, text="注册", command=attempt_register, bg="#2196F3", fg="white", font=("SimHei", 12, "bold"), relief=tk.FLAT, padx=10, pady=3, bd=0, activebackground="#1e88e5", activeforeground="white").pack(pady=15)
    tk.Button(main_frame, text="返回", command=login_screen, bg="#555555", fg="white", font=("SimHei", 10, "bold"), relief=tk.FLAT, padx=10, pady=3, bd=0, activebackground="#444444", activeforeground="white").pack(pady=5)

def user_home():
    clear_frame(); username = game_data["current_user"]
    if not username: login_screen(); return
    stats = game_data["player_stats"]
    info_frame = tk.Frame(main_frame, bg="#222222"); info_frame.pack(fill="x", pady=5)
    avatar_img = display_avatar(stats["avatar"], size=(60, 60))
    if avatar_img: avatar_label = tk.Label(info_frame, image=avatar_img, bg="#222222"); avatar_label.image = avatar_img; avatar_label.pack(side="left", padx=10, pady=5)
    info_text = f"用户：{username}\n等级：{stats['level']} | 积分：{stats['score']} | 最高分：{stats['high_score']}"
    tk.Label(info_frame, text=info_text, font=("SimHei", 12), fg="white", bg="#222222", justify=tk.LEFT).pack(side="left", padx=10)
    calculate_player_stats(); final_max_hp = stats.get('final_max_hp', stats['max_hp']); current_hp = stats['current_hp']
    current_hp = max(0, min(current_hp, final_max_hp)); stats['current_hp'] = current_hp
    hp_text = f"HP: {int(current_hp)} / {int(final_max_hp)}"
    hp_ratio = current_hp / final_max_hp if final_max_hp > 0 else 0
    hp_color = "green" if hp_ratio > 0.6 else "orange" if hp_ratio > 0.3 else "red"
    tk.Label(info_frame, text=hp_text, font=("Helvetica", 12, "bold"), fg=hp_color, bg="#222222").pack(side="right", padx=20)
    tk.Label(main_frame, text=f"欢迎，{username}！", font=("SimHei", 18, "bold"), fg="white", bg="#111111").pack(pady=20)
    button_frame = tk.Frame(main_frame, bg="#111111"); button_frame.pack()
    home_button_style = {"font": ("SimHei", 14, "bold"), "fg": "white", "width": 22, "pady": 6, "relief": tk.FLAT, "bd": 0, "activeforeground": "white"}
    tk.Button(button_frame, text="⚔️ 开始战斗", command=start_game, bg="#c62828", activebackground="#b71c1c", **home_button_style).pack(pady=7)
    tk.Button(button_frame, text="🎒 物品栏/装备", command=inventory_screen, bg="#455A64", activebackground="#37474F", **home_button_style).pack(pady=7)
    tk.Button(button_frame, text="🛒 商店", command=show_shop_ui, bg="#388E3C", activebackground="#2E7D32", **home_button_style).pack(pady=7)
    tk.Button(button_frame, text="🏆 排行榜", command=show_leaderboard_ui, bg="#FFA000", fg="#111111", activebackground="#FF8F00", activeforeground="#111111", font=("SimHei", 14, "bold"), width=22, pady=6, relief=tk.FLAT, bd=0).pack(pady=7)
    secondary_button_style = {"font": ("SimHei", 12, "bold"), "fg": "white", "width": 22, "pady": 5, "relief": tk.FLAT, "bd": 0, "activeforeground": "white"}
    tk.Button(button_frame, text="⚙️ 设置 (更换头像)", command=change_avatar_ui, bg="#546E7A", activebackground="#455A64", **secondary_button_style).pack(pady=7)
    tk.Button(button_frame, text="🚪 登出", command=logout, bg="#616161", activebackground="#424242", **secondary_button_style).pack(pady=7)

def logout():
    username = game_data["current_user"]
    if username and username in game_data["users"]:
        user_data = game_data["users"][username]; stats_to_save = game_data["player_stats"]
        user_data["score"] = stats_to_save["score"]; user_data["level"] = stats_to_save["level"]
        user_data["inventory"] = stats_to_save["inventory"]; user_data["equipped_items"] = stats_to_save["equipped_items"]
        user_data["high_score"] = stats_to_save["high_score"]; user_data["max_hp"] = stats_to_save["max_hp"]
        user_data["defeated_bosses"] = stats_to_save["defeated_bosses"]
        save_users(); save_score(username, stats_to_save["score"])
    game_data["current_user"] = None
    game_data["player_stats"] = {"score": 0, "level": 1, "avatar": os.path.join(AVATAR_FOLDER, DEFAULT_AVATAR), "inventory": {}, "equipped_items": {"weapon": None, "armor": None, "accessories": []}, "max_hp": 50, "current_hp": 50, "high_score": 0, "defeated_bosses": []}
    login_screen()

def change_avatar_ui():
    clear_frame(); username = game_data["current_user"]
    if not username: login_screen(); return
    tk.Label(main_frame, text=f"为 {username} 更换头像", font=("SimHei", 18), fg="white", bg="#111111").pack(pady=10)
    current_avatar_path = game_data["player_stats"]["avatar"]; selected_avatar_path = [current_avatar_path]
    avatar_preview_label = tk.Label(main_frame, text="已选头像：", font=("SimHei", 12), bg="#111111", fg="white"); avatar_preview_label.pack(pady=(10, 0))
    avatar_img_label = tk.Label(main_frame, bg="#111111"); avatar_img_label.pack()
    def update_avatar_preview(path):
        selected_avatar_path[0] = path; img = display_avatar(path, (100, 100))
        if img: avatar_img_label.config(image=img); avatar_img_label.image = img
        else: avatar_img_label.config(image='')
    update_avatar_preview(current_avatar_path)
    tk.Label(main_frame, text="选择新头像：", font=("SimHei", 12), bg="#111111", fg="white").pack(pady=(10, 5))
    avatar_frame = tk.Frame(main_frame, bg="#222222", bd=1, relief=tk.SUNKEN); avatar_frame.pack(pady=5)
    row, col = 0, 0; max_cols = 6
    try: avatar_files = sorted(os.listdir(AVATAR_FOLDER))
    except FileNotFoundError: avatar_files = []; print(f"错误：更换头像时未找到头像文件夹 '{AVATAR_FOLDER}'。")
    for file in avatar_files:
        if file.lower().endswith((".png", ".jpg", ".jpeg")):
            path = os.path.join(AVATAR_FOLDER, file); img = display_avatar(path, (64, 64))
            if img:
                btn = tk.Button(avatar_frame, image=img, command=lambda p=path: update_avatar_preview(p), bg="#444444", bd=1, relief=tk.RAISED, width=64, height=64)
                btn.image = img; btn.grid(row=row, column=col, padx=5, pady=5); col += 1
                if col >= max_cols: col = 0; row += 1
    def save_new_avatar():
        new_avatar = selected_avatar_path[0]
        if new_avatar != game_data["player_stats"]["avatar"]:
            game_data["player_stats"]["avatar"] = new_avatar
            if username in game_data["users"]:
                game_data["users"][username]["avatar"] = new_avatar; save_users()
                messagebox.showinfo("头像已更换", "你的头像已更新。")
            else: messagebox.showerror("错误", "找不到用户数据来保存头像。")
        user_home()
    tk.Button(main_frame, text="保存头像", command=save_new_avatar, bg="#4CAF50", fg="white", font=("SimHei", 12, "bold"), relief=tk.FLAT, padx=10, pady=3, bd=0, activebackground="#45a049", activeforeground="white").pack(pady=15)
    tk.Button(main_frame, text="取消", command=user_home, bg="#777777", fg="white", font=("SimHei", 10, "bold"), relief=tk.FLAT, padx=10, pady=3, bd=0, activebackground="#666666", activeforeground="white").pack(pady=5)

def show_leaderboard_ui():
    clear_frame()
    tk.Label(main_frame, text="🏆 排行榜 🏆", font=("SimHei", 20, "bold"), fg="#FFD700", bg="#111111").pack(pady=15)
    scores = load_scores(); sorted_scores = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    rank_frame = tk.Frame(main_frame, bg="#111111"); rank_frame.pack(pady=10)
    tk.Label(rank_frame, text="排名", font=("SimHei", 12, "bold"), fg="white", bg="#222222", width=5, relief=tk.SOLID, bd=1).grid(row=0, column=0, padx=1, pady=1, sticky="ew")
    tk.Label(rank_frame, text="用户", font=("SimHei", 12, "bold"), fg="white", bg="#222222", width=20, relief=tk.SOLID, bd=1).grid(row=0, column=1, padx=1, pady=1, sticky="ew")
    tk.Label(rank_frame, text="积分", font=("SimHei", 12, "bold"), fg="white", bg="#222222", width=10, relief=tk.SOLID, bd=1).grid(row=0, column=2, padx=1, pady=1, sticky="ew")
    if not sorted_scores: tk.Label(rank_frame, text="暂无积分记录。", font=("SimHei", 11), fg="orange", bg="#333333", columnspan=3).grid(row=1, column=0, pady=10)
    else:
        for i, (user, score) in enumerate(sorted_scores[:10], start=1):
            bg_color = "#333333" if i % 2 == 0 else "#444444"
            tk.Label(rank_frame, text=f"{i}", font=("Helvetica", 11), fg="white", bg=bg_color, width=5, relief=tk.SOLID, bd=1).grid(row=i, column=0, sticky="ew", padx=1, pady=1)
            tk.Label(rank_frame, text=f"{user}", font=("SimHei", 11), fg="white", bg=bg_color, width=20, anchor="w", padx=5, relief=tk.SOLID, bd=1).grid(row=i, column=1, sticky="ew", padx=1, pady=1)
            tk.Label(rank_frame, text=f"{score}", font=("Helvetica", 11), fg="white", bg=bg_color, width=10, relief=tk.SOLID, bd=1).grid(row=i, column=2, sticky="ew", padx=1, pady=1)
    tk.Button(main_frame, text="返回", command=user_home, bg="#555555", fg="white", font=("SimHei", 12, "bold"), relief=tk.FLAT, padx=10, pady=3, bd=0, activebackground="#444444", activeforeground="white").pack(pady=20)

def show_shop_ui():
    clear_frame()
    tk.Label(main_frame, text="🛒 装备商店 🛒", font=("SimHei", 20, "bold"), fg="#4CAF50", bg="#111111").pack(pady=15)
    tk.Label(main_frame, text=f"你的积分：{game_data['player_stats']['score']}", font=("SimHei", 14), fg="white", bg="#111111").pack(pady=5)
    shop_frame = tk.Frame(main_frame, bg="#222222"); shop_frame.pack(pady=10, padx=20, fill="both", expand=True)
    tooltip = None
    def show_tooltip(event, text):
        nonlocal tooltip; 
        if tooltip: tooltip.destroy()
        x, y, _, _ = event.widget.bbox("insert"); x += event.widget.winfo_rootx() + 25; y += event.widget.winfo_rooty() + 20
        tooltip = tk.Toplevel(event.widget); tooltip.wm_overrideredirect(True); tooltip.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tooltip, text=text, justify='left', background="#FFFFE0", relief='solid', borderwidth=1, wraplength=200, font=("SimHei", 9, "normal"))
        label.pack(ipadx=2, ipady=2)
    def hide_tooltip(event): nonlocal tooltip
    if tooltip:
        tooltip.destroy();tooltip = None
    header_frame = tk.Frame(shop_frame, bg="#333333"); header_frame.pack(fill="x", pady=(0, 5))
    tk.Label(header_frame, text="物品", font=("SimHei", 12, "bold"), fg="white", bg="#333333", width=15, anchor="w").pack(side="left", padx=5)
    tk.Label(header_frame, text="等级", font=("SimHei", 12, "bold"), fg="white", bg="#333333", width=5).pack(side="left", padx=5)
    tk.Label(header_frame, text="属性", font=("SimHei", 12, "bold"), fg="white", bg="#333333", width=10).pack(side="left", padx=5)
    tk.Label(header_frame, text="价格", font=("SimHei", 12, "bold"), fg="white", bg="#333333", width=8).pack(side="left", padx=5)
    tk.Label(header_frame, text="操作", font=("SimHei", 12, "bold"), fg="white", bg="#333333", width=10).pack(side="left", padx=5)

    def buy_or_upgrade(item_id):
        item_def = SHOP_ITEMS[item_id]; player_inventory = game_data["player_stats"]["inventory"]
        current_score = game_data["player_stats"]["score"]; username = game_data["current_user"]
        if not username or username not in game_data["users"]: messagebox.showerror("错误", "无法执行操作。未找到用户数据。"); return
        if item_id in player_inventory: 
            current_level = player_inventory[item_id].get("level", 1)
            cost = int(item_def["base_cost"] * current_level * item_def["upgrade_multiplier"])
            if current_score >= cost:
                game_data["player_stats"]["score"] -= cost; player_inventory[item_id]["level"] += 1
                game_data["users"][username]["inventory"] = player_inventory; game_data["users"][username]["score"] = game_data["player_stats"]["score"]
                save_users(); show_shop_ui()
            else: messagebox.showwarning("积分不足", f"你需要 {cost} 积分来升级 {item_def['name']}。")
        else: 
            cost = item_def["base_cost"]
            if current_score >= cost:
                game_data["player_stats"]["score"] -= cost; player_inventory[item_id] = {"level": 1}
                game_data["users"][username]["inventory"] = player_inventory; game_data["users"][username]["score"] = game_data["player_stats"]["score"]
                save_users(); show_shop_ui()
            else: messagebox.showwarning("积分不足", f"你需要 {cost} 积分来购买 {item_def['name']}。")

    player_inventory = game_data["player_stats"]["inventory"]; item_keys = list(SHOP_ITEMS.keys())
    for idx, item_id in enumerate(item_keys):
        item_def = SHOP_ITEMS[item_id]; bg_color = "#444444" if idx % 2 == 0 else "#555555"
        item_frame = tk.Frame(shop_frame, bg=bg_color); item_frame.pack(fill="x", pady=2)
        name_label = tk.Label(item_frame, text=item_def["name"], font=("SimHei", 11), fg="white", bg=bg_color, width=15, anchor="w")
        name_label.pack(side="left", padx=5, pady=3)
        name_label.bind("<Enter>", lambda e, text=item_def['description']: show_tooltip(e, text)); name_label.bind("<Leave>", hide_tooltip)
        level_str = "-"; cost = item_def["base_cost"]; action_text = "购买"; action_bg = "#2196F3"; button_state = tk.NORMAL
        stat_text = f"{item_def['base_stat']:.1f}" if isinstance(item_def['base_stat'], float) else str(item_def['base_stat']); stat_text += f" / Lv 1"
        if item_id in player_inventory:
            level = max(1, player_inventory[item_id].get("level", 1)); level_str = str(level)
            cost = int(item_def["base_cost"] * level * item_def["upgrade_multiplier"]); action_text = "升级"; action_bg = "#FF9800"
            current_stat = item_def["base_stat"] + (item_def["stat_growth"] * (level - 1))
            stat_text = f"{current_stat:.1f}" if isinstance(current_stat, float) else str(int(current_stat)); stat_text += f" / Lv {level}"
        tk.Label(item_frame, text=level_str, font=("Helvetica", 11), fg="white", bg=bg_color, width=5).pack(side="left", padx=5)
        tk.Label(item_frame, text=stat_text, font=("Helvetica", 10), fg="#DDDDDD", bg=bg_color, width=10).pack(side="left", padx=5)
        tk.Label(item_frame, text=str(cost), font=("Helvetica", 11), fg="#FFD700", bg=bg_color, width=8).pack(side="left", padx=5)
        tk.Button(item_frame, text=action_text, command=lambda i=item_id: buy_or_upgrade(i), bg=action_bg, fg="white", font=("SimHei", 10, "bold"), relief=tk.FLAT, width=8, bd=0, state=button_state, activebackground="#1c7fd2" if action_bg=="#2196F3" else "#e88c00", activeforeground="white").pack(side="left", padx=5)
    tk.Button(main_frame, text="返回主界面", command=user_home, bg="#555555", fg="white", font=("SimHei", 12, "bold"), relief=tk.FLAT, padx=10, pady=3, bd=0, activebackground="#444444", activeforeground="white").pack(pady=20)


# --- NEW: Inventory Screen ---
def inventory_screen():
    clear_frame()
    username = game_data["current_user"]
    player_inv = game_data["player_stats"]["inventory"]
    equipped = game_data["player_stats"]["equipped_items"]

    tk.Label(main_frame, text="🎒 物品栏 / 装备 🎒", font=("SimHei", 20, "bold"), fg="#607D8B", bg="#111111").pack(pady=15)

    content_frame = tk.Frame(main_frame, bg="#111111")
    content_frame.pack(fill="both", expand=True, padx=20, pady=10)

    inventory_list_frame = tk.Frame(content_frame, bg="#222222", bd=2, relief=tk.SUNKEN)
    inventory_list_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
    
    equipped_info_frame = tk.Frame(content_frame, bg="#222222", bd=2, relief=tk.SUNKEN, width=280) 
    equipped_info_frame.pack(side="right", fill="y", expand=False) 
    equipped_info_frame.pack_propagate(False) 

    tk.Label(inventory_list_frame, text="所有物品", font=("SimHei", 14, "bold"), fg="white", bg="#333333").pack(fill="x", pady=5)
    
    cols = ("name", "level", "type", "action")
    inventory_tree = ttk.Treeview(inventory_list_frame, columns=cols, show="headings", style="Dark.Treeview")
    style = ttk.Style()
    style.theme_use("clam") 
    style.configure("Dark.Treeview", background="#333333", foreground="white", fieldbackground="#333333", rowheight=25)
    style.map("Dark.Treeview", background=[('selected', '#555555')], foreground=[('selected', 'white')])
    style.configure("Dark.Treeview.Heading", background="#444444", foreground="white", font=("SimHei", 11, "bold"))

    inventory_tree.heading("name", text="名称")
    inventory_tree.heading("level", text="等级")
    inventory_tree.heading("type", text="类型")
    inventory_tree.heading("action", text="操作")
    inventory_tree.column("name", width=150, anchor="w")
    inventory_tree.column("level", width=50, anchor="center")
    inventory_tree.column("type", width=80, anchor="center")
    inventory_tree.column("action", width=100, anchor="center")
    inventory_tree.pack(fill="both", expand=True, padx=5, pady=5)

    def populate_inventory_tree():
        for i in inventory_tree.get_children(): 
            inventory_tree.delete(i)
        
        for item_id, data in player_inv.items():
            if item_id in SHOP_ITEMS:
                item_def = SHOP_ITEMS[item_id]
                level = data.get("level", 1)
                item_type_cn = {"weapon": "武器", "armor": "护甲", "accessory": "饰品"}.get(item_def["type"], "未知")
                action_text = "装备"; is_equipped = False
                if item_def["type"] == "weapon" and equipped["weapon"] == item_id: is_equipped = True
                elif item_def["type"] == "armor" and equipped["armor"] == item_id: is_equipped = True
                elif item_def["type"] == "accessory" and item_id in equipped["accessories"]: is_equipped = True
                if is_equipped: action_text = "卸下"
                inventory_tree.insert("", "end", values=(item_def["name"], level, item_type_cn, action_text), tags=(item_id,))
    
    populate_inventory_tree()

    tk.Label(equipped_info_frame, text="当前装备", font=("SimHei", 14, "bold"), fg="white", bg="#333333").pack(fill="x", pady=5)
    equipped_labels_container = tk.Frame(equipped_info_frame, bg="#222222") 
    equipped_labels_container.pack(fill="x")

    def update_equipped_display():
        for widget in equipped_labels_container.winfo_children(): 
            widget.destroy()
        
        calculate_player_stats() 

        tk.Label(equipped_labels_container, text="武器:", font=("SimHei", 11, "bold"), fg="white", bg="#222222", anchor="w").pack(fill="x", padx=10, pady=(5,0))
        w_name = "无"
        if equipped["weapon"] and equipped["weapon"] in SHOP_ITEMS: w_name = SHOP_ITEMS[equipped["weapon"]]["name"]
        tk.Label(equipped_labels_container, text=w_name, font=("SimHei", 10), fg="#ADD8E6", bg="#222222", anchor="w").pack(fill="x", padx=20)

        tk.Label(equipped_labels_container, text="护甲:", font=("SimHei", 11, "bold"), fg="white", bg="#222222", anchor="w").pack(fill="x", padx=10, pady=(5,0))
        a_name = "无"
        if equipped["armor"] and equipped["armor"] in SHOP_ITEMS: a_name = SHOP_ITEMS[equipped["armor"]]["name"]
        tk.Label(equipped_labels_container, text=a_name, font=("SimHei", 10), fg="#ADD8E6", bg="#222222", anchor="w").pack(fill="x", padx=20)

        tk.Label(equipped_labels_container, text=f"饰品 ({len(equipped['accessories'])}/{MAX_ACCESSORIES_EQUIPPED}):", font=("SimHei", 11, "bold"), fg="white", bg="#222222", anchor="w").pack(fill="x", padx=10, pady=(5,0))
        if not equipped["accessories"]:
            tk.Label(equipped_labels_container, text="无", font=("SimHei", 10), fg="#ADD8E6", bg="#222222", anchor="w").pack(fill="x", padx=20)
        else:
            for acc_id in equipped["accessories"]:
                if acc_id in SHOP_ITEMS:
                    tk.Label(equipped_labels_container, text=f"- {SHOP_ITEMS[acc_id]['name']}", font=("SimHei", 10), fg="#ADD8E6", bg="#222222", anchor="w").pack(fill="x", padx=20)
        
        tk.Label(equipped_labels_container, text="角色属性:", font=("SimHei", 12, "bold"), fg="white", bg="#333333").pack(fill="x", pady=(15,5),_pady=5) 
        stats = game_data["player_stats"]
        tk.Label(equipped_labels_container, text=f"攻击力: {int(stats['calculated_damage'])}", font=("SimHei", 10), fg="white", bg="#222222", anchor="w").pack(fill="x", padx=10)
        tk.Label(equipped_labels_container, text=f"防御力: {int(stats['calculated_defense'])}", font=("SimHei", 10), fg="white", bg="#222222", anchor="w").pack(fill="x", padx=10)
        tk.Label(equipped_labels_container, text=f"最大HP: {int(stats['final_max_hp'])}", font=("SimHei", 10), fg="white", bg="#222222", anchor="w").pack(fill="x", padx=10)

    update_equipped_display() 

    def on_item_select(event):
        selected_tree_item = inventory_tree.focus() 
        if not selected_tree_item: return
        item_id_tuple = inventory_tree.item(selected_tree_item, "tags")
        if not item_id_tuple: return 
        item_id = item_id_tuple[0]

        if not item_id or item_id not in SHOP_ITEMS: return
        item_def = SHOP_ITEMS[item_id]; item_type = item_def["type"]

        if item_type == "weapon":
            if equipped["weapon"] == item_id: equipped["weapon"] = None
            else: equipped["weapon"] = item_id
        elif item_type == "armor":
            if equipped["armor"] == item_id: equipped["armor"] = None
            else: equipped["armor"] = item_id
        elif item_type == "accessory":
            if item_id in equipped["accessories"]: equipped["accessories"].remove(item_id)
            else: 
                if len(equipped["accessories"]) < MAX_ACCESSORIES_EQUIPPED:
                    equipped["accessories"].append(item_id)
                else:
                    messagebox.showwarning("饰品槽已满", f"你最多只能装备 {MAX_ACCESSORIES_EQUIPPED} 件饰品。")
                    return 
        
        game_data["users"][username]["equipped_items"] = equipped
        save_users()
        populate_inventory_tree() 
        update_equipped_display() 

    inventory_tree.bind("<<TreeviewSelect>>", on_item_select) 
    tk.Button(main_frame, text="返回主界面", command=user_home, bg="#555555", fg="white", font=("SimHei", 12, "bold"), relief=tk.FLAT, padx=10, pady=3, bd=0, activebackground="#444444", activeforeground="white").pack(pady=15, side=tk.BOTTOM)


# --- start_game and combat logic ---
def start_game():
    clear_frame(); stats = game_data["player_stats"]; username = game_data["current_user"]
    if not username: login_screen(); return
    calculate_player_stats(); stats["current_hp"] = stats["final_max_hp"]
    player_level = stats["level"]
    is_boss_level = (player_level % BOSS_LEVEL_INTERVAL == 0) and (player_level in BOSS_TYPES)
    defeated_bosses_list = stats.get("defeated_bosses", [])
    if not isinstance(defeated_bosses_list, list): defeated_bosses_list = []; stats["defeated_bosses"] = defeated_bosses_list; print(f"警告：用户 {username} 的 defeated_bosses 不是列表。已重置。")
    boss_already_defeated = player_level in defeated_bosses_list
    is_boss_fight = False; enemy_level = player_level; enemy_display_name = ""

    if is_boss_level and not boss_already_defeated:
        boss_data = BOSS_TYPES[player_level]; enemy_display_name = boss_data["name"]
        enemy_max_hp = boss_data["hp"]; enemy_hp = enemy_max_hp; enemy_attack = boss_data["attack"]
        enemy_defense = boss_data["defense"]; enemy_score_reward = boss_data["score_reward"]; is_boss_fight = True
        tk.Label(main_frame, text=f"🚨 首领战！ 🚨\n等级 {player_level}：{enemy_display_name}", font=("SimHei", 20, "bold"), fg="#FF00FF", bg="#111111", justify=tk.CENTER).pack(pady=15)
    else:
        available_enemies = list(REGULAR_ENEMY_TYPES.keys())
        if not available_enemies: messagebox.showerror("错误", "没有定义普通敌人类型！"); user_home(); return
        chosen_enemy_key = random.choice(available_enemies); enemy_base = REGULAR_ENEMY_TYPES[chosen_enemy_key]
        enemy_name_cn = enemy_base.get("name_cn", chosen_enemy_key)
        scale_factor = (1 + 0.15 * (enemy_level - 1)); enemy_display_name = f"{enemy_level}级 {enemy_name_cn}"
        enemy_max_hp = int(enemy_base["hp"] * scale_factor); enemy_hp = enemy_max_hp
        enemy_attack = int(enemy_base["attack"] * scale_factor); enemy_defense = int(enemy_base.get("defense", 0) * scale_factor)
        enemy_score_reward = int(enemy_base["score"] * (1 + 0.1 * (enemy_level - 1)))
        tk.Label(main_frame, text=f"正在对战 {enemy_display_name}！", font=("SimHei", 18, "bold"), fg="#cc4444", bg="#111111").pack(pady=15)

    combat_info_frame = tk.Frame(main_frame, bg="#222222"); combat_info_frame.pack(pady=10, padx=20, fill="x")
    player_hp_label = tk.Label(combat_info_frame, text=f"你的HP: {int(stats['current_hp'])}/{int(stats['final_max_hp'])}", font=("SimHei", 12), fg="green", bg="#222222")
    player_hp_label.pack(side="left", padx=20)
    enemy_hp_label = tk.Label(combat_info_frame, text=f"敌人HP: {int(enemy_hp)}/{int(enemy_max_hp)}", font=("SimHei", 12), fg="red", bg="#222222")
    enemy_hp_label.pack(side="right", padx=20)
    log_frame = tk.Frame(main_frame, bg="#1a1a1a", height=150, bd=1, relief=tk.SUNKEN); log_frame.pack(pady=10, padx=20, fill="x")
    log_text = tk.Text(log_frame, height=8, width=70, bg="#1a1a1a", fg="white", state="disabled", wrap=tk.WORD, font=("SimHei", 10), bd=0, highlightthickness=0)
    log_text.pack(padx=5, pady=5, fill="both", expand=True)
    log_text.tag_configure("default", foreground="white"); log_text.tag_configure("player_attack", foreground="cyan"); log_text.tag_configure("enemy_attack", foreground="red")
    log_text.tag_configure("defense", foreground="grey"); log_text.tag_configure("win", foreground="yellow"); log_text.tag_configure("boss_win", foreground="lime green")
    log_text.tag_configure("lose", foreground="#FF5733"); log_text.tag_configure("flee", foreground="orange"); log_text.tag_configure("level_up", foreground="magenta"); log_text.tag_configure("info", foreground="#CCCCCC")
    def add_log(message, tag="default"): log_text.config(state="normal"); log_text.insert(tk.END, message + "\n", tag); log_text.see(tk.END); log_text.config(state="disabled")
    add_log(f"野生的 {enemy_display_name} 出现了！", "info")
    action_frame = tk.Frame(main_frame, bg="#111111"); action_frame.pack(pady=10)
    combat_button_style = {"font": ("SimHei", 12, "bold"), "fg": "white", "width": 12, "height": 2, "relief": tk.FLAT, "bd": 0, "activeforeground": "white"}
    attack_button = tk.Button(action_frame, text="⚔️ 攻击", command=lambda: player_turn(), bg="#c62828", activebackground="#b71c1c", **combat_button_style)
    flee_button = tk.Button(action_frame, text="🏃 逃跑", command=lambda: flee(), bg="#616161", activebackground="#424242", **combat_button_style)
    continue_button = tk.Button(action_frame, text="继续 ✔️", command=user_home, bg="#388E3C", activebackground="#2E7D32", **combat_button_style)
    return_hub_button = tk.Button(action_frame, text="返回主界面", command=user_home, bg="#455A64", activebackground="#37474F", **combat_button_style)
    attack_button.pack(side="left", padx=10); flee_button.pack(side="left", padx=10)

    def update_hp_labels():
        player_hp_label.config(text=f"你的HP: {int(stats['current_hp'])}/{int(stats['final_max_hp'])}"); enemy_hp_label.config(text=f"敌人HP: {int(enemy_hp)}/{int(enemy_max_hp)}")
        hp_ratio = stats['current_hp'] / stats['final_max_hp'] if stats['final_max_hp'] > 0 else 0
        hp_color = "green" if hp_ratio > 0.6 else "orange" if hp_ratio > 0.3 else "red"; player_hp_label.config(fg=hp_color)

    def player_turn():
        nonlocal enemy_hp; attack_button.config(state="disabled"); flee_button.config(state="disabled")
        player_damage, _ = calculate_player_stats(); damage_dealt = random.randint(int(player_damage * 0.8), int(player_damage * 1.2))
        actual_damage = max(0, damage_dealt - enemy_defense); enemy_hp -= actual_damage; enemy_hp = max(0, enemy_hp)
        add_log(f"你对 {enemy_display_name} 造成了 {actual_damage} 点伤害！", "player_attack"); update_hp_labels()
        if enemy_hp <= 0: win_combat()
        else: root.after(800, enemy_turn)

    def enemy_turn():
        nonlocal enemy_hp; enemy_base_dmg = enemy_attack; damage_dealt_by_enemy = random.randint(int(enemy_base_dmg * 0.8), int(enemy_base_dmg * 1.2))
        _, player_defense = calculate_player_stats(); damage_taken = max(0, damage_dealt_by_enemy - int(player_defense))
        stats["current_hp"] -= damage_taken; stats["current_hp"] = max(0, stats["current_hp"])
        if damage_taken > 0: add_log(f"{enemy_display_name} 对你造成了 {damage_taken} 点伤害！", "enemy_attack"); blocked_damage = damage_dealt_by_enemy - damage_taken
        if blocked_damage > 0: add_log(f"（你的护甲抵挡了 {blocked_damage} 点伤害！）", "defense")
        else: add_log(f"{enemy_display_name} 的攻击被你的护甲弹开了！", "defense")
        update_hp_labels()
        if stats["current_hp"] <= 0: lose_combat()
        else: attack_button.config(state="normal"); flee_button.config(state="normal")

    def win_combat():
        attack_button.pack_forget(); flee_button.pack_forget(); needs_user_save = False
        if is_boss_fight:
            add_log(f"胜利！你击败了首领：{enemy_display_name}！", "boss_win"); stats["score"] += enemy_score_reward
            add_log(f"你获得了 {enemy_score_reward} 点巨额积分！", "boss_win")
            if player_level not in stats["defeated_bosses"]: stats["defeated_bosses"].append(player_level); needs_user_save = True
            stats["level"] += 1; stats["max_hp"] += 15; calculate_player_stats(); stats["current_hp"] = stats["final_max_hp"]
            add_log(f"升级！你达到了 {stats['level']} 级！", "level_up"); add_log(f"最大生命值大幅提升！生命值已回满！", "level_up"); needs_user_save = True
        else:
            add_log(f"你击败了 {enemy_display_name}！", "win"); stats["score"] += enemy_score_reward
            add_log(f"你获得了 {enemy_score_reward} 点积分。", "win")
            score_needed_for_next_level = 100 + ((stats["level"])**2 * 50)
            if stats["score"] >= score_needed_for_next_level:
                stats["level"] += 1; stats["max_hp"] += 5; calculate_player_stats(); stats["current_hp"] = stats["final_max_hp"]
                add_log(f"升级！你达到了 {stats['level']} 级！", "level_up"); add_log(f"最大生命值提升！生命值已回满！", "level_up"); needs_user_save = True
        if save_score(game_data["current_user"], stats["score"]): needs_user_save = True
        if needs_user_save and username in game_data["users"]:
             user_data = game_data["users"][username]; user_data["score"] = stats["score"]; user_data["level"] = stats["level"]
             user_data["max_hp"] = stats["max_hp"]; user_data["defeated_bosses"] = stats["defeated_bosses"]; user_data["high_score"] = stats["high_score"]
             user_data["equipped_items"] = game_data["player_stats"]["equipped_items"] 
             save_users()
        continue_button.pack(side="left", padx=10)

    def lose_combat():
        attack_button.pack_forget(); flee_button.pack_forget(); add_log("你被击败了！", "lose")
        score_loss = max(10, int(stats["score"] * 0.1)); stats["score"] = max(0, stats["score"] - score_loss)
        add_log(f"你失去了 {score_loss} 点积分。", "lose"); needs_user_save = save_score(game_data["current_user"], stats["score"])
        if username in game_data["users"]:
             game_data["users"][username]["score"] = stats["score"]
             if needs_user_save: game_data["users"][username]["high_score"] = stats["high_score"]; save_users()
        return_hub_button.pack(side="left", padx=10)

    def flee():
        attack_button.pack_forget(); flee_button.pack_forget(); add_log("你逃离了战斗！", "flee")
        return_hub_button.pack(side="left", padx=10)

# --- Main Application Setup ---
root = tk.Tk()
root.title("巫师冒险")
root.geometry("800x700") 
root.configure(bg="#111111")
main_frame = tk.Frame(root, bg="#111111")
main_frame.pack(fill="both", expand=True)
login_screen()
root.mainloop()
