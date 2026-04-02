# -*- coding: utf-8 -*-
# --- 巫师游戏完整版 (包含商店、装备属性、增强UI、头像选择器、物品出售、金币系统、设置菜单和等级解锁BOSS) ---

import tkinter as tk
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk
import os
import json
import random
from collections import OrderedDict # 用于按顺序处理BOSS

# --- 配置 ---
USERS_FILE = "users.json"
SCORES_FILE = "scores.txt"
AVATAR_FOLDER = "avatars"
DEFAULT_AVATAR = "default.png"
SELL_PERCENTAGE = 0.3
STARTING_GOLD = 10

# --- 按钮样式 ---
STONE_BG = "#A9A9A9"; STONE_ACTIVE_BG = "#8B8989"; STONE_FG = "#222222"
STONE_RELIEF = tk.RIDGE; STONE_BORDERWIDTH = 3

# --- 确保头像文件夹存在 ---
if not os.path.exists(AVATAR_FOLDER):
    os.makedirs(AVATAR_FOLDER)
    print(f"已创建 '{AVATAR_FOLDER}' 文件夹。请添加一些 .png 或 .jpg 图片作为头像。")

# --- 游戏数据 (全局状态) ---
game_data = {
    "current_user": None, "users": {},
    "player_stats": {
        "score": 0, "level": 1, "gold": 0, "avatar": os.path.join(AVATAR_FOLDER, DEFAULT_AVATAR),
        "inventory": {}, "max_hp": 50, "current_hp": 50, "high_score": 0,
        "defeated_bosses": [] # 新增：追踪已击败的BOSS ID列表
    }
}

# --- 商店物品定义 ---
SHOP_ITEMS = {
    "wooden_sword": {"name": "木剑", "type": "weapon", "description": "一把基础的剑。", "base_cost": 20, "upgrade_multiplier": 1.2, "base_stat": 2, "stat_growth": 1},
    "iron_sword": {"name": "铁剑", "type": "weapon", "description": "一把更坚固的剑。", "base_cost": 100, "upgrade_multiplier": 1.5, "base_stat": 5, "stat_growth": 2},
    "steel_sword": {"name": "钢剑", "type": "weapon", "description": "精心锻造的利剑。", "base_cost": 350, "upgrade_multiplier": 1.7, "base_stat": 10, "stat_growth": 3},
    "basic_wand": {"name": "基础魔杖", "type": "weapon", "description": "引导微弱的魔法。", "base_cost": 50, "upgrade_multiplier": 1.3, "base_stat": 3, "stat_growth": 1.5},
    "fire_wand": {"name": "火焰魔杖", "type": "weapon", "description": "蕴含火焰力量的魔杖。", "base_cost": 250, "upgrade_multiplier": 1.6, "base_stat": 7, "stat_growth": 2.5},
    "battle_axe": {"name": "战斧", "type": "weapon", "description": "沉重但威力巨大。", "base_cost": 400, "upgrade_multiplier": 1.8, "base_stat": 12, "stat_growth": 3.5},
    "leather_armor": {"name": "皮甲", "type": "armor", "description": "简单的保护。", "base_cost": 30, "upgrade_multiplier": 1.2, "base_stat": 1, "stat_growth": 0.5},
    "chainmail_armor": {"name": "锁子甲", "type": "armor", "description": "更好的保护。", "base_cost": 150, "upgrade_multiplier": 1.6, "base_stat": 3, "stat_growth": 1},
    "steel_armor": {"name": "钢甲", "type": "armor", "description": "坚固的钢制盔甲。", "base_cost": 450, "upgrade_multiplier": 1.8, "base_stat": 6, "stat_growth": 1.5},
    "magic_robe": {"name": "魔法长袍", "type": "armor", "description": "附魔布料制成，防御力尚可。", "base_cost": 300, "upgrade_multiplier": 1.5, "base_stat": 4, "stat_growth": 1.2},
    "health_amulet": {"name": "生命护符", "type": "accessory", "description": "增加最大生命值。", "base_cost": 80, "upgrade_multiplier": 1.4, "base_stat": 10, "stat_growth": 5},
    "strength_ring": {"name": "力量戒指", "type": "accessory", "description": "略微增加攻击力。", "base_cost": 200, "upgrade_multiplier": 1.5, "base_stat": 1, "stat_growth": 0.5},
    "defense_amulet": {"name": "防御护符", "type": "accessory", "description": "略微增加防御力。", "base_cost": 220, "upgrade_multiplier": 1.5, "base_stat": 0.5, "stat_growth": 0.25}
}

# --- BOSS 定义 ---
# 使用 OrderedDict 确保按等级顺序检查
BOSSES = OrderedDict([
    ("goblin_king", {
        "name": "哥布林王", "required_level": 10,
        "hp": 200, "attack": 15, "defense": 5,
        "score_reward": 500, "gold_reward": 250,
        "description": "戴着歪斜王冠的巨大哥布林，脾气暴躁。"
    }),
    ("ogre_chieftain", {
        "name": "食人魔酋长", "required_level": 20,
        "hp": 500, "attack": 25, "defense": 10,
        "score_reward": 1500, "gold_reward": 700,
        "description": "挥舞着巨大棒槌的食人魔首领，皮糙肉厚。"
    }),
    ("lich_sorcerer", {
        "name": "巫妖法师", "required_level": 30,
        "hp": 400, "attack": 35, "defense": 8, # HP 稍低，攻击高
        "score_reward": 3000, "gold_reward": 1500,
        "description": "不死巫妖，掌握着黑暗魔法，攻击致命。"
    }),
    ("metal_ogre", {
        "name": "金刚巨猿", "required_level": 40,
        "hp": 700, "attack": 45, "defense": 50,
        "score_reward": 5000, "gold_reward": 4500,
        "description": "古老的巨猿，被金刚之恶魔所附身。"
    }),
    ("", {
        "name": "北海龙王", "required_level": 50,
        "hp": 1200, "attack": 50, "defense": 20,
        "score_reward": 10000, "gold_reward": 5000,
        "description": "古老的龙王，喷出来的水可以腐蚀掉钢铁。"
    }),
    ("", {
        "name": "南海龙王", "required_level": 60,
        "hp": 1500, "attack": 70, "defense": 30,
        "score_reward": 12000, "gold_reward": 6000,
        "description": "古老的龙王，喷出来的水可以腐蚀掉钢铁。"
    }),
    ("", {
        "name": "西海龙王", "required_level": 70,
        "hp": 1800, "attack": 90, "defense": 40,
        "score_reward": 14000, "gold_reward": 7000,
        "description": "古老的龙王，喷出来的水可以腐蚀掉钢铁。"
    }),
    ("", {
        "name": "东海龙王", "required_level": 80,
        "hp": 2000, "attack": 110, "defense": 50,
        "score_reward": 16000, "gold_reward": 5000,
        "description": "古老的龙王，喷出来的水可以腐蚀掉钢铁。"
    }),
    ("", {
        "name": "咕噜巨兽", "required_level": 90,
        "hp": 2500, "attack": 150, "defense": 100,
        "score_reward": 1000000, "gold_reward": 500000,
        "description": "古老的石头生物咕噜，组合起来生成了咕噜巨兽。"
    }),
    ("", {
        "name": "火龙王", "required_level": 100,
        "hp": 3000, "attack": 500, "defense": 120,
        "score_reward": 10000000, "gold_reward": 5000000,
        "description": "古老的龙王，喷出来的火可以融化钢铁。"
    }),
    ("", {
        "name": "恶魔巨龙", "required_level": 1000,
        "hp": 30000, "attack": 5000, "defense": 1200,
        "score_reward": 100000000, "gold_reward": 50000000,
        "description": "古老的龙，释放的邪念可以控制别人。"
    }),
    
])


