"""全プロジェクトで共有する定数。

担当ごとに自分のセクションへ定数を追記する。マジックナンバーは原則として
ここに集約する。
"""

# ===== 画面・描画（ベース） =====
SCREEN_WIDTH: int = 960
SCREEN_HEIGHT: int = 540
FPS: int = 60

# ===== 色 =====
COLOR_BG: tuple[int, int, int] = (18, 22, 28)
COLOR_TEXT: tuple[int, int, int] = (238, 238, 238)
COLOR_WHITE: tuple[int, int, int] = (255, 255, 255)
COLOR_BLACK: tuple[int, int, int] = (0, 0, 0)
COLOR_PLAYER: tuple[int, int, int] = (80, 180, 255)
COLOR_ENEMY: tuple[int, int, int] = (240, 90, 90)
COLOR_TOWER: tuple[int, int, int] = (100, 220, 150)
COLOR_FORTRESS: tuple[int, int, int] = (200, 200, 80)
COLOR_BULLET: tuple[int, int, int] = (255, 220, 120)
COLOR_HP_BAR_BG: tuple[int, int, int] = (60, 60, 60)
COLOR_HP_BAR_FG: tuple[int, int, int] = (90, 220, 120)

# ===== ゲームバランス（ベース） =====
INITIAL_GOLD: int = 100
FORTRESS_MAX_HP: int = 1000
PLAYER_MAX_HP: int = 100
ENEMY_BASE_HP: int = 30
ENEMY_BASE_DAMAGE: int = 5
ENEMY_BASE_REWARD: int = 1
TOWER_BASE_RANGE: float = 140.0
TOWER_BASE_DAMAGE: int = 8
TOWER_BASE_COOLDOWN: float = 0.8
BULLET_SPEED: float = 360.0

# ===== ネットワーク（ベース） =====
SERVER_HOST: str = "127.0.0.1"
SERVER_PORT: int = 50000

# ===== 進化AI（担当①） =====
# 担当①が記述

# ===== ネットワーク（担当②） =====
# 担当②が記述

# ===== タワー属性（担当③） =====
# 担当③が記述

# ===== 前線戦闘・演出（担当④） =====
# 担当④が記述

# ===== 対戦・可視化・サウンド（担当⑤） =====
# 担当⑤が記述
