# 難易度設計（ゲーム拡張 / Epic #125）

> solo / host モードの難易度カーブと、その調整に使う定数をまとめたドキュメント。
> 数値はすべて `core/constants.py` の「難易度スケーリング」節に集約されている。
> **定数を変更したら、このドキュメントも合わせて更新すること。**

関連 Issue: #126（最大ウェーブ延長）/ #127（敵HP）/ #128（特殊敵・ボス）/ #129（クリアボーナス）

---

## 1. 全体方針

ゲームの難易度は次の 4 つで上昇する。

1. **最大ウェーブ数の延長**：5 → 15 ウェーブまで遊べる
2. **敵 HP のスケーリング**：通常敵は「世代」、特殊敵・ボスは「ウェーブ」で硬くなる
3. **特殊敵の増加**：後半ウェーブほど高速敵・盾持ち敵が混ざる
4. **ウェーブクリアボーナス**：難易度上昇に対するプレイヤー側の成長手段

加えて、敵の出現数自体も `WaveManager` 既定で `BASE_SPAWN_COUNT + (wave-1)*2` と増える。

### 重要：スケーリング基準が「世代」と「ウェーブ」で分かれている理由

| 対象 | 基準 | 理由 |
|------|------|------|
| 通常敵（`EvolvedEnemy`） | **世代（generation）** | 進化AIの fitness 評価対象。1 世代の個体群を複数ウェーブで round-robin 評価するため、ウェーブ基準だと同一世代内で個体ごとに HP が変わり、生存時間・前進距離による fitness に**選択バイアス**が乗る。世代基準なら同一世代内の HP が一定になり公平。 |
| 特殊敵 / ボス | **ウェーブ / 出現回** | fitness 評価の対象外（`EvolutionDriver.spawn_enemy` を経由しない）。バイアスを生まないのでウェーブ基準でよい。 |

> この区別は #127 のレビュー指摘（同一世代で HP スケールを揃える）への対応で確定したもの。**通常敵をウェーブ基準でスケールし直してはいけない。**

---

## 2. スケーリング式と定数

### 2.1 最大ウェーブ数（#126）

| 定数 | 値 | 説明 |
|------|----|------|
| `SOLO_MAX_WAVE` | 15 | solo / host の最大ウェーブ数 |
| `BOSS_WAVE_MODULO` | 5 | この倍数ウェーブ（5,10,15）でボス出現 |

- `main.py` の `_build_solo_kwargs()` が `max_wave=SOLO_MAX_WAVE` を渡す。
- `BOSS_WAVE_MODULO` の倍数にしておくと、最終ウェーブがボス戦で締まる。

### 2.2 通常敵 HP（#127, 世代基準）

適用箇所：`EvolutionDriver.spawn_enemy()` → `BaseEnemy.scale_hp()`

```
HP = ENEMY_BASE_HP × (1 + ENEMY_HP_GROWTH_PER_GENERATION × (世代 - 1))
```

| 定数 | 値 | 説明 |
|------|----|------|
| `ENEMY_BASE_HP` | 30 | 通常敵の基礎 HP |
| `ENEMY_HP_GROWTH_PER_GENERATION` | 0.15 | 世代ごとに +15%（世代1 は等倍） |

### 2.3 特殊敵（#128, ウェーブ基準）

適用箇所：`WaveManager` のスポーン処理。通常スポーン枠を確率で特殊敵に置き換える。

```
出現率   = min(SPECIAL_ENEMY_PROBABILITY_MAX,
               SPECIAL_ENEMY_BASE_PROBABILITY + SPECIAL_ENEMY_PROBABILITY_GROWTH_PER_WAVE × (wave - 1))
特殊敵HP = 基礎HP × (1 + SPECIAL_ENEMY_HP_GROWTH_PER_WAVE × (wave - 1))
```

fast / shielded の内訳は `create_special_enemy()` が `SPECIAL_FAST_PROBABILITY : SPECIAL_SHIELDED_PROBABILITY`（= 0.2 : 0.1）の相対比で決める。