# --- 数据处理函数 ---
def load_users():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r", encoding="utf-8") as f: return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError): print(f"警告：无法加载或解码 {USERS_FILE}。将重新开始。"); return {}
    return {}
def save_users():
    try:
        with open(USERS_FILE, "w", encoding="utf-8") as f: json.dump(game_data["users"], f, indent=4, ensure_ascii=False)
    except IOError as e: messagebox.showerror("保存错误", f"无法保存用户数据：{e}")
def load_scores():
    scores = {};
    if os.path.exists(SCORES_FILE):
        with open(SCORES_FILE, "r", encoding="utf-8") as f:
            for line in f: parts = line.strip().split("|");
            if len(parts) == 2: user, score_str = parts;
            try: score = int(score_str); scores[user] = max(score, scores.get(user, 0))
            except ValueError: print(f"跳过无效的积分行：{line.strip()}")
    return scores
def save_score(user, score):
    if user in game_data["users"]:
         current_high = game_data["users"][user].get("high_score", 0)
         if score > current_high: game_data["users"][user]["high_score"] = score; game_data["player_stats"]["high_score"] = score
    scores = load_scores(); scores[user] = max(score, scores.get(user, 0))
    try:
        with open(SCORES_FILE, "w", encoding="utf-8") as f:
            for u, s in scores.items(): f.write(f"{u}|{s}\n")
    except IOError as e: messagebox.showerror("保存错误", f"无法保存积分：{e}")
def update_username_in_scores(old_username, new_username):
    scores = load_scores()
    if old_username in scores:
        score_value = scores[old_username]; del scores[old_username]
        scores[new_username] = max(score_value, scores.get(new_username, 0))
        try:
            with open(SCORES_FILE, "w", encoding="utf-8") as f:
                for u, s in scores.items(): f.write(f"{u}|{s}\n")
            print(f"分数文件中的用户名已从 '{old_username}' 更新为 '{new_username}'。")
        except IOError as e: messagebox.showerror("保存错误", f"无法更新分数文件中的用户名：{e}")
    else: print(f"在分数文件中未找到旧用户名 '{old_username}'，无需更新。")

# --- UI 辅助函数 ---
def clear_frame(frame=None): target_frame = frame or main_frame; [widget.destroy() for widget in target_frame.winfo_children()]
def display_avatar(path, size=(100, 100)):
    try:
        if not path or not os.path.exists(path): path = os.path.join(AVATAR_FOLDER, DEFAULT_AVATAR)
        if not os.path.exists(path): return None
        img = Image.open(path); img = img.resize(size, Image.Resampling.LANCZOS); return ImageTk.PhotoImage(img)
    except Exception as e:
        print(f"加载图片 {path} 时出错：{e}")
        try: img = Image.open(os.path.join(AVATAR_FOLDER, DEFAULT_AVATAR)); img = img.resize(size, Image.Resampling.LANCZOS); return ImageTk.PhotoImage(img)
        except Exception: print(f"错误：默认头像 '{DEFAULT_AVATAR}' 也找不到或无法加载。"); return None

# --- 玩家属性计算 ---
def calculate_player_stats():
    inventory = game_data["player_stats"]["inventory"]; total_damage = 0; total_defense = 0; added_max_hp = 0; accessory_damage_bonus = 0; accessory_defense_bonus = 0
    for item_id, data in inventory.items():
        if item_id in SHOP_ITEMS: item_def = SHOP_ITEMS[item_id]; level = data.get("level", 1); stat_value = item_def["base_stat"] + (item_def["stat_growth"] * (level - 1))
        if item_def["type"] == "weapon": total_damage += stat_value
        elif item_def["type"] == "armor": total_defense += stat_value
        elif item_def["type"] == "accessory":
                 if item_id == "health_amulet": added_max_hp += stat_value
                 elif item_id == "strength_ring": accessory_damage_bonus += stat_value
                 elif item_id == "defense_amulet": accessory_defense_bonus += stat_value
    base_damage = 1; base_defense = 0; base_hp = 50
    game_data["player_stats"]["calculated_damage"] = base_damage + total_damage + accessory_damage_bonus
    game_data["player_stats"]["calculated_defense"] = base_defense + total_defense + accessory_defense_bonus
    game_data["player_stats"]["max_hp"] = base_hp + added_max_hp
    game_data["player_stats"]["current_hp"] = min(game_data["player_stats"]["current_hp"], game_data["player_stats"]["max_hp"])
    return game_data["player_stats"]["calculated_damage"], game_data["player_stats"]["calculated_defense"]

# --- 商店辅助函数 ---
def calculate_upgrade_cost(item_id, current_level):
    if item_id not in SHOP_ITEMS: return 0
    item_def = SHOP_ITEMS[item_id]; cost = int(item_def["base_cost"] * current_level * item_def["upgrade_multiplier"]); return cost
def calculate_sell_price(item_id):
    if item_id not in game_data["player_stats"]["inventory"] or item_id not in SHOP_ITEMS: return 0
    item_def = SHOP_ITEMS[item_id]; current_level = game_data["player_stats"]["inventory"][item_id]["level"]
    cost_basis = calculate_upgrade_cost(item_id, current_level); sell_price = int(cost_basis * SELL_PERCENTAGE); return max(1, sell_price)

# --- 创建风格化按钮的辅助函数 ---
def create_styled_button(parent, text, command, width=None, font_size=12, **kwargs):
    bg = kwargs.get("bg", STONE_BG); fg = kwargs.get("fg", STONE_FG); active_bg = kwargs.get("activebackground", STONE_ACTIVE_BG)
    relief = kwargs.get("relief", STONE_RELIEF); bd = kwargs.get("bd", STONE_BORDERWIDTH); font_family = kwargs.get("font_family", "微软雅黑")
    button = tk.Button(parent, text=text, command=command, font=(font_family, font_size, "bold"), bg=bg, fg=fg, activebackground=active_bg, activeforeground=fg, relief=relief, bd=bd, width=width if width else 0, padx=kwargs.get("padx", 10), pady=kwargs.get("pady", 5))
    # 将 state 参数传递给按钮
    if 'state' in kwargs: button.config(state=kwargs['state'])
    return button

# --- BOSS 相关函数 ---
def get_available_boss():
    """查找当前玩家可挑战的下一个未击败的BOSS。"""
    player_level = game_data["player_stats"]["level"]
    defeated = game_data["player_stats"]["defeated_bosses"]
    for boss_id, boss_data in BOSSES.items():
        if player_level >= boss_data["required_level"] and boss_id not in defeated:
            return boss_id # 返回第一个符合条件的BOSS ID
    return None # 没有可挑战的BOSS

# --- UI 屏幕 ---

