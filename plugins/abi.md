---
title: "\"gh\" 함수 (원본 ABI)"
nav_order: 7
parent: 플러그인
redirect_from:
  - /abi
  - /abi.html
---

# "gh" 함수 (원본 ABI)
{: .no_toc }

SDK가 감싸는 서버 함수들입니다(서버 쪽 `server.wasm`). 게임 쪽 `client.wasm`이 쓰는 모듈 `"ghc"`는 [아래](#게임-쪽-ghc). Rust SDK로는 `greenhaven_plugin::sys`에 그대로 있고, 다른 언어로 WebAssembly를 만들 때는
모듈 `"gh"`에서 가져옵니다.

1. TOC
{:toc}

## 약속

- 모듈은 `memory`를 내보냅니다.
- 이벤트: SDK 없이는 `on_event() -> i32` (0 그대로, 아니면 막음)를 내보내고 plugin.json의 `events`로 구독합니다.
  규칙을 등록하려면 `"enable"`을 구독하고 거기서 `register`를 부릅니다(샘플 `wild_fish`).
  SDK는 핸들러마다 내보내기를 만들고 "gh" 커스텀 섹션에 `on\t<이벤트>\t<우선순위>\t<내보내기>\n`,
  `command\t<이름>\t<설명>\n` 줄을 씁니다.
- 글을 넘길 때: `(ptr, len)` (UTF-8).
- 글을 받을 때: `(ptr, cap)`에 복사되고 **전체 길이**를 돌려줍니다. 돌려준 길이가 `cap`보다 크면 그만큼 버퍼를 늘려 다시 부르세요.
  바이트를 받는 `*_get`은 없을 때 `-1`.
- 이벤트 하나에 연료 5 000 000 명령, 메모리 16 MB ([샌드박스](server#샌드박스)).

## 읽기

| 함수 | |
|---|---|
| `event(p, cap) -> i32` | 이벤트 이름 |
| `kind(p, cap) -> i32` | 행동 종류 |
| `id(p, cap) -> i32` | 아이템·작물·대상 |
| `tool(p, cap) -> i32` | 도구 |
| `me(p, cap) -> i32` | 이벤트의 플레이어 이름 (`""` 월드 주인; tick은 `player(i)`로 고른 사람) |
| `x() -> i64` `z() -> i64` `n() -> i64` | 칸, 개수 |
| `num(k, kl) -> f64` | 이벤트의 숫자 ([키](events#num--text의-키)) |
| `text(k, kl, p, cap) -> i32` | 이벤트의 글 |
| `roll(k: i64) -> f64` | 정해진 난수 [0, 1) |
| `setting(k, kl, p, cap) -> i64` | 이 플러그인의 설정 값 (글자; −1 없음) |

## 이벤트 값과 효과

| 함수 | |
|---|---|
| `set(k, kl, v: f64)` | 이벤트 값 바꾸기 |
| `refuse(p, len)` | 막기 (이유) |
| `drop(p, len, n: i64)` | 이벤트의 칸에 아이템 떨구기 |
| `give(p, len, n: i64)` | 아이템 주기 (음수면 빼기) |
| `inv_count(p, len) -> i64` | 그 플레이어의 가방에 그 아이템이 몇 개 |
| `inv_list(p, cap) -> i32` | 가방의 모든 것: 한 줄에 하나 `id	n	tier	마법:레벨,…` (이벤트가 시작될 때의 것) |
| `inv_clear(tools: i32)` | 가방 비우기 (`tools` 0이 아니면 도구까지; 착용한 장비는 그대로) |
| `inv_enchant(ip, il, ep, el, level: i64)` | 그 사람의 도구 `ip`에 마법 `ep`를 그 레벨로 (0: 떼기; 규칙의 `enchant_max`까지) |
| `gold(d: i64)` `energy(d: f64)` | 골드, 기력 |
| `prop(p, len, v: f64)` | 그 칸에 선 것의 속성 (`scale`) |
| `say(p, len)` | 플레이어에게 한마디 |
| `fx(p, len)` | 그 칸에서 소리 |
| `particle(p, len, x, y, z: f64)` `sound(p, len, x, y, z: f64)` | 파티클, 소리 (월드의 모두에게) |
| `strike(x, z, r: f64, damage: i64)` | 둘레의 몬스터 공격 |
| `reply(p, len)` | `words`: 주민이 대신 할 말 / `chat`: 대신 할 말 |
| `gui(p, len)` | 창: `{"id", "title", "text", "npc", "image", "buttons": [{"id", "label", "style"}], "inputs": [{"id", "label", "placeholder", "max", "secret"}]}`; 닫기 `{"id", "close": true}` |

## 플레이어

| 함수 | |
|---|---|
| `where_text(p, len)` `title(p, len)` `chat(p, len)` | 위치 문구, 큰 제목, 채팅 한 줄 |
| `broadcast(p, len)` | 월드 모두의 채팅 |
| `teleport(x, z: f64)` `heal(n: f64)` | 옮기기, 체력 |
| `xp(p, len, n: i64)` `friendship(p, len, n: i64)` | 경험치, 호감도 |
| `open_shop(p, len)` | 가게 열기 |
| `set_walk_speed(times: f64)` | 걸음 빠르기 |
| `mount(id: i64, speed, seat: f64)` `dismount()` | 이 플러그인의 엔티티에 태우기 (걸음 `speed`배, `seat` m 위에 앉음), 내리기 ([탈것](moving#탈것)) |
| `set_check(p, len, on: i32)` | 서버의 이동 검사 하나(`speed` `walls` `air` `teleport` `reach`)를 그 플레이어에게만 끄고 켬 ([이동 방식 만들기](moving#서버의-이동-검사)) |
| `death(hold: i32)` `respawn()` | 쓰러뜨림 (`hold` 0이 아니면 쓰러진 채 대기), 일으킴 |
| `set_model(p, len)` | [커스텀 모델](models) (빈 문자열: 원래 모습) |
| `play_anim(p, len)` `stop_anim()` | [감정 표현](models) 재생, 끝내기 |
| `set_time(minute: i64)` | 그 월드의 시각 |
| `visit(p, len)` `home()` | 열기구로 그 월드에 / 집으로 |
| `music_play(p, len)` `music_all(p, len)` | 그 플레이어 / 월드 모두에게 곡 |
| `player(i: i32) -> i32` | tick: i번째 플레이어를 고름 (뒤의 `pget` `me` 등이 그 사람) |

## 값과 데이터

| 함수 | |
|---|---|
| `wget(k, kl) -> f64` `wset(k, kl, v)` | 월드의 값 (플러그인마다) |
| `pget(k, kl) -> f64` `pset(k, kl, v)` | 플레이어의 값 |
| `sget(k, kl) -> f64` `sset(k, kl, v)` | 서버의 값 (`sset`은 `login`·그 창·`server.tick`에서만) |
| `data_put(k, kl, p, len) -> i32` | 월드의 바이트 (1 성공, 0 한도 넘음) |
| `data_get(k, kl, p, cap) -> i64` | (−1 없음) |
| `data_del(k, kl)` | |
| `data_keys(prefix, pl, p, cap) -> i64` | 키들, 줄바꿈으로 |
| `player_data_put` `player_data_get` `player_data_del` | 그 플레이어(`me`)의 바이트 (같은 모양) |
| `save_now()` | 월드를 지금 저장 |
| `set_live_saving(on: i32)` | 실시간 저장 |
| `set_quit_warning(p, len)` | 나가기 경고 |
| `set_shared_world(on: i32)` | 모두의 월드 |

## 접속하지 않은 플레이어

그 사람의 마지막으로 저장된 게임, 읽기만. 이벤트 한 번에 디스크에서 32명까지.

| 함수 | |
|---|---|
| `offline_names(p, cap) -> i64` | 들어온 적 있는 모두, 줄바꿈으로 |
| `offline_has(np, nl) -> i32` | 저장된 게임이 있으면 1 |
| `offline_num(np, nl, kp, kl) -> f64` | `gold` `day` `energy` `seen` `level.<스킬>` `xp.<스킬>` `friendship.<주민>` `item.<id>`, 이 플러그인의 `w.<키>` `p.<키>` |
| `offline_data(np, nl, kp, kl, p, cap) -> i64` | 이 플러그인이 그 사람 월드에 맡긴 바이트 (−1 없음) |
| `offline_player_data(np, nl, kp, kl, p, cap) -> i64` | 그 사람 월드에서 그 사람에게 맡긴 바이트 |

## 하루와 날씨

| 함수 | |
|---|---|
| `set_weather(p, len, ahead: i64)` | 그날의 날씨 |
| `set_day(day: i64)` | 날짜 |
| `set_morning_time(minute: i64)` `set_night_time(minute: i64)` `set_dawn_time(minute: i64)` | 밤이 끝나는, 시작되는, 몬스터가 강해지는 시각 (음수: 규칙 값으로) |
| `end_day()` | 하루를 끝냄 |

## 엔티티, 주민, 몬스터

| 함수 | |
|---|---|
| `ent_spawn(p, len, x, y, z: f64) -> i64` | 엔티티 만들기 (id, 0 실패) |
| `ent_get(id, k, kl) -> f64` `ent_set(id, k, kl, v)` | `x` `y` `z` `yaw` `scale` (`alive`); `glide`(초)를 먼저 쓰고 `x` `y` `z`를 쓰면 그만큼에 걸쳐 그려지며 감 (SDK의 `glide_to`) |
| `ent_anim(id, p, len)` `ent_remove(id)` | 클립 (아바타: 동작, 부를 때마다 한 번) |
| `ent_look(id, p, len)` `ent_held(id, p, len)` | 아바타(`ent_spawn("avatar", …)`)의 CatLook JSON, 손에 든 아이템 id |
| `ent_name(id, p, len)` | 아바타 머리 위 이름 (`""` 없음) |
| `ent_text(id, kp, kl, p, cap) -> i32` | `model` `anim` `held` `name` |
| `ent_count() -> i64` `ent_at(i) -> i64` | 이 플러그인의 엔티티 |
| `npc_count() -> i64` `npc_id(i, p, cap) -> i32` | 주민 목록 |
| `npc_get(ip, il, kp, kl) -> f64` | `x` `z` `moving` `hidden` `indoors` |
| `npc_goto(ip, il, x, z, hold: f64)` `npc_say(ip, il, tp, tl)` | 보내기, 한마디 |
| `npc_spawn(p, len) -> i32` `npc_set(ip, il, p, len)` `npc_remove(ip, il)` | 더하기 (1/0), 바꾸기, 빼기 |
| `mob_set(n, k, kl, v)` `mob_attack(n, damage, reach: f64)` | 몬스터 값, 공격 |
| `mob_spawn(p, len, x, z: f64)` `mob_remove(n)` | 소환, 없애기 |
| `mob_anim(n, p, len)` | 그 몬스터 모델의 클립 한 번 (그 층의 모든 게임) |
| `mine_rock(i, j: i32, p, len)` | `mine.floor`: 바위 놓기 (`""` 치우기) |

## 블록과 구조물

| 함수 | |
|---|---|
| `block(x, y, z: i64) -> i32` | 블록 |
| `block_id(p, len) -> i32` | 이름의 번호 (−1 없음) |
| `top(x, z: i64) -> i64` | 가장 높은 단단한 블록 |
| `set_block(x, y, z: i64, b: i32)` | |
| `fill(x0, y0, z0, x1, y1, z1: i64, b: i32)` | 양 끝 포함, 한 번에 청크 넷까지 |
| `props_clear()` | `chunk.generate`: 그 청크의 덤불·풀·유목 치우기 |
| `set_blocks(p, len)` | 블록 여럿을 한 번에: 블록마다 `i32` x, y, z, 번호 (리틀 엔디언, 16바이트), 65 536개까지. `chunk.generate` / `chunk.load`에서는 그 청크의 것만 |
| `chunk_mark(x, z: i64, p, len) -> i64` | 청크 (x, z)에 이 플러그인이 남긴 숫자 `name` (0 없음; 월드와 함께 저장) |
| `chunk_set_mark(x, z: i64, p, len, v: i64)` | 그 숫자 정하기 |
| `structure_count() -> i64` `structure_id(i) -> i64` | 구조물 목록 |
| `structure_get(id, k, kl) -> f64` | `x` `z` `y` `yaw` `w` `d` `scale` |
| `structure_text(id, k, kl, p, cap) -> i32` | `k` `m` `plot` `n` `key` `kind` `label` `text` `s` `owner` |
| `structure_put(p, len) -> i64` | 세우기 (id, 0 실패) |
| `structure_remove(id)` `structure_remove_plot(p, len)` `structure_move(id, x, z, yaw: f64)` | |
| `debris_at(x, z: i64, p, cap) -> i32` | 그 칸(지상)의 야생 것 id (`""` 없음) |
| `tree_fell(x, z: i64, tx, tz: f64) -> i32` | 나무를 마지막 도끼질처럼 (tx, tz) 쪽으로 베기 (1/0): 그루터기, 나무는 누구나 |
| `debris_break(x, z: i64) -> i32` | 돌·잡초·그루터기·광맥 부수기 (1/0) |
| `ground_drop(p, len, n: i64, x, y, z: f64, floor: i64) -> i64` `ground_remove(id)` | 땅에 아이템 놓기(번호, 0 실패; 누구나 바로 주움) / 치우기 |
| `debris_hp(x, z: i64) -> i64` | 그 칸의 야생 것의 남은 체력 (0 없음) |
| `debris_damage(x, z, n: i64, tx, tz: f64) -> i64` | `n`만큼 치기: 남은 체력 (흔들림), 0이면 쓰러짐/부서짐(나무는 (tx, tz) 쪽으로), −1 없음 |
| `ground_count() -> i64` `ground_at(i) -> i64` | 땅의 아이템 번호들 (이벤트가 시작될 때의 것, 이번에 가져간 것 빼고) |
| `ground_get(id, k, kl) -> f64` `ground_item(id, p, cap) -> i32` | `x` `y` `z` `n` `floor` `alive` (NaN 없음) / 아이템 id |
| `ground_move(id, x, y, z: f64)` | 옮기기 |
| `ground_model(id, p, len)` `ground_anim(id, p, len)` | 아이템 대신 그릴 `res://` 모델 (`""` 아이템 모양), 그 모델의 클립 (부를 때마다) |
| `ground_consume(id, x, y, z: f64)` | 그곳의 무언가가 먹음: 없어지고, 게임은 그쪽으로 날아가게 그림 |
| `room_get(np, nl, kp, kl) -> f64` | 방: `x` `z` `y`(바닥) `door_x` `door_z` `out_x` `out_z` `w` `d` (NaN 없음) |

## 등록과 화면

| 함수 | |
|---|---|
| `register(p, len)` | 규칙 위에 덮을 JSON 객체 ([규칙 등록](rules)). `enable` 이벤트에서만 (다른 때는 무시), 한 번에 1 MB까지 |
| `hud(p, len)` `hud_all(p, len)` | HUD 작업 하나 (그 플레이어 / 월드 모두): `{"op", …}` (`op`: `add` `set` `remove` `clear` `hide` `show` `key`) ([화면](screen#sdk-없이)), 64 KB까지 |
| `send(cp, cl, p, len)` `send_all(cp, cl, p, len)` | 채널 `cp`에 바이트 (그 플레이어 / 모두), 256 KB까지 |
| `send_png(cp, cl, w, h: i32, p, len, all: i32) -> i32` | RGBA8 픽셀(`w` × `h`, 512까지)을 PNG로 채널에 (`all` 0이 아니면 모두에게). PNG의 바이트 수, `len`이 `w × h × 4`가 아니면 0 |
| `columns(x0, z0, w, d: i64, p, cap) -> i64` | 위에서 본 땅: 기둥마다 2바이트(가장 높은 단단한 블록 번호(위에 물이면 물), 높이 − (−8)), `w`개씩 줄로, 256 × 256까지. 전체 바이트 수 |
| `inv_open(p, len)` | 인벤토리 창 `{"id", "title", "rows", "cols", "slots", "bag"}` / 닫기 `{"id", "close": true}` |

게임에서 오는 것은 이벤트로: `packet`(`text("channel")` `text("data")`), `inventory`(`text("inv")` `text("side")` `n()` 칸
`text("click")` `text("bag_item")`).

## 이벤트 말고 내보내는 것

`reel(tick: i64, fish_y: f64, level: f64, roll: f64) -> f64` — 낚시 물고기의 길 ([낚시의 손맛](rules#낚시의-손맛)).

## 게임 쪽 (`"ghc"`)

[게임 쪽 코드](client)(`client.wasm`)가 가져다 쓸 수 있는 것은 모듈 `"ghc"`의 여섯 함수뿐입니다(`greenhaven_client::sys`). 게임은
이것 말고는 아무것도 연결하지 않고, 다른 것을 가져다 쓰는 모듈은 로드하지 않습니다. 글을 넘기고 받는 약속은 [위](#약속)와 같습니다.
상태를 바꾸는 함수는 없습니다: 모두 이번 호출에 게임이 알려 준 것을 읽거나, 게임이 그릴 작업을 남깁니다.

| 함수 | |
|---|---|
| `num(k, kl) -> f64` | 게임이 알려 준 숫자 (`dt` `time` `me.x` `me.y` `me.z` `me.yaw` `me.vx` `me.vy` `me.vz` `me.ground` `cam.x` `cam.y` `cam.z` `cam.yaw` `screen.w` `screen.h` `mouse.x` `mouse.y` `minute` `day` `pressed` `held.<키>`; 없으면 NaN) |
| `text(k, kl, p, cap) -> i32` | 게임이 알려 준 글 (`me` `server` `channel` `data` `key`) |
| `send(cp, cl, dp, dl)` | 서버 쪽에 채널 `cp`로 패킷 (서버의 `packet` 이벤트; 플러그인 하나가 1초에 8개까지) |
| `op(kp, kl, jp, jl)` | 게임이 그릴 작업 하나: 종류 `kp`(`hud` `camera` `screen` `fx` `log` `local` `entity` `me` `input`)와 그 JSON `jp` (호출 한 번에 256개, 하나 64 KB까지) |
| `query(kp, kl, jp, jl, p, cap) -> i32` | 엔진에 묻기: `raycast` `[x0,y0,z0,x1,y1,z1]`, `ground` `[x,z]`, `path` `[x0,z0,x1,z1]` → 답의 JSON |
| `local_id() -> i64` | 자기에게만 보이는 물체(`Local`)에 줄 새 id |

내보내는 것: `ghc_load` `ghc_frame` `ghc_packet` `ghc_input` (`() -> i32`, 있는 것만; SDK의 `client!`가 만듦).
