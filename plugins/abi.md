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

SDK가 감싸는 서버 함수들입니다. Rust SDK로는 `greenhaven_plugin::sys`에 그대로 있고, 다른 언어로 WebAssembly를 만들 때는
모듈 `"gh"`에서 가져옵니다.

1. TOC
{:toc}

## 약속

- 모듈은 `memory`를 내보냅니다.
- 이벤트: SDK 없이는 `on_event() -> i32` (0 그대로, 아니면 막음)를 내보내고 plugin.json의 `events`로 구독합니다.
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
| `set_day(day: i64)` `set_day_start(minute: i64)` `set_day_end(minute: i64)` | 날짜, 아침 시각, 하루의 끝 |
| `end_day()` | 하루를 끝냄 |

## 엔티티, 주민, 몬스터

| 함수 | |
|---|---|
| `ent_spawn(p, len, x, y, z: f64) -> i64` | 엔티티 만들기 (id, 0 실패) |
| `ent_get(id, k, kl) -> f64` `ent_set(id, k, kl, v)` | `x` `y` `z` `yaw` `scale` (`alive`) |
| `ent_anim(id, p, len)` `ent_remove(id)` | |
| `ent_count() -> i64` `ent_at(i) -> i64` | 이 플러그인의 엔티티 |
| `npc_count() -> i64` `npc_id(i, p, cap) -> i32` | 주민 목록 |
| `npc_get(ip, il, kp, kl) -> f64` | `x` `z` `moving` `hidden` `indoors` |
| `npc_goto(ip, il, x, z, hold: f64)` `npc_say(ip, il, tp, tl)` | 보내기, 한마디 |
| `npc_spawn(p, len) -> i32` `npc_set(ip, il, p, len)` `npc_remove(ip, il)` | 더하기 (1/0), 바꾸기, 빼기 |
| `mob_set(n, k, kl, v)` `mob_attack(n, damage, reach: f64)` | 몬스터 값, 공격 |
| `mob_spawn(p, len, x, z: f64)` `mob_remove(n)` | 소환, 없애기 |
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
| `structure_count() -> i64` `structure_id(i) -> i64` | 구조물 목록 |
| `structure_get(id, k, kl) -> f64` | `x` `z` `y` `yaw` `w` `d` `scale` |
| `structure_text(id, k, kl, p, cap) -> i32` | `k` `m` `plot` `n` `key` `kind` `label` `text` `s` `owner` |
| `structure_put(p, len) -> i64` | 세우기 (id, 0 실패) |
| `structure_remove(id)` `structure_remove_plot(p, len)` `structure_move(id, x, z, yaw: f64)` | |

## 이벤트 말고 내보내는 것

`reel(tick: i64, fish_y: f64, level: f64, roll: f64) -> f64` — 낚시 물고기의 길 ([낚시의 손맛](rules#낚시의-손맛)).