def login_screen():
    clear_frame(); game_data["current_user"] = None; game_data["users"] = load_users()
    tk.Label(main_frame, text="巫师冒险", font=("微软雅黑", 24, "bold"), fg="#FFD700", bg="#111111").pack(pady=20)
    create_styled_button(main_frame, text="登录", command=login_ui, width=20, font_size=14, bg="#558B2F", activebackground="#33691E", fg="white").pack(pady=10)
    create_styled_button(main_frame, text="注册", command=register_ui, width=20, font_size=14, bg="#4682B4", activebackground="#2E5A87", fg="white").pack(pady=10)
    create_styled_button(main_frame, text="退出", command=root.quit, width=15, font_size=12, bg="#B22222", activebackground="#8B0000", fg="white").pack(pady=20)

def login_ui():
    clear_frame(); tk.Label(main_frame, text="登录", font=("微软雅黑", 18), fg="white", bg="#111111").pack(pady=10)
    tk.Label(main_frame, text="用户名:", font=("微软雅黑", 11), bg="#111111", fg="white").pack()
    name_entry = tk.Entry(main_frame, width=30, bg="#333333", fg="white", insertbackground="white", font=("微软雅黑", 10)); name_entry.pack(pady=5)
    tk.Label(main_frame, text="密码:", font=("微软雅黑", 11), bg="#111111", fg="white").pack()
    pass_entry = tk.Entry(main_frame, show="*", width=30, bg="#333333", fg="white", insertbackground="white", font=("微软雅黑", 10)); pass_entry.pack(pady=5)
    def attempt_login():
        name = name_entry.get(); pwd = pass_entry.get(); users = game_data["users"]
        if name in users and users[name]["password"] == pwd:
            game_data["current_user"] = name; player_data = users[name]
            game_data["player_stats"]["score"] = player_data.get("score", 0); game_data["player_stats"]["level"] = player_data.get("level", 1)
            game_data["player_stats"]["gold"] = player_data.get("gold", 0); game_data["player_stats"]["avatar"] = player_data.get("avatar", os.path.join(AVATAR_FOLDER, DEFAULT_AVATAR))
            game_data["player_stats"]["inventory"] = player_data.get("inventory", {}); game_data["player_stats"]["high_score"] = player_data.get("high_score", 0)
            game_data["player_stats"]["defeated_bosses"] = player_data.get("defeated_bosses", []) # 加载已击败BOSS列表
            calculate_player_stats(); game_data["player_stats"]["current_hp"] = player_data.get("current_hp", game_data["player_stats"]["max_hp"])
            game_data["player_stats"]["current_hp"] = min(game_data["player_stats"]["current_hp"], game_data["player_stats"]["max_hp"]); user_home()
        else: messagebox.showerror("登录失败", "用户名或密码无效。")
    create_styled_button(main_frame, text="登录", command=attempt_login, font_size=12, bg="#558B2F", activebackground="#33691E", fg="white").pack(pady=15)
    create_styled_button(main_frame, text="返回", command=login_screen, font_size=10).pack(pady=5)

def register_ui():
    clear_frame(); tk.Label(main_frame, text="注册", font=("微软雅黑", 18), fg="white", bg="#111111").pack(pady=10)
    tk.Label(main_frame, text="用户名:", font=("微软雅黑", 11), bg="#111111", fg="white").pack()
    name_entry = tk.Entry(main_frame, width=30, bg="#333333", fg="white", insertbackground="white", font=("微软雅黑", 10)); name_entry.pack(pady=5)
    tk.Label(main_frame, text="密码:", font=("微软雅黑", 11), bg="#111111", fg="white").pack()
    pass_entry = tk.Entry(main_frame, show="*", width=30, bg="#333333", fg="white", insertbackground="white", font=("微软雅黑", 10)); pass_entry.pack(pady=5)
    selected_avatar_path = [os.path.join(AVATAR_FOLDER, DEFAULT_AVATAR)]
    avatar_preview_label = tk.Label(main_frame, text="已选头像:", font=("微软雅黑", 11), bg="#111111", fg="white"); avatar_preview_label.pack(pady=(10, 0))
    avatar_img_label = tk.Label(main_frame, bg="#111111"); avatar_img_label.pack()
    def update_avatar_preview(path): selected_avatar_path[0] = path; img = display_avatar(path, (64, 64)); avatar_img_label.config(image=img if img else ''); avatar_img_label.image = img
    update_avatar_preview(selected_avatar_path[0])
    tk.Label(main_frame, text="选择头像:", font=("微软雅黑", 11), bg="#111111", fg="white").pack(pady=(10, 5))
    avatar_frame = tk.Frame(main_frame, bg="#222222", bd=1, relief=tk.SUNKEN); avatar_frame.pack(pady=5)
    avatar_canvas = tk.Canvas(avatar_frame, bg="#222222", height=80, width=400, highlightthickness=0); scrollbar = tk.Scrollbar(avatar_frame, orient="horizontal", command=avatar_canvas.xview)
    scrollable_frame = tk.Frame(avatar_canvas, bg="#222222"); scrollable_frame.bind("<Configure>", lambda e: avatar_canvas.configure(scrollregion=avatar_canvas.bbox("all")))
    avatar_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw"); avatar_canvas.configure(xscrollcommand=scrollbar.set); avatar_canvas.pack(side="top", fill="x", expand=True); scrollbar.pack(side="bottom", fill="x")
    col = 0; available_avatars = False
    for file in sorted(os.listdir(AVATAR_FOLDER)):
        if file.lower().endswith((".png", ".jpg", ".jpeg")): available_avatars = True; path = os.path.join(AVATAR_FOLDER, file); img = display_avatar(path, (50, 50))
        if img: btn = tk.Button(scrollable_frame, image=img, command=lambda p=path: update_avatar_preview(p), bg="#444444", bd=1, relief=tk.RAISED, width=50, height=50); btn.image = img; btn.grid(row=0, column=col, padx=5, pady=5); col += 1
    if not available_avatars: tk.Label(scrollable_frame, text="在 'avatars' 文件夹中找不到头像。", font=("微软雅黑", 9), fg="orange", bg="#222222").pack()
    def attempt_register():
        name = name_entry.get().strip(); pwd = pass_entry.get(); avatar = selected_avatar_path[0]
        if not name or not pwd: messagebox.showerror("错误", "用户名和密码不能为空。"); return
        if '|' in name or '|' in pwd: messagebox.showerror("错误", "用户名或密码不能包含 '|' 字符。"); return
        if name in game_data["users"]: messagebox.showerror("错误", "用户名已存在。"); return
        game_data["users"][name] = {"password": pwd, "avatar": avatar, "score": 0, "level": 1, "high_score": 0, "gold": STARTING_GOLD, "inventory": {"wooden_sword": {"level": 1}, "leather_armor": {"level": 1}}, "current_hp": 50, "defeated_bosses": []} # 初始化 defeated_bosses
        save_users(); messagebox.showinfo("成功", "注册成功！请登录。"); login_screen()
    create_styled_button(main_frame, text="注册", command=attempt_register, font_size=12, bg="#4682B4", activebackground="#2E5A87", fg="white").pack(pady=15)
    create_styled_button(main_frame, text="返回", command=login_screen, font_size=10).pack(pady=5)

