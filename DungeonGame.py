import pyxel
import csv
import json
import random
from typing import Final

# シーン番号の定義
# タイトル画面
SNO_TITLE: Final[int]
SNO_TITLE = 0
SNO_TITLE_2: Final[int]
SNO_TITLE_2 = 1
# オープニング画面
SNO_OP_DEMO: Final[int]
SNO_OP_DEMO = 2
# 探索画面
SNO_SEARCH: Final[int]
SNO_SEARCH = 3

# 戦闘画面
SNO_BATTLE: Final[int]
SNO_BATTLE = 10
SNO_BATTLE_1: Final[int]
SNO_BATTLE_1 = 11
SNO_BATTLE_2: Final[int]
SNO_BATTLE_2 = 12
# 戦闘(勝利)画面
SNO_BATTLE_VICTORY: Final[int]
SNO_BATTLE_VICTORY = 13

# 宝箱発見画面
SNO_TREASURE: Final[int]
SNO_TREASURE = 20
SNO_TREASURE_1: Final[int]
SNO_TREASURE_1 = 21

# レベルアップ画面
SNO_LEVEL_UP: Final[int]
SNO_LEVEL_UP = 30

# ゲームオーバー画面
SNO_GAMEOVER: Final[int]
SNO_GAMEOVER = 40

# エンディング画面
SNO_END: Final[int]
SNO_END = 50

# 画面の揺れフレーム
SHAKE_FRAME: Final[int]
SHAKE_FRAME = 10
# 点滅フレーム
BLINK_FRAME: Final[int]
BLINK_FRAME = 10
# OPのループ間隔
OP_LOOP_TIME: Final[int]
OP_LOOP_TIME = 400

# 区分
NORMAL_TYPE: Final[str]
NORMAL_TYPE = "N"
UNIQUE_TYPE: Final[str]
UNIQUE_TYPE = "U"

# タイトル画像
TITLE_FILE: Final[str]
TITLE_FILE = "title_logo.png"

# 音楽ファイル
MUSIC_FILE_1: Final[str]
MUSIC_FILE_1 = "json/music_floor1"
MUSIC_FILE_2: Final[str]
MUSIC_FILE_2 = "json/music_floor2"
MUSIC_FILE_3: Final[str]
MUSIC_FILE_3 = "json/music_floor3"
MUSIC_FILE_4: Final[str]
MUSIC_FILE_4 = "json/music_floor4"
MUSIC_FILE_5: Final[str]
MUSIC_FILE_5 = "json/music_floor5"
MUSIC_FILE_6: Final[str]
MUSIC_FILE_6 = "json/music_title"

# デバッグフラグ
DBUG_FLAG: Final[int]
DBUG_FLAG = True

