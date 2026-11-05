---
title: 이벤트
nav_order: 3
parent: 플러그인
redirect_from:
  - /events
  - /events.html
---

# 이벤트
{: .no_toc }

1. TOC
{:toc}

## 핸들러

```rust
#[on(Harvest)]                      // 이 이벤트마다 불림
fn grown(e: Harvest) { /* … */ }

#[on(ActionBefore, priority = -10)] // 낮은 숫자가 먼저 (기본 0). 플러그인들 사이에서도 이 순서
fn first(e: ActionBefore) { /* … */ }

#[command("이름", "설명")]           // 채팅 "/이름 …" 일 때만
fn cmd(c: Command) { /* … */ }
```

- 핸들러는 이벤트를 값으로 받고 아무것도 돌려주지 않습니다.
- 같은 이벤트의 핸들러들은 우선순위 차례로 돌고, **앞 핸들러(앞 플러그인)가 `set`으로 바꾼 값을 뒤 핸들러가 받습니다.**
- 이벤트는 두 갈래입니다.
  - **취소할 수 있는 이벤트** (`Cancellable`): `e.cancel(why)` — 일어나지 않고, `why`가 플레이어에게 보입니다(`""`면 아무 말 없음).
    `e.set_cancelled(true)`는 `cancel("")`. 한 번 막히면 막힌 채이고, 뒤 핸들러(뒤 플러그인)는 불리지 않습니다.
  - **알리기만 하는 이벤트**: `cancel`이 아예 없어서 부르면 컴파일되지 않습니다.

## 모든 이벤트에 있는 것 (`Base`)