def user_home():
    clear_frame(); username = game_data["current_user"]; stats = game_data["player_stats"]
    info_frame = tk.Frame(main_frame, bg="#222222"); info_frame.pack(fill="x", pady=5)
    avatar_img = display_avatar(stats["avatar"], size=(60, 60))
    if avatar_img: avatar_label = tk.Label(info_frame, image=avatar_img, bg="#222222"); avatar_label.image = avatar_img; avatar_label.pack(side="left", padx=10, pady=5)
    info_text = f"用户: {username}\n等级: {stats['level']} | 积分: {stats['score']} | 金币: {stats['gold']} 💰 | 最高分: {stats['high_score']}"
    tk.Label(info_frame, text=info_text, font=("微软雅黑", 11), fg="white", bg="#222222", justify=tk.LEFT).pack(side="left", padx=10)
    calculate_player_stats(); stats["current_hp"] = min(stats["current_hp"], stats["max_hp"])
    hp_text = f"生命值: {stats['current_hp']} / {stats['max_hp']}"
    hp_ratio = stats["current_hp"] / stats["max_hp"] if stats["max_hp"] > 0 else 0
    hp_color = "green" if hp_ratio > 0.6 else "orange" if hp_ratio > 0.3 else "red"
    tk.Label(info_frame, text=hp_text, font=("微软雅黑", 11, "bold"), fg=hp_color, bg="#222222").pack(side="right", padx=20)
    tk.Label(main_frame, text=f"欢迎，{username}！", font=("微软雅黑", 18, "bold"), fg="white", bg="#111111").pack(pady=20)

    button_frame = tk.Frame(main_frame, bg="#111111"); button_frame.pack()
    create_styled_button(button_frame, text="⚔️ 开始战斗", command=start_game, font_size=14, width=20, bg="#B22222", activebackground="#8B0000", fg="white").pack(pady=5)
    create_styled_button(button_frame, text="🛒 商店", command=show_shop_ui, font_size=14, width=20, bg="#558B2F", activebackground="#33691E", fg="white").pack(pady=5)

    # --- BOSS 按钮逻辑 ---
    available_boss_id = get_available_boss()
    boss_button_state = tk.NORMAL if available_boss_id else tk.DISABLED
    boss_button_text = "挑战Boss"
    if available_boss_id:
        boss_button_text = f"挑战 {BOSSES[available_boss_id]['name']} (Lv.{BOSSES[available_boss_id]['required_level']})"

    # 将挑战首领按钮添加到主按钮区域
    challenge_boss_button = create_styled_button(
        button_frame,
        text=boss_button_text,
        command=lambda: start_boss_fight(available_boss_id) if available_boss_id else None, # 传递 boss_id
        font_size=14, width=20, # 稍宽以容纳BOSS名字
        bg="#8A2BE2", activebackground="#4B0082", fg="white", # 紫色系
        state=boss_button_state
    )
    challenge_boss_button.pack(pady=5)
    # --- END BOSS 按钮逻辑 ---

    create_styled_button(button_frame, text="🏆 排行榜", command=show_leaderboard_ui, font_size=14, width=20, bg="#DAA520", activebackground="#B8860B", fg="black").pack(pady=5)

    bottom_frame = tk.Frame(main_frame, bg="#111111"); bottom_frame.pack(pady=10)
    create_styled_button(bottom_frame, text="⚙️ 设置", command=show_settings_ui, font_size=12, width=15).pack(side=tk.LEFT, padx=10, pady=5)
    create_styled_button(bottom_frame, text="🚪 退出登录", command=logout, font_size=12, width=15).pack(side=tk.LEFT, padx=10, pady=5)

def logout():
    username = game_data["current_user"]
    if username and username in game_data["users"]:
        user_data = game_data["users"][username]
        user_data["score"] = game_data["player_stats"]["score"]; user_data["level"] = game_data["player_stats"]["level"]
        user_data["gold"] = game_data["player_stats"]["gold"]; user_data["inventory"] = game_data["player_stats"]["inventory"]
        user_data["high_score"] = game_data["player_stats"]["high_score"]; user_data["current_hp"] = game_data["player_stats"]["current_hp"]
        user_data["defeated_bosses"] = game_data["player_stats"]["defeated_bosses"] # 保存已击败BOSS列表
        save_users(); save_score(username, game_data["player_stats"]["score"])
    game_data["current_user"] = None
    game_data["player_stats"] = {"score": 0, "level": 1, "gold": 0, "avatar": os.path.join(AVATAR_FOLDER, DEFAULT_AVATAR), "inventory": {}, "max_hp": 50, "current_hp": 50, "high_score": 0, "defeated_bosses": []} # 重置时也包含 defeated_bosses
    login_screen()

def show_settings_ui():
    clear_frame(); tk.Label(main_frame, text="⚙️ 设置 ⚙️", font=("微软雅黑", 20, "bold"), fg="white", bg="#111111").pack(pady=20)
    create_styled_button(main_frame, text="更换头像", command=change_avatar_ui, font_size=14, width=20).pack(pady=10)
    create_styled_button(main_frame, text="修改用户名", command=change_username_ui, font_size=14, width=20).pack(pady=10)
    create_styled_button(main_frame, text="返回主页", command=user_home, font_size=12, width=15).pack(pady=20)

def change_avatar_ui():
    clear_frame(); username = game_data["current_user"]
    tk.Label(main_frame, text=f"为 {username} 更换头像", font=("微软雅黑", 18), fg="white", bg="#111111").pack(pady=10)
    current_avatar_path = game_data["player_stats"]["avatar"]; selected_avatar_path = [current_avatar_path]
    avatar_preview_label = tk.Label(main_frame, text="已选头像:", font=("微软雅黑", 11), bg="#111111", fg="white"); avatar_preview_label.pack(pady=(10, 0))
    avatar_img_label = tk.Label(main_frame, bg="#111111"); avatar_img_label.pack()
    def update_avatar_preview(path): selected_avatar_path[0] = path; img = display_avatar(path, (100, 100)); avatar_img_label.config(image=img if img else ''); avatar_img_label.image = img
    update_avatar_preview(current_avatar_path)
    tk.Label(main_frame, text="选择新头像:", font=("微软雅黑", 11), bg="#111111", fg="white").pack(pady=(10, 5))
    avatar_frame = tk.Frame(main_frame, bg="#222222", bd=1, relief=tk.SUNKEN); avatar_frame.pack(pady=5)
    row, col, max_cols = 0, 0, 6
    for file in sorted(os.listdir(AVATAR_FOLDER)):
        if file.lower().endswith((".png", ".jpg", ".jpeg")): path = os.path.join(AVATAR_FOLDER, file); img = display_avatar(path, (64, 64))
        if img: btn = tk.Button(avatar_frame, image=img, command=lambda p=path: update_avatar_preview(p), bg="#444444", bd=1, relief=tk.RAISED, width=64, height=64); btn.image = img; btn.grid(row=row, column=col, padx=5, pady=5); col += 1
        if col >= max_cols: col = 0; row += 1
    def save_new_avatar():
        new_avatar = selected_avatar_path[0]
        if new_avatar != game_data["player_stats"]["avatar"]:
            game_data["player_stats"]["avatar"] = new_avatar
            if username in game_data["users"]: game_data["users"][username]["avatar"] = new_avatar; save_users(); messagebox.showinfo("头像已更换", "你的头像已更新。")
            else: messagebox.showerror("错误", "找不到用户数据来保存头像。")
        show_settings_ui()
    create_styled_button(main_frame, text="保存头像", command=save_new_avatar, font_size=12, bg="#558B2F", activebackground="#33691E", fg="white").pack(pady=15)
    create_styled_button(main_frame, text="取消", command=show_settings_ui, font_size=10).pack(pady=5)

