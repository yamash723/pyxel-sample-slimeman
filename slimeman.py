import pyxel
import time
from random import randint
from dataclasses import dataclass

SCREEN_WIDTH = 160
SCREEN_HEIGHT = 120
BACKGROUND_COLOR_NUM = 12

STARTING_POINT_X = 75
STARTING_POINT_Y = 80

CLEAR_POINT = 2000 # クリアに必要なポイント数
COIN_POINT = 100 # 1コインのポイント

# シーン管理定数
SCENE_TITLE = 0
SCENE_PLAY = 1
SCENE_GAMEOVER = 2

# 降らせる数と間隔を調整して画面上のコイン数を調整
COINS_NUMBER = 8 # 降らせるコインの数
COIN_MARGIN = 10 # コイン同士のY軸間隔固定値
COIN_BETWEEN_ADJUST = 5 # コイン同士の間隔調整
COIN_TOUCH_ADJUST = 6 # コイン接触判定時の許容値

@dataclass
class Sprite:
    img: int
    u: int
    v: int
    w: int
    h: int
    colkey: int = -1

class Player:
    __SPEED = 4
    __SPRITE_WIDTH = 15
    __SPRITE_HEIGHT = 15

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.__sprite = Sprite(0, 0, 0, self.__SPRITE_WIDTH, self.__SPRITE_HEIGHT, 13)

    def move_left(self):
        self.x = max(self.x - self.__SPEED, 0)

    def move_up(self):
        self.y = max(self.y - self.__SPEED, 0)

    def move_right(self):
        limit_pos_x = pyxel.width - self.__SPRITE_WIDTH
        self.x = min(self.x + self.__SPEED, limit_pos_x)

    def move_down(self):
        limit_pos_y = pyxel.height - self.__SPRITE_HEIGHT
        self.y = min(self.y + self.__SPEED, limit_pos_y)

    def draw(self):
        pyxel.blt(
            self.x,
            self.y,
            self.__sprite.img,
            self.__sprite.u,
            self.__sprite.v,
            self.__sprite.w,
            self.__sprite.h,
            self.__sprite.colkey)


class Coin:
    __SPEED = 6
    __SPRITE_WIDTH = 16
    __SPRITE_HEIGHT = 16

    def __init__(self, order):
        self.x = 0
        self.y = 0
        self.is_active = True
        self.point = COIN_POINT
        self.__order = order
        self.__sprite = Sprite(0, 16, 0, self.__SPRITE_WIDTH, self.__SPRITE_HEIGHT, 13)

        self.reset()

    def reset(self):
        self.x = randint(0, pyxel.width - self.__SPRITE_WIDTH)
        self.y = (COIN_MARGIN * self.__order + randint(0, COIN_BETWEEN_ADJUST)) * -1 # 初期表示は画面外にするためマイナスにする
        self.is_active = True


    def fall(self):
        self.y += self.__SPEED

        if self.y > (pyxel.height):
            limit_pos_x = pyxel.width - self.__SPRITE_WIDTH
            self.reset()

    def draw(self):
        pyxel.blt(
            self.x,
            self.y,
            self.__sprite.img,
            self.__sprite.u,
            self.__sprite.v,
            self.__sprite.w,
            self.__sprite.h,
            self.__sprite.colkey)

class App:
    def __init__(self):
        pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT, scale=3, caption="Slimeman")
        pyxel.load("assets/assets.pyxres")

        self.reset()
        self.scene = SCENE_TITLE

        pyxel.run(self.update, self.draw)
    
    def reset(self):
        self.player = Player(STARTING_POINT_X, STARTING_POINT_Y)
        self.coins = [Coin(i) for i in range(COINS_NUMBER)]
        self.score = 0
        self.begintime = time.time()
        self.playtime = 0
    
    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

        if self.scene == SCENE_TITLE:
            self.update_title()
        elif self.scene == SCENE_PLAY:
            self.update_play()
        elif self.scene == SCENE_GAMEOVER:
            self.update_gameover()

    def update_title(self):
        if pyxel.btnp(pyxel.KEY_ENTER):
            self.scene = SCENE_PLAY

    def update_play(self):
        if pyxel.btn(pyxel.KEY_LEFT):
            self.player.move_left()
        if pyxel.btn(pyxel.KEY_RIGHT):
            self.player.move_right()
        if pyxel.btn(pyxel.KEY_UP):
            self.player.move_up()
        if pyxel.btn(pyxel.KEY_DOWN):
            self.player.move_down()

        for coin in self.coins:
            coin.fall()
        
        self.check_get_coin()

        if self.score >= CLEAR_POINT:
            self.scene = SCENE_GAMEOVER
        
        self.playtime = time.time() - self.begintime

    def update_gameover(self):
        if pyxel.btnp(pyxel.KEY_ENTER):
            self.reset()
            self.scene = SCENE_PLAY

    def draw(self):
        pyxel.cls(BACKGROUND_COLOR_NUM)

        if self.scene == SCENE_TITLE:
            self.draw_title_scene()
        elif self.scene == SCENE_PLAY:
            self.draw_play_scene()
        elif self.scene == SCENE_GAMEOVER:
            self.draw_gameover_scene()

    def draw_title_scene(self):
        pyxel.text(65, 50, "Slimeman", pyxel.frame_count % 16)
        pyxel.text(50, 60, "- PRESS ENTER -", 13)

    def draw_play_scene(self):
        self.draw_object()

    def draw_gameover_scene(self):
        self.draw_object()

        pyxel.text(65, 50, "GAME OVER", 8)
        pyxel.text(50, 60, "- PRESS ENTER -", 13)

    def draw_object(self):
        self.player.draw()
        for coin in self.coins:
            if coin.is_active:
                coin.draw()

        score_txt = "Score {:>4}".format(self.score)
        pyxel.text(5, 4, score_txt, 1)
        pyxel.text(4, 4, score_txt, 7)

        time_txt = "Time {:.4g}".format(self.playtime)
        pyxel.text(5, 12, time_txt, 1)
        pyxel.text(4, 12, time_txt, 7)

    def check_get_coin(self):
        player_x = self.player.x
        player_y = self.player.y

        for coin in self.coins:
            is_touched = abs(coin.x - player_x) < COIN_TOUCH_ADJUST and abs(coin.y - player_y) < COIN_TOUCH_ADJUST
            if coin.is_active and is_touched:
                self.score += coin.point
                coin.is_active = False
                pyxel.play(0, 0)

App()