class DungeonGame:

    def __init__(self):
        pyxel.init(256, 256, title="Dungeon 100")
        # スマホでタッチを使うために必要
        pyxel.mouse(True)

        # # 音楽ファイルを読込
        # self.set_music_file(MUSIC_FILE_6)

        # pyxel.load("assets.pyxres")  # モンスター画像を含むリソースを読み込む
        # self.scene = SNO_OP_DEMO
        self.normal_monster_data = self.load_monster_data("monsters.csv", NORMAL_TYPE)  # モンスター情報を読み込む
        self.unique_monster_data = self.load_monster_data("monsters.csv", UNIQUE_TYPE)  # モンスター情報を読み込む
        self.monster_messages = self.load_messages("monster_messages.csv")  # 出現メッセージを読み込む
        self.weapon_data = self.load_data("weapons.csv")  # 剣のデータを読み込む
        self.shield_data = self.load_data("shields.csv")  # 盾のデータを読み込む
        self.reset_game()

        # ボタン位置（画面右下に配置）
        self.button_a_x = 170
        self.button_a_y = 180
        self.button_d_x = 200
        self.button_d_y = 180
        self.button_h_x = 230
        self.button_h_y = 180
        self.button_radius = 10
        
        pyxel.run(self.update, self.draw)

    def debug_print(self, *args):
        if DBUG_FLAG:
            print(args)
            print("scene:", self.scene)
            print("floor:", self.floor)
            print("is_player_turn:", self.is_player_turn)
            print("waiting_for_input:", self.waiting_for_input)
            print("waiting_for_push:", self.waiting_for_push)
            print("monster:", self.monster)
            print("message:", self.message)
            print("clear_20:", self.clear_20)
            print("clear_40:", self.clear_40)
            print("clear_60:", self.clear_60)
            print("clear_80:", self.clear_80)
            print("clear_100:", self.clear_100)

    def load_data(self, filename):
        """CSVファイルからデータを読み込む"""
        data = []
        with open(filename, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                for key in row:  # 数値データを変換
                    if row[key] is None:
                        continue
                    if row[key].isdigit():
                        row[key] = int(row[key])
                data.append(row)
        return data

    def load_monster_data(self, filename, type):
        """CSVファイルからデータを読み込む"""
        data = []
        with open(filename, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["type"] != type:
                    continue
                for key in row:  # 数値データを変換
                    if row[key].isdigit():
                        row[key] = int(row[key])
                row["MAX_HP"] = row["HP"]
                data.append(row)
        return data

    def load_messages(self, filename):
        """CSVファイルから出現メッセージを読み込む"""
        messages = []
        with open(filename, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                messages.append(row["message"])
        return messages
    
    def set_music_file(self, file):
        try:
            with open(f"./{file}.json", "rt") as fin:
                self.music = json.loads(fin.read())
            # if pyxel.play_pos(0) is None:
            for ch, sound in enumerate(self.music):
                pyxel.sound(ch).set(*sound)
                pyxel.play(ch, ch, loop=True)
        except Exception as e:
            self.message = f"Error loading {file}: {str(e)}"
            print(self.message)

    def start_shake(self, duration):
        """画面を揺らす開始（duration: 揺れの長さ）"""
        self.shake_timer = duration

    def start_blinking(self, duration):
        """点滅開始（duration: 点滅の長さ）"""
        self.blink_timer = duration
        self.is_blinking = True

    def reset_game(self):
        self.floor = 0
        self.player = {
            "HP": 100,
            "ATK": 10,
            "DEF": 5,
            "weapon": self.weapon_data[0],
            "shield": self.shield_data[0],
        }
        self.scene = SNO_OP_DEMO
        self.buttle_mode = False
        self.is_player_turn = False
        self.message = ""

        # リソースのリロード
        self.set_music_file(MUSIC_FILE_6)
        pyxel.load("assets.pyxres")  # モンスター画像を含むリソースを読み込む
        # キー入力待機フラグ
        self.waiting_for_input = False
        self.waiting_for_push = False
        self.waiting_for_time = 0
        # モンスター
        self.monster = None
        # 階層管理用
        self.clear_0 = False
        self.clear_20 = False
        self.clear_40 = False
        self.clear_60 = False
        self.clear_80 = False
        self.clear_100 = False
        # OPループまでのタイマー
        self.op_loop_timer = 0
        # 揺れの残り時間
        self.shake_timer = 0  
        # 点滅タイマー
        self.blink_timer = 0
        # 点滅中かどうか
        self.is_blinking = False
        # オープニングデモのテキストの初期位置（画面の下に設定）
        self.op_text_y = pyxel.height
        # オープニングデモのスクロール速度
        self.op_text_speed = 0.4


    def update(self):

        # 揺れのタイマーを減らす
        if self.shake_timer > 0:
            self.shake_timer -= 1
            return

        # 点滅タイマーの更新
        if self.is_blinking:
            self.blink_timer -= 1
            if self.blink_timer <= 0:
                # 点滅終了
                self.is_blinking = False  
            return

        # 1階からBGMを変更
        if self.floor >= 1 and not self.clear_0:
            self.set_music_file(MUSIC_FILE_1)
            pyxel.load("assets.pyxres")  # モンスター画像を含むリソースを読み込む
            self.clear_0 = True
        # 21階からBGMを変更
        if self.floor >= 21 and not self.clear_20:
            self.set_music_file(MUSIC_FILE_2)
            pyxel.load("assets.pyxres")  # モンスター画像を含むリソースを読み込む
            self.clear_20 = True
        # 41階からBGMを変更
        if self.floor >= 41 and not self.clear_40:
            self.set_music_file(MUSIC_FILE_3)
            pyxel.load("assets.pyxres")  # モンスター画像を含むリソースを読み込む
            self.clear_40 = True
        # 61階からBGMを変更
        if self.floor >= 61 and not self.clear_60:
            self.set_music_file(MUSIC_FILE_4)
            pyxel.load("assets.pyxres")  # モンスター画像を含むリソースを読み込む
            self.clear_60 = True
        # 81階からBGMを変更
        if self.floor >= 81 and not self.clear_80:
            self.set_music_file(MUSIC_FILE_5)
            pyxel.load("assets.pyxres")  # モンスター画像を含むリソースを読み込む
            self.clear_80 = True

        # キーの押下が必要
        if self.waiting_for_input:
            if pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                self.waiting_for_input = False
            return

        # キーの入力が必要
        if self.waiting_for_push:
            if pyxel.btn(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                self.waiting_for_push = False
            return

        # オープニング
        if self.scene == SNO_OP_DEMO:
            self.op_text = (
                "Long ago,\n"
                "a dungeon suddenly appeared\n"
                "in this world.\n"
                "\n\n"
                "From its dark depths,\n"
                "countless monsters spilled out,\n"
                "plunging the world into chaos.\n"
                "\n\n"
                "But one man rose to challenge it.\n"
                "His name is still unknown.\n"
                "\n\n\n\n\n\n"
                "Yet, it is his courage\n"
                "that will save the world.\n"
            )
            # テキストをスクロール
            if self.op_text_y + len(self.op_text.split("\n")) * 8 > 0:
                self.op_text_y -= self.op_text_speed
                if pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                    self.scene = SNO_TITLE
            else:
                # # テキストが画面外に出たら、次の処理を行う
                # # 再度スクロール位置をリセットして繰り返し
                # self.text_y = pyxel.height / 2
                self.scene = SNO_TITLE
                # pyxel.text(80, 120, op_text, 7)
                self.waiting_for_input = False
            return

        # ゲームオーバー
        if self.scene == SNO_GAMEOVER:
            self.message  = (
                "Game Over\n"
                f"You reached Floor {self.floor}"
                "\n"
                "\n"
                "Press SPACE to Retry"
            )
            # pyxel.text(80, 50, message, pyxel.COLOR_RED)
            self.waiting_for_input = False
            if pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                self.reset_game()

        # エンディング
        if self.scene == SNO_END:
            self.op_text = (
                "Long ago,\n"
                "a dungeon suddenly appeared\n"
                "in this world.\n"
                "\n\n"
                "From its dark depths,\n"
                "countless monsters spilled out,\n"
                "plunging the world into chaos.\n"
                "\n\n"
                "But one man rose to challenge it.\n"
                "His name is still unknown.\n"
                "\n\n\n\n\n\n"
                "Yet, it is his courage\n"
                "that will save the world.\n"
            )
            # テキストをスクロール
            if self.op_text_y + len(self.op_text.split("\n")) * 8 > 0:
                self.op_text_y -= self.op_text_speed
                if pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                    self.scene = SNO_TITLE
            else:
                # # テキストが画面外に出たら、次の処理を行う
                # # 再度スクロール位置をリセットして繰り返し
                # self.text_y = pyxel.height / 2
                self.scene = SNO_TITLE
                # pyxel.text(80, 120, op_text, 7)
                self.waiting_for_input = False
            return

        # タイトル画面
        if self.scene == SNO_TITLE:
            # テキストが画面外に出たら終了せず、適切に次の処理を行う
            self.op_text_y = pyxel.height / 2  # 再度スクロール位置をリセットして繰り返し
            self.op_text = (
                "Press SPACE to START"
            )
            self.op_loop_timer += 1
            # OPループまでのカウント
            if self.op_loop_timer >= OP_LOOP_TIME:
                self.scene = SNO_OP_DEMO
                self.op_loop_timer = 0
            # スペースでゲーム開始
            if pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                # 効果音を再生
                pyxel.play(3, 33)  # チャンネル3
                self.scene = SNO_TITLE_2
                self.waiting_for_time = 30
            return

        # タイトル画面
        if self.scene == SNO_TITLE_2:
            # 待機が必要
            if self.waiting_for_time > 0:
                self.waiting_for_time -= 1
                if self.waiting_for_time <= 0:
                    self.waiting_for_time = 0
                    self.scene = SNO_SEARCH
            return

        if self.scene == SNO_SEARCH:  # 表示するメッセージを配列で持ち、表示しきるまでFlaseとする処理を追加する
            # self.floor += 10
            self.floor += 1
            self.monster = self.choose_unique_monster()
            if self.monster:
                self.scene = SNO_BATTLE
            else:
                # 次のイベント
                self.choose_random_monster_or_treasure()
            return

        if self.scene == SNO_LEVEL_UP:
            self.message = ("Choose: A (+2 ATK), D (+2 DEF), H (+10 HP)")
            """成長選択モードの処理"""
            if pyxel.btnp(pyxel.KEY_A) or self.is_button_a_pressed():  # 攻撃力アップ
                self.handle_level_up("ATK")
                self.scene = SNO_SEARCH
            elif pyxel.btnp(pyxel.KEY_D) or self.is_button_d_pressed():  # 防御力アップ
                self.handle_level_up("DEF")
                self.scene = SNO_SEARCH
            elif pyxel.btnp(pyxel.KEY_H) or self.is_button_h_pressed():  # HP回復
                self.handle_level_up("HP")
                self.scene = SNO_SEARCH
            return

        if self.scene == SNO_TREASURE:  # 宝箱発見時の処理
            self.obtain_treasure()
            self.scene = SNO_TREASURE_1
            return
        if self.scene == SNO_TREASURE_1:  # 宝箱発見時の処理
            self.scene = SNO_SEARCH
            return

        # 戦闘モード
        # 戦闘開始
        if self.scene == SNO_BATTLE:
            self.scene = SNO_BATTLE_1
            self.buttle_mode = True
            return
        # 攻撃
        if self.scene == SNO_BATTLE_1:
            if self.is_player_turn:
                self.player_attack()
                self.scene = SNO_BATTLE_2
            elif not self.is_player_turn:
                self.monster_attack()
                self.scene = SNO_BATTLE_2
            return
        # 戦闘終了の判定
        if self.scene == SNO_BATTLE_2:
            if self.check_victory():
                self.buttle_mode = False
                return
            if self.check_defeat():
                return
            self.scene = SNO_BATTLE_1
        if self.scene == SNO_BATTLE_VICTORY:
            self.scene = SNO_LEVEL_UP
            return

    def draw(self):
        pyxel.cls(0)

        if self.scene == SNO_OP_DEMO:
            # テキストを白で描画
            for i, line in enumerate(self.op_text.split("\n")):
                pyxel.text(10, self.op_text_y + i * 8, line, pyxel.COLOR_WHITE)  # 7は白色
            return


        if self.scene == SNO_TITLE or self.scene == SNO_TITLE_2:
            x = (pyxel.width - 128) // 2
            y = (pyxel.height - 128) // 2 - 20

            # 画像のロード（画像はassets.pyxres内で管理されていると仮定）
            pyxel.image(0).load(0, 0, TITLE_FILE)  # 画像ファイルのパスに変更
            # x, y は表示位置、0 は使用する画像のインデックス
            pyxel.blt(x, y, 0, 0, 0, 128, 128)  # 16x16の画像を(50, 50)に表示

            # テキストを白で描画
            pyxel.text(x + 25, y + 128, self.op_text, pyxel.COLOR_WHITE)  # 7は白色
            return

        if self.scene == SNO_TITLE_2:
            # テキストを白で描画
            pyxel.text(10, self.op_text_y + 20, self.op_text, pyxel.COLOR_WHITE)  # 7は白色
            return


        # 揺れのオフセットを計算
        shake_x = 0
        shake_y = 0
        if self.shake_timer > 0:  # 揺れが有効なとき
            shake_x = random.randint(-2, 2)  # -2から2ピクセルのランダムなオフセット
            shake_y = random.randint(-2, 2)
        # カメラをオフセットして描画
        pyxel.camera(shake_x, shake_y)

        # ゲーム情報を描画
        self.draw_ui()

        if self.scene == SNO_TREASURE:
            # 宝箱発見
            pyxel.text(80, 120, "You found a treasure chest!", pyxel.COLOR_YELLOW)
        
        if self.buttle_mode:
            if self.monster:
                # # モンスターのHPを右上に表示
                # pyxel.text(200, 10, f"{self.monster['name_en']} : {self.monster['HP']}", 8)
                # モンスターのHPバーを描画
                monster_x = pyxel.width - 134
                monster_y = pyxel.height - 124
                self.draw_hp_bar(monster_x - 8, monster_y + 18, 32, 4, self.monster["HP"], self.monster["MAX_HP"])

                # 点滅中でないか、または奇数フレームならモンスターを描画
                if not self.is_blinking or pyxel.frame_count % 6 < 3:
                    # モンスター画像を画面中央に表示
                    self.draw_monster_image()

        # メッセージボックスを描画
        self.draw_message_box()

        # カメラをリセット
        pyxel.camera(0, 0)

        # A/Bボタンを描画
        self.draw_buttons()

    def get_text_color(self):
        if self.player["HP"] <= 20:
            return pyxel.COLOR_RED
        if self.player["HP"] <= 50:
            return pyxel.COLOR_YELLOW
        if self.player["HP"] >= 120:
            return pyxel.COLOR_LIGHT_BLUE
        return pyxel.COLOR_WHITE

    def draw_ui(self):
        # プレイヤーのステータス表示
        pyxel.text(10, 10, f"Floor: {self.floor}", self.get_text_color())
        pyxel.text(10, 20, f"HP: {self.player['HP']}", self.get_text_color())
        pyxel.text(10, 30, f"ATK: {self.player['ATK']} (+{self.player['weapon']['bonus_atk']})", self.get_text_color())
        pyxel.text(10, 40, f"DEF: {self.player['DEF']} (+{self.player['shield']['bonus_def']})", self.get_text_color())
        pyxel.text(10, 50, f"Weapon: {self.player['weapon']['name_en']}", self.get_text_color())
        pyxel.text(10, 60, f"Shield: {self.player['shield']['name_en']}", self.get_text_color())

    def draw_monster_image(self):
        """モンスター画像を画面中央に描画"""
        if self.monster is None:
            return  # モンスター情報が不完全なら描画しない
        x = (pyxel.width - 64) // 2
        y = (pyxel.height - 64) // 2 - 20

        # 画像のロード（画像はassets.pyxres内で管理されていると仮定）
        # pyxel.image(0).load(0, 0, "goblin.png")  # 画像ファイルのパスに変更
        pyxel.image(0).load(0, 0, self.monster["image_file"])  # 画像ファイルのパスに変更

        # モンスター画像を画面に描画
        # x, y は表示位置、0 は使用する画像のインデックス
        pyxel.blt(x, y, 0, 0, 0, 64, 64)  # 16x16の画像を(50, 50)に表示

    def draw_hp_bar(self, x, y, width, height, current_hp, max_hp):
        """HPバーを描画する関数"""
        # HPバーの背景（黒）
        pyxel.rect(x, y, width, height, 0)

        # 現在のHPバー（緑）
        hp_width = int(width * (current_hp / max_hp))  # HPに応じたバーの幅
        pyxel.rect(x, y, hp_width, height, 11)  # 緑色（色コード: 11）

    def handle_level_up(self, div):
        """成長選択モードの処理"""
        if div == "ATK":  # 攻撃力アップ
            self.player["ATK"] += 2
            self.message = "You gained +2 ATK!"
            self.waiting_for_input = True
        if div == "DEF":  # 防御力アップ
            self.player["DEF"] += 2
            self.message = "You gained +2 DEF!"
            self.waiting_for_input = True
        if div == "HP":  # HP回復
            self.player["HP"] += 10
            self.message = "You recovered 10 HP!"
            self.waiting_for_input = True

    def obtain_treasure(self):
        """宝箱を開けて装備を取得"""
        if random.choice([True, False]):  # ランダムで剣か盾を選択
            new_weapon = self.get_higher_rank_item(self.weapon_data, self.player["weapon"]["rank"])
            if new_weapon:
                self.player["weapon"] = new_weapon
                self.message = f"You found a {new_weapon['name_en']}! ATK +{new_weapon['bonus_atk']}."
            else:
                self.message = "You found a chest, but no better weapon was inside."
        else:
            new_shield = self.get_higher_rank_item(self.shield_data, self.player["shield"]["rank"])
            if new_shield:
                self.player["shield"] = new_shield
                self.message = f"You found a {new_shield['name_en']}! DEF +{new_shield['bonus_def']}."
            else:
                self.message = "You found a chest, but no better shield was inside."
        self.waiting_for_input = True

    def get_higher_rank_item(self, items, current_rank):
        """現在よりランク高い装備品をランダムに取得"""
        # 1か2ランクの高い装備品を取得
        rank = random.randint(1, 2)
        higher_rank_items = [item for item in items if item["rank"] == (current_rank + rank)]
        if higher_rank_items:
            return random.choice(higher_rank_items)

    def player_attack(self):
        # チャンネル3で攻撃効果音を再生
        pyxel.play(3, self.player["weapon"]["se"])
        # pyxel.playm(14, loop=True)  # 0番目の音楽トラックをループ再生
        # モンスターを点滅
        self.start_blinking(BLINK_FRAME)

        damage_to_monster = max(1, self.player["ATK"] + self.player["weapon"]["bonus_atk"] - self.monster["DEF"])
        if self.monster["HP"] < damage_to_monster:
            self.monster["HP"] = 0
        else:
            self.monster["HP"] -= damage_to_monster

        self.message = f"You attacked! Monster took {damage_to_monster} damage."
        self.waiting_for_push = True
        self.is_player_turn = False

    def monster_attack(self):
        # チャンネル3で攻撃効果音を再生
        pyxel.play(3, self.monster["se"])
        # 画面を揺らす
        self.start_shake(SHAKE_FRAME)

        damage_to_player = max(1, self.monster["ATK"] - (self.player["DEF"] + self.player["shield"]["bonus_def"]))
        self.player["HP"] -= damage_to_player
        self.message = f"Monster attacked! You took {damage_to_player} damage."
        self.waiting_for_push = True
        self.is_player_turn = True

    def check_victory(self):
        if self.monster["HP"] <= 0:
            self.message = ("Monster defeated!")
            self.waiting_for_push = True
            self.scene = SNO_BATTLE_VICTORY
            self.is_player_turn = False
            return True
        return False

    def check_defeat(self):
        if self.player["HP"] <= 0:
            # フロアごとのメッセージ
            if self.floor <= 20:
                self.message = "The darkness has consumed you..."
            elif self.floor <= 40:
                self.message = "So close to the deep floors..."
            elif self.floor <= 60:
                self.message = "Your story will be remembered."
            elif self.floor <= 80:
                self.message = "A shining hero, defeated in shadow."
            else:
                self.message = "You almost became the savior..."
            # self.message = "Game Over! You were defeated."
            self.waiting_for_input = True
            self.scene = SNO_GAMEOVER
            # pyxel.quit()
            return True
        return False

    def choose_random_monster_or_treasure(self):
        """次に出現するイベントをランダムに決定"""
        if random.random() < 0.2:  # 20%の確率で宝箱を出現
            self.scene = SNO_TREASURE
            self.is_player_turn = False
            self.message = "You found a treasure chest! Press SPACE to open it."
            self.waiting_for_push = True
        else:
            #戦闘イベント
            self.scene = SNO_BATTLE
            self.is_player_turn = True
            self.buttle_mode = True
            self.monster = self.choose_random_monster()

    def choose_random_monster(self):
        # """CSVデータからランダムでモンスターを選択"""
        """ランダムにモンスターを選択し、出現メッセージを設定"""
        monsters = []
        for monster in self.normal_monster_data:
            if monster["l_floor"] > self.floor:
                continue
            if monster["u_floor"] < self.floor:
                continue
            monsters.append(monster)

        monster = random.choice(monsters).copy()
        appearance_message = random.choice(self.monster_messages)
        self.message = appearance_message.format(monster_name=monster["name_en"])
        self.waiting_for_push = True
        return monster

    def choose_unique_monster(self):
        for monster in self.unique_monster_data:
            if monster["l_floor"] > self.floor:
                continue
            if monster["u_floor"] < self.floor:
                continue
            appearance_message = random.choice(self.monster_messages)
            self.message = appearance_message.format(monster_name=monster["name_en"])
            return monster.copy()

    def draw_message_box(self):
        # メッセージボックスの設定
        box_x = 10
        box_y = 200
        box_width = 236
        box_height = 40

        # メッセージボックスの背景を黒で描画
        # 枠線を白（7）
        pyxel.rectb(box_x, box_y, box_width, box_height, 7)
        # 背景を黒（0）
        pyxel.rect(box_x + 1, box_y + 1, box_width - 2, box_height - 2, 0)
        
        # メッセージを白色で描画
        pyxel.text(box_x + 10, box_y + 10, self.message, self.get_text_color())

    #-----------------------------------
    #  A / Bボタン押下判定
    #-----------------------------------
    def is_button_a_pressed(self):
        """Aボタンが押されたか"""
        return (
            pyxel.btnp(pyxel.KEY_A)
            or self.is_touch_in_button(self.button_a_x, self.button_a_y)
        )

    def is_button_d_pressed(self):
        """Dボタンが押されたか"""
        return (
            pyxel.btnp(pyxel.KEY_D)
            or self.is_touch_in_button(self.button_d_x, self.button_d_y)
        )

    def is_button_h_pressed(self):
        """Hボタンが押されたか"""
        return (
            pyxel.btnp(pyxel.KEY_H)
            or self.is_touch_in_button(self.button_h_x, self.button_h_y)
        )

    def is_touch_in_button(self, bx, by):
        """タッチ位置がボタン範囲内かを判定"""
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            dx = pyxel.mouse_x - bx
            dy = pyxel.mouse_y - by
            return dx * dx + dy * dy <= self.button_radius * self.button_radius
        return False

    #-----------------------------------
    #  ボタン描画
    #-----------------------------------
    def draw_buttons(self):
        # Aボタン
        pyxel.circ(self.button_a_x, self.button_a_y, self.button_radius, pyxel.COLOR_LIGHT_BLUE)
        pyxel.text(self.button_a_x - 3, self.button_a_y - 3, "A", pyxel.COLOR_WHITE)

        # Bボタン
        pyxel.circ(self.button_d_x, self.button_d_y, self.button_radius, pyxel.COLOR_RED)
        pyxel.text(self.button_d_x - 3, self.button_d_y - 3, "D", pyxel.COLOR_WHITE)

        # Hボタン
        pyxel.circ(self.button_h_x, self.button_h_y, self.button_radius, pyxel.COLOR_RED)
        pyxel.text(self.button_h_x - 3, self.button_h_y - 3, "H", pyxel.COLOR_WHITE)

if __name__ == "__main__":
    DungeonGame()