def change_username_ui():
    clear_frame(); current_username = game_data["current_user"]
    tk.Label(main_frame, text="修改用户名", font=("微软雅黑", 18), fg="white", bg="#111111").pack(pady=10)
    tk.Label(main_frame, text=f"当前用户名: {current_username}", font=("微软雅黑", 12), fg="white", bg="#111111").pack(pady=5)
    tk.Label(main_frame, text="输入新用户名:", font=("微软雅黑", 11), bg="#111111", fg="white").pack()
    new_name_entry = tk.Entry(main_frame, width=30, bg="#333333", fg="white", insertbackground="white", font=("微软雅黑", 10)); new_name_entry.pack(pady=5); new_name_entry.focus_set()
    def attempt_change_username():
        new_username = new_name_entry.get().strip(); old_username = game_data["current_user"]
        if not new_username: messagebox.showerror("错误", "新用户名不能为空。"); return
        if new_username == old_username: messagebox.showinfo("提示", "新用户名与当前用户名相同，无需修改。"); return
        if '|' in new_username: messagebox.showerror("错误", "用户名不能包含 '|' 字符。"); return
        if new_username in game_data["users"]: messagebox.showerror("错误", "此用户名已被占用，请选择其他用户名。"); return
        confirm = messagebox.askyesno("确认修改", f"确定要将用户名从 '{old_username}' 修改为 '{new_username}' 吗？\n（此操作也会更新排行榜中的用户名）")
        if not confirm: return
        try:
            user_data_copy = game_data["users"][old_username].copy(); del game_data["users"][old_username]
            game_data["users"][new_username] = user_data_copy; game_data["current_user"] = new_username; save_users()
            update_username_in_scores(old_username, new_username)
            messagebox.showinfo("成功", f"用户名已成功修改为 '{new_username}'！")
            show_settings_ui()
        except Exception as e: messagebox.showerror("修改失败", f"修改用户名时发生错误：{e}\n请尝试重新登录。"); login_screen()
    create_styled_button(main_frame, text="确认修改", command=attempt_change_username, font_size=12, bg="#558B2F", activebackground="#33691E", fg="white").pack(pady=15)
    create_styled_button(main_frame, text="取消", command=show_settings_ui, font_size=10).pack(pady=5)

def show_leaderboard_ui():
    clear_frame(); tk.Label(main_frame, text="🏆 排行榜 (按积分) 🏆", font=("微软雅黑", 20, "bold"), fg="#FFD700", bg="#111111").pack(pady=15)
    scores = load_scores(); sorted_scores = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    rank_frame = tk.Frame(main_frame, bg="#111111"); rank_frame.pack(pady=10)
    tk.Label(rank_frame, text="排名", font=("微软雅黑", 12, "bold"), fg="white", bg="#222222", width=5, relief=tk.SOLID, bd=1).grid(row=0, column=0, padx=1, pady=1)
    tk.Label(rank_frame, text="用户", font=("微软雅黑", 12, "bold"), fg="white", bg="#222222", width=20, relief=tk.SOLID, bd=1).grid(row=0, column=1, padx=1, pady=1)
    tk.Label(rank_frame, text="积分", font=("微软雅黑", 12, "bold"), fg="white", bg="#222222", width=10, relief=tk.SOLID, bd=1).grid(row=0, column=2, padx=1, pady=1)
    for i, (user, score) in enumerate(sorted_scores[:10], start=1):
        bg_color = "#333333" if i % 2 == 0 else "#444444"
        tk.Label(rank_frame, text=f"{i}", font=("微软雅黑", 11), fg="white", bg=bg_color, width=5, relief=tk.SOLID, bd=1).grid(row=i, column=0, sticky="ew", padx=1, pady=1)
        tk.Label(rank_frame, text=f"{user}", font=("微软雅黑", 11), fg="white", bg=bg_color, width=20, anchor="w", padx=5, relief=tk.SOLID, bd=1).grid(row=i, column=1, sticky="ew", padx=1, pady=1)
        tk.Label(rank_frame, text=f"{score}", font=("微软雅黑", 11), fg="white", bg=bg_color, width=10, relief=tk.SOLID, bd=1).grid(row=i, column=2, sticky="ew", padx=1, pady=1)
    create_styled_button(main_frame, text="返回", command=user_home, font_size=12).pack(pady=20)

