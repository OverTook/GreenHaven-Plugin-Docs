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
| [`Damage`](#damage) | `damage` | ✔ | 몬스터가 플레이어를 침 |
| [`Strike`](#strike) | `strike` | ✔ | 플레이어가 몬스터를 침 |
| [`Spawn`](#spawn) | `spawn` | ✔ | 몬스터가 나옴 (밤, 광산 층) |
| [`Tick`](#tick) | `tick` | | 누가 있는 월드에서 1초에 두 번 |
| [`ServerTick`](#servertick) | `server.tick` | | 서버의 틱, 아무도 없어도 1초에 두 번 |
| [`DayEnd`](#dayend) | `day.end` | ✔ | 하루가 끝나려 함 |
| [`DayChange`](#daychange) | `day.change` | ✔ | 아침에 날짜가 넘어가려 함 |
| [`Button`](#button) | `button` | ✔ | 플러그인 버튼이나 창의 버튼을 누름 |
| [`Command`](#command) | `command` | ✔ | 채팅 명령어 |
| [`Morning`](#morning) | `morning` | | 밤이 지나고 아침 (농장 주인에게) |
| [`Join`](#join--leave) | `join` | | 월드에 들어옴 |
| [`Leave`](#join--leave) | `leave` | | 월드에서 나감 |
| [`PlayerLogin`](#playerlogin) | `login` | ✔ | 서버에 들어오기 직전 |
| [`PlayerItemHeld`](#playeritemheld) | `held` | | 손에 든 도구가 바뀜 |
| [`PlayerVisit`](#playervisit) | `visit` | ✔ | 열기구 여행 |
| [`Chat`](#chat) | `chat` | ✔ | 채팅 한 줄 |
| [`Words`](#words) | `words` | ✔ | 주민에게 말을 걸음 |
| [`MobStep`](#mobstep) | `mob` | | `script` 몬스터의 한 걸음 |
| [`MineFloor`](#minefloor) | `mine.floor` | | 광산 층이 그날 처음 만들어짐 |
| [`PlayerMove`](#playermove) | `move` | ✔ | 플레이어가 걸음 |
| [`WorldCreate`](#worldcreate) | `world.create` | | 월드가 만들어짐 |
| [`ChunkGenerate`](#chunkgenerate) | `chunk.generate` | | 청크가 처음 만들어짐 |
| [`PlayerDeath`](#playerdeath) | `death` | | 플레이어가 쓰러짐 |
| [`MobDeath`](#mobdeath) | `mob.death` | | 플레이어가 몬스터를 쓰러뜨림 |
| [`LevelUp`](#levelup) | `level` | | 스킬 레벨이 오름 |
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
| `BlockBreak` | `hit` | 나무·바위·잡초·광맥을 도구로 침 |
| `BlockPlace` | `place` `furnish` | 땅에 설치물, 집에 가구 놓기 |
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

게임에 쓰임새가 없는 아이템(플러그인이 `rules.json`으로 더한 것 등)을 썼을 때. `id()` 아이템. 가져가려면 `player().take(id, 1)`.

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

### Damage

몬스터가 플레이어를 칠 때. `amount()` / `set_amount(n)` (0이면 안 다침). 취소: 안 다침.

### Strike

플레이어가 몬스터를 칠 때. `damage()` / `set_damage(n)`. 취소: 휘두름이 없던 일.

### Spawn

몬스터가 나올 때: 밤, 그리고 광산 층. `kind_id()` 종류, `floor()` 0은 지상(밤), 아니면 광산 층. 취소: 나오지 않음.

### MobStep

`rules.json`의 `monsters_add`에서 `"script": true`인 종류의 몬스터마다, 서버의 한 걸음(1초에 10번)에 옵니다. 한 걸음의
몬스터 모두를 모듈 하나가 차례로 받습니다.

| | |
|---|---|
| `mob()` → [`Mob`](sdk#mob) | 그 몬스터 (`get("x")` `"z"` `"hp"` `"tier"` `"speed"` `"damage"` `"size"` `"t"`(나온 뒤 초)) |
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

플레이어가 쓰러질 때(체력이 다했거나 `Player::death`). `keep_inventory(true)`: 가방과 장비를 지킴. `hold(true)`: 바로 일어나지 않고 `Player::respawn`까지 쓰러진 채 대기.

## 플레이어

### PlayerLogin

서버에 들어오기 직전, 그 사람의 것이 아무것도 읽히기 전. `who()` 누구. 아직 월드가 없어 `World::get`은 아무것도 읽지 않습니다.

- 취소: 접속을 돌려보냄 (이유가 화면에).
- `player().show(&Gui)`: 들어오기 전에 입력 창. 버튼을 누르면 `Button` 이벤트가 오고, 거기서 또 창을 띄우거나 막거나,
  아무것도 안 하면 들어옵니다.
- 여기와 그 창의 `Button`에서 [`Server`](sdk#server) 값을 읽고 씁니다. 예: `plugins/server_password`.

### Join / Leave

`Join`: 월드에 들어옴 — 접속, 열기구 착륙, 집에 돌아옴, LAN 일꾼이 들어옴. `Leave`: 나감 — 접속 끊김, 열기구로 떠남.
`who()` 누구.

### PlayerMove

플레이어가 걸을 때 (1초에 5번까지). `from()` → `(x, z)`, `to()` → `(x, y, z)` (y는 발). 취소: 있던 곳으로 돌려보냄.

### PlayerItemHeld

손에 든 도구가 바뀔 때. `item()` 그 모델 (`""` 빈손).

### PlayerVisit

열기구 여행, `owner()`의 월드에서 불림. `who()` 누가, `kind()`:

| `kind()` | | 취소 |
|---|---|---|
| `"fly"` | 그 월드로 떠남 | 못 감 |
| `"land"` | 내려옴 | 못 내림 (떠 있음) |
| `"home"` | 집으로 돌아감 | 알리기만 |

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

누가 있는 월드에서 1초에 두 번. `players()`가 월드의 모두를 차례로 줍니다: 그 `Player`에 하는 일은 그 사람에게
갑니다(단, `give` `take` `add_gold` `add_energy` `say`는 tick에서 월드 주인에게).

### ServerTick

서버의 틱: 아무도 없어도 1초에 두 번, 어느 월드에도 속하지 않습니다. 여기서 [`Server::set`](sdk#server)으로 서버 값을
바꾸고(월드의 이벤트들은 읽기만), `Server::set_shared_world`를 부를 수 있습니다. `num("players")` 지금 접속 수, `now()` 벽시계.

### DayEnd

하루가 끝나려 할 때. `reason()`, 이유마다 하루에 한 번 (`"end_day"`는 부를 때마다). `num("minute")`.

| `reason()` | 언제 | 취소하면 |
|---|---|---|
| `"clock"` | 하루의 끝 시각 (rules.json `day_end`) | 시계가 계속 감, 날짜 그대로 |
| `"sleep"` | 모두 잠듦 | 자던 사람들이 일어남, 하루가 이어짐 |
| `"end_day"` | 플러그인의 `World::end_day()` | 아무 일도 없음 |
| `"limit"` | 넘을 수 없는 끝 (다음날 6:00, 더 늦은 day_end면 그것) | 아침이 오지 않음(작물·출하·생성 없음, 저장도 없음), 날짜 그대로, 시계는 하루의 시작으로 |

기본 규칙에서는 하루의 끝이 곧 다음날 6:00(=limit)이라 시계로 끝나는 날은 `"limit"`입니다. `"clock"`은
rules.json의 `day_end`를 앞당긴 서버에서 옵니다.

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

### MineFloor

광산 층이 그날 처음 만들어질 때(누가 처음 내려갈 때, 아무도 보기 전). **바위만** 바꿀 수 있습니다: 벽과 사다리는
배치(`rules.json`의 [`mine_layout`](rules#광산-mine_layout))의 것입니다.

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
