import pygame as pg
import sys

pg.init()
screen = pg.display.set_mode((640, 200))
pg.display.set_caption("日本語フォントテスト画面")

# 1. あなたが配置した本物のフォントを読み込む
try:
    font = pg.font.Font("assets/font/NotoSansJP-Regular.ttf", 28)
except FileNotFoundError:
    print("\n❌ エラー: assets/font/ の中に NotoSansJP-Regular.ttf が見つかりません！\n")
    sys.exit()

# 2. テスト用の日本語メッセージ（常用漢字入り）
text_surface = font.render("日本語テスト完了！ 漢字・機能・確認OK", True, (255, 255, 255))

# 画面の表示ループ
while True:
    screen.fill((40, 40, 40))  # 背景を暗いグレーに
    screen.blit(text_surface, (50, 80))  # 文字を描画
    pg.display.flip()

    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()