def show_shop_ui():
    clear_frame(); tk.Label(main_frame, text="🛒 装备商店 🛒", font=("微软雅黑", 20, "bold"), fg="#4CAF50", bg="#111111").pack(pady=15)
    tk.Label(main_frame, text=f"你的金币: {game_data['player_stats']['gold']} 💰", font=("微软雅黑", 14), fg="#FFD700", bg="#111111").pack(pady=5)
    canvas = tk.Canvas(main_frame, bg="#222222", highlightthickness=0); scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
    shop_scrollable_frame = tk.Frame(canvas, bg="#222222"); shop_scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=shop_scrollable_frame, anchor="nw"); canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True, padx=(20, 0), pady=10); scrollbar.pack(side="right", fill="y", padx=(0, 20), pady=10)
    header_frame = tk.Frame(shop_scrollable_frame, bg="#333333"); header_frame.pack(fill="x", pady=(0, 5))
    tk.Label(header_frame, text="物品", font=("微软雅黑", 11, "bold"), fg="white", bg="#333333", width=15, anchor="w").pack(side="left", padx=5)
    tk.Label(header_frame, text="操作 (价格单位: 金币)", font=("微软雅黑", 11, "bold"), fg="white", bg="#333333", width=25, anchor="e").pack(side="right", padx=5)
    def buy_or_upgrade(item_id):
        item_def = SHOP_ITEMS[item_id]; player_inventory = game_data["player_stats"]["inventory"]; current_gold = game_data["player_stats"]["gold"]
        if item_id in player_inventory:
            current_level = player_inventory[item_id]["level"]; cost = calculate_upgrade_cost(item_id, current_level)
            if current_gold >= cost: game_data["player_stats"]["gold"] -= cost; player_inventory[item_id]["level"] += 1; game_data["users"][game_data["current_user"]]["inventory"] = player_inventory; game_data["users"][game_data["current_user"]]["gold"] = game_data["player_stats"]["gold"]; save_users(); show_shop_ui()
            else: messagebox.showwarning("金币不足", f"你需要 {cost} 金币来升级 {item_def['name']}。")
        else:
            cost = item_def["base_cost"]
            if current_gold >= cost: game_data["player_stats"]["gold"] -= cost; player_inventory[item_id] = {"level": 1}; game_data["users"][game_data["current_user"]]["inventory"] = player_inventory; game_data["users"][game_data["current_user"]]["gold"] = game_data["player_stats"]["gold"]; save_users(); show_shop_ui()
            else: messagebox.showwarning("金币不足", f"你需要 {cost} 金币来购买 {item_def['name']}。")
    def sell_item(item_id):
        if item_id not in game_data["player_stats"]["inventory"]: messagebox.showerror("错误", "你并不拥有此物品。"); return
        if item_id not in SHOP_ITEMS: messagebox.showerror("错误", "未知的物品ID。"); return
        item_def = SHOP_ITEMS[item_id]; sell_price = calculate_sell_price(item_id); item_level = game_data["player_stats"]["inventory"][item_id]["level"]
        confirm = messagebox.askyesno("确认出售", f"你确定要出售 {item_level}级 {item_def['name']} 吗？\n售价: {sell_price} 金币")
        if confirm: game_data["player_stats"]["gold"] += sell_price; del game_data["player_stats"]["inventory"][item_id]; game_data["users"][game_data["current_user"]]["inventory"] = game_data["player_stats"]["inventory"]; game_data["users"][game_data["current_user"]]["gold"] = game_data["player_stats"]["gold"]; save_users(); messagebox.showinfo("出售成功", f"你以 {sell_price} 金币出售了 {item_def['name']}。"); show_shop_ui()
    player_inventory = game_data["player_stats"]["inventory"]; item_index = 0
    for item_id, item_def in SHOP_ITEMS.items():
        bg_color = "#444444" if item_index % 2 == 0 else "#555555"; item_frame = tk.Frame(shop_scrollable_frame, bg=bg_color); item_frame.pack(fill="x", pady=2, padx=2); item_index += 1
        info_frame = tk.Frame(item_frame, bg=bg_color); info_frame.pack(side="left", fill="y", padx=(0, 5))
        name_label = tk.Label(info_frame, text=item_def["name"], font=("微软雅黑", 10, "bold"), fg="white", bg=bg_color, width=15, anchor="w"); name_label.pack(anchor="w")
        def show_tooltip(event, text): tooltip = tk.Toplevel(root); tooltip.wm_overrideredirect(True); tooltip.wm_geometry(f"+{event.x_root+15}+{event.y_root+10}"); label = tk.Label(tooltip, text=text, justify='left', bg="#FFFFE0", relief='solid', borderwidth=1, font=("微软雅黑", 9)); label.pack(ipadx=1); event.widget.tooltip = tooltip
        def hide_tooltip(event):
            if hasattr(event.widget, 'tooltip'): event.widget.tooltip.destroy(); delattr(event.widget, 'tooltip')
        name_label.bind("<Enter>", lambda e, text=item_def['description']: show_tooltip(e, text)); name_label.bind("<Leave>", hide_tooltip)
        level_str = "-"; stat_text = ""; base_stat_val = item_def['base_stat']; stat_growth_val = item_def['stat_growth']; stat_suffix = ""
        if item_def['type'] == 'weapon': stat_suffix = " 伤"
        elif item_def['type'] == 'armor': stat_suffix = " 防"
        elif item_id == 'health_amulet': stat_suffix = " 血"
        elif item_id == 'strength_ring': stat_suffix = " 伤"
        elif item_id == 'defense_amulet': stat_suffix = " 防"
        stat_text = f"{base_stat_val:.1f}{stat_suffix} / 1级"
        if item_id in player_inventory: level = player_inventory[item_id]["level"]; level_str = str(level); current_stat = base_stat_val + (stat_growth_val * (level - 1)); stat_text = f"{current_stat:.1f}{stat_suffix} / {level}级"
        else: level_str = "未拥有"
        tk.Label(info_frame, text=f"等级: {level_str}", font=("微软雅黑", 9), fg="#CCCCCC", bg=bg_color, anchor="w").pack(anchor="w")
        tk.Label(info_frame, text=f"属性: {stat_text}", font=("微软雅黑", 9), fg="#DDDDDD", bg=bg_color, anchor="w").pack(anchor="w")
        action_frame = tk.Frame(item_frame, bg=bg_color); action_frame.pack(side="right", fill="y", padx=(5, 0)); button_font_size = 9
        if item_id in player_inventory:
            current_level = player_inventory[item_id]["level"]; upgrade_cost = calculate_upgrade_cost(item_id, current_level); sell_price = calculate_sell_price(item_id)
            create_styled_button(action_frame, text=f"升级 ({upgrade_cost}💰)", command=lambda i=item_id: buy_or_upgrade(i), font_size=button_font_size, width=11, bg="#FF9800", activebackground="#E65100", fg="white", bd=2, relief=tk.RAISED).pack(pady=(2,1))
            create_styled_button(action_frame, text=f"出售 ({sell_price}💰)", command=lambda i=item_id: sell_item(i), font_size=button_font_size, width=11, bg="#f44336", activebackground="#c62828", fg="white", bd=2, relief=tk.RAISED).pack(pady=(1,2))
        else: buy_cost = item_def["base_cost"]; create_styled_button(action_frame, text=f"购买 ({buy_cost}💰)", command=lambda i=item_id: buy_or_upgrade(i), font_size=button_font_size, width=11, bg="#2196F3", activebackground="#0D47A1", fg="white", bd=2, relief=tk.RAISED).pack(expand=True, fill="both", pady=2)
    back_button_frame = tk.Frame(main_frame, bg="#111111"); back_button_frame.pack(fill="x", pady=(0,10))
    create_styled_button(back_button_frame, text="返回主页", command=user_home, font_size=12).pack(pady=10)