| 메서드 | |
|---|---|
| `name()` | 이벤트 이름 (`"harvest"`, `"action.before"` …) |
| `kind()` | 행동 종류 (`action.before`/`after`: `"till"` `"water"` `"buy"` …) |
| `id()` | 무엇에 대한 것: 아이템, 작물, 주민, 명령어 이름, 버튼 … |
| `tool()` | 쓴 도구 |
| `cell()` → `(i64, i64)` | 일어난 칸 |
| `n()` → `i64` | 행동의 개수 (산 개수, 판 개수 …) |
| `num(k)` → `f64` | 이벤트의 숫자 (아래) |
| `text(k)` → `String` | 이벤트의 글 (아래) |
| `set(k, v)` | 이벤트의 숫자 바꾸기 (서버가 플러그인들 다음에 읽음) |
| `roll(k)` → `f64` | 정해진 난수 [0, 1). 같은 이벤트면 다시 돌려도 같음 (`k` 0~63로 여럿) |
| `day()` `season()` `date()` | 며칠째(1부터), 계절(0 봄 … 3 겨울), 계절의 날(1~28) |
| `player()` → [`Player`](sdk#player) | 이벤트의 플레이어 |
| `world()` → [`World`](sdk#world) | 이벤트의 월드 |
| `drop_item(item, n)` | 이벤트의 칸에 아이템 떨구기 (수확처럼) |
| `fx(name)` | 이벤트의 칸에서 게임의 소리 (`"hit"` `"pickup"` `"click"` …), 월드의 모두에게 |
| `prop(name, v)` | 그 칸에 선 것의 속성 (`"scale"`: 나무·바위·과일나무를 그 크기로 그림) |

### `num` / `text`의 키

| 키 | |
|---|---|
| `day` `season` `date` `minute` | 날짜와 시각 (`minute`: 하루의 분, 6:00 = 360) |
| `gold` `energy` | 플레이어의 골드, 기력 |
| `me.x` `me.z` `me.fx` `me.fz` | 행동한 플레이어의 위치(칸)와 바라보는 방향 |
| `tile.*` `tree.*` `debris.*` `prop.*` | 그 칸의 밭·과일나무·야생 나무와 바위·선 것 (`text("tile.crop")` `text("tree.id")` `text("debris.id")`) |
| `weather` | `text`: 날씨 (`grow`에도) |
| 이벤트마다의 값 | `price`, `count`, `quality`, `days`, `amount`, `damage` … (아래 각 이벤트) |
| `now` | 벽시계: 1970년부터의 ms (서버의 모든 월드에 같음; [`now()`](sdk#함수)) |
| `players`, `player.N.x`, `player.N.z` | `tick`의 사람 수와 위치 (`Tick::players()`가 감쌈) |

## 이벤트 목록

| SDK 타입 | 이름 | 취소 | 언제 |
|---|---|:-:|---|
| [`ActionBefore`](#actionbefore--actionafter) | `action.before` | ✔ | 플레이어 행동 직전 |
| [`ActionAfter`](#actionbefore--actionafter) | `action.after` | | 행동이 받아들여진 뒤 |
| [`Use`](#use) | `use` | ✔ | 게임에 쓰임새가 없는 아이템을 씀 |
| [`Grow`](#grow) | `grow` | ✔ | 밤마다 작물 하나 |
| [`Harvest`](#harvest) | `harvest` | ✔ | 수확 |
| [`Price`](#price--sell) | `price` | | 상점의 값 |
| [`Sell`](#price--sell) | `sell` | | 파는 값 |
| [`PlayerDamage`](#playerdamage) (`Damage`) | `damage` | ✔ | 플레이어가 다치려 함: 몬스터, `Player::damage`, 다른 플레이어의 타격 |
| [`Strike`](#strike) | `strike` | ✔ | 플레이어가 몬스터를 침 |
| [`Spawn`](#spawn) | `spawn` | ✔ | 몬스터가 나옴 (밤, 광산 층) |
| [`Tick`](#tick) | `tick` | | 누가 있는 월드에서 플러그인마다 기본 1초에 한 번 (`Registry::tick_rate(n)`, `#[every(초)]`) |
| [`ServerTick`](#servertick) | `server.tick` | | 서버의 틱, 아무도 없어도 1초에 두 번 |
| [`DayEnd`](#dayend) | `day.end` | ✔ | 하루가 끝나려 함 |
| [`DayChange`](#daychange) | `day.change` | ✔ | 아침에 날짜가 넘어가려 함 |
| [`Button`](#button) | `button` | ✔ | 플러그인 버튼이나 창의 버튼을 누름 |
| [`Command`](#command) | `command` | ✔ | 채팅 명령어 |
| [`Morning`](#morning) | `morning` | | 밤이 지나고 아침 (농장 주인에게) |
| [`Join`](#join--leave) | `join` | | 월드에 들어옴 |
| [`Leave`](#join--leave) | `leave` | | 월드에서 나감 |
| [`PlayerLogin`](#playerlogin) | `login` | ✔ | 서버에 들어오기 직전 |
| [`PlayerItemHeld`](#playeritemheld) | `held` | | 단축바의 다른 칸을 고르거나 고른 칸의 것이 바뀜 |
| [`Chat`](#chat) | `chat` | ✔ | 채팅 한 줄 |
| [`Words`](#words) | `words` | ✔ | 주민에게 말을 걸음 |
| [`MobStep`](#mobstep) | `mob` | | `script` 몬스터의 한 걸음 |
| [`MineFloor`](#minefloor) | `mine.floor` | | 광산 층이 그날 처음 만들어짐 |
| [`PlayerMove`](#playermove) | `move` | ✔ | 플레이어가 움직임 (가로나 위아래로) |
| [`WorldCreate`](#worldcreate) | `world.create` | | 월드가 만들어짐 |
| [`ChunkGenerate`](#chunkgenerate) | `chunk.generate` | | 청크가 처음 만들어짐 |
| [`PlayerDeath`](#playerdeath) | `death` | | 플레이어가 쓰러짐 (`killer()`) |
| [`PlayerRespawn`](#playerrespawn) | `respawn` | | 쓰러졌다 일어남 |
| [`PlayerTeleport`](#playerteleport) | `teleport` | ✔ | 플러그인이 플레이어를 옮기려 함 |
| [`PlayerInteractPlayer`](#playerinteractplayer) | `player.interact` | ✔ | 다른 플레이어에게 E |
| [`ModelEntityDamage`](#modelentitydamage--modelentitydeath) | `entity.damage` | ✔ | 체력 있는 이 플러그인의 엔티티를 플레이어가 침 |
| [`ModelEntityDeath`](#modelentitydamage--modelentitydeath) | `entity.death` | | 그 엔티티의 체력이 0 |
| [`ProjectileHit`](#projectilehit) | `projectile.hit` | | 이 플러그인의 발사체가 무언가에 닿음 |
| [`MobDeath`](#mobdeath) | `mob.death` | | 플레이어가 몬스터를 쓰러뜨림 |
| [`LevelUp`](#levelup) | `level` | | 스킬 레벨이 오름 |
| [`Enable`](#enable) | `enable` | | 서버가 켜질 때, 플러그인마다 한 번: [규칙 등록](rules) |
| [`BlockPlace`](#blockplace--blockbreak) | `block.place` | ✔ | 플레이어가 가방의 블록을 놓음 |
| [`BlockBreak`](#blockplace--blockbreak) | `block.break` | ✔ | 플레이어가 플러그인 블록을 부숨 |
| [`ChunkLoad`](#chunkload) | `chunk.load` | | 청크가 서버의 메모리에 들어옴 |
| [`Packet`](#packet) | `packet` | | 게임이 이 플러그인의 채널로 보낸 패킷 (HUD 버튼·입력·키) |
| [`FastPacket`](#fastpacket) | `fast` | | 게임 쪽 코드가 보낸 빠른 패킷 (데이터그램) |
| [`InventoryClick`](#inventoryclick) | `inventory` | | 이 플러그인의 인벤토리 창을 누름 |
| [`EntityInteract`](#entityinteract) | `entity.interact` | | 플레이어가 이 플러그인의 엔티티를 E로 씀 |
| [`WindowOpen`](#windowopen) | `packet`의 `"window"` | | 이 플러그인이 가져간(`Hud::replace`) 게임의 창을 엶 |
| [`Dismount`](#dismount) | `dismount` | | 서버가 플레이어를 탈것에서 내림 (문, 다른 월드로 감, 나감) |
| [`Timer`](#timer) | `timer` | | 이 플러그인의 타이머(`Scheduler::run_later` / `run_every`)가 됨 |
| [`EffectStart`](#effectstart--effectend) | `effect.start` | ✔ | 상태 효과가 시작되려 함 (`Player::add_effect`) |
| [`EffectEnd`](#effectstart--effectend) | `effect.end` | | 상태 효과가 끝남 (시간이 다 됨, `remove_effect`) |
| [행동마다의 이벤트](#행동마다의-이벤트) | `action.before` (그 종류만) | ✔ | |

### 별칭

같은 이벤트를 이 이름으로도 씁니다.

| 별칭 | = |
|---|---|
| `PlayerJoin` / `PlayerQuit` | `Join` / `Leave` |
| `PlayerChat` / `PlayerCommand` | `Chat` / `Command` |
| `PlayerInteract` / `PlayerInteractNpc` | `Use` / `Words` |
| `BlockGrow` | `Grow` |
| `EntityDamage` / `EntityDamageByPlayer` | `Damage` / `Strike` |
| `CreatureSpawn` / `EntityDeath` | `Spawn` / `MobDeath` |
| `PlayerLevelChange` | `LevelUp` |

예전의 별칭 `BlockBreak`(`hit`)·`BlockPlace`(`place` `furnish`)는 [`WildHit`·`ThingPlace`](#행동마다의-이벤트)로 바뀌었고,
`BlockBreak` `BlockPlace`는 이제 [블록](#blockplace--blockbreak)의 이벤트입니다.

## 켜질 때

### Enable

서버가 켜질 때 플러그인마다 한 번(Bukkit의 `onEnable`). 월드도 플레이어도 없습니다. **`Registry`가 등록하는 곳은 여기뿐**입니다:
아이템, 작물, 블록, 몬스터, 동물, 주민, 모델, 글자, 규칙의 숫자 … ([규칙 등록](rules)).

```rust
#[on(Enable)]
fn enable(_e: Enable) {
    Registry::set("bag.slots", "48");
    Registry::block("ruby_block", &BlockKind::new("루비 블록", "stone", "e0405a"));
}
```

## 행동

### ActionBefore / ActionAfter

플레이어의 모든 행동이 서버에 올라올 때 `action.before`(막을 수 있음), 서버가 받아들인 뒤 `action.after`가 옵니다.
`kind()`가 행동 종류입니다. 일어난 뒤를 보려면 `ActionAfter`에서 `kind()`를 보세요.

```rust
#[on(ActionAfter)]
fn watered(e: ActionAfter) {
    if e.kind() == "water" && e.roll(0) < 0.1 { e.drop_item("fiber", 1) }
}
```

### 행동마다의 이벤트

모두 `action.before`의 그 종류만 받는 타입입니다(취소 가능). 다른 종류의 행동에는 불리지 않습니다.

| SDK 타입 | 행동 종류 (`kind()`) | |
|---|---|---|
| `PlayerTill` | `till` | 괭이로 밭 갈기 |
| `PlayerPlant` | `plant` `sapling` | 씨앗·묘목 심기 (`id` 씨앗) |
| `PlayerWater` | `water` | 물 주기 |
| `PlayerHarvest` | `harvest` `fruit` | 작물·과일나무 거두기 (거둔 양은 [`Harvest`](#harvest)) |
| `WildHit` | `hit` | 나무·바위·잡초·광맥을 도구로 침 |
| `ThingPlace` | `place` `furnish` | 땅에 설치물, 집에 가구 놓기 |
| `BlockRemove` | `unplace` `unfurnish` | 놓은 것 다시 줍기 |
| `PlayerFish` | `cast` `fish` `release` | 던지기, 낚아 올림, 놓아줌 |
| `PlayerEat` | `eat` | 먹기 |
| `PlayerCraft` | `craft` | 제작 |
| `PlayerSell` | `ship` `sell` | 출하 상자, 상점에 팔기 |
| `PlayerBuy` | `gold` | 상점에서 사기, 돈 내기 |
| `PlayerTalk` | `talk` | 주민에게 말 걸기 |
| `PlayerGift` | `gift` | 선물 |
| `PlayerSleep` | `sleep` | 잠자리에 듦 |
| `PlayerDoor` | `door` | 건물의 문 (`id` 방, `n` 1 들어감 / 0 나감) |
| `PlayerMine` | `mine` | 광산의 구멍·사다리 (`n` 층) |
| `PlayerPickup` | `item` | 땅에서 줍기, 채집, 동물의 생산물, 우편 |
| `PlayerDrop` | `discard` | 버리기 |
| `PlayerAnimal` | `pet` `feed` `animal` | 쓰다듬기, 먹이 주기, 사기 |
| `PlayerEquip` | `equip` `unequip` | 장비 |
| `PlayerChest` | `store` `take` | 상자에 넣기·꺼내기 |
| `PlayerAttack` | `strike` | 몬스터에게 휘두름 |
| `PlayerQuest` | `quest` `request` `daily` `giveup` | 퀘스트·오늘의 의뢰 받기, 마치기, 포기 |
| `PlayerUpgrade` | `upgrade` `smith_pick` `enchant` | 대장간 도구 강화, 대장장이 고르기, 마법 부여 |
| `PlayerBuild` | `build` | 목수에게 건물 주문 |
| `PlayerGate` | `gate` | 레버로 성문 열기·닫기 |

```rust
#[on(PlayerSleep)]
fn no_sleep(e: PlayerSleep) { e.cancel("이 서버에선 잠들 수 없어요") }
```

### Use

게임에 쓰임새가 없는 아이템(플러그인이 [등록](rules)한 것 등)을 썼을 때. `id()` 아이템. 가져가려면 `player().take(id, 1)`.
아이템에 `"action"`(동작)이 있으면 게임이 그 동작을 하고 `"hit"`의 순간에 옵니다: [도구 동작](moving#도구-동작-플러그인-아이템).

## 농사와 장사

### Grow

밤마다 작물 하나에. 취소하면 오늘 밤 자라지 않습니다.

| | |
|---|---|
| `crop()` | 작물 id (`text("tile.crop")`) |
| `weather()` | 날씨 |
| `set_grows(bool)` | 오늘 밤 자라는지 |
| `set_days(f64)` | 오늘 밤 며칠치 자라는지 (원래 1) |

### Harvest

수확. 취소하면 거둬지지 않습니다.

| | |
|---|---|
| `crop()` | 작물 id |
| `count()` / `set_count(n)` | 거두는 개수 |
| `quality()` / `set_quality(q)` | 품질 |

### Price / Sell

상점의 사는 값 / 파는 값. 막을 수는 없고 값을 바꿉니다.

| | |
|---|---|
| `item()` | 아이템 id |
| `price()` / `set_price(gold)` | 값 |

```rust
#[on(Sell)]
fn festival(e: Sell) {
    if e.date() % 7 == 0 { e.set_price(e.price() * 1.25) }
}
```

### Morning

밤이 지나고 아침, 농장 주인에게. `player().give` `add_gold` `add_energy` `say` 등으로 아침의 선물.

## 전투와 몬스터

### PlayerDamage

플레이어가 다치려 할 때(Bukkit의 EntityDamageEvent): 몬스터의 접촉, 플러그인의 [`Player::damage`](sdk#피해-체력-pvp-팀), PvP가 켜진
월드에서 다른 플레이어의 휘두름. `amount()` / `set_amount(n)` (0이면 안 다침), `cause()` ("monster", "player", 또는 플러그인이 준 원인),
`by()` 친 사람의 이름("" 없음), `attacker()` → `Option<Player>`. 취소: 안 다침. 예전 이름 `Damage`도 그대로.

```rust
#[on(PlayerDamage)]
fn armor(e: PlayerDamage) {
    if e.cause() == "player" && e.player().team() == "수비" { e.set_amount(e.amount() * 0.5) }
}
```

### Strike

플레이어가 몬스터를 칠 때. `damage()` / `set_damage(n)`. 취소: 휘두름이 없던 일.

### Spawn

몬스터가 나올 때: 밤, 그리고 광산 층. `kind_id()` 종류, `floor()` 0은 지상(밤), 아니면 광산 층. 취소: 나오지 않음.

### MobStep

[등록](rules#몬스터-monsters_add)한 `monsters_add`에서 `"script": true`인 종류의 몬스터마다, 서버의 한 걸음(1초에 10번)에 옵니다. 한 걸음의
몬스터 모두를 모듈 하나가 차례로 받습니다.

| | |
|---|---|
| `mob()` → [`Mob`](sdk#enemyentity) | 그 몬스터 (`get("x")` `"z"` `"hp"` `"tier"` `"speed"` `"damage"` `"size"` `"t"`(나온 뒤 초)) |
| `kind_id()` | 종류 |
| `target()` → `Option<(이름, x, z, 거리)>` | 같은 층의 가장 가까운 플레이어 |
| `num("floor")` | 광산 층 (0 지상) |

```rust
#[on(MobStep)]
fn circle(e: MobStep) {
    let m = e.mob();
    if let Some((_, tx, tz, d)) = e.target() {
        if d < 1.5 { m.attack(2.0, 1.5) }
        let (dx, dz) = (tx - m.get("x"), tz - m.get("z"));
        m.set("vx", -dz * 0.5 + dx * 0.2); // 둘레를 돌며 다가감
        m.set("vz", dx * 0.5 + dz * 0.2);
    }
}
```

`mob` 이벤트에서 낸 `particle` `sound`는 월드의 모두에게 보입니다. 예: `plugins/new_creatures`.

### MobDeath

플레이어가 몬스터를 쓰러뜨렸을 때. `kind_id()` 종류, `position()` → `(x, z)`. `drop_item`은 그 몬스터 자리에 떨굽니다.

### PlayerDeath

플레이어가 쓰러질 때(체력이 다했거나 `Player::death`). `reason()` "monster" "plugin"(`death`) "damage"(`Player::damage`, 타격), `cause()`,
`killer()` 마지막으로 친 사람("" 없음: 킬 피드). `keep_inventory(true)`: 가방과 장비를 지킴. `hold(true)`: 바로 일어나지 않고 `Player::respawn`까지 쓰러진 채 대기. `respawn_at_spawn(true)`: 의료실 대신 월드의 스폰에서. `no_letter()`: 도구 편지 없음. 월드 전체로는 `World::set_vanilla("fall", false)`(잃는 것 없이 스폰에서). 그 사람을 쫓던 몬스터만 사라집니다.

### PlayerRespawn

쓰러졌다 일어날 때(바로, 또는 `Player::respawn`; Bukkit의 PlayerRespawnEvent). `set_location(x, z)`: 거기서 일어남(팀 스폰).

### PlayerTeleport

플러그인이 플레이어를 옮기기 직전(`teleport`, `teleport_to`). `from()` / `to()` → `(x, y, z)` (y NaN: 땅 위), `set_to(x, y, z)`. 취소: 그대로.
이 이벤트 안에서 한 다른 일은 하지 않습니다.

### PlayerInteractPlayer

다른 플레이어 가까이서 E(행동 `interact`의 `a`가 그 이름; 손 닿는 거리). `target()` → `Option<Player>`, `target_name()`, `held()` 손에 든 것. 취소 가능.
술래의 터치, 거래. 예: `plugins/tag`.

### ModelEntityDamage / ModelEntityDeath

`ModelEntity::set_health(hp, max)`로 체력을 준 이 플러그인의 엔티티를 플레이어의 휘두름이 맞힐 때: `entity()`, `amount()` / `set_amount(n)`,
`by()` 친 사람; 취소: 안 다침. 0이 되면 `ModelEntityDeath`(`drop_item`은 친 사람 자리에) 뒤 사라집니다. 그 플러그인에만 옵니다.
(`EntityDamage` / `EntityDeath`는 예전부터 `Damage` / `MobDeath`의 별칭입니다.)

### ProjectileHit

`World::projectile`로 날린 이 플러그인의 발사체가 처음 닿은 것: `hit()`(`kind` `who` `entity` `at` `normal`, `player()` 맞은 사람),
`projectile()`(이 이벤트 뒤 사라짐), `player()` 쏜 사람. 그 플러그인에만 옵니다. 예: `plugins/blaster`의 돌 대포.

## 플레이어

### PlayerLogin

서버에 들어오기 직전, 그 사람의 것이 아무것도 읽히기 전. `who()` 누구. 아직 월드가 없어 `World::get`은 아무것도 읽지 않습니다.

- 취소: 접속을 돌려보냄 (이유가 화면에).
- `player().show(&Gui)`: 들어오기 전에 입력 창. 버튼을 누르면 `Button` 이벤트가 오고, 거기서 또 창을 띄우거나 막거나,
  아무것도 안 하면 들어옵니다.
- 여기와 그 창의 `Button`에서 [`Server`](sdk#server) 값을 읽고 씁니다. 예: `plugins/server_password`.

### Join / Leave

`Join`: 월드에 들어옴 — 접속, LAN 일꾼이 들어옴, [`Player::move_world`](sdk#player)로 옴. `Leave`: 나감 — 접속 끊김, `move_world`로 떠남.
`who()` 누구. `e.player().give(..)` `add_gold` `inventory().add(..)`는 그 사람의 가방에 들어가고 게임에 바로 보입니다(`Leave`에서는 그날이 저장되는 서버에서만 남음; [Player](sdk#player)).

### PlayerMove

플레이어가 가로나 위아래로 움직일 때마다 (플레이어당 1초에 5~30번). 취소: 있던 곳으로 돌려보냄.

| | |
|---|---|
| `from()` → `(x, z)` / `from_y()` | 지난 걸음의 자리와 발 높이 |
| `to()` → `(x, y, z)` | 이번 자리 (y는 발) |
| `dt()` | 지난 걸음부터의 초 (`from` → `to`에 걸린 시간) |
| `on_ground()` | 서버가 본 발밑에 무언가 있음 (땅, 지붕, 갑판) |
| `mode()` | 게임 쪽 코드가 알린 이동 모드 (`Me::set_move_mode`; `""` 게임 그대로). 주장일 뿐이니 믿지 말고 판단의 근거로만 |
| `mount()` | 탄 엔티티의 번호 (0 없음; [`Player::mount`](sdk#player)) |

걸음마다 오니 핸들러를 가볍게 두세요. 새 이동 방식을 판정하는 법은 [이동 방식 만들기](moving#playermove로-판정하기).

### PlayerItemHeld

단축바의 다른 칸을 고르거나, 고른 칸의 것이 바뀔 때. 알리기만 합니다.

| | |
|---|---|
| `new_slot()` / `previous_slot()` | 지금 고른 칸 / 전의 칸 (−1: 아직 없음, 또는 칸을 알리지 않는 옛 게임) |
| `item_id()` / `previous_item_id()` | 지금 칸의 아이템 / 전에 손에 있던 아이템 (`""` 없음) |
| `item()` | 손에 그려지는 모델 (`""`: 없음. 씨앗·음식 …은 손에 그리지 않음) |

### Dismount

서버가 플레이어를 탈것([`Player::mount`](sdk#player))에서 내렸을 때(Bukkit의 EntityDismountEvent). 알리기만 합니다. 플러그인이
부른 `Player::dismount()`에는 오지 않습니다.

| | |
|---|---|
| `reason()` | `"door"` 건물 안으로 (방 안에는 탈것 없음), `"world"` 다른 월드로 감 (`Player::move_world`), `"quit"` 서버를 나감 |
| `mount()` → `ModelEntity` | 탔던 엔티티 (내린 자리에 남음) |
| `player()` | 내린 사람 |

예: `plugins/riding`([이동 방식 만들기 › 탈것](moving#탈것)).

### LevelUp

스킬 레벨이 오를 때. `skill()`, `level()` 새 레벨.

## 채팅, 버튼, 창

### Command

채팅의 `/이름 나머지`. `#[command]` 핸들러는 자기 이름일 때만 불립니다. `args()` 나머지. 취소: 이유가 채팅에.

### Chat

채팅 한 줄. `who()`, `line()`, `replace(line)` 대신 할 말. 취소: 말하지 않음.

### Button

plugin.json의 버튼, 또는 [`Gui`](sdk#gui) 창의 버튼을 눌렀을 때. 쿨다운은 서버가 지킵니다.

| | |
|---|---|
| `button()` | 버튼 id |
| `gui()` | 창의 id (`""`: plugin.json의 버튼) |
| `input(id)` | 누를 때 그 창의 입력 칸에 쓴 글 |
| `player().facing()` | 누를 때 바라보던 방향 |

```rust
#[command("하늘", "하늘을 불러요")]
fn call(c: Command) {
    c.player().show(&Gui::new("haneul").npc("haneul").title("하늘").text("무슨 일이에요?")
        .button("story", "이야기 들려줘").button_styled("bye", "아니야", "red"));
}

#[on(Button)]
fn pressed(e: Button) {
    if e.gui() == "haneul" && e.button() == "story" {
        e.player().show(&Gui::new("haneul").npc("haneul").text("옛날 옛적에…").button("bye", "고마워"));
    } else if e.gui() == "haneul" {
        e.player().show(&Gui::close("haneul"));
    }
}
```

### Packet

게임이 이 플러그인의 채널로 보낸 패킷(Bukkit의 plugin messaging): [HUD](screen)의 버튼·입력 칸의 `on`, 묶은 키(`Hud::key`).
다른 플러그인의 패킷은 오지 않습니다.

| | |
|---|---|
| `channel()` | 채널 (플러그인 이름 없이: `"map/zoom"`) |
| `data()` | 함께 온 것 (버튼: `""`, 입력 칸: 쓴 글; 4 KB까지) |
| `player()` | 보낸 사람 |

이 플러그인의 [게임 쪽 코드](client)가 `send(채널, 데이터)`로 보낸 것도 여기로 옵니다(게임 쪽은 1초에 8개까지). 받은 데이터는
요청일 뿐이니 판단은 여기서 하세요.

### FastPacket

이 플러그인의 [게임 쪽 코드](client)가 `send_fast(채널, 데이터)`로 보낸 빠른 패킷([빠른 통신](client#빠른-통신)). 데이터그램이라
플레이어 한 명에 1초에 60개까지, 순서가 없고, 잃은 것은 다시 오지 않습니다. 이 플러그인에만 옵니다. 알리기만 합니다.

| | |
|---|---|
| `channel()` | 채널 |
| `data()` | 함께 온 것 (1000바이트까지) |
| `player()` | 보낸 사람 |

**행동이 아니라서** 플레이어의 것을 바꾸지 못합니다(`give` `add_gold` … 없음). 플레이어 값(`Player::set`)에 담아 두었다가 `Tick`
등에서 쓰거나, 서버 쪽 `hud().send_fast`로 답하세요.

### WindowOpen

이 플러그인이 [`Hud::replace(window)`](screen#게임의-창-바꾸기)로 가져간 게임의 창을 플레이어가 열었을 때(Bukkit의
InventoryOpenEvent와 비슷하지만 인벤토리가 아닌 창(대화, 잠자기 물음, 아침 결산 …)에도 옵니다). **이미 취소된 것**입니다: 게임은
아무것도 열지 않았으니 자기 것을 보여 주거나, `Hud::open`으로 게임의 것을 열어 줍니다. 같은 것이 채널 `"window"`의 `Packet`으로도 옵니다.

| | |
|---|---|
| `window()` | `"bag"` `"shop"` `"chest"` `"dialogue"` `"sleep"` … |
| `get(key)` | 무엇이었는지, 글로 (`"tab"` `"shop"` `"selling"` `"x"` `"z"` …; 숫자는 `"12"`처럼; `""` 없음) |

```rust
#[on(WindowOpen)]
fn opened(e: WindowOpen) {
    if e.window() == "bag" {
        e.player().open_inventory(&Inventory::new("bag", "보따리", 1, 3).with_bag());
    }
}
```

예전 이름 `InventoryOpen`은 없어졌습니다(별칭도 없음).

### EntityInteract

플레이어가 이 플러그인의 엔티티(`Entity::set_interact`로 쓸 수 있게 한 것)에 가까이 가서 E를 눌렀을 때(Bukkit의
PlayerInteractEntityEvent). 서버가 거리를 확인합니다. 무엇을 할지는 모두 플러그인이: 말하기, 선물 받기, 상점 창, 퀘스트 …

| | |
|---|---|
| `entity()` | 쓴 엔티티 (`ModelEntity`; 아바타면 `as_avatar()`) |
| `held()` | 그때 손에 든 아이템 (`""`: 없음). 가져가려면 `player().take(…)` |
| `player()` | 쓴 사람 |

### InventoryClick

이 플러그인의 [인벤토리 창](screen#인벤토리-창)(`Player::open_inventory`)을 눌렀을 때. **아무것도 저절로 옮겨지지 않습니다**:
주고, 가져가고, 칸을 다시 보여 주는 것은 플러그인이 합니다.

| | |
|---|---|
| `inventory()` | 창의 id |
| `side()` | `"top"` 창의 칸, `"bag"` 옆의 가방, `"close"` 닫음 |
| `slot()` | 칸 번호 |
| `click()` | `"left"` / `"right"` |
| `bag_item()` | 누른 가방 칸의 아이템 (`""`: 없음, 또는 `"bag"`이 아님) |

### Words

주민에게 말을 걸 때(또는 마을 소식을 들을 때). 주민의 말은 서버가 대사 표에서 고릅니다.

| | |
|---|---|
| `npc()` → [`Npc`](sdk#npc) | 누구 |
| `topic()` | `"talk"` 말을 걸었음, `"town"` 마을 소식 |
| `line()` | 하려던 말 |
| `reply(line)` | 대신 할 말 |
| `player().show(&Gui)` | 대신 선택지 창 |

## 시간과 하루

### Tick

누가 있는 월드에서 **플러그인마다 기본 1초에 한 번**. 월드 자체는 server.properties의 `tick-rate`(기본 20, 1~20)번 1초에
스텝을 돌지만(마인크래프트의 월드 틱), 대부분의 플러그인 일은 그렇게 자주 할 필요가 없어 서버의 플러그인 CPU 몫([CPU 예산](server#cpu-예산))을
아끼려고 1초에 한 번만 부릅니다. 더 자주 필요하면(움직임처럼 매끄러워야 하는 것) `Enable`에서 `Registry::tick_rate(n)`으로
1초에 n번을 요청합니다(월드의 `tick-rate`보다 자주는 못 함). 함수 하나만 따로 정하려면 `#[on(Tick)]` 대신 `#[every(초)]`
(Bukkit의 `runTaskTimer`: 그 초마다 한 번, 첫 틱에는 바로).
`players()`가 월드의 모두를 차례로 줍니다: 그 `Player`에 하는 일은 그 사람에게 갑니다(단, `give` `take` `add_gold` `add_energy`
`say`는 tick에서 아무것도 하지 않음).

`dt()`는 **그 함수가 지난번에 불린 뒤 지난 초**입니다(처음에는 그 주기). **시간에 따라 바뀌는 것은 `dt()`만큼씩** 바꾸세요:
불리는 횟수를 세면 서버와 플러그인의 빈도마다 빠르기가 달라집니다(샘플은 모두 `dt()`나 `now()`로 잽니다).

```rust
#[on(Enable)]
fn enable(_e: Enable) {
    Registry::tick_rate(20);          // 이 플러그인의 Tick을 1초에 20번 (기본 1번)
}

#[on(Tick)]
fn fly(t: Tick) { /* 매끄러워야 하는 것: 1초에 20번 */ }

#[every(1.0)]
fn regen(t: Tick) {
    for p in t.players() {
        p.set("mana", (p.get("mana") + 5.0 * t.dt()).min(100.0)); // 1초에 5씩, 몇 번 불리든
    }
}
```

### Timer

이 플러그인의 타이머가 될 때, 그 플러그인에만(Bukkit의 `runTaskLater` / `runTaskTimer`): `Scheduler::run_later(태그, 초)`(한 번),
`run_every(태그, 초)`(그 초마다, 첫 번째도 그 초 뒤), `cancel(태그)`. `tag()`로 어느 것인지. 플레이어가 없으니 필요하면 이름을
태그에 넣고 `Server::player`로. 월드에 저장되고(서버가 다시 켜져도), 플러그인마다 64개, 가장 짧은 주기 50 ms; 늦은 스텝에선
놓친 만큼이 아니라 한 번만.

```rust
#[command("보스", "")]
fn boss(c: Command) { /* ... */ Scheduler::run_every("boss_regen", 2.0); }

#[on(Timer)]
fn timer(e: Timer) {
    if e.tag() == "boss_regen" { /* 보스의 체력 +5 */ }
}
```

### EffectStart / EffectEnd

`Player::add_effect`가 놓은 상태 효과가 월드의 다음 스텝에 시작될 때(`effect()` `strength()` `secs()`; 막으면 붙지 않음),
끝날 때(`effect()`, `reason()` "expired" / "removed"). `player()`가 그 사람. [SDK › 상태 효과](sdk#상태-효과-타이머-쿨다운).

### ServerTick

서버의 틱: 아무도 없어도 1초에 두 번, 어느 월드에도 속하지 않습니다. 여기서 [`Server::set`](sdk#server)으로 서버 값을
바꾸고(월드의 이벤트들은 읽기만), `Server::create_world`(플러그인의 월드)를 부를 수 있습니다. `num("players")` 지금 접속 수, `now()` 벽시계.

### DayEnd

하루가 끝나려 할 때. `reason()`, 이유마다 하루에 한 번 (`"end_day"`는 부를 때마다). `num("minute")`.

| `reason()` | 언제 | 취소하면 |
|---|---|---|
| `"clock"` | 하루의 끝 시각 (규칙의 `day_end`) | 시계가 계속 감, 날짜 그대로 |
| `"sleep"` | 모두 잠듦 | 자던 사람들이 일어남, 하루가 이어짐 |
| `"end_day"` | 플러그인의 `World::end_day()` | 아무 일도 없음 |
| `"limit"` | 넘을 수 없는 끝 (다음날 6:00, 더 늦은 day_end면 그것) | 아침이 오지 않음(작물·출하·생성 없음, 저장도 없음), 날짜 그대로, 시계는 하루의 시작으로 |

기본 규칙에서는 하루가 새벽 2:00(`day_end` 1560)에 `"clock"`으로 끝나고, 그때 자지 않던 사람은 기절합니다(규칙
`pass_out`: 다음 아침 집 침대 옆, 기력 절반; 광산·던전에 있던 사람은 늘 집에서). `day_end`를 1800(다음날 6:00)으로 늦추면
시계로 끝나는 날은 `"limit"`입니다. 기절하지 않게 하려면 `pass_out`을 false로, 자지 않은 아침에 정산 화면을 띄우지 않으려면
`summary_awake`를 false로 (예제 [`stay_up`](samples)). 게임의 "summary" 창을 가져간 플러그인은 `WindowOpen`의 `get("slept")`로
그 아침이 잠든 아침인지 압니다.

### DayChange

아침에 날짜가 넘어가려 할 때. `day()` 지금, `next()` 바뀔 날짜. 취소하면 아침의 일(작물, 동물, 출하, 시계)은 그대로 하고
날짜만 그대로입니다. 정해진 난수는 날짜로 굴리므로 같은 날짜가 되풀이되면 그날의 날씨·생성·편지도 같게 나옵니다.

## 월드 만들기

### WorldCreate

월드가 만들어진 직후, 아무도 들어오기 전. 바닐라 마을·성벽·주민이 놓인 상태에서 여기서 바꾼 것이 처음부터 그 월드입니다.
이미 있는 월드에는 불리지 않습니다. [월드와 하루](world) 참고.

### ChunkGenerate

청크가 처음 만들어질 때(바닐라 땅이 이미 들어 있음). 그 청크의 블록만 `World::fill` / `set_block`으로 바꿀 수 있습니다(이웃
청크는 무시).

| | |
|---|---|
| `chunk()` → `(x, z)` | 청크 번호 |
| `first_cell()` → `(x0, z0)` | 첫 칸: 칸은 `x0..x0+size`, `z0..z0+size` |
| `size()` | 한 변의 칸 수 (32) |
| `clear_props()` | 그 위의 덤불·풀·유목 치우기 |

### BlockPlace / BlockBreak

플레이어가 손에 든 블록(아이템 `"type": "block"`)을 사용 버튼으로 앞 칸에 놓을 때 / 플러그인이 [등록한 블록](world#새-블록-종류)을
곡괭이로 부술 때(아이템이 있는 종류면 가방에). 바닐라 땅의 블록은 부서지지 않습니다. 취소하면 일어나지 않습니다.

| | |
|---|---|
| `block()` | 블록 종류의 id (`"ruby_block"`) |
| `at()` → `(x, y, z)` | 그 칸 |
| `player()` | 놓거나 부순 사람 |

```rust
#[on(BlockPlace)]
fn placed(e: BlockPlace) {
    if e.at().1 > 12 { e.cancel("그렇게 높이는 쌓을 수 없어요") }
}
```

### ChunkLoad

청크가 서버의 메모리에 들어올 때, 게임이 그 청크를 달라고 해서(Bukkit의 ChunkLoadEvent). 방금 만든 청크도, 오래전에 만든
청크도 옵니다. 여기서 바꾼 것(그 청크 안만: `World::set_blocks`)이 그대로 게임에 갑니다. **이미 만들어진 청크에 새 블록을 한 번씩
넣는** 방법: 청크 표시(`World::chunk_mark` / `set_chunk_mark`, 월드와 함께 저장)를 보고, 아직이면 바꾸고 표시합니다.

| | |
|---|---|
| `chunk()` → `(x, z)` | 청크 번호 (칸은 `x * CHUNK ..`; `CHUNK` = 32) |
| `first_cell()` → `(x0, z0)` | 첫 칸 |
| `is_new()` | 방금 만들어짐 (전에 보낸 적 없음) |

```rust
#[on(ChunkLoad)]
fn loaded(e: ChunkLoad) {
    let (cx, cz) = e.chunk();
    let w = e.world();
    if w.chunk_mark(cx, cz, "pillar") >= 1 { return }   // 이미 넣음
    let (x0, z0) = e.first_cell();
    let (x, z) = (x0 + CHUNK / 2, z0 + CHUNK / 2);
    let y = w.top(x, z);
    if let Some(ruby) = Block::named("ruby_block") {
        w.set_blocks(&[(x, y + 1, z, ruby), (x, y + 2, z, ruby)]);
    }
    w.set_chunk_mark(cx, cz, "pillar", 1);
}
```

예: `plugins/blocks`.

### MineFloor

광산 층이 그날 처음 만들어질 때(누가 처음 내려갈 때, 아무도 보기 전). **바위만** 바꿀 수 있습니다: 벽과 사다리는
배치(규칙의 [`mine_layout`](rules#광산-mine_layout))의 것입니다.

| | |
|---|---|
| `floor()` | 층 |
| `size()` → `(w, d)` | 층의 폭·깊이 (칸) |
| `cell()` | 층의 (0, 0) 칸의 마을 좌표 |
| `rocks()` → `Vec<(i, j, id)>` | 층의 바위 (층 자신의 칸) |
| `set_rock(i, j, id)` | 그 칸에 바위 놓기 (`gold_node` 등 debris id), `""` 치우기. 벽 위와 사다리 둘레는 안 됨 |
| `num("up_x")` `"up_z"` `"down_x"` `"down_z"` | 올라가는·내려가는 사다리 |

예: `plugins/deep_mines`.

## SDK 없이 (원본 ABI)

모듈은 `memory`와 `on_event() -> i32`를 내보냅니다(0이면 그대로, 아니면 막음). plugin.json의 `events`로 구독하고, 이벤트
이름은 `event` 함수로 읽습니다. SDK는 핸들러마다 내보내기 하나와 "gh" 커스텀 섹션의 줄(`on\t이벤트\t우선순위\t내보내기`,
`command\t이름\t설명`)을 만들고, 서버는 그 이벤트에 그것들을 우선순위 차례로 부릅니다. ["gh" 함수](abi) 참고.