| 定数 | 値 | 説明 |
|------|----|------|
| `SPECIAL_ENEMY_BASE_PROBABILITY` | 0.1 | wave1 の特殊敵出現率 |
| `SPECIAL_ENEMY_PROBABILITY_GROWTH_PER_WAVE` | 0.04 | ウェーブごとに出現率 +0.04 |
| `SPECIAL_ENEMY_PROBABILITY_MAX` | 0.5 | 出現率の上限 |
| `SPECIAL_ENEMY_HP_GROWTH_PER_WAVE` | 0.1 | 特殊敵 HP をウェーブごと +10% |
| `FAST_ENEMY_HP` / `SHIELDED_ENEMY_HP` | 12 / 22 | 各特殊敵の基礎 HP |

### 2.4 ボス（#128, 出現回基準）

適用箇所：`WaveManager` のボススポーン。`出現回 = wave // BOSS_WAVE_MODULO`（wave5→1, wave10→2, wave15→3）。

```
ボスHP   = 基礎HP   × (1 + BOSS_HP_GROWTH_PER_APPEARANCE × (出現回 - 1))
ボスDMG  = 基礎DMG  × (1 + BOSS_DAMAGE_GROWTH_PER_APPEARANCE × (出現回 - 1))
```

基礎 HP は `ENEMY_BASE_HP × BOSS_HP_MULTIPLIER`（= 30 × 15 = 450）。

| 定数 | 値 | 説明 |
|------|----|------|
| `BOSS_HP_MULTIPLIER` | 15 | 通常敵 HP に対するボス HP 倍率 |
| `BOSS_HP_GROWTH_PER_APPEARANCE` | 0.3 | 出現回ごとに HP +30% |
| `BOSS_DAMAGE_GROWTH_PER_APPEARANCE` | 0.15 | 出現回ごとに接触ダメージ +15% |

### 2.5 ウェーブクリアボーナス（#129）

適用箇所：`SoloGame._award_wave_clear_bonus()`（BATTLE→SUMMARY 遷移で発火）。拠点 HP は `Fortress.set_hp` 側で最大 HP にクランプ。

| 定数 | 値 | 説明 |
|------|----|------|
| `WAVE_CLEAR_GOLD_BONUS` | 20 | 通常クリアで得る資源 |
| `WAVE_CLEAR_FORTRESS_HEAL` | 30 | 通常クリアで回復する拠点 HP |
| `BOSS_WAVE_CLEAR_GOLD_BONUS` | 40 | ボスウェーブクリアの追加資源 |
| `BOSS_WAVE_CLEAR_FORTRESS_HEAL` | 60 | ボスウェーブクリアの追加拠点 HP |

ボスウェーブ（5の倍数）クリア時は通常分に上乗せされる（例：wave5 で資源 +60 / 拠点HP +90）。

---

## 3. 想定する難易度カーブ

| 区間 | ウェーブ | 狙い |
|------|---------|------|
| 序盤 | 1〜4 | 操作とタワー設置に慣れる。特殊敵はたまに出る程度（出現率 0.1〜0.22）。 |
| 中盤 | 5〜10 | 初ボス（wave5）。世代が進んで通常敵が硬くなり、特殊敵も増える。クリアボーナスでタワーを増強。 |
| 終盤 | 11〜15 | 特殊敵出現率が上限（0.5）付近。ボスは 3 体目で HP +60% / ダメージ +30%。進化AIも経路を学習済みで最難関。 |

---

## 4. 調整の早見表

「難しすぎ / 易しすぎ」を感じたら、まず以下を触る（すべて `core/constants.py`）。

| 変えたいこと | 触る定数 | 上げると |
|--------------|----------|----------|
| 全体の長さ | `SOLO_MAX_WAVE` | プレイ時間が延びる |
| 通常敵の硬さの伸び | `ENEMY_HP_GROWTH_PER_GENERATION` | 世代が進むほど急激に硬くなる |
| 特殊敵の多さ | `SPECIAL_ENEMY_BASE_PROBABILITY` / `..._GROWTH_PER_WAVE` / `..._MAX` | 特殊敵が増える |
| 特殊敵の硬さ | `SPECIAL_ENEMY_HP_GROWTH_PER_WAVE` | 後半の特殊敵が硬くなる |
| ボスの強さの伸び | `BOSS_HP_GROWTH_PER_APPEARANCE` / `BOSS_DAMAGE_GROWTH_PER_APPEARANCE` | 2 体目以降のボスが強くなる |
| プレイヤーの立て直しやすさ | `WAVE_CLEAR_*` / `BOSS_WAVE_CLEAR_*` | 易しくなる（資源・回復が増える） |

> 数値を変更したら、本ドキュメントの該当箇所も更新すること。