def start_game():
    clear_frame(); stats = game_data["player_stats"]; calculate_player_stats(); stats["current_hp"] = stats["max_hp"]
    if game_data["current_user"] in game_data["users"]: game_data["users"][game_data["current_user"]]["current_hp"] = stats["current_hp"]; save_users()
    enemy_level = stats["level"]
    enemy_types = {"哥布林": {"hp": 15, "attack": 3, "score": 15, "gold_reward": 10}, "兽人": {"hp": 40, "attack": 6, "score": 30, "gold_reward": 25}, "骷髅": {"hp": 25, "attack": 4, "defense": 1, "score": 25, "gold_reward": 20}, "史莱姆": {"hp": 50, "attack": 2, "defense": 0, "score": 20, "gold_reward": 15}, "恶狼": {"hp": 30, "attack": 5, "defense": 0, "score": 28, "gold_reward": 22}, "巨魔": {"hp": 80, "attack": 8, "defense": 2, "score": 60, "gold_reward": 50}}
    possible_enemies = ["哥布林"];
    if enemy_level >= 2: possible_enemies.extend(["兽人", "骷髅", "恶狼"])
    if enemy_level >= 5: possible_enemies.extend(["史莱姆", "巨魔"])
    if enemy_level >= 7: possible_enemies.append("巨魔")
    chosen_enemy_type = random.choice(possible_enemies)
    enemy_base = enemy_types[chosen_enemy_type]; enemy_max_hp = int(enemy_base["hp"] * (1 + 0.2 * (enemy_level - 1))); enemy_hp = enemy_max_hp
    enemy_attack = int(enemy_base["attack"] * (1 + 0.15 * (enemy_level - 1))); enemy_defense = int(enemy_base.get("defense", 0) * (1 + 0.1 * (enemy_level - 1)))
    enemy_score_reward = int(enemy_base["score"] * (1 + 0.1 * (enemy_level - 1))); enemy_gold_reward = int(enemy_base["gold_reward"] * (1 + 0.1 * (enemy_level - 1)))
    tk.Label(main_frame, text=f"遭遇 {enemy_level}级 {chosen_enemy_type}！", font=("微软雅黑", 18, "bold"), fg="#cc4444", bg="#111111").pack(pady=15)
    combat_info_frame = tk.Frame(main_frame, bg="#222222"); combat_info_frame.pack(pady=10, padx=20, fill="x")
    player_hp_label = tk.Label(combat_info_frame, text=f"你的生命值: {stats['current_hp']}/{stats['max_hp']}", font=("微软雅黑", 12), fg="green", bg="#222222"); player_hp_label.pack(side="left", padx=20)
    enemy_hp_label = tk.Label(combat_info_frame, text=f"敌人生命值: {enemy_hp}/{enemy_max_hp}", font=("微软雅黑", 12), fg="red", bg="#222222"); enemy_hp_label.pack(side="right", padx=20)
    log_frame = tk.Frame(main_frame, bg="#1a1a1a", height=150, bd=1, relief=tk.SUNKEN); log_frame.pack(pady=10, padx=20, fill="x")
    log_text = tk.Text(log_frame, height=8, width=70, bg="#1a1a1a", fg="white", state="disabled", wrap=tk.WORD, font=("微软雅黑", 10)); log_text.pack(padx=5, pady=5, fill="both", expand=True)
    def add_log(message, color="white"): log_text.config(state="normal"); log_text.insert(tk.END, message + "\n", color); log_text.tag_config(color, foreground=color); log_text.see(tk.END); log_text.config(state="disabled")
    add_log(f"一只野生的{chosen_enemy_type}出现了！")
    action_frame = tk.Frame(main_frame, bg="#111111"); action_frame.pack(pady=10)
    attack_button = create_styled_button(action_frame, text="⚔️ 攻击", command=lambda: player_turn(), font_size=12, width=12, height=2, bg="#B22222", activebackground="#8B0000", fg="white"); attack_button.pack(side="left", padx=10)
    flee_button = create_styled_button(action_frame, text="🏃 逃跑", command=lambda: flee(), font_size=12, width=12, height=2); flee_button.pack(side="left", padx=10)
    def update_hp_labels(): stats['current_hp'] = min(stats['current_hp'], stats['max_hp']); player_hp_label.config(text=f"你的生命值: {stats['current_hp']}/{stats['max_hp']}"); enemy_hp_label.config(text=f"敌人生命值: {enemy_hp}/{enemy_max_hp}"); hp_ratio = stats['current_hp'] / stats['max_hp'] if stats['max_hp'] > 0 else 0; hp_color = "green" if hp_ratio > 0.6 else "orange" if hp_ratio > 0.3 else "red"; player_hp_label.config(fg=hp_color)
    def player_turn():
        nonlocal enemy_hp; player_damage, player_defense = calculate_player_stats(); damage_dealt = random.randint(int(player_damage * 0.8), int(player_damage * 1.2))
        damage_dealt = max(0, damage_dealt - enemy_defense); enemy_hp = max(0, enemy_hp - damage_dealt)
        add_log(f"你攻击了{chosen_enemy_type}，造成 {damage_dealt} 点伤害！", "cyan"); update_hp_labels()
        if enemy_hp <= 0: win_combat()
        else: attack_button.config(state="disabled"); flee_button.config(state="disabled"); root.after(800, enemy_turn)
    def enemy_turn():
        nonlocal enemy_hp
        if enemy_hp <= 0:
            if attack_button['state'] == 'disabled': attack_button.config(state="normal")
            if flee_button['state'] == 'disabled': flee_button.config(state="normal")
            return
        enemy_base_dmg = enemy_attack; damage_dealt = random.randint(int(enemy_base_dmg * 0.8), int(enemy_base_dmg * 1.2))
        _, player_defense = calculate_player_stats(); damage_taken = max(0, damage_dealt - int(player_defense))
        stats["current_hp"] = max(0, stats["current_hp"] - damage_taken)
        if damage_taken > 0: add_log(f"{chosen_enemy_type}攻击了你，造成 {damage_taken} 点伤害！", "red");
        if damage_dealt > damage_taken: add_log(f"(你的护甲格挡了 {damage_dealt - damage_taken} 点伤害！)", "grey")
        else: add_log(f"{chosen_enemy_type}的攻击被你的护甲弹开了！", "grey")
        update_hp_labels()
        if stats["current_hp"] <= 0: lose_combat()
        else: attack_button.config(state="normal"); flee_button.config(state="normal")
    def win_combat():
        add_log(f"你击败了{chosen_enemy_type}！", "yellow"); stats["score"] += enemy_score_reward; stats["gold"] += enemy_gold_reward
        add_log(f"你获得了 {enemy_score_reward} 积分。", "yellow"); add_log(f"你获得了 {enemy_gold_reward} 金币 💰。", "#FFD700")
        score_needed_for_next_level = stats["level"] * 100; leveled_up = False
        while stats["score"] >= score_needed_for_next_level: stats["level"] += 1; leveled_up = True; stats["max_hp"] += 5; add_log(f"升级！你达到了 {stats['level']} 级！", "magenta"); add_log(f"最大生命值增加！", "magenta"); score_needed_for_next_level = stats["level"] * 100
        if leveled_up: stats["current_hp"] = stats["max_hp"]; add_log(f"生命值已完全恢复！", "magenta")
        save_score(game_data["current_user"], stats["score"])
        if game_data["current_user"] in game_data["users"]: user_data = game_data["users"][game_data["current_user"]]; user_data["score"] = stats["score"]; user_data["level"] = stats["level"]; user_data["gold"] = stats["gold"]; user_data["current_hp"] = stats["current_hp"]; save_users()
        attack_button.config(state="disabled"); flee_button.config(state="disabled"); create_styled_button(action_frame, text="继续 ✔️", command=user_home, font_size=12, width=12, height=2, bg="#558B2F", activebackground="#33691E", fg="white").pack(side="left", padx=10)
    def lose_combat():
        add_log("你被击败了！", "darkred"); score_loss = int(stats["score"] * 0.1); stats["score"] = max(0, stats["score"] - score_loss); add_log(f"你损失了 {score_loss} 积分。", "darkred"); stats["current_hp"] = 0
        save_score(game_data["current_user"], stats["score"])
        if game_data["current_user"] in game_data["users"]: user_data = game_data["users"][game_data["current_user"]]; user_data["score"] = stats["score"]; user_data["current_hp"] = stats["current_hp"]; save_users()
        attack_button.config(state="disabled"); flee_button.config(state="disabled"); create_styled_button(action_frame, text="返回主页", command=user_home, font_size=12, width=12, height=2).pack(side="left", padx=10)
    def flee():
        add_log("你逃离了战斗！", "orange")
        if game_data["current_user"] in game_data["users"]: game_data["users"][game_data["current_user"]]["current_hp"] = stats["current_hp"]; save_users()
        attack_button.config(state="disabled"); flee_button.config(state="disabled"); create_styled_button(action_frame, text="返回主页", command=user_home, font_size=12, width=12, height=2).pack(side="left", padx=10)

