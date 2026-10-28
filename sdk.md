---
title: SDK 레퍼런스
nav_order: 4
---

# SDK 레퍼런스 (`greenhaven-plugin`)
{: .no_toc }

`use greenhaven_plugin::*;` 하나로 아래가 모두 들어옵니다. 좌표는 모두 **칸**(1 m)이고, y는 블록의 가운데입니다
(마을 땅은 y 0의 블록, 윗면 0.5).

1. TOC
{:toc}

## 함수

| | |
|---|---|
| `now()` → `f64` | 벽시계: 1970년부터의 ms (UTC), 서버의 모든 월드에 같음 |
| `setting(key)` → `Option<String>` | 이 플러그인의 [설정](plugin-json#설정-settings) 값, 글자로 (`"12.5"`, `"true"`); 없는 설정은 `None` |
| `setting_num(key, or)` → `f64` | 숫자 설정, 없으면 `or` |
| `setting_bool(key, or)` → `bool` | 켜기/끄기 설정, 없으면 `or` |

## Player

이벤트의 플레이어 (`e.player()`). `Tick::players()`가 주는 것은 그 사람.

| 메서드 | |
|---|---|
| `name()` → `String` | 이름 (`""`: 월드 주인) |
| `position()` → `(f64, f64)` | 위치 (칸) |
| `facing()` → `(f64, f64)` | 바라보는 방향 (행동의) |
| `give(item, n)` / `take(item, n)` | 아이템 주기 / 가져가기 |
| `add_gold(d)` | 골드 (음수면 뺌) |
| `add_energy(d)` | 기력 |
| `heal(n)` | 체력 |
| `add_xp(skill, n)` | 스킬 경험치 |
| `add_friendship(villager, points)` | 주민 호감도 |
| `teleport(x, z)` | 옮기기 (서버의 이동 판정도 그 자리를 받아들임) |
| `set_time(minute)` | 그 사람이 있는 월드의 시각 (6:00 = 360 ~ 2:00 = 1560; 날짜는 그대로), 그 월드의 게임에 바로 알림 |
| `set_walk_speed(times)` | 걸음 빠르기 배수 (1이 원래). 게임의 걸음과 서버의 이동 판정이 함께 바뀜. 바꿀 때까지 유지 |
| `say(line)` | 머리 위의 한마디 |
| `message(line)` | 채팅 한 줄 |
| `title(line)` | 화면 가운데 큰 제목 |
| `where_text(line)` | 화면의 장소 문구 (`""`: 게임의 것) |
| `open_shop(shop)` | 가게 열기 (`VillagerData.SHOPS`의 id) |
| `play_music(track)` | 지금 곡 틀기 (`Music.TRACKS`의 id나 `res://….ogg`; `""`: 원래 목록으로) |
| `visit(owner)` | 열기구로 그 사람 월드에 바로 내림 (`PlayerVisit`이 불림) |
| `home()` | 자기 월드로 |
| `show(&Gui)` | 창 띄우기 ([`Gui`](#gui)). `PlayerLogin`에서는 들어오기 전의 입력 창 |
| `get(k)` / `set(k, v)` | 그 사람에게 남기는 숫자 (이 플러그인의 것; 저장됨). plugin.json의 바가 보여 주는 값 |
| `data_put(key, &[u8])` → `bool` | 그 사람의 바이트 ([데이터 저장](#데이터-저장)) |
| `data_get(key)` → `Option<Vec<u8>>` | |
| `data_del(key)` | |

{: .note }
`Tick`에서 `Tick::players()`가 준 `Player`라도 `give` `take` `add_gold` `add_energy` `say`는 월드 주인에게 갑니다.

## World

이벤트의 월드 (`e.world()`).

### 알림과 효과

| 메서드 | |
|---|---|
| `broadcast(line)` | 월드 모두의 채팅 |
| `play_music(track)` | 월드의 모두에게 곡 (`""`: 원래 목록으로) |
| `particle(name, x, y, z)` | 파티클: `"fire"` `"smoke"` `"sparkle"` `"splash"` `"leaf"` `"hit"` 또는 `res://….png` |
| `sound(name, x, y, z)` | 소리: `"hit"` `"pickup"` `"click"` `"step_soft"` `"step_hard"` 또는 `res://….ogg` |
| `set_weather(name, days_ahead)` | 그날(0 오늘)의 날씨: `"sunny"` `"rain"` `"storm"` `"snow"` … |

### 몬스터와 엔티티

| 메서드 | |
|---|---|
| `strike(x, z, radius, damage)` | 그 둘레의 몬스터 공격 |
| `spawn_mob(kind, x, z)` | 이벤트의 층에 몬스터 하나 (지상은 밤에만 남음) |
| `spawn(model, x, y, z)` → `Option<Entity>` | 이 플러그인의 엔티티: `res://` 모델(glb, 씬) 또는 png(늘 카메라를 보는 그림) |
| `entities()` → `Vec<Entity>` | 이 플러그인의 엔티티들 |
| `npcs()` → `Vec<Npc>` | 주민들 |

### 값과 데이터

| 메서드 | |
|---|---|
| `get(k)` / `set(k, v)` | 월드에 남기는 숫자 (이 플러그인의 것; 저장됨) |
| `data_put(key, &[u8])` → `bool` | [데이터 저장](#데이터-저장) |
| `data_get(key)` → `Option<Vec<u8>>` | |
| `data_del(key)` | |
| `data_keys(prefix)` → `Vec<String>` | 이 플러그인의 키 중 `prefix`로 시작하는 것 |
| `save_now()` | 월드를 아침처럼 지금 저장 (게임, 블록, 데이터; 날은 그대로 이어짐) |
| `set_live_saving(on)` | 1분마다·플레이어가 나갈 때 저장 (잠이 없는 서버). server.properties `save-mode`보다 우선 |
| `set_quit_warning(text)` | 자기 전에 나갈 때 게임이 띄우는 경고 (`""` 없음, 200자까지). server.properties `quit-warning`보다 우선 |

### 하루

| 메서드 | |
|---|---|
| `set_day(day)` | 날짜 (1이 첫날; 계절은 날짜에서). 월드의 게임에 바로 알림 |
| `set_day_start(minute)` | 이 월드의 아침 시각 (6:00 = 360) |
| `set_day_end(minute)` | 이 월드의 하루의 끝 (그때 `DayEnd` `"clock"`; 다음날 6:00 = 1800) |
| `end_day()` | 지금 하루를 끝냄, 모두 잔 것처럼 (먼저 `DayEnd` `"end_day"`) |

### 블록

| 메서드 | |
|---|---|
| `block(x, y, z)` → [`Block`](#block) | 그 블록 (아직 안 만든 청크는 바닐라 땅으로) |
| `top(x, z)` → `i64` | 기둥에서 가장 높은 단단한 블록의 y (없으면 `Block::LOWEST - 1`) |
| `set_block(x, y, z, b)` | 블록 놓기 (저장됨) |
| `fill(from, to, b)` | 상자 모양 채우기, 양 끝 포함, 한 번에 청크 넷까지 |

### 구조물과 주민

| 메서드 | |
|---|---|
| `structures()` → `Vec<Structure>` | 월드에 선 것들 (건물, 울타리, 성벽, 성문, 정거장 …) |
| `put_structure(json)` → `Option<Structure>` | 세우기: `{"k": "building", "m": "house_Lv1", "x", "z", "yaw", "plot"}`, 칸 사각형 종류는 `{"k": "block", "cells": [x, z, w, d]}` |
| `remove_plot(plot)` | 구획 통째로 치우기 (`"wall"`: 성벽·성문·바위 둑·암초, `"station"`, `"core"` 마을 한가운데 …) |
| `spawn_npc(json)` → `bool` | 주민 더하기 (`{"id", "name", "look", "home", "shop", "schedule": [[480, "square"]] …}`) |

[월드와 하루](world)에 자세히.

## Server

월드와 상관없는 서버의 값. `Server` (단위 구조체)로 씁니다.

| 메서드 | |
|---|---|
| `get(k)` → `f64` | 어느 이벤트에서나 읽음 |
| `set(k, v)` | `PlayerLogin`과 그 입력 창의 `Button`, `ServerTick`에서만 |
| `set_shared_world(on)` | 모두의 월드 ([월드와 하루](world#모두의-월드)). `ServerTick`이나 `PlayerLogin`에서만 |

```rust
#[on(ServerTick)]
fn count(_e: ServerTick) {
    Server.set("clock", Server.get("clock") + 1.0);
}
```

## OfflinePlayer

지금 접속해 있지 않은 사람까지, 이 서버에 한 번이라도 들어온 누구든 읽습니다. 읽기 전용입니다.

| | |
|---|---|
| `Server.offline_player(name)` → `OfflinePlayer` | 이름으로 |
| `Server.offline_players()` → `Vec<OfflinePlayer>` | 들어온 적 있는 모두, 처음 들어온 순서 |

| 메서드 | |
|---|---|
| `name()` | 이름 |
| `has_played()` → `bool` | 저장된 게임이 있는지 |
| `gold()` `day()` | 골드, 그 사람 월드의 날짜 |
| `last_seen()` → `f64` | 마지막으로 나간 때 (1970년부터의 ms) |
| `level(skill)` `friendship(villager)` `item_count(item)` | 스킬 레벨, 주민 호감도, 가방의 개수 |
| `num(k)` | `"gold"` `"day"` `"energy"` `"seen"` `"level.<스킬>"` `"xp.<스킬>"` `"friendship.<주민>"` `"item.<id>"` |
| `get(k)` | 이 플러그인이 그 사람에게 남긴 숫자, 그 사람 월드에서 (`Player::get`) |
| `world_get(k)` | 이 플러그인이 그 사람 월드에 남긴 숫자 (`World::get`) |
| `data_get(key)` / `world_data_get(key)` | 이 플러그인이 그 사람에게 / 그 사람 월드에 맡긴 바이트 |

```rust
#[command("부자", "골드가 가장 많은 농장 주인")]
fn richest(c: Command) {
    let best = Server.offline_players().into_iter().max_by_key(|p| p.gold());
    if let Some(p) = best {
        c.player().message(&format!("{}: {}골드", p.name(), p.gold()));
    }
}
```

- **마지막으로 저장된 상태**를 읽습니다 (그 사람 월드의 아침, `save_now`, 실시간 저장). 지금 접속해 있는 사람도 그렇게 읽히니,
  그날 한 일까지 보려면 그 사람 월드의 이벤트에서 `Player`를 쓰세요.
- 다른 플러그인의 값과 데이터는 보이지 않습니다.
- 이벤트 한 번에 디스크에서 읽는 사람은 32명까지입니다(넘으면 없는 사람처럼 읽힘). 한 번 읽은 사람은 파일이 바뀔 때까지
  다시 읽지 않으니, 같은 사람을 여러 번 읽는 것은 괜찮습니다.

## Npc

주민 (`Npc(id)`; `Words::npc()`, `World::npcs()`).

| 메서드 | |
|---|---|
| `get(k)` | `"x"` `"z"` `"moving"` `"hidden"` `"indoors"` |
| `position()` → `(f64, f64)` | |
| `go_to(x, z, hold_secs)` | 그곳(설 수 있는 가장 가까운 칸)으로 보내 몇 초 머물게 함. 일정보다 먼저 |
| `say(line)` | 머리 위의 한마디, 월드의 모두에게 |
| `set(json)` | 덮어쓰기 (`{"home": "...", "schedule": [...]}`) |
| `remove()` | 월드에서 빼기 |

## Entity

이 플러그인의 엔티티 (`World::spawn`). **저장되지 않습니다**: 서버를 다시 켜면 사라지니, 남길 것은 `World::set`에.

| 메서드 | |
|---|---|
| `get(k)` / `set(k, v)` | `"x"` `"y"` `"z"` `"yaw"` `"scale"` (`get`은 `"alive"`도) |
| `position()` → `(x, y, z)` | |
| `move_to(x, y, z)` | |
| `play(clip)` | 모델의 애니메이션 |
| `remove()` | |

```rust
#[on(Button)]
fn fireball(e: Button) {
    let (x, z) = e.player().position();
    let (fx, fz) = e.player().facing();
    if let Some(ball) = e.world().spawn("res://plugins/example/fireball.glb", x, 1.0, z) {
        e.world().set(&format!("ball.{}.vx", ball.0), fx * 8.0);
        e.world().set(&format!("ball.{}.vz", ball.0), fz * 8.0);
    }
}
```

## Mob

몬스터 하나 (`Mob(serial)`; `MobStep::mob()`).

| 메서드 | |
|---|---|
| `get(k)` | `mob` 이벤트에서: `"x"` `"z"` `"hp"` `"tier"` `"speed"` `"damage"` `"size"` `"t"` |
| `set(k, v)` | `"x"` `"z"`(옮기기) `"hp"`(0이면 사라짐) `"speed"` `"damage"`, `"vx"` `"vz"`(이번 걸음의 속도: 원래 움직임 대신) |
| `attack(damage, reach)` | 그 거리 안의 가장 가까운 플레이어를 침 (닿을 때의 공격은 따로 그대로) |
| `remove()` | 없애기 (떨굼 없음) |

어느 이벤트에서나 쓸 수 있습니다(`tick`·`button`에서 소환한 것을 움직이는 등).

## Structure

월드에 선 것 하나 (`Structure(id)`).

| 메서드 | |
|---|---|
| `get(k)` → `f64` | `"x"` `"z"` `"y"` `"yaw"` `"w"` `"d"` `"scale"` |
| `text(k)` → `String` | `"k"`(무엇) `"m"`(모델) `"plot"` `"n"` `"key"` `"kind"` `"label"` `"text"` `"s"` `"owner"` |
| `kind()` / `plot()` | `text("k")` / `text("plot")` |
| `remove()` | |
| `move_to(x, z, yaw)` | |

## Block

블록 종류 (`Block(번호)`).

| 상수 | 번호 | |
|---|---|---|
| `Block::AIR` | 0 | |
| `Block::GRASS` | 1 | |
| `Block::SAND` | 2 | |
| `Block::SNOW` | 3 | |
| `Block::STONE` | 4 | |
| `Block::DIRT` | 5 | |
| `Block::ROAD` | 6 | |
| `Block::BED` | 7 | 물 밑 모래 |
| `Block::WATER` | 8 | |
| `Block::LOWEST` | -8 | 가장 낮은 블록의 y (그 아래는 모두 단단함). 청크는 이로부터 64칸 높이 |

`Block::named("stone")` → `Option<Block>`: 이름(또는 번호)으로.

## Gui

플레이어에게 보이는 창 (`Player::show`). 빌더로 만듭니다.

| 메서드 | |
|---|---|
| `Gui::new(id)` | 창의 id (버튼을 누르면 `Button::gui()`) |
| `Gui::close(id)` | 열린 그 창 닫기 (`show`로 보냄) |
| `.title(s)` | 제목 |
| `.text(s)` | 본문 |
| `.npc(id)` | 주민의 얼굴과 이름 |
| `.image(path)` | `res://` 그림 |
| `.button(id, label)` | 버튼 (나무) |
| `.button_styled(id, label, style)` | `"go"`(초록) `"red"` `""`(나무) |
| `.input(id, label, placeholder, max)` | 한 줄 입력 칸 (`max` 글자, 1~256). 누르면 `Button::input(id)` |
| `.secret(id, label, placeholder, max)` | 가려 쓰는 칸 (비밀번호) |
| `.json()` | 보낼 JSON (원본 ABI의 `gui`) |

```rust
#[on(PlayerLogin)]
fn ask(e: PlayerLogin) {
    e.player().show(&Gui::new("pw").title("비밀번호").text("이 서버의 비밀번호를 넣어 주세요")
        .secret("pw", "비밀번호", "", 64).button_styled("ok", "들어가기", "go"));
}
```

## 데이터 저장

플러그인이 파일 대신 서버에 맡기는 바이트입니다 (`World::data_*`, 플레이어마다 `Player::data_*`: 그 월드 안, 그 사람 것).

- 키·플러그인마다의 한도는 없고, 월드 하나의 모든 플러그인 데이터가 합쳐 **100 MB**까지 (넘는 `put`은 `false`).
- 다른 플러그인의 키는 보이지 않습니다.
- 저장 시점은 게임과 같습니다 (아침, `save_now`, 실시간 저장). 그 전에도 읽으면 방금 넣은 것이 보입니다.
- 위치: `<data>/plugin_data/<월드>/<플러그인>/`.

```rust
let w = e.world();
w.data_put("log/1", "첫 수확".as_bytes());
for k in w.data_keys("log/") {
    let line = String::from_utf8(w.data_get(&k).unwrap_or_default()).unwrap_or_default();
}
```

## `sys` — 원본 함수

SDK가 감싸지 않은 것은 `greenhaven_plugin::sys`에 "gh" 함수 그대로 있습니다 ([목록](abi)).
