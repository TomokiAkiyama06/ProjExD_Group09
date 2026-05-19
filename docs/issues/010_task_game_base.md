---
title: "core/game.py：Game基底クラスの実装"
labels: ["task", "core"]
assignees: []
milestone: null
parent: "008_epic_core_package.md"
depends_on: ["009_task_constants.md"]
---

## 概要

`HostGame`, `ClientGame`, `SoloGame` が共通で継承するゲームループの枠組みを `core/game.py` に実装する。

## 作業

- `Game` 基底クラスを定義
- 必須メソッド：
  - `__init__()`：pygame初期化、画面作成
  - `update()`：1フレーム分の状態更新（派生クラスでオーバーライド）
  - `draw()`：1フレーム分の描画（派生クラスでオーバーライド）
  - `run()`：メインループ
- 型ヒント・docstring 必須

### 例

```python
import pygame as pg
from core.constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS


class Game:
    """ゲームの基底クラス。共通のループ構造を提供する。"""

    def __init__(self) -> None:
        pg.init()
        self._screen: pg.Surface = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self._clock: pg.time.Clock = pg.time.Clock()
        self._running: bool = True

    def update(self) -> None:
        """1フレーム分の更新。派生クラスでオーバーライドする。"""
        raise NotImplementedError

    def draw(self) -> None:
        """1フレーム分の描画。派生クラスでオーバーライドする。"""
        raise NotImplementedError

    def run(self) -> None:
        """メインループ。"""
        while self._running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self._running = False
            self.update()
            self.draw()
            pg.display.flip()
            self._clock.tick(FPS)
        pg.quit()
```

## 完了条件

- 派生クラスから継承して画面表示できる
- ウィンドウの×ボタンで終了できる