# --- BOSS 战斗逻辑 ---
def start_boss_fight(boss_id):
    """初始化BOSS战斗屏幕。"""
    if not boss_id or boss_id not in BOSSES:
        messagebox.showerror("错误", "无效的首领ID。")
        return

    boss_data = BOSSES[boss_id]
    clear_frame(); stats = game_data["player_stats"]
    calculate_player_stats(); stats["current_hp"] = stats["max_hp"] # BOSS战前满血
    if game_data["current_user"] in game_data["users"]: game_data["users"][game_data["current_user"]]["current_hp"] = stats["current_hp"]; save_users()

    # BOSS 属性 (可以考虑不同的缩放方式，但暂时用基础值)
    enemy_name = boss_data["name"]
    enemy_max_hp = boss_data["hp"]
    enemy_hp = enemy_max_hp
    enemy_attack = boss_data["attack"]
    enemy_defense = boss_data["defense"]
    enemy_score_reward = boss_data["score_reward"]
    enemy_gold_reward = boss_data["gold_reward"]

    tk.Label(main_frame, text=f"🔥 挑战首领：{enemy_name} 🔥", font=("微软雅黑", 20, "bold"), fg="#FF4500", bg="#111111").pack(pady=15) # 醒目的标题

    combat_info_frame = tk.Frame(main_frame, bg="#222222"); combat_info_frame.pack(pady=10, padx=20, fill="x")
    player_hp_label = tk.Label(combat_info_frame, text=f"你的生命值: {stats['current_hp']}/{stats['max_hp']}", font=("微软雅黑", 12), fg="green", bg="#222222"); player_hp_label.pack(side="left", padx=20)
    enemy_hp_label = tk.Label(combat_info_frame, text=f"首领生命值: {enemy_hp}/{enemy_max_hp}", font=("微软雅黑", 12), fg="red", bg="#222222"); enemy_hp_label.pack(side="right", padx=20)

    log_frame = tk.Frame(main_frame, bg="#1a1a1a", height=150, bd=1, relief=tk.SUNKEN); log_frame.pack(pady=10, padx=20, fill="x")
    log_text = tk.Text(log_frame, height=8, width=70, bg="#1a1a1a", fg="white", state="disabled", wrap=tk.WORD, font=("微软雅黑", 10)); log_text.pack(padx=5, pady=5, fill="both", expand=True)
    def add_log(message, color="white"): log_text.config(state="normal"); log_text.insert(tk.END, message + "\n", color); log_text.tag_config(color, foreground=color); log_text.see(tk.END); log_text.config(state="disabled")
    add_log(f"强大的 {enemy_name} 出现在你面前！", "orange")
    if boss_data.get("description"): add_log(boss_data["description"], "grey")

    action_frame = tk.Frame(main_frame, bg="#111111"); action_frame.pack(pady=10)
    attack_button = create_styled_button(action_frame, text="⚔️ 攻击", command=lambda: player_turn(), font_size=12, width=12, height=2, bg="#B22222", activebackground="#8B0000", fg="white"); attack_button.pack(side="left", padx=10)
    # BOSS战通常不能逃跑
    # flee_button = create_styled_button(action_frame, text="🏃 逃跑", command=lambda: flee(), font_size=12, width=12, height=2); flee_button.pack(side="left", padx=10)

    def update_hp_labels(): stats['current_hp'] = min(stats['current_hp'], stats['max_hp']); player_hp_label.config(text=f"你的生命值: {stats['current_hp']}/{stats['max_hp']}"); enemy_hp_label.config(text=f"首领生命值: {enemy_hp}/{enemy_max_hp}"); hp_ratio = stats['current_hp'] / stats['max_hp'] if stats['max_hp'] > 0 else 0; hp_color = "green" if hp_ratio > 0.6 else "orange" if hp_ratio > 0.3 else "red"; player_hp_label.config(fg=hp_color)
    def player_turn():
        nonlocal enemy_hp; player_damage, player_defense = calculate_player_stats(); damage_dealt = random.randint(int(player_damage * 0.8), int(player_damage * 1.2))
        damage_dealt = max(0, damage_dealt - enemy_defense); enemy_hp = max(0, enemy_hp - damage_dealt)
        add_log(f"你攻击了{enemy_name}，造成 {damage_dealt} 点伤害！", "cyan"); update_hp_labels()
        if enemy_hp <= 0: win_boss_combat() # 调用BOSS胜利函数
        else: attack_button.config(state="disabled"); root.after(900, enemy_turn) # BOSS攻击可能稍慢
    def enemy_turn():
        nonlocal enemy_hp
        if enemy_hp <= 0:
            if attack_button['state'] == 'disabled': attack_button.config(state="normal")
            return
        enemy_base_dmg = enemy_attack; damage_dealt = random.randint(int(enemy_base_dmg * 0.9), int(enemy_base_dmg * 1.1)) # BOSS攻击更稳定?
        _, player_defense = calculate_player_stats(); damage_taken = max(0, damage_dealt - int(player_defense))
        stats["current_hp"] = max(0, stats["current_hp"] - damage_taken)
        if damage_taken > 0: add_log(f"{enemy_name}攻击了你，造成 {damage_taken} 点伤害！", "red");
        if damage_dealt > damage_taken: add_log(f"(你的护甲格挡了 {damage_dealt - damage_taken} 点伤害！)", "grey")
        else: add_log(f"{enemy_name}的攻击被你的护甲弹开了！", "grey")
        update_hp_labels()
        if stats["current_hp"] <= 0: lose_boss_combat() # 调用BOSS失败函数
        else: attack_button.config(state="normal")

    def win_boss_combat():
        add_log(f"🎉 你成功击败了强大的 {enemy_name}！ 🎉", "lime green")
        stats["score"] += enemy_score_reward; stats["gold"] += enemy_gold_reward
        add_log(f"你获得了 {enemy_score_reward} 积分！", "yellow"); add_log(f"你获得了 {enemy_gold_reward} 金币 💰！", "#FFD700")
        # 记录已击败的BOSS
        if boss_id not in stats["defeated_bosses"]: stats["defeated_bosses"].append(boss_id)
        # 检查是否因击败BOSS获得的分数而升级
        score_needed_for_next_level = stats["level"] * 100; leveled_up = False
        while stats["score"] >= score_needed_for_next_level: stats["level"] += 1; leveled_up = True; stats["max_hp"] += 5; add_log(f"升级！你达到了 {stats['level']} 级！", "magenta"); add_log(f"最大生命值增加！", "magenta"); score_needed_for_next_level = stats["level"] * 100
        if leveled_up: stats["current_hp"] = stats["max_hp"]; add_log(f"生命值已完全恢复！", "magenta")
        # 保存所有更新的数据
        save_score(game_data["current_user"], stats["score"])
        if game_data["current_user"] in game_data["users"]:
            user_data = game_data["users"][game_data["current_user"]]
            user_data["score"] = stats["score"]; user_data["level"] = stats["level"]; user_data["gold"] = stats["gold"]
            user_data["current_hp"] = stats["current_hp"]; user_data["defeated_bosses"] = stats["defeated_bosses"] # 保存更新后的列表
            save_users()
        attack_button.config(state="disabled"); create_styled_button(action_frame, text="返回主页 ✔️", command=user_home, font_size=12, width=12, height=2, bg="#558B2F", activebackground="#33691E", fg="white").pack(side="left", padx=10)

    def lose_boss_combat():
        add_log(f"你被 {enemy_name} 击败了...再接再厉！", "darkred")
        score_loss = int(stats["score"] * 0.15) # BOSS战失败惩罚可能更高
        stats["score"] = max(0, stats["score"] - score_loss); add_log(f"你损失了 {score_loss} 积分。", "darkred"); stats["current_hp"] = 0
        # 失败不损失金币
        save_score(game_data["current_user"], stats["score"])
        if game_data["current_user"] in game_data["users"]: user_data = game_data["users"][game_data["current_user"]]; user_data["score"] = stats["score"]; user_data["current_hp"] = stats["current_hp"]; save_users()
        attack_button.config(state="disabled"); create_styled_button(action_frame, text="返回主页", command=user_home, font_size=12, width=12, height=2).pack(side="left", padx=10)

# --- 主应用程序设置 ---
root = tk.Tk(); root.title("巫师冒险"); root.geometry("850x650"); root.configure(bg="#111111")
main_frame = tk.Frame(root, bg="#111111"); main_frame.pack(fill="both", expand=True)
login_screen(); root.mainloop()
