---
title: SDK 레퍼런스
nav_order: 4
parent: 플러그인
redirect_from:
  - /sdk
  - /sdk.html
---

# SDK 레퍼런스 (`greenhaven-plugin`)
{: .no_toc }

`use greenhaven_plugin::*;` 하나로 아래가 모두 들어옵니다. 좌표는 모두 **칸**(1 m)이고, y는 블록의 가운데입니다
(마을 땅은 y 0의 블록, 윗면 0.5).

이것은 서버 쪽(`server.wasm`)의 SDK입니다. 게임 안에서 도는 쪽(`client.wasm`)은 `greenhaven-client`: [게임 쪽 코드](client).

1. TOC
{:toc}

## 함수

| | |
|---|---|
| `now()` → `f64` | 벽시계: 1970년부터의 ms (UTC), 서버의 모든 월드에 같음 |
| `setting(key)` → `Option<String>` | 이 플러그인의 [설정](plugin-json#설정-settings) 값, 글자로 (`"12.5"`, `"true"`); 없는 설정은 `None` |
| `setting_num(key, or)` → `f64` | 숫자 설정, 없으면 `or` |
| `setting_bool(key, or)` → `bool` | 켜기/끄기 설정, 없으면 `or` |
| `find(plugin, name)` → `Option<Func>` | 다른 플러그인(또는 서비스)의 `#[export]` 함수; `Func::call(args)` → `Result<R, CallError>` ([플러그인끼리](interop)) |
| `caller()` → `String` | (`#[export]` 함수 안에서) 부른 플러그인의 이름, 이벤트로 불렸으면 `""` |

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
| `inventory()` → [`PlayerInventory`](#playerinventory) | 그 사람의 가방 (Bukkit의 getInventory) |
| `gear(id)` → `Option<`[`Gear`](#gear)`>` | 그 사람의 도구·장비 하나의 등급과 마법 (가방에 없으면 `None`) |
| `mount(&entity, speed, seat)` | 이 플러그인의 엔티티에 태움: 모든 게임이 그 엔티티를 탄 사람 아래에 그리고 `seat` m 위에 앉힘, 걸음은 `speed`배로 판정. 그 사람이 한 일의 이벤트에서만 (`EntityInteract`, 명령어, 버튼, `Packet`); 저장되지 않음 ([탈것](moving#탈것)) |
| `dismount()` | 내림: 엔티티는 그 자리에, 걸음은 전과 같이 |
| `set_check(check, on)` | 서버의 이동 검사 하나를 이 사람에게만 끄고 켬: `"speed"` `"walls"` `"air"` `"teleport"` `"reach"`. 끄면 플러그인이 `PlayerMove`에서 대신 검사해야 함. 저장되지 않음 (`Join`에서 다시). 모두에게는 `Registry::set("checks.air", "false")` ([이동 방식 만들기](moving#서버의-이동-검사)) |
| `death(hold)` | 쓰러뜨림 (`PlayerDeath`도 불림). `false`: 게임 규칙대로 진료소에서 바로 일어남. `true`: `respawn`까지 쓰러진 채 대기, 아침이 지나도 그대로. 다른 사람의 잠은 이 사람을 기다리지 않지만, 쓰러진 사람만으로 하루가 끝나지는 않음 |
| `respawn()` | 쓰러진 채 대기 중인 사람을 진료소에서 일으킴 (체력 가득) |
| `set_model(id)` `clear_model()` | [커스텀 모델](models)로 그림 / 원래 모습으로. 연결된 동안만, 계정은 그대로 |
| `play_anim(id)` `stop_anim()` | [감정 표현](models) 재생 / 끝내기. 가만히 서 있을 때만, 움직이거나 행동하면 끝남 |
| `say(line)` | 머리 위의 한마디 |
| `message(line)` | 채팅 한 줄 |
| `title(line)` | 화면 가운데 큰 제목 |
| `where_text(line)` | 화면의 장소 문구 (`""`: 게임의 것) |
| `open_shop(shop)` | 가게 열기 (`VillagerData.SHOPS`의 id) |
| `play_music(track)` | 지금 곡 틀기 (`Music.TRACKS`의 id나 `res://….ogg`; `""`: 원래 목록으로) |
| `move_world(world, by_station)` | 서버의 다른 월드로 옮김 (`world`: [`Server::create_world`](#server)로 만든 id, `""` 모두의 월드). `by_station`이면 그 월드의 열기구 정거장으로, 아니면 농장 집 앞으로. 떠난 월드에서 `Leave`, 간 월드에서 `Join`; 가방·돈·스킬은 그대로 따라감 |
| `show(&Gui)` | 창 띄우기 ([`Gui`](#gui)). `PlayerLogin`에서는 들어오기 전의 입력 창 |
| `hud()` → `Hud` | 그 사람의 화면: HUD 요소, 게임 HUD 숨기기, 키, 채널 ([화면](screen)) |
| `open_inventory(&Inventory)` / `close_inventory(id)` | 이 플러그인의 인벤토리 창 열기(다시 부르면 지금 칸으로) / 닫기 ([인벤토리 창](screen#인벤토리-창)) |
| `get(k)` / `set(k, v)` | 그 사람에게 남기는 숫자 (이 플러그인의 것; 저장됨). plugin.json의 바가 보여 주는 값 |
| `data_put(key, &[u8])` → `bool` | 그 사람의 바이트 ([데이터 저장](#데이터-저장)) |
| `data_get(key)` → `Option<Vec<u8>>` | |
| `data_del(key)` | |

{: .note }
`give` `take` `add_gold` `add_energy` `say`(그리고 `drop_item` `fx` `prop`)는 플레이어가 한 일의 이벤트(행동, 명령어, 버튼, `Words`, `Use`, `Morning`, `PlayerDeath`, `LevelUp`, `MobDeath`, `BlockPlace` `BlockBreak` `Packet` `InventoryClick`)에서만 됩니다. `Tick` `Join` `Leave` `Chat` `PlayerMove` `PlayerItemHeld` `DayEnd` `DayChange` `WorldCreate` `ChunkGenerate` `ChunkLoad` `MobStep` `MineFloor`에서는 아무것도 하지 않고, `heal` `add_xp` `add_friendship` `set_walk_speed`는 거기서 월드 주인에게만 닿습니다. `Tick::players()`의 `Player`는 모아 두어도(`collect`) 저마다 그 사람입니다.

## PlayerInventory

`Player::inventory()` (Bukkit의 PlayerInventory). 아이템은 id와 개수뿐입니다.

| 메서드 | |
|---|---|
| `items()` → `Vec<(String, i64)>` | 가방의 모든 것 (id, 개수), id 순서 |
| `count(id)` → `i64` / `contains(id)` → `bool` | 개수 / 있는지 |
| `add(id, n)` | 넣기 (한 번에 999까지; `Player::give`) |
| `remove(id, n)` | 빼기: 있는 만큼만 (`Player::take`는 모자라면 아무것도 안 가져감) |
| `clear(include_tools)` | 비우기. `false`면 도구는 남김 (착용한 장비는 가방에 없으므로 늘 그대로) |

- 읽는 것은 **이벤트가 시작될 때**의 모습, 바꾸는 것은 **이벤트가 끝난 뒤**에 됩니다(`give`가 되는 이벤트에서만).
- 그 이벤트의 플레이어 것만 됩니다(`Tick::players()`의 다른 사람은 비어 보임).
- 가방은 그 사람의 것 하나로, 어느 월드에 있든 같습니다.

## Gear

도구·장비의 등급과 마법은 아이템 하나하나가 아니라 **그 사람의 그 도구**에 붙습니다(도끼는 한 사람에 하나: 대장간과 마법
부여대가 바꾸는 것). 그래서 `Player::gear(id)`로 따로 다룹니다.

| | |
|---|---|
| `id` `tier` `enchants` | 필드: 아이템 id, 등급, `Vec<(마법, 레벨)>` |
| `enchant(name)` → `i64` | 그 마법의 레벨 (0 없음) |
| `set_enchant(name, level)` | 그 레벨로 (규칙의 `enchant_max`까지, 칸 수는 세지 않음; 0이면 뗌). 가방에 있는 것에만 |
| `remove_enchant(name)` | 떼기 |

```rust
#[command("효율", "도끼에 효율 마법을 한 단계 더해요")]
fn efficiency(c: Command) {
    if let Some(axe) = c.player().gear("axe") {
        axe.set_enchant("efficiency", axe.enchant("efficiency") + 1);
    }
}
```

## World

이벤트의 월드 (`e.world()`). `id()`: 어느 월드인지 (`"world"` 모두의 월드, 아니면 [`Server::create_world`](#server)로 만든 id).

### 알림과 효과

| 메서드 | |
|---|---|
| `broadcast(line)` | 월드 모두의 채팅 |
| `play_music(track)` | 월드의 모두에게 곡 (`""`: 원래 목록으로) |
| `particle(name, x, y, z)` | 파티클: `"fire"` `"smoke"` `"sparkle"` `"splash"` `"leaf"` `"hit"` 또는 `res://….png` |
| `sound(name, x, y, z)` | 소리: `"hit"` `"pickup"` `"click"` `"step_soft"` `"step_hard"` 또는 `res://….ogg` |
| `set_weather(name, days_ahead)` | 그날(0 오늘, 112일 뒤까지)의 날씨: 규칙 `weather`의 이름 `"Clear Sky"` `"Cloudy 1"` `"Rain"` `"Storm"` `"Snow"` `"Foggy"` … (다른 이름은 무시) |

### 몬스터와 엔티티

| 메서드 | |
|---|---|
| `strike(x, z, radius, damage)` | 그 둘레의 몬스터 공격 |
| `spawn_mob(kind, x, z)` | 이벤트의 층에 몬스터 하나 (지상은 밤에만 남음) |
| `spawn(model, x, y, z)` → `Option<ModelEntity>` | 이 플러그인의 엔티티: `res://` 모델(glb, 씬) 또는 png(늘 카메라를 보는 그림) |
| `spawn_avatar(x, y, z)` → `Option<Avatar>` | 플레이어 아바타 엔티티 (게임이 플레이어처럼 그림; [`Avatar`](#avatar)) |
| `entities()` → `Vec<ModelEntity>` | 이 플러그인의 엔티티들 (아바타는 `as_avatar()`) |
| `items()` → `Vec<ItemEntity>` | 땅에 놓인 모든 아이템 (이벤트가 시작될 때의 것에서 이번 이벤트가 가져간 것을 뺀 것; 이번에 놓은 것은 없음) |
| `items_near(x, z, radius)` → `Vec<ItemEntity>` | 그 둘레(지상)의 아이템, 가까운 것부터 |
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
| `set_spawn(x, y, z, yaw)` | 월드의 스폰: 칸, 발 높이(높이 y 블록의 윗면은 y + 0.5), 바라보는 쪽(도). 침대·의료실·정거장이 없는 월드에서는 아침, 쓰러진 뒤, 내릴 때도 여기. 월드에 저장 ([월드 만들기](world#월드-만들기)) |
| `set_vanilla(feature, on)` | 게임의 기능 하나 켜고 끄기, 월드에 저장: `"villagers"` `"night"`(땅 위 밤 몬스터) `"farming"` `"wild"` `"tutorial"` `"shops"` `"sleep"`. 정하지 않으면 바닐라 마을이 있는 월드는 켜짐, 없는 월드는 꺼짐 |
| `set_quit_warning(text)` | 자기 전에 나갈 때 게임이 띄우는 경고 (`""` 없음, 200자까지). server.properties `quit-warning`보다 우선 |

### 하루

| 메서드 | |
|---|---|
| `set_day(day)` | 날짜 (1이 첫날; 계절은 날짜에서). 월드의 게임에 바로 알림 |
| `set_morning_time(minute)` `clear_morning_time()` | 밤이 끝나는 시각 (해가 뜨고 몬스터가 사라짐, 6:30 = 390) / 계절의 해 뜨는 시각으로 |
| `set_night_time(minute)` `clear_night_time()` | 밤이 시작되는 시각 (해가 지고 몬스터가 나옴, 18:00 = 1080) / 계절의 해 지는 시각으로 |
| `set_dawn_time(minute)` `clear_dawn_time()` | 몬스터가 강해지는 시각 (2:00 = 120), 아침까지 / 기본값으로 |
| `end_day()` | 지금 하루를 끝냄, 모두 잔 것처럼 (먼저 `DayEnd` `"end_day"`) |

### 블록

| 메서드 | |
|---|---|
| `block(x, y, z)` → [`Block`](#block) | 그 블록 (아직 안 만든 청크는 바닐라 땅으로) |
| `top(x, z)` → `i64` | 기둥에서 가장 높은 단단한 블록의 y (없으면 `Block::LOWEST - 1`) |
| `set_block(x, y, z, b)` | 블록 놓기 (저장됨) |
| `fill(from, to, b)` | 상자 모양 채우기, 양 끝 포함, 한 번에 청크 넷까지 |
| `set_blocks(&[(x, y, z, Block)])` | 여러 블록을 한 번에 (65 536개까지). `ChunkGenerate` / `ChunkLoad`에서는 그 청크의 것만 |
| `chunk_mark(x, z, name)` → `i64` / `set_chunk_mark(x, z, name, v)` | 청크 (x, z)에 이 플러그인이 남기는 숫자 (0: 없음; 월드와 함께 저장). 이미 넣은 것의 표시로 |
| `columns(x0, z0, w, d)` → `Vec<(Block, i64)>` | 위에서 본 땅: `w` × `d` 기둥(256 × 256까지, `w`개씩 줄로), 각 기둥의 가장 높은 단단한 블록(위에 물이면 물)과 높이 |
| `columns_raw(x0, z0, w, d)` → `Vec<u8>` | 같은 것을 기둥마다 두 바이트(블록 번호, 높이 − `Block::LOWEST`)로: 반복에서 읽기 쌈 ([미니맵](screen#미니맵)) |
| `hud()` → `Hud` | 월드 모두의 화면 ([화면](screen)) |

### 야생과 땅, 방

| 메서드 | |
|---|---|
| `debris_at(x, z)` → `String` | 그 칸(지상)의 야생 것: `"oak"` `"maple"` `"rock_small"` `"weeds"` 광맥 … (`""` 없음) |
| `tree_fell(x, z, toward_x, toward_z)` → `bool` | 그 나무를 플레이어의 마지막 도끼질처럼 그쪽으로 베어 쓰러뜨림: 그루터기가 남고 나무는 꼭대기가 닿는 곳에, 누구나 바로 주움. 모든 게임에서 쓰러짐 |
| `debris_break(x, z)` → `bool` | 돌·잡초·그루터기·광맥을 마지막 곡괭이·낫질처럼 부숨 (떨굼은 누구나) |
| `debris_hp(x, z)` → `i64` | 그 칸의 야생 것이 사라지기까지 남은 체력 (참나무 5, 큰 돌 3 …; 기본 도구 한 번이 1; 0 없음) |
| `debris_damage(x, z, n, toward_x, toward_z)` → `Option<i64>` | 도구 한 번처럼 `n`만큼 침: 모든 게임에서 흔들림, `Some(남은 체력)`. 0이 되면 마지막 한 번처럼 나무는 그쪽으로 쓰러지고(`tree_fell`) 나머지는 부서짐(`debris_break`): `Some(0)`. `None`: 아무것도 없음 |
| `ground_drop(item, n, x, y, z, floor)` → `Option<ItemEntity>` | 땅에 놓인 아이템(누구나 바로 주움; 게임이 모르는 아이템은 놓이지 않음) |
| `ground_remove(id)` | 그 번호의 것 치우기 (`ItemEntity::remove`) |
| `path((x0, z0), (x1, z1))` → `Vec<(f64, f64)>` | 마을 안의 걸어갈 길(주민의 길찾기와 같음: 지은 것을 돌아서, 길은 싸게): 첫 걸음 뒤로 꺾이는 점들, 마지막이 목적지. 비어 있으면 길이 없음. 한쪽이라도 마을 격자 밖이거나 마을 없는 월드면 `path_blocks`로(각 기둥 맨 위에서), 칸마다 |
| `path_blocks((x, y, z), (x, y, z), max)` → `Vec<(f64, f64, f64)>` | 어느 월드 어디서나 블록 위로 걷는 길: 첫 걸음부터 목적지까지 칸마다 `(x, 발 높이, z)`, 비어 있으면 길이 없음. 끝은 발 아래(조금 묻혀도) 가장 높은 설 수 있는 칸, 물속이면 물 위. 설 수 있는 칸: 단단한 블록 위에 몸 들어갈 두 칸(1.6 m)이 비었거나 물 맨 위(헤엄). 한 번에 한 칸 위로(플레이어 점프 1.5 m, 물에서 나올 때도), 네 칸까지 아래로, 여덟 방향, 모서리는 몸이 들어갈 때만. 플러그인의 단단하지 않은 블록은 지나감. `max`: 살필 칸 수(16384까지), 시작에서 가로세로 64칸 안. 엔진의 A*: 연료가 아니라 걸린 시간으로 셈 |
| `room(name)` → `Option<Room>` | 건물 방(`"Farmhouse"` …): `x` `z` 가운데, `y` 바닥(땅 아래), `door` 안쪽 문 앞, `out` 바깥 문 앞, `size`. 엔티티를 `(door.0, y, door.1)`로 옮기면 방 안 |

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
| `create_world(id)` → `bool` | 플러그인의 월드 하나 (바닐라 땅과 마을, 저만의 씨앗, 여느 월드처럼 저장; `id`는 영문·숫자·`_ - .` 32자까지, `false`: 쓸 수 없는 이름). 그 월드에서 `WorldCreate`·`ChunkGenerate`가 불림 ([플러그인의 월드](world#플러그인의-월드)) |
| `create_world_with(id, generator, town)` → `bool` | 생성기를 골라: `"vanilla"` `"flat"` `"void"`, `town` false면 바닐라 땅에 마을 없이 ([월드 만들기](world#월드-만들기)) |
| `data_put(key, &[u8])` → `bool` | 서버 하나의 바이트: 어느 월드의 이벤트에서든 같은 것 (월드를 오가도 따라가야 하는 것: 서버 안 친구 목록, 순위). **넣는 즉시 디스크에** 저장 ([데이터 저장](#데이터-저장)) |
| `data_get(key)` → `Option<Vec<u8>>` | |
| `data_del(key)` | |
| `data_keys(prefix)` → `Vec<String>` | 이 플러그인의 서버 키 중 `prefix`로 시작하는 것 |

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

## 엔티티

Bukkit의 `Entity` 계층처럼, 월드에 있는 것은 모두 `Entity` 트레잇을 구현합니다. Rust에는 클래스 상속이 없어서 종류마다
타입이 따로 있고, 공통 동작은 트레잇으로 나눕니다(`&dyn Entity`는 어느 것이든 받음).

```text
Entity (트레잇)            location  move_to  play_anim  stop_anim  remove  is_alive  distance_to
├── ModelEntity            이 플러그인의 모델 (World::spawn)
├── ItemEntity             땅에 놓인 아이템 (World::items, ground_drop)
├── EnemyEntity (= Mob)    몬스터 (MobStep::mob)
└── PlayerEntity (트레잇)  name  facing
    ├── Avatar             플러그인이 만든 플레이어 아바타 (World::spawn_avatar)
    └── Player             진짜 플레이어
```

### Entity

| 메서드 | |
|---|---|
| `location()` → `(x, y, z)` | 칸 좌표, y는 발 높이 (진짜 플레이어와 몬스터는 0: 땅 위) |
| `move_to(x, y, z)` | 그곳으로 (진짜 플레이어는 `Player::teleport`, 몬스터는 x z). 플러그인의 엔티티는 게임이 플러그인의 말 사이를 고른 빠르기로 그려서 틱마다의 걸음이 부드럽게 보임 (8 m 넘게는 바로) |
| `glide_to(x, y, z, secs)` | `secs`초에 걸쳐 고른 빠르기로 그려지며 감: 걷기 하나나 비행 하나를 한 번에 (자리는 이미 끝: `location`). 플러그인의 엔티티만, 다른 것은 `move_to`와 같음 |
| `play_anim(clip)` / `stop_anim()` | 모두에게 보이는 애니메이션: 모델은 그 클립, 아바타는 동작, 진짜 플레이어는 이모트(서 있을 때만), 몬스터는 클립 한 번, 아이템은 `set_model`한 모델의 클립 |
| `remove()` | 월드에서 없앰 (진짜 플레이어는 아무 일 없음) |
| `is_alive()` → `bool` | 아직 있음 (플레이어: 쓰러져 있지 않음) |
| `distance_to(&dyn Entity)` → `f64` | 땅 위의 거리 |
| `set_interact(label)` | 플레이어가 E로 쓸 수 있음: 가까이 가면 「E: label」, 누르면 [`EntityInteract`](events#entityinteract) (이 플러그인에만). `""` 끄기. 플러그인의 엔티티(`ModelEntity` `Avatar`)만 |
| `say(text)` | 머리 위 말풍선 (가까운 모두에게). 플러그인의 엔티티만 |

### ModelEntity

이 플러그인의 엔티티 (`World::spawn`). **저장되지 않습니다**: 서버를 다시 켜면 사라지니, 남길 것은 `World::set`에.

| 메서드 | |
|---|---|
| `get(k)` / `set(k, v)` | `"x"` `"y"` `"z"` `"yaw"`(라디안, 0이 +z) `"scale"` (`get`은 `"alive"`도) |
| `text(k)` → `String` | `"model"` `"anim"` `"held"` `"name"` |
| `as_avatar()` → `Option<Avatar>` | 아바타면 그것으로 |

### Avatar

플레이어 아바타 엔티티 (`World::spawn_avatar`): 게임이 플레이어처럼 그립니다. `PlayerEntity`.

| 메서드 | |
|---|---|
| `play_anim(동작)` | `"idle"` `"walk"` `"run"`(걷기·달리기는 빠르기로) `"sleep"` `"swim"` `"jump"` `"fall"`, 도구 `"axe"` `"pickaxe"` `"hoe"` `"scythe"` `"sword"` `"water"` `"cast"`(부를 때마다 한 번 휘두름), `"emote:<id>"` |
| `set_look(json)` | 모습: CatLook JSON `{"species": "Dog", "skin": "Dog03", "hat": "Cap_turboA"}` (`"{}"` 기본 고양이) |
| `hold(item)` | 손에 든 아이템 (`"axe"` …, `""` 없음) |
| `set_name(name)` / `name()` | 머리 위 이름 (`""` 없음) |
| `facing()` | 바라보는 쪽 (`yaw`에서) |
| `entity()` → `ModelEntity` | 모델 엔티티로서 (`set("yaw", ..)` `set("scale", ..)`) |

### ItemEntity

땅에 놓인 아이템 하나 (그 번호). 플레이어가 지나가면 줍고, 어느 엔티티든 먹을 수 있습니다.

| 메서드 | |
|---|---|
| `item()` → `String` / `amount()` / `floor()` | 아이템 id (`""` 없음), 개수, 광산 층 (0 지상) |
| `consume_by(&dyn Entity)` | 그 엔티티가 먹음: 땅에서 없어지고(아무도 못 얻음), 모든 게임에서 그쪽으로 날아 들어감 |
| `set_model(path)` | 아이템 대신 그 `res://` 모델로 그림 (`""` 아이템 모양으로) — 그 모델의 클립은 `play_anim` |
| `move_to(x, y, z)` | 옮김 (게임에서 미끄러지듯) |

```rust
// 가까운 사과를 먹는 아바타
if let Some(apple) = w.items_near(x, z, 2.0).into_iter().find(|i| i.item() == "apple") {
    apple.consume_by(&avatar);
}
```

### PlayerEntity

`Avatar`와 `Player`가 구현: `name()`(진짜 플레이어 `""`은 월드 주인), `facing()`.

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

## EnemyEntity

몬스터 하나 (`EnemyEntity(serial)`, 예전 이름 `Mob`; `MobStep::mob()`). `Entity`: `play_anim(clip)`은 그 종류 모델의 클립을
그 층의 모든 게임에서 한 번(`"Attack01"` `"Victory"` …), `location()`은 자기 `mob` 이벤트 안에서만.

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

`Block::named("stone")` → `Option<Block>`: 이름(또는 번호)으로. 플러그인이 등록한 종류(9부터)도 이름으로 찾습니다
([새 블록 종류](world#새-블록-종류)). `CHUNK` = 32: 청크 한 변의 칸 수.

## Registry

규칙에 더하고 바꾸기. [`Enable`](events#enable)에서만 됩니다(다른 이벤트에서는 아무것도 안 함). 자세히: [규칙 등록](rules).

| | |
|---|---|
| `Registry::patch(json)` | JSON 객체를 규칙 위에 덮음 (`"key+"`는 목록에 더함) |
| `Registry::set(path, json)` | 값 하나: `Registry::set("bag.slots", "48")` |
| `Registry::add(table, id, json)` | 표에 하나 |
| `Registry::block(id, &BlockKind)` | 블록 종류 ([새 블록 종류](world#새-블록-종류)): `BlockKind::new(name, look, tint)` `textured(name, png)` `model(name, glb, size)`, `solid` `item` `texture` `top` `bottom` `alpha` `model` `side` `size` |
| `Registry::item` `crop` `monster` `animal` `villager` `model` `emote` `(id, json)` | `items` `crops` `monsters_add` `animals_add` `villagers_add` `models_add` `emotes_add` |
| `Registry::text(from, to)` | 화면 글자 바꾸기 |
| `Registry::tick_rate(n)` | 이 플러그인의 [`Tick`](events#tick)을 1초에 n번 (기본 1번; 월드의 `tick-rate`보다 자주는 아님). `Enable`에서 |

## 화면 (`Hud`, `El`, `Inventory`)

`Player::hud()` / `World::hud()`의 `Hud`: `add(id, &El)` `set(id, &El)` `remove(id)` `clear()` `hide(part)` `show(part)` `key(key, on)`
`send(chan, &[u8])` `send_text(chan, text)` `send_png(chan, w, h, &rgba)` `send_fast(chan, text)`(게임 쪽 코드에 빠른 패킷: 데이터그램, 1000바이트까지, 순서 없음; [빠른 통신](client#빠른-통신)). `El::panel` `text` `image` `bar` `button` `input`에
`anchor(Anchor::…)` `pos` `size` `color` `bind` `follow` `zoom` `rotate` `round` `marker` `child` …. `Inventory::new(id, title, rows, cols)`
`.slot(i, item, n, name, lore)` `.with_bag()`. 모두 [화면](screen)에.

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
- 서버 하나의 것은 `Server.data_*`: 어느 월드에서나 같은 것을 읽고 쓰고, 아침을 기다리지 않고 넣는 즉시 저장됩니다. 플러그인마다
  따로, 모든 플러그인 합쳐 100 MB. 위치: `<data>/plugin_data/@server/<플러그인>/`.

```rust
let w = e.world();
w.data_put("log/1", "첫 수확".as_bytes());
for k in w.data_keys("log/") {
    let line = String::from_utf8(w.data_get(&k).unwrap_or_default()).unwrap_or_default();
}
```

## `sys` — 원본 함수

SDK가 감싸지 않은 것은 `greenhaven_plugin::sys`에 "gh" 함수 그대로 있습니다 ([목록](abi)).
