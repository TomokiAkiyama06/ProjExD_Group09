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
FITNESS_DAMAGE_WEIGHT: float = 10.0
FITNESS_SURVIVAL_WEIGHT: float = 1.0
FITNESS_DISTANCE_WEIGHT: float = 5.0
EVOLUTION_ELITE_RATE: float = 0.2
EVOLUTION_TOURNAMENT_SIZE: int = 3

# ===== ネットワーク（担当②） =====
NET_STATE_HZ: int = 20  # ホスト→クライアントの状態ブロードキャスト周波数
NET_INPUT_HZ: int = 30  # クライアント→ホストの操作送信周波数
NET_PING_INTERVAL_SEC: float = 0.5  # ping を送る間隔（2Hz）
NET_TIMEOUT_SEC: float = 5.0  # 最終受信からこの秒数経過で切断扱い
NET_ACK_RESEND_INTERVAL_SEC: float = 0.5  # ACK 待ちタイムアウト→再送
NET_ACK_MAX_RETRIES: int = 5  # ACK 再送の最大回数
NET_RECV_BUFFER_BYTES: int = 4096  # recvfrom のバッファサイズ
NET_RECV_TIMEOUT_SEC: float = 0.2  # 受信スレッドの select タイムアウト

# ===== タワー属性（担当③） =====
# 火炎タワー
FIRE_DAMAGE: int = 10
FIRE_RANGE: float = 130.0
FIRE_COOLDOWN: float = 1.0
FIRE_EXPLOSION_RADIUS: float = 50.0
FIRE_EXPLOSION_FALLOFF: float = 0.6  # 中心から離れるほどダメージが下がる係数

# 氷タワー
ICE_DAMAGE: int = 5
ICE_RANGE: float = 130.0
ICE_COOLDOWN: float = 1.2
ICE_SLOW_FACTOR: float = 0.5  # 速度を半分にする
ICE_SLOW_DURATION: float = 3.0  # 3秒間

# 雷タワー
LIGHTNING_DAMAGE: int = 8
LIGHTNING_RANGE: float = 150.0
LIGHTNING_COOLDOWN: float = 0.6
LIGHTNING_CHAIN_RADIUS: float = 90.0
LIGHTNING_CHAIN_COUNT: int = 3  # 最大連鎖数（初撃含めて 3 体）
LIGHTNING_CHAIN_FALLOFF: float = 0.8  # 連鎖ごとにダメージ係数
LIGHTNING_VISUAL_DURATION: float = 0.2  # 稲妻ラインの表示秒数

# 物理タワー
PHYSICAL_DAMAGE: int = 22
PHYSICAL_RANGE: float = 180.0
PHYSICAL_COOLDOWN: float = 1.6
PHYSICAL_PIERCE_RATIO: float = 0.5  # 残HP割合に応じて最大 +50% のダメージ

# 色（属性別表示色）
COLOR_FIRE: tuple[int, int, int] = (240, 110, 60)
COLOR_ICE: tuple[int, int, int] = (110, 200, 240)
COLOR_LIGHTNING: tuple[int, int, int] = (250, 230, 80)
COLOR_PHYSICAL: tuple[int, int, int] = (200, 200, 200)

# アップグレード（共通）
TOWER_MAX_LEVEL: int = 3
TOWER_UPGRADE_COST_PER_LEVEL: tuple[int, ...] = (0, 30, 50)  # Lv1→2 が 30、Lv2→3 が 50
TOWER_UPGRADE_DAMAGE_BONUS: float = 0.4  # Lv ごとに +40%
TOWER_UPGRADE_RANGE_BONUS: float = 0.15  # Lv ごとに +15%
TOWER_UPGRADE_COOLDOWN_MULT: float = 0.85  # Lv ごとに ×0.85
TOWER_SELL_REFUND_RATIO: float = 0.5  # 総投資額の 50% を返金

# ===== 前線戦闘・演出（担当④） =====
# 担当④が記述

# ===== 対戦・可視化・サウンド（担当⑤） =====
# 担当⑤が記述
