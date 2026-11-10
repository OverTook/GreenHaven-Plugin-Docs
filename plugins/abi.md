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

농장 게임(바닐라 모듈)의 함수(`gold` `energy` `set_energy` `xp` `friendship` `open_shop` `set_vanilla` `vanilla_on` `set_dawn_time`
`strike` `mob_*` `npc_*` `debris_*` `tree_fell` `room_get` `equip_*` `inv_enchant` `mine_rock`)도 같은 모듈 `"gh"`에 있지만, Rust SDK는
그것들을 `greenhaven_plugin::vanilla`의 트레잇으로만 감쌉니다([SDK › 바닐라 모듈](sdk#바닐라-모듈-greenhaven_pluginvanilla)). 농장이 없는
서버·월드에서는 아무것도 하지 않습니다.

1. TOC
{:toc}

## 약속

- 모듈은 `memory`를 내보냅니다.
- 이벤트: SDK 없이는 `on_event() -> i32` (0 그대로, 아니면 막음)를 내보내고 plugin.json의 `events`로 구독합니다.
  규칙을 등록하려면 `"enable"`을 구독하고 거기서 `register`를 부릅니다(샘플 `wild_fish`).
  SDK는 핸들러마다 내보내기를 만들고 "gh" 커스텀 섹션에 `on\t<이벤트>\t<우선순위>\t<내보내기>\n`
  (`#[every]`는 뒤에 `\t<밀리초>`: 그 주기로만 불림), `command\t<이름>\t<설명>\n`, `export\t<이름>\t<내보내기>\n`([플러그인끼리](#플러그인끼리)) 줄을 씁니다.
- Tick 빈도: `register`의 패치에 `{"plugin":{"tick_rate":n}}`(규칙이 아니라 이 플러그인의 요청: 1초에 n번, 기본 1).
- 글을 넘길 때: `(ptr, len)` (UTF-8).
- 글을 받을 때: `(ptr, cap)`에 복사되고 **전체 길이**를 돌려줍니다. 돌려준 길이가 `cap`보다 크면 그만큼 버퍼를 늘려 다시 부르세요.
  바이트를 받는 `*_get`은 없을 때 `-1`.
- 이벤트 하나에 연료 5 000 000 명령, 실제 시간 약 50 ms(호스트 함수 포함), 메모리 16 MB ([샌드박스](server#샌드박스)).

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
| `inv_clear(tools: i32)` | 가방 비우기 (`tools` 0이 아니면 도구까지: SDK의 `PlayerInventory::clear()`는 1, 바닐라의 `clear_keep_tools()`는 0; 착용한 장비는 그대로) |
| `inv_size() -> i32` `inv_held() -> i32` | 칸 수, 손에 든 단축바 칸 |
| `inv_get(slot, p, cap) -> i32` | 한 칸: `id	n` 그리고 메타 한 줄씩 (`name	..` `lore	..` `tint	..` `model	..` `data	키	값` `unbreakable` `glow` `tier	등급` `ench	마법	단계`); 비면 `""` |
| `inv_set(slot, ip, il, n: i64, mp, ml)` | 그 칸을 n개의 `ip`로, 메타 `mp`(JSON, 빈 것: 없음; n 0: 비우기) |
| `inv_fill(p, len)` | 가방 전체 `[[id, n, meta] 또는 null, ...]` |
| `inv_set_held(slot)` `inv_give(ip, il, n: i64, mp, ml)` | 든 칸, 메타 붙여 주기 |
| `inv_enchant(ip, il, ep, el, level: i64)` | 그 사람의 도구 `ip`에 마법 `ep`를 그 레벨로 (0: 떼기; 규칙의 `enchant_max`까지) |
| `gold(d: i64)` `energy(d: f64)` | 골드, 기력 |
| `prop(p, len, v: f64)` | 그 칸에 선 것의 속성 (`scale`) |
| `say(p, len)` | 플레이어에게 한마디 |
| `fx(p, len)` | 그 칸에서 소리 (SDK `Base::sound_here`) |
| `particle(p, len, x, y, z: f64)` `sound(p, len, x, y, z: f64)` | 파티클, 소리 (월드의 모두에게; SDK `World`의 `Audience::particle` / `sound`) |
| `strike(x, z, r: f64, damage: i64)` | 둘레의 몬스터 공격 |
| `reply(p, len)` | `words`: 주민이 대신 할 말 / `chat`: 대신 할 말 |
| `gui(p, len)` | 창: `{"id", "title", "text", "npc", "image", "buttons": [{"id", "label", "style"}], "inputs": [{"id", "label", "placeholder", "max", "secret"}]}`; 닫기 `{"id", "close": true}` |

## 플레이어

| 함수 | |
|---|---|
| `where_text(p, len)` `title(p, len)` `chat(p, len)` | 위치 문구, 큰 제목, 채팅 한 줄 (SDK `Player`의 `Audience`) |
| `broadcast(p, len)` | 월드 모두의 채팅 (SDK `World`의 `Audience::message`) |
| `teleport(x, z: f64)` `heal(n: f64)` | 옮기기, 체력 |
| `xp(p, len, n: i64)` `friendship(p, len, n: i64)` | 경험치, 호감도 |
| `open_shop(p, len)` | 가게 열기 |
| `set_walk_speed(times: f64)` | 걸음 빠르기 |
| `mount_seat(id: i64, seat: i32, speed, x, y, z: f64)` | 자리 `seat`(0 운전석, 나머지 승객)에 태우기, 승객은 엔티티의 (x 오른쪽, y 위, z 앞) m에 ([탈것](moving#탈것)) |
| `mount(id: i64, speed, seat: f64)` `dismount()` | 이 플러그인의 엔티티에 태우기 (걸음 `speed`배, `seat` m 위에 앉음), 내리기 ([탈것](moving#탈것)) |
| `set_check(p, len, on: i32)` | 서버의 이동 검사 하나(`speed` `walls` `air` `teleport` `reach`)를 그 플레이어에게만 끄고 켬 ([이동 방식 만들기](moving#서버의-이동-검사)) |
| `death(hold: i32)` `respawn()` | 쓰러뜨림 (`hold` 0이 아니면 쓰러진 채 대기), 일으킴 |
| `set_model(p, len)` | [커스텀 모델](models) (빈 문자열: 원래 모습) |
| `play_anim(p, len)` `stop_anim()` | [감정 표현](models) 재생, 끝내기 (SDK `Player::play_emote` / `stop_emote`) |
| `set_time(minute: i64)` | 그 월드의 시각 (SDK `World::set_minute`) |
| `move_world_at(p, len, ap, al)` | 그 플레이어를 서버의 그 월드로 (`""` 모두의 월드), 게임 모듈이 아는 자리 `ap`(32바이트까지)로: 농장의 `"station"`(그 월드의 열기구 정거장) `"desert"`(사막의 정거장); `""`이나 모르는 이름이면 그 월드의 스폰. 예전의 `move_world(p, len, station: i32)`는 없어졌습니다 |
| `music_play(p, len)` `music_all(p, len)` | 그 플레이어 / 월드 모두에게 곡 (SDK `Audience::music` / `music_with`) |
| `player(i: i32) -> i32` | tick: i번째 플레이어를 고름 (뒤의 `pget` `me` 등이 그 사람; -1: 이벤트의 그 사람으로 돌아감) |
| `player_named(p, len) -> i32` | 서버 어디든 접속한 그 이름의 사람을 `player(i)`의 번호로 (-1: 없음; `num("player.i.x")` 등도 채움) |
| `char_view(p, len)` | 보기 그룹 (`Player::set_view_group`; 빈 이름: 없음) |
| `char_invisible(on: i32)` `char_hide_from(p, len, on: i32)` | 그 플레이어를 아무에게도 / 그 이름의 한 사람에게 보내지 않기 |
| `char_disguise(ent: i64, snap: i32)` | 이 플러그인의 엔티티로 변장 (0: 끄기, 엔티티 지움) |
| `char_nametag(p, len, cp, cl)` `char_nametag_visible(on: i32)` `char_scale(s: f64)` | 이름표 글과 색, 보이기, 크기 (0.25-4) |
| `char_clip(p, len, upper: i32, looped: i32, speed: f64)` | 걷는 몸 위에 겹치는 클립 (`""` 멈춤; 빠르기 0.1-4) |
| `char_jump(s: f64)` `char_gravity(s: f64)` `char_freeze(on: i32)` `char_spectator(on: i32)` | 점프·중력 배율 (서버의 공중 검사도), 제자리, 관전자 |
| `char_public(kp, kl, vp, vl)` `ent_public(id: i64, kp, kl, vp, vl)` | 공개 값 (값은 JSON: 숫자, 글, `null`) |
| `online(p, cap) -> len` | 접속한 사람들 `"이름\t월드\n"` |
| `broadcast_all(p, len)` | 서버 모두의 채팅 |
| `teleport_to(x, y, z, yaw: f64)` | 3D로 옮기기 (NaN: 땅 위 / 바라보던 대로) |
| `damage(amount: f64, cp, cl, bp, bl)` | 피해 (원인, 친 사람) — `plugin_api/combat.rs` |
| `set_health(n: f64)` `set_max_health(n: f64)` | 체력, 최대 체력 |
| `set_pvp(on: i32)` `pvp() -> i32` | 월드의 PvP |
| `ent_set_health(id: i64, hp, max: f64)` `ent_health(id: i64) -> f64` | 엔티티의 체력 (SDK `LivingEntity::set_health` / `set_max_health`) |
| `ent_damage(id: i64, amount: f64)` | 엔티티에 피해: 폭발의 한 대처럼 `EntityDamage` / `EntityDeath`(원인은 플러그인 이름, 친 사람은 이벤트의 플레이어), `Explosion` 이벤트 없음 |
| `cast(x, y, z, dx, dy, dz, len: f64, wp, wl, p, cap) -> len` | 광선 판정 → `"kind	who	x	y	z	nx	ny	nz	거리"`(`""` 없음; kind `block` `box` `player` `entity`); `wp` 이름이 있으면 그 사람의 한 발(되감기, 눈, PvP, 초당 20) |
| `trail_at(wp, wl, ms_ago: f64, p, cap) -> len` | 그 사람(`""` 이벤트의 사람)이 있던 곳 `"x	y	z	yaw"` |
| `projectile(mp, ml, x, y, z, vx, vy, vz, g, radius, life: f64) -> i64` | 발사체 엔티티 (−1 못 만듦) — `plugin_api/projectile.rs` |
| `ent_gravity(id: i64, g: f64)` `ent_velocity(id: i64, vx, vy, vz: f64)` `ent_persist(id: i64, on: i32)` | 엔티티의 중력, 속도, 저장 |
| `projectile_with(mp, ml, x, y, z, vx, vy, vz, g, radius, life: f64, bounces: i32, restitution, friction, drag: f64) -> i64` | 튕기는 발사체 |
| `ent_body(id: i64, restitution, friction, drag: f64)` | 엔티티의 튕김·마찰·저항 |
| `explode(x, y, z, radius, damage, falloff, knock: f64, mask: i32, bp, bl, fp, fl, p, cap) -> len` | 폭발 → `"kind	who	거리	피해"` 한 줄씩 — `plugin_api/combat.rs` |
| `sight(x, y, z, range: f64, p, cap) -> len` | 그 점을 보는 사람 → `"이름	거리	각도"` 한 줄씩 |
| `zone_belt(p, len, vx, vz: f64)` `zone_watch(p, len, on: i32)` | 구역을 컨베이어로, 엔티티를 지켜봄 — `plugin_api/zones.rs` |
| `rand(tp, tl) -> f64` | 월드의 이 플러그인의 난수 흐름의 다음 수 — `plugin_api/effects.rs` |
| `team_set(p, len, jp, jl) -> i32` `team_remove(p, len)` | 팀 만들기·바꾸기(`{"color","friendly_fire"}`) / 없애기 — `plugin_api/teams.rs` |
| `team_join(p, len) -> i32` `team_leave()` `team_of(p, cap) -> len` | 그 플레이어의 팀 |
| `team_members(np, nl, p, cap) -> len` `teams(p, cap) -> len` | 팀의 사람들, 팀들 (줄마다 하나) |

이벤트의 그 사람이 아닌 플레이어(`player`, `player_named`로 고른)에게 한 `give` `gold` `energy` `heal` `teleport` `damage` ... 는
그 사람이 있는 월드의 다음 스텝에 그 사람의 몫에 됩니다(서버의 `srv.op` 대기열).

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
| `server_data_put` `server_data_get` `server_data_del` `server_data_keys` | 서버 하나의 바이트 (같은 모양; 어느 월드에서나 같은 것, 넣는 즉시 저장) |
| `save_now()` | 월드를 지금 저장 |
| `set_live_saving(on: i32)` | 실시간 저장 |
| `set_quit_warning(p, len)` | 나가기 경고 |
| `create_world(p, len) -> i32` | 플러그인의 월드 하나 (1 / 0: 쓸 수 없는 이름; id만이면 서버의 생성기 `level-type`); id 대신 JSON `{"id", "generator": "vanilla" \| "flat" \| "void" \| "map" \| "<플러그인>:<이름>", ...그 생성기의 옵션}`(농장의 `"town": false`, 맵의 `"glb"` `"collision"` `"spawn": [x, y, z, yaw 도]`); `"template"`: 그 월드의 복사 |
| `set_spawn(x: f64, y: f64, z: f64, yaw: f64)` | 월드의 스폰 (yaw 도; SDK `World::set_spawn`은 라디안을 받아 바꿔 넘김) |
| `set_rule(kp, kl, jp, jl) -> i32` `clear_rules()` | 이 월드의 규칙 패치 (키, JSON 값; 1 / 0: JSON이 아니거나 월드마다 둘 수 없는 키) |
| `set_clock_rate(f: f64)` | 이 월드의 시계 배율 (0 멈춤, 음수 규칙대로) |
| `set_inventory_group(p, len)` | 이 월드의 가방 그룹 (`""` 서버의) |
| `set_mode(p, len) -> i32` | `"none"` / `"vanilla"` (server.properties `game-module`과 같은 이름; 1 / 0: 그런 모드 없음) |
| `set_action_rate(rate: f64, burst: f64)` | 이 월드의 행동 한도 (음수: 서버의 것) |
| `world_hud(p, len, hidden: i32)` | 이 월드 모두의 HUD 부분 숨김 / 보임 |
| `world_view(flags: i32, fog: f64, sight: f64)` | 이 월드를 그리는 법: `flags` 비트 1 곡률, 비트 2 가림 컬링(occlusion); 음수면 server.properties의 것 (SDK `World::set_view(&View)`) |
| `set_sync(p, len)` | JSON `{"tiers": [[m, ms], ...], "chat": m, "full": n, "send": 초당}` (`{}` 서버의 것으로) |
| `world_list(p, cap) -> i32` | 만들었거나 읽은 월드마다 `id	players	loaded
` |
| `remove_world(ip, il, tp, tl) -> i32` `reset_world(...)` | 이 플러그인이 만든 월드를 지움 / 다시 만듦, 안의 사람은 먼저 `to`로 (1 / 0: 쓸 수 없는 이름) |
| `player_reset()` | 이벤트의 플레이어 몫을 새 손으로 |
| `set_vanilla(p, len, on: i32)` | 게임의 기능 하나 켜고 끄기 (`villagers` `night` `farming` `wild` `tutorial` `shops` `sleep` `mining` `dungeon` `balloon` `quests` `mail` `love` `festivals` `furniture` `fishing` `crafting` `energy` `fall` `day_end`; 모르는 이름은 서버 로그에 한 줄) |
| `vanilla_on(p, len) -> i32` | 그 기능이 켜졌는지 (1 / 0, -1 그런 기능 없음) |
| `set_day_end_time(m: i64)` | 월드의 하루 끝 시각 (자정부터 분; 음수: 규칙 값) |
| `has_permission(p, len) -> i32` `set_permission(p, len, v: i32)` | 그 플레이어의 권한 (v: 1 줌, 0 막음, -1 기본값으로) |
| `is_op() -> i32` `set_op(on: i32)` | 운영자인지, 운영자로 / 빼기 |
| `kick(p, len)` `ban(p, len)` | 이유를 띄우고 내보내기 / 차단(서버의 차단 목록)하고 내보내기 |
| `whitelist_set(on)` `whitelist_on() -> i32` `whitelist_add(p, len)` `whitelist_remove(p, len)` `whitelisted(p, len) -> i32` `whitelist(p, cap) -> i32` | 허용 목록 (목록은 줄바꿈으로) |
| `ban_name(np, nl, p, len)` `unban(np, nl)` `is_banned(np, nl) -> i32` `bans(p, cap) -> i32` | 이름으로 차단·풀기 (이벤트가 끝난 뒤), 차단됐는지, `이름\t이유\t때\n`마다 |
| `server_info(p, cap) -> i32` `set_motd(p, len)` `set_max_players(n: i64)` | `motd\tmax\tversion`; 소개 (`""` 파일의 것), 한도 (0 없음, 음수 파일의 것) |
| `char_state(p, cap) -> i32` `char_can_see(p, len) -> i32` | `scale\tjump\tgravity\tinvisible\tnametag_visible\tfrozen\tspectator\thand_visible\tnametag\tcolour`; 그 사람을 보는지 |
| `player_info(p, cap) -> i32` | `lang\tdevice\tping\tdoing\ton_ground\tvx\tvy\tvz\twalk\tmode\tdeclined` (declined는 줄바꿈으로) |
| `transfer(tp, tl, dp, dl)` `transfer_all(tp, tl)` | 그 플레이어를 / 모두를 다른 서버 `tp`로 (데이터 `dp`, 4096바이트까지; 넘으면 보내지 않음) |
| `world_id(p, cap) -> i32` | 이벤트의 월드 (`"world"` 모두의 것), 길이 |

## 접속하지 않은 플레이어

그 사람의 마지막으로 저장된 게임, 읽기만. 이벤트 한 번에 디스크에서 32명까지.

| 함수 | |
|---|---|
| `offline_names(p, cap) -> i64` | 들어온 적 있는 모두, 줄바꿈으로 |
| `offline_has(np, nl) -> i32` | 저장된 게임이 있으면 1 |
| `offline_num(np, nl, kp, kl) -> f64` | `gold` `day` `energy` `seen` `level.<스킬>` `xp.<스킬>` `friendship.<주민>` `item.<id>`, 이 플러그인의 `w.<키>` `p.<키>` |
| `offline_data(np, nl, kp, kl, p, cap) -> i64` | 이 플러그인이 그 사람 월드에 맡긴 바이트 (−1 없음) |
| `offline_player_data(np, nl, kp, kl, p, cap) -> i64` | 그 사람 월드에서 그 사람에게 맡긴 바이트 |
| `offline_text(np, nl, kp, kl, p, cap) -> i64` | `id`(이름의 해시, 저장된 게임 없이도), `world`(마지막으로 나간 월드) |

`offline_num`의 키에는 `first`(처음 들어온 때 ms), `x` `y` `z`(마지막으로 나간 곳)도.

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
| `ent_get(id, k, kl) -> f64` `ent_set(id, k, kl, v)` | `x` `y` `z` `yaw` `pitch` `roll` `scale` (`get`은 `alive` `hp` `max_hp`도); `glide`(초)를 먼저 쓰고 `x` `y` `z`를 쓰면 그만큼에 걸쳐 그려지며 감 (SDK의 `glide_to`) |
| `ent_var(id, k, kl) -> f64` `ent_set_var(id, k, kl, v: f64)` | 엔티티에 이 플러그인이 남기는 숫자 (SDK `Store for ModelEntity`): NaN 없음 / NaN을 쓰면 지움. 게임에 안 감, 엔티티와 함께 사라짐, 엔티티에 64개, 키 32바이트 |
| `ent_anim(id, p, len)` `ent_remove(id)` | 클립 (아바타: 동작, 부를 때마다 한 번; SDK `Entity::play_clip`) |
| `ent_look(id, p, len)` `ent_held(id, p, len)` | 아바타(`ent_spawn("avatar", …)`)의 CatLook JSON, 손에 든 아이템 id |
| `ent_name(id, p, len)` | 아바타 머리 위 이름 (`""` 없음) |
| `ent_text(id, kp, kl, p, cap) -> i32` | `model` `anim` `held` `name` |
| `ent_count() -> i64` `ent_at(i) -> i64` | 이 플러그인의 엔티티 |
| `ent_solid(id, on: i32)` | 단단하게 (충돌층에; 히트박스가 없으면 모델 크기, 아니면 한 칸 두 블록) |
| `ent_hitbox(id, p, len)` | 히트박스 JSON `[[x, z, w, d, y, h], …]` ([히트박스](world#히트박스와-충돌)) |
| `npc_count() -> i64` `npc_id(i, p, cap) -> i32` | 주민 목록 |
| `npc_get(ip, il, kp, kl) -> f64` | `x` `z` `moving` `hidden` `indoors` |
| `npc_goto(ip, il, x, z, hold: f64)` `npc_say(ip, il, tp, tl)` | 보내기, 한마디 |
| `npc_spawn(p, len) -> i32` `npc_set(ip, il, p, len)` `npc_remove(ip, il)` | 더하기 (1/0), 바꾸기, 빼기 |
| `mob_set(n, k, kl, v)` `mob_attack(n, damage, reach: f64)` | 몬스터 값, 공격 |
| `mob_get(n, k, kl) -> f64` `mob_kind(n, p, cap) -> i32` | 어느 이벤트에서나 그 번호의 몬스터(이벤트의 층): `x` `z` `hp` `max_hp` `tier` `speed` `damage` `size` `t`, NaN 없음 / 종류 id (`""` 없음) |
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
| `set_block_rules(p, len)` | 이 월드의 바닐라 블록 규칙 (JSON; `{}` 서버의 것으로) |
| `block_data(x, y, z: i64, kp, kl, p, cap) -> i32` | 블록 데이터의 키 하나 ("" 없음) |
| `set_block_data(x, y, z: i64, kp, kl, vp, vl)` | ("" 지움) |
| `show_block(x, y, z: i64, b: i32)` `clear_fake_blocks()` | 그 플레이어의 게임에만 보이는 블록, 거두기 |
| `fill(x0, y0, z0, x1, y1, z1: i64, b: i32)` | 양 끝 포함, 한 번에 청크 넷까지 |
| `props_clear()` | `chunk.generate`: 그 청크의 덤불·풀·유목 치우기 |
| `chunk_put(p, len, op, ol)` | 생성기의 청크 하나 통째로 (`"gen:<이름>"` 이벤트에서만; SDK `#[generator]`의 `run_generator`): `p`는 기둥 32 × 32개 × 높이 64바이트(블록 번호, y는 `Block::LOWEST`부터; 기둥 (lx, lz)는 `(lz * 32 + lx) * 64`에서), `op`는 청크 밖에 놓은 큰 블록들(13바이트씩: x, y, z `i32` 리틀 엔디언, 블록 번호)로 이 청크에 들어오는 부품이 놓임 ([생성기](world#플러그인의-월드-생성기)) |
| `set_blocks(p, len)` | 블록 여럿을 한 번에: 블록마다 `i32` x, y, z, 번호 (리틀 엔디언, 16바이트), 65 536개까지. `chunk.generate` / `chunk.load`에서는 그 청크의 것만 |
| `chunk_mark(x, z: i64, p, len) -> i64` | 청크 (x, z)에 이 플러그인이 남긴 숫자 `name` (0 없음; 월드와 함께 저장) |
| `chunk_set_mark(x, z: i64, p, len, v: i64)` | 그 숫자 정하기 |
| `structure_count() -> i64` `structure_id(i) -> i64` | 구조물 목록 |
| `structure_get(id, k, kl) -> f64` | `x` `z` `y` `yaw`(도) `w` `d` `scale` (SDK는 타입 있는 `Structure` 메서드, yaw 라디안) |
| `structure_text(id, k, kl, p, cap) -> i32` | `k` `m` `plot` `n` `key` `kind` `label` `text` `s` `owner` |
| `structure_put(p, len) -> i64` | 세우기: `{"k", "m", "x", "z", "y", "yaw"(도), "scale", "plot", "cells": [x, z, w, d], "hit": [[..]]}` (id, 0 실패; `"hit"`: 히트박스, 누군가의 몸에 걸리면 놓이지 않음; SDK `&Placement`) |
| `solid_at(x, y, z: f64) -> i32` | 그 칸이 단단한가 (블록이나 충돌층의 상자: 1/0) |
| `raycast(x, y, z, dx, dy, dz, most: f64) -> f64` | 광선이 처음 닿는 단단한 칸까지 m (−1 없음, 256 m까지; SDK `World::cast_blocks`) |
| `structure_remove(id)` `structure_remove_plot(p, len)` `structure_move(id, x, z, yaw: f64)` | 치우기, 구획 통째로, 옮기기 (yaw 도; NaN은 그대로) |
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
| `send_fast(cp, cl, p, len)` `send_fast_all(cp, cl, p, len)` | 게임 쪽 코드에 빠른 패킷 (그 플레이어 / 모두): 데이터그램, 1000바이트까지 |
| `send_png(cp, cl, w, h: i32, p, len, all: i32) -> i32` | RGBA8 픽셀(`w` × `h`, 512까지)을 PNG로 채널에 (`all` 0이 아니면 모두에게). PNG의 바이트 수, `len`이 `w × h × 4`가 아니면 0 |
| `path_blocks(x0, y0, z0, x1, y1, z1: f64, max, p, cap: i32) -> i32` | 블록 위 길(`World::path_blocks`): `[[x, 발 높이, z], …]` JSON, 없으면 `[]`. 전체 바이트 수 |
| `columns(x0, z0, w, d: i64, p, cap) -> i64` | 위에서 본 땅: 기둥마다 2바이트(가장 높은 단단한 블록 번호(위에 물이면 물), 높이 − (−8)), `w`개씩 줄로, 256 × 256까지. 전체 바이트 수 |
| `inv_open(p, len)` | 인벤토리 창 `{"id", "title", "rows", "cols", "slots", "bag"}` / 닫기 `{"id", "close": true}` |

게임에서 오는 것은 이벤트로: `packet`(`text("channel")` `text("data")`), `fast`(게임 쪽 코드의 빠른 패킷: 같은 키), `inventory`(`text("inv")` `text("side")` `n()` 칸
`text("click")` `text("bag_item")`).

## 플러그인끼리

[플러그인끼리](interop)의 원본. 부를 수 있는 함수는 커스텀 섹션 `gh`의 `export\t<이름>\t<내보내기>\n` 줄로 알리고, 그 내보내기는
`() -> i32`(0 성공, 아니면 실패)입니다. 인자와 결과는 바이트이며 SDK는 리틀 엔디언 숫자, 길이(u32)가 앞에 붙은 글자·목록으로 씁니다.

| 함수 | |
|---|---|
| `call_find(pp, pl, fp, fl) -> i64` | 플러그인(또는 `provides`의 서비스) `pp`의 함수 `fp`: 번호, 없으면 `-1` |
| `call(handle: i64, ap, al) -> i32` | 그 함수를 인자 바이트(64 KB까지)로 부름: 결과의 길이, 또는 `-1` 없음·`Enable` 중, `-2` 불린 쪽 예산 없음, `-3` 실패, `-4` 되돌아 부름·사슬 4개 넘음 |
| `call_result(p, cap) -> i32` | 마지막 `call`의 결과 바이트 |
| `call_args(p, cap) -> i32` | (불린 쪽) 받은 인자 바이트 |
| `call_return(p, len)` | (불린 쪽) 돌려줄 결과 바이트, 64 KB까지 |
| `call_caller(p, cap) -> i32` | (불린 쪽) 부른 플러그인의 이름 (`""` 이벤트로 불림) |
| `fire_event(np, nl, dp, dl) -> i32` | 이 플러그인의 이벤트 `np`(64바이트까지)를 데이터 `dp`와 함께 다른 플러그인들에게: `1` 누가 취소함, `0` 아님, `-1` 이름이 없음·`Enable` 중, `-4` 사슬 4개 넘음. 듣는 쪽은 커스텀 섹션의 `on\tcustom:<이름>\t<우선순위>\t<내보내기>\n` 줄 (이벤트 `id()`는 그 이름, `text("data")`, `text("from")`) |
| `budget_left() -> f64` | 이 플러그인의 CPU 몫이 남은 정도 0-1 |
| `log(level, p, len)` | 로그 한 줄 (`0` 디버그 `1` 정보 `2` 경고 `3` 오류): 서버 출력과 서버 관리 › 콘솔, 1초에 20줄 |
| `run_command(p, len)` | 이벤트의 플레이어가 그 줄("/이름 인자")을 친 것처럼 (그 사람의 권한, 그 월드의 다음 스텝) |
| `server_command(p, len)` | 콘솔이 친 것처럼 (모든 권한, `text("console")`이 "1") |
| `perm_list(p, cap) -> i32` | 플레이어의 권한 `"이름\t<있음>\t<정해 줌>\n"`…, 각각 1 또는 0 |
| `tick_ms() -> f64` | 월드 한 스텝의 요즘 시간 (ms) |

## 이벤트 말고 내보내는 것

`reel(tick: i64, fish_y: f64, level: f64, roll: f64) -> f64` — 낚시 물고기의 길 ([낚시의 손맛](rules#낚시의-손맛)).

## 게임 쪽 (`"ghc"`)

[게임 쪽 코드](client)(`client.wasm`)가 가져다 쓸 수 있는 것은 모듈 `"ghc"`의 여섯 함수뿐입니다(`greenhaven_client::sys`). 게임은
이것 말고는 아무것도 연결하지 않고, 다른 것을 가져다 쓰는 모듈은 로드하지 않습니다. 글을 넘기고 받는 약속은 [위](#약속)와 같습니다.
상태를 바꾸는 함수는 없습니다: 모두 이번 호출에 게임이 알려 준 것을 읽거나, 게임이 그릴 작업을 남깁니다.

| 함수 | |
|---|---|
| `num(k, kl) -> f64` | 게임이 알려 준 숫자 (`fast` `dt` `time` `me.x` `me.y` `me.z` `me.yaw` `me.vx` `me.vy` `me.vz` `me.ground` `cam.x` `cam.y` `cam.z` `cam.yaw` `cam.pitch` `cam.fx` `cam.fy` `cam.fz` `screen.w` `screen.h` `mouse.x` `mouse.y` `minute` `day` `pressed` `held.<키>` `balloon`(열기구: 0 땅, 1 오르는 중, 2 하늘, 3 내려오는 중) `world.ready`, 입력의 `mouse.dx` `mouse.dy` `wheel` `move.x` `move.y` `look.x` `look.y`, `step` `step.dt`; 없으면 NaN) |
| `text(k, kl, p, cap) -> i32` | 게임이 알려 준 글 (`me` `server` `world`(지금 있는 월드) `channel` `data` `key` `on` `action` `input.device`) |
| `send(cp, cl, dp, dl)` | 서버 쪽에 채널 `cp`로 패킷 (서버의 `packet` 이벤트; 플러그인 하나가 1초에 8개까지) |
| `op(kp, kl, jp, jl)` | 게임이 할 작업 하나: 종류 `kp`(`hud` `camera` `screen` `fx` `log` `local` `entity` `me` `input` `fast` `sound` `draw` `material` `mesh` `target`, 입력의 `bind`, 조준의 `aim`(`kick` `attach` `detach` `beam`), 연출의 `light` `highlight` `particles` `trail`, 그리고 게임 모듈의 것)와 그 JSON `jp` (호출 한 번에 256개, 하나 64 KB까지, `mesh`는 4 MB까지). `fast`는 빠른 패킷 `[채널, 데이터]`. 게임 모듈의 종류는 엔진의 고정 목록에 없고 게임이 알려 준 것만 받습니다(`allow_module`): 농장의 `balloon` `{"do": "up"}` 이륙 / `{"do": "down"}` 착륙. `target`은 월드에 그려진 것 하나를 이 게임에서만: `{"target": "me" \| "player:<id>" \| "local:<id>" \| "entity:<id>" \| 게임 모듈의 "종류:번호"(농장의 몬스터 "mob:<번호>"), "do": ...}`, `"clip"`(`clip`("" 멈춤) `speed` `blend` `upper` `loop`), `"material"`(`material`: 재질 id, "" 제 것), `"fade"`(`alpha` `secs` `free`), `"remove"`(Local 것, 게임 모듈이 맡긴 것만). `entity`는 `{"id", "drive": [x, y, z, yaw, pitch, roll] \| null}`(예측과 놓기)만 |
| `query(kp, kl, jp, jl, p, cap) -> i32` | 엔진에 묻기: `raycast` `[x0,y0,z0,x1,y1,z1]`, `ground` `[x,z]` → 답의 JSON; 이 게임에 온 것 읽기: `players` `[]` → `[id,x,y,z,yaw,doing,…]`, `player` `[id]` → 이름, `entities` `[]` → `[id,x,y,z,yaw,…]`, `entity` `[id]` → 모델, `public` `["p"\|"e", id, key]` → 값; 조준: `cast` `[x,y,z,dx,dy,dz,len]` → `[kind,id,x,y,z,nx,ny,nz,거리]`(kind 0 블록, 1 상자, 2 플레이어, 3 엔티티), `overlap` `[x0,y0,z0,x1,y1,z1]` → `[kind,id,…]`, `screen_ray` `[px,py]` → `[x,y,z,dx,dy,dz]`, `to_screen` `[x,y,z]` → `[sx,sy]`; 게임 모듈의 질의(게임이 알려 준 것만, `allow_module`): 농장의 `path` `[x0,z0,x1,z1]` → `[x,z,…]`, `mobs` `[r]` → `[n,x,y,z,hp,…]`, `mob` `[n]` → 종류 |
| `local_id() -> i64` | 자기에게만 보이는 물체(`Local`)에 줄 새 id |

내보내는 것: `ghc_load` `ghc_frame` `ghc_packet` `ghc_input` `ghc_click` `ghc_action` `ghc_step` `ghc_public` `ghc_module` (`() -> i32`, 있는 것만; SDK의 `client!`가 만듦). `ghc_module`은 게임 모듈의 이벤트: `text("module.kind")` 이름(농장의 `"v.mob_death"`), 그 값은 `num("module.<키>")` / `text("module.<키>")`(`v.mob_death`: `n` `x` `y` `z`, 글 `id`). 대상 키(`Highlight` `Trail` `Particles`의 `on`)에는 `me` `local:<id>` `entity:<id>` `player:<id>`와 게임 모듈의 `<종류>:<번호>`(농장의 `mob:<번호>`).

## 상태 효과, 타이머, 쿨다운 (`plugin_api/effects.rs`)

| 함수 | |
|---|---|
| `effect_add(name, len, secs: f64, strength: f64, icon, len) -> i32` | 1 / 0 (이름 1~32자, 아이콘 `""` 또는 `res://`, 한 사람 16개) |
| `effect_remove(name, len)`, `effect_left(name, len) -> f64`, `effects(ptr, cap) -> i32` | `"이름\t초\t세기\n"` |
| `timer_start(tag, len, secs: f64, every: i32) -> i32`, `timer_cancel(tag, len)` | `timer` 이벤트, `text("tag")`; 플러그인마다 64개 |
| `cooldown(key, len, secs: f64) -> i32`, `cooldown_left(key, len) -> f64` | 1 준비됨(지금부터 식음) / 0 |

## 한 사람의 화면, 장비, 월드 읽기

| 함수 | |
|---|---|
| `title_with(t, tl, s, sl, in: f64, stay: f64, out: f64)`, `action_bar(p, len)` | 그 사람의 화면 (`ui.title`, `ui.bar`; SDK `Player`의 `Audience::title_with(&Title)` / `action_bar`) |
| `sound_to(name, len, x, y, z)`, `particle_to(...)` | 그 사람만 (`ui.fx`; SDK `Player`의 `Audience::sound` / `particle`) |
| `set_energy(n: f64)` | |
| `equip_list(ptr, cap) -> i32`, `equip_set(slot, len, id, len)` | `"칸\t아이템\n"` (`""` 빔) |
| `world_weather(ptr, cap) -> i32`, `world_spawn(i) -> f64` | 0 x 1 y 2 z 3 yaw, NaN 없음 |
| `mob_list(ptr, cap) -> i32` | `"번호\tx\tz\n"` |
| `set_minute(m: i64)`, `loot_set(json, len)` | `loot` 이벤트에서 `[[id, n], …]` |

팀의 `team_set` JSON은 `prefix` `suffix` `nametag` `collide`도 받습니다.

HUD의 새 연산(`tween` `pin_to` `sweep` `push` `float` `board`)은 새 함수 없이 `hud` / `hud_all`의 JSON입니다(`sdk/common` `ops`).

