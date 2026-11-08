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

이벤트의 플레이어 (`e.player()`). `Tick::players()`, `Server::player(이름)`, `World::players()`가 주는 것은 그 사람.

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
| `teleport(x, z)` | 옮기기 (서버의 이동 판정도 그 자리를 받아들임; `PlayerTeleport`가 먼저) |
| `teleport_to(x, y, z, yaw)` | 3D로 옮기기 (`y` NaN: 그 자리의 땅 위, `yaw` NaN: 바라보던 대로; 라디안, 게임의 것) |
| `y()` `yaw()` | 발의 높이, 바라보는 방향(라디안) — 그 게임이 마지막으로 알린 것 (pitch는 서버가 모름) |
| `damage(amount, cause, by)` | 피해 (`cause` "": 플러그인 이름, `by` `Some(&친 사람)`): `PlayerDamage` 뒤 보호구가 몫을 덜고, 체력이 다하면 쓰러짐(`PlayerDeath`의 `killer()`). 방 안에서도 |
| `set_health(n)` `set_max_health(n)` | 체력을 n으로 (0으로 쓰러지지는 않음: `damage`로) / 그 사람의 최대 체력 (저장됨; 0: 규칙의 `max_health`) |
| `team()` `join_team(team)` `leave_team()` | 이 월드에서의 팀 ([피해, 체력, PvP, 팀](#피해-체력-pvp-팀)) |
| `set_time(minute)` | 그 사람이 있는 월드의 시각 (6:00 = 360 ~ 2:00 = 1560; 날짜는 그대로), 그 월드의 게임에 바로 알림 |
| `set_walk_speed(times)` | 걸음 빠르기 배수 (1이 원래). 게임의 걸음과 서버의 이동 판정이 함께 바뀜. 바꿀 때까지 유지 |
| `inventory()` → [`PlayerInventory`](#playerinventory) | 그 사람의 가방 (Bukkit의 getInventory) |
| `gear(id)` → `Option<`[`Gear`](#gear)`>` | 그 사람의 도구·장비 하나의 등급과 마법 (가방에 없으면 `None`) |
| `mount_seat(&entity, seat, speed, (x, y, z))` | 자리 `seat`에 태움: 0 운전석(`mount`처럼), 나머지 승객(엔티티 가운데에서 오른쪽·위·앞 m에 실려 감, 걸음은 판정하지 않고 탈것 근처인지만) ([탈것](moving#탈것)) |
| `mount(&entity, speed, seat)` | 이 플러그인의 엔티티에 태움: 모든 게임이 그 엔티티를 탄 사람 아래에 그리고 `seat` m 위에 앉힘, 걸음은 `speed`배로 판정. 그 사람이 한 일의 이벤트에서만 (`EntityInteract`, 명령어, 버튼, `Packet`); 저장되지 않음 ([탈것](moving#탈것)) |
| `push(vx, vy, vz)` | 밀기(넉백, 점프대, 돌진; m/s, 칸 기준, 축마다 30까지): 그 사람의 게임이 속도로 받고 서버의 걸음 검사가 그만큼만 봐줌 ([밀기](moving#밀기)) |
| `dismount()` | 내림: 엔티티는 그 자리에, 걸음은 전과 같이 |
| `set_check(check, on)` | 서버의 이동 검사 하나를 이 사람에게만 끄고 켬: `"speed"` `"walls"` `"air"` `"teleport"` `"reach"`. 끄면 플러그인이 `PlayerMove`에서 대신 검사해야 함. 저장되지 않음 (`Join`에서 다시). 모두에게는 `Registry::set("checks.air", "false")` ([이동 방식 만들기](moving#서버의-이동-검사)) |
| `death(hold)` | 쓰러뜨림 (`PlayerDeath`도 불림). `false`: 게임 규칙대로 진료소에서 바로 일어남. `true`: `respawn`까지 쓰러진 채 대기, 아침이 지나도 그대로. 다른 사람의 잠은 이 사람을 기다리지 않지만, 쓰러진 사람만으로 하루가 끝나지는 않음 |
| `respawn()` | 쓰러진 채 대기 중인 사람을 진료소에서 일으킴 (체력 가득) |
| `set_model(id)` `clear_model()` | [커스텀 모델](models)로 그림 / 원래 모습으로. 연결된 동안만, 계정은 그대로 |
| `set_invisible(on)` | 아무에게도 안 보임: 위치·목소리·손에 든 것·모습·번호가 **어떤 게임에도 가지 않음**(보내지 않기; 자기 게임 빼고). 채팅은 그대로(`Chat`을 취소) |
| `hide_from(other, on)` | `other`(이름) 한 사람에게만 숨김 (술래가 기다리는 동안). 변장의 엔티티도 그 사람에게는 가지 않음 |
| `set_view_group(name)` | 보기 그룹 (`""` 없음: 그룹 없는 사람끼리가 한 그룹). 그룹이 다른 사람끼리는 위치·모습·음성·주변 채팅·팀 채팅·손에 든 것·탈것·변장 엔티티가 오가지 않고, 쏘기·발사체·폭발·`overlap`·`seen_from`도 그 이벤트의 플레이어 그룹만 맞힘. 몬스터·주민은 모두를 봄(주민의 말 중 다른 그룹 사람을 부르는 줄은 그 그룹에게만). 한 번 부르면 되고 인원 한도 없음 (채널: 예제 `channels`). 세션마다 처음엔 없음 |
| `disguise(Disguise::Block(kind) \| Disguise::Model(path), snap)` → `Option<ModelEntity>` | 변장: 투명이 되고 이 플러그인의 엔티티(`"block:<kind>"` 블록 모습, 또는 모델)가 걷는 대로 따라감(`snap`: 칸 가운데). 다른 엔티티와 구별할 수 없음(그 사람과 이어진 필드 없음); 자기 게임에서만 반투명. `set_interact`로 맞힐 수 있게 |
| `undisguise()` | 원래대로 (엔티티 지움; 나가거나 월드를 옮겨도) |
| `set_nametag(text, colour)` `set_nametag_visible(on)` | 머리 위 이름 (`""` 이름 그대로; 색 `"ff3030"`, `""` 게임 색), 보이기 |
| `set_scale(times)` | 모든 게임에서 그 크기로 (0.25-4) |
| `play_clip(clip, upper, looped)` `play_clip_at(clip, upper, looped, speed)` `stop_clip()` | 걷고 뛰는 몸 위에 겹치는 클립 (장전, 조준, 시전, 달리며 손 흔들기): `upper`면 척추부터 위만 (다리는 걷기 그대로), 아니면 몸 전체; `looped`면 멈출 때까지, 아니면 한 번; 빠르기 0.1-4. 클립: [감정 표현](models) id, `res://` 경로 (팩의 GLB는 `"경로#클립"`), 게임의 것 (`"ATK1"` `"Shoot"` `"Victory"` `"Greet"` `"cast"`). 모든 게임에서 보임. 도구 동작·감정 표현 중에는 그 아래에서 기다림 |
| `set_body(half_width, tall)` | 몸의 크기 (m; 0, 0이면 게임의 것): 게임의 캡슐이 그 크기로 움직이고 **서버의 걸음 판정도 그 몸으로** (키는 블록 단위, 1 m 넘게 넓으면 세 칸 폭). **맞는 상자도 그 크기** (정한 쪽만; 나머지는 0.4 × 1.6 m × `set_scale`): 서버의 cast·cast_for·overlap·explode·발사체, 게임 쪽 조준(AimHitbox)도. 숨바꼭질의 소품, 작은 동물 |
| `set_jump_power(times)` `set_gravity(times)` | 점프 높이 배수 (0-10), 중력 배수 (0.1-5): 게임이 그렇게 움직이고 **서버의 공중 검사도 그 배율로** 판정 |
| `freeze(on)` | 제자리 (게임의 걷기·점프 꺼짐, 걸음은 서버가 되돌림): 카운트다운 |
| `set_hand_visible(on)` | `false`: 손에 든 것을 안 그림 (자기 게임에서도, 남이 보는 아바타에서도: 서버가 모델을 전하지 않음). 게임 쪽 뷰모델과 함께; `hud().hide("hotbar")`면 숫자 키·휠도 칸을 안 바꿈 |
| `set_spectator(on)` | 관전자: 아무에게도 안 보이고, 모든 것을 뚫고 날며(서버의 공중·벽 검사 꺼짐), 구경꾼처럼만 행동(도구·농사 없음), 몬스터도 안 따라옴 |
| `set_public(key, value)` | 월드의 모든 게임이 읽는 값 (게임 쪽 [`Players::get(id).public(key)`](client#세상-읽기)): 숫자, 글(64자), `Public::None`(지움); 32키, 키 24자. 공개이니 비밀은 넣지 말 것. 연결된 동안만 |
| `play_anim(id)` `stop_anim()` | [감정 표현](models) 재생 / 끝내기. 가만히 서 있을 때만, 움직이거나 행동하면 끝남 |
| `show_block(x, y, z, b)` `clear_fake_blocks()` | 그 사람의 게임에만 보이는 [가짜 블록](world#가짜-블록), 모두 거두기 |
| `say(line)` | 머리 위의 한마디 |
| `message(line)` | 채팅 한 줄 |
| `title(line)` | 화면 가운데 큰 제목 |
| `where_text(line)` | 화면의 장소 문구 (`""`: 게임의 것) |
| `open_shop(shop)` | 가게 열기 (`VillagerData.SHOPS`의 id) |
| `play_music(track)` | 지금 곡 틀기 (`Music.TRACKS`의 id나 `res://….ogg`; `""`: 원래 목록으로) |
| `reset()` | 지금 가방 그룹의 몫(가방·돈·기력·체력·스킬)을 이 월드 규칙의 새 손으로 (그 월드의 `starter`: 경기마다 새 장비); 있는 곳은 그대로 |
| `move_world(world, by_station)` | 서버의 다른 월드로 옮김 (`world`: [`Server::create_world`](#server)로 만든 id, `""` 모두의 월드). `by_station`이면 그 월드의 열기구 정거장으로, 아니면 농장 집 앞으로. 떠난 월드에서 `Leave`, 간 월드에서 `Join`; 가방·돈·스킬은 그대로 따라감 |
| `has_permission(perm)` → `bool` | 권한이 있는지 (준 것·막은 것, 없으면 plugin.json `permissions`의 `default`; 선언하지 않은 권한은 운영자만) ([권한](server#권한과-운영자)) |
| `set_permission(perm, on)` `unset_permission(perm)` | 권한 주기·막기 / 기본값으로 (서버의 `permissions.json`에 저장; `"*"` 모든 권한) |
| `is_op()` `set_op(on)` | 서버의 운영자 (`ops.json`) |
| `kick(reason)` `ban(reason)` | 내보내기 / 차단하고 내보내기 (`/unban 이름`, `Server::unban`으로 풀기) |
| `doing()` `on_ground()` `velocity()` | 게임이 알리는 하는 일(`idle` `walk` `run` `asleep` `tool` `swim` `jump` `fall` `bite` `reel`; 바뀌면 [`PlayerPose`](events#playerpose)), 발이 땅에, 속도(칸/초, 마지막으로 검사한 걸음 둘 사이) — 어느 이벤트에서나 |
| `walk_speed()` `move_mode()` `packs_declined()` `id()` | `set_walk_speed`의 배, 게임 쪽이 알린 이동 방식, 받지 않은 선택 팩, 어느 서버에서나 같은 id |
| `scale()` `jump_power()` `gravity()` `is_invisible()` `is_nametag_visible()` `is_frozen()` `is_spectator()` `is_hand_visible()` `nametag()` | 플러그인이 마지막으로 정한 값 다시 읽기 (이벤트에서 바꾼 것은 다음 이벤트부터) |
| `can_see(name)` → `bool` | 그 사람을 보는지 (접속해 있고 투명·관전·변장이 아니며 이 사람에게서 숨지 않음) |
| `transfer(to, data)` | 다른 서버로 (`host:port`나 `GS-` 아이디, 데이터 4 KB까지; `Server::transfer_all(to)`는 모두). [다른 서버로](server#다른-서버로) |
| `show(&Gui)` | 창 띄우기 ([`Gui`](#gui)). `PlayerLogin`에서는 들어오기 전의 입력 창 |
| `hud()` → `Hud` | 그 사람의 화면: HUD 요소, 게임 HUD 숨기기, 키, 채널 ([화면](screen)) |
| `open_inventory(&Inventory)` / `close_inventory(id)` | 이 플러그인의 인벤토리 창 열기(다시 부르면 지금 칸으로) / 닫기 ([인벤토리 창](screen#인벤토리-창)) |
| `get(k)` / `set(k, v)` | 그 사람에게 남기는 숫자 (이 플러그인의 것; 저장됨). plugin.json의 바가 보여 주는 값 |
| `data_put(key, &[u8])` → `bool` | 그 사람의 바이트 ([데이터 저장](#데이터-저장)) |
| `data_get(key)` → `Option<Vec<u8>>` | |
| `data_del(key)` | |

{: .note }
**아무 플레이어에게나** (Bukkit의 `Server#getPlayer`): 이벤트의 그 사람이 아닌 사람(`Tick::players()`, `Server::player`, `PlayerDamage::attacker()`,
남의 명령어 ...)에게 한 `give` `take` `add_gold` `add_energy` `heal` `add_xp` `add_friendship` `set_walk_speed` `teleport` `teleport_to` `damage`
`set_health` `set_max_health` `set_check` `mount` `death` `respawn`은 그 사람이 있는 월드의 다음 스텝(1/5초 안)에 그 사람의 몫에 되고
그 게임에 알려집니다(`{"t":"own"}`). 어느 이벤트에서든: `Tick`, `ServerTick`, `Chat`, `FastPacket`, `PlayerMove` ...

{: .note }
그 사람 자신에게는: `give` `take` `add_gold` `add_energy`와 가방 바꾸기(`inventory()`의 `add` `remove` `clear`, `set_enchant`)는 플레이어가 한 일의 이벤트(행동, 명령어, 버튼, `Words`, `Use`, `Morning`, `PlayerDeath`, `LevelUp`, `MobDeath`, `BlockPlace` `BlockBreak` `Packet` `InventoryClick`)와 그 플레이어의 이벤트(`Join`, `Leave`, `Chat`, `PlayerMove`, `PlayerItemHeld`, `FastPacket`, `EntityDismount`)에서 그 사람의 가방·돈·기력에 됩니다 (Bukkit의 `PlayerJoinEvent#getPlayer().getInventory().addItem`처럼; 게임에도 바로 보임). `Leave`에서 준 것은 그날이 저장되는 서버(`save-mode=live`, `World::set_live_saving`)에서만 남습니다. `say` `drop_item` `fx` `prop`는 플레이어가 한 일의 이벤트에서만 됩니다. `Tick::players()`의 `Player`는 모아 두어도(`collect`) 저마다 그 사람이고, 남을 고른 뒤의 `e.player()`도 다시 이벤트의 그 사람입니다.

## 피해, 체력, PvP, 팀

`plugin_api/combat.rs`, `projectile.rs`, `teams.rs`; 예: `plugins/tag`(술래잡기), `plugins/blaster`(물총 놀이: 조준과 판정).

| | |
|---|---|
| `World::set_pvp(on)` `pvp()` | 플레이어의 휘두름이 플레이어를 침 (월드에 저장, 기본 꺼짐). 몬스터처럼 그 부채꼴(사거리 `night.reach`, 앞쪽, 위아래 2 m) 안의 사람마다 `PlayerDamage`(cause `"player"`, by 친 사람). 꺼져 있으면 낮에 몬스터 없는 휘두름은 거절 |
| `World::team(name, color, friendly_fire)` → `bool` | 팀 만들기·바꾸기 (`color` 이름표 색 `"#ff4040"`; 64개까지) |
| `World::remove_team(name)` `teams()` `team_members(name)` | |
| `Player::join_team(name)` → `bool` `leave_team()` `team()` | 한 팀에만; 같은 팀끼리는 `friendly_fire`일 때만 맞음 |
| `ModelEntity::set_health(hp, max)` `health()` | 엔티티의 체력: 휘두름이 맞히면 [`ModelEntityDamage`](events#modelentitydamage--modelentitydeath), 0이면 사라짐 |
| `World::cast(from, dir, len)` → `Option<Hit>` | 광선 판정: 블록(`HitKind::Block`), 충돌층의 상자(`Box`), 플레이어의 몸(`Player`, `who`; 폭 0.8 m, 발에서 1.6 m, 이벤트의 플레이어는 빼고), 체력 있거나 단단한 엔티티(`Entity`, `entity`) 가운데 처음 것, `at` `normal` `distance` (256 m까지) |
| `World::cast_for(&쏜 사람, from, dir, len)` → `Option<Hit>` | 그 사람의 한 발을 **그 사람이 본 그대로**: 다른 플레이어를 그 사람의 왕복 시간 + 100 ms(게임이 남을 그리는 지연)만큼 되돌려(최대 300 ms) 맞혀 봄. 움직이는 엔티티(체력 있거나 단단한 것)와 몬스터도 왕복 시간의 반 + 100 ms 전 자리로. 몬스터에 맞으면 `Hit::mob()` → `EnemyEntity`, `damage(양)`으로 피해(0이면 쓰러지고 드롭·경험치). 시작점이 서버가 아는 눈에서 0.5 m 넘게 멀면 눈에서; PvP 꺼짐·friendly_fire 없는 같은 팀은 지나침; 초당 20발까지(넘으면 `None`). 연사 속도·탄약·쿨다운은 플러그인이 `Player::set`으로 |
| `Player::eye()` → `Option<((x, y, z), yaw)>` `position_at(ms 전)` → `Option<(x, 발, z, yaw)>` | 쏘는 눈 (발 + 0.95 m), 그 사람이 있던 곳 (1초까지) |
| `World::overlap(center, r, mask)` `overlap_box(min, max, mask)` → `Vec<Found>` | 범위 안의 것(폭발, 범위 스킬): `PLAYERS`(몸 있는 모두: 이벤트의 그 사람과 숨은 사람도; PvP·팀은 플러그인이), `ENTITIES`(날아가는 것 빼고), `MOBS`(그 사람의 층의 몬스터)를 `\|`로. 가까운 것부터 256개까지, 반지름·반폭 64 m까지; `Found`의 `kind` `who` `entity` `at`(발) `distance`, `player()` `model_entity()` `mob()` |
| `World::projectile(모델, from, vel, gravity, radius, life)` → `Option<ModelEntity>` | 발사체: 서버가 스텝마다 움직이고 게임은 미끄러지듯 그림; 처음 닿는 블록·상자·플레이어(쏜 사람 빼고, PvP는 위와 같음)·엔티티에서 끝나고 [`ProjectileHit`](events#projectilehit); 한 월드에 64개 |
| `World::projectile_with(&Shot)` → `Option<ModelEntity>` | 튕기는 발사체: 세게(초속 1.5 m 이상) 닿으면 `bounces`번까지 `restitution`으로 튕기고([`EntityBump`](events#entityland--entitybump)), 땅에서는 세지 않고 굴러가다 `friction`으로 멈춤, `drag`로 줄어듦; 수명이 다하면 [`ProjectileExpire`](events#projectileexpire)(신관) |
| `ModelEntity::set_body(restitution, friction, drag)` | 떨어지는 엔티티가 땅·벽에서 튕기고 땅을 따라 미끄러짐; [`EntityLand`](events#entityland--entitybump), `EntityBump` |
| `World::explode(&Blast)` → `Vec<BlastHit>` | 폭발 한 번에(서버 엔진): `radius` 안에서 폭발 점이 보이는 것만(벽 뒤는 안전), `damage × (1 − 거리/radius)^falloff`(플레이어 `PlayerDamage` cause "explosion", 엔티티 `ModelEntityDamage`, 몬스터), `knock`으로 밀어냄(`Player::push`), `particle`, 그 뒤 [`Explosion`](events#explosion) |
| `World::seen_from(점, range)` → `Vec<Seen>` | 그 점을 보는 사람(눈과 점 사이에 블록·상자 없음, 128 m까지)과 바라보는 쪽에서 몇 도(0 정면): 섬광탄은 서버가 이걸로 정하고 게임 쪽은 그리기만 |
| `World::conveyor(id, min, max, vx, vz)` `watch_entities(id, on)` | 컨베이어 구역(중력 있는 엔티티, 땅의 아이템, 그 위의 사람을 실어 감), 엔티티가 들어오면 [`ZoneEntityEnter`](events#zoneentityenter) |
| `World::rand()` `rand_in(tag)` `rand_range(tag, lo, hi)` | 월드의 이 플러그인의 난수: 같은 월드는 같은 순서로 같은 수, 다시 켜도 이어짐 |
| `ModelEntity::set_gravity(g)` `set_velocity(vx, vy, vz)` `set_persistent(on)` | 블록·상자 위로 떨어짐(m/s²), 움직임(블록·상자·다른 단단한 엔티티에 옆으로도 부딪힘: 비스듬히 가면 벽을 따라 미끄러지고 정면이면 멈춤, 천장에서 멈춤, 내려앉으면 멈춤; 몸은 0.8 × 1.6 m에 `scale`배; 단단한 엔티티는 플레이어의 몸에서도 멈춤, 이미 몸 안이면 빠져나감), 월드와 함께 저장(다시 켜도 그 자리에) |
| `Server::player(name)` → `Option<Player>` | 서버 어디든 접속한 사람 (위치는 1초마다의 것) |
| `Server::players()` → `Vec<(이름, 월드)>` `worlds()` → `Vec<(월드, 사람 수)>` `broadcast(line)` | 접속한 사람들, 누가 있는 월드, 서버 모두의 채팅 |
| `World::players()` → `Vec<Player>` | 이 월드에 있는 사람들 |

게임은 팀을 `{"t":"teams","l":{팀: {"color","ff","members"}},"pvp"}`로(상태의 `teams` `pvp`도) 받습니다: `Net.teams`, `Net.team_of(name)`, `Net.pvp`.

## PlayerInventory

`Player::inventory()` (Bukkit의 PlayerInventory). 가방은 서버가 **칸으로** 갖고 있습니다(규칙 `bag.slots`, 앞의 12칸이 단축바):
게임이 칸을 옮기면 서버가 판정하고(가진 것보다 많이, 다른 것 든 칸에 나눠 옮기기는 거절), 그 사람이 옮기는 것도
[`InventoryClick`](events#inventoryclick)으로 모든 플러그인에게 갑니다(취소하면 안 옮겨짐). 한 칸은 [`ItemStack`](#itemstack).

| 메서드 | |
|---|---|
| `items()` → `Vec<(String, i64)>` | 가방의 모든 것 (id, 개수), id 순서 |
| `count(id)` → `i64` / `contains(id)` → `bool` | 개수 / 있는지 |
| `add(id, n)` | 넣기 (한 번에 999까지; `Player::give`) |
| `remove(id, n)` | 빼기: 있는 만큼만 (`Player::take`는 모자라면 아무것도 안 가져감) |
| `clear(include_tools)` | 비우기. `false`면 도구는 남김 (착용한 장비는 가방에 없으므로 늘 그대로) |
| `size()` / `get(slot)` → `Option<ItemStack>` / `slots()` | 칸 수 / 한 칸 / 모든 칸 |
| `set(slot, Some(&stack))` / `set(slot, None)` | 그 칸을 그것으로 / 비우기 (있던 것은 없어짐) |
| `held_slot()` / `set_held_slot(i)` / `held()` | 손에 든 단축바 칸 / 그 칸을 들게 / 든 것 |
| `add_stack(&stack)` | 메타 붙은 것을 넣기 (같은 것 위, 아니면 첫 빈 칸) |

`Player`에도: `set_inventory(&[Option<ItemStack>])`(가방 전체를 칸 그대로: 키트, 미니게임; 착용 장비는 그대로)
`clear_inventory()` `give_item(&stack)`. 다른 플레이어에게도 됩니다(그 사람 월드의 다음 걸음에).

- 읽는 것은 **이벤트가 시작될 때**의 모습, 바꾸는 것은 **이벤트가 끝난 뒤**에 됩니다(`give`가 되는 이벤트에서만).
- 그 이벤트의 플레이어 것만 됩니다(`Tick::players()`의 다른 사람은 비어 보임).
- 가방은 그 사람의 것 하나로, 어느 월드에 있든 같습니다.

## ItemStack

한 칸: `id`(품질 `@2`까지) `n`과 메타(Bukkit의 ItemMeta): `name`(48자) `lore`(8줄, 80자) `tint`(`"rrggbb"`) `model`(손에 든
모델 `res://..glb`) `data`(플러그인의 키-값 16개, PersistentDataContainer) `unbreakable` `glow` `tier`(등급, `.tier(2)`) `ench`(마법과 단계, `.ench("luck", 1)`). 바닐라의 대장간과 마법사도 도구의 등급과 마법을 이 메타에 씁니다(`hoe#{"tier":2,"ench":[["speed",1]]}`): 플러그인의 아이템도 등급·마법이 이름과 함께 보이고, 도구는 같은 id라도 한 개 한 개가 제 등급을 가집니다. 메타가 같은 것끼리만 쌓이고, 게임은
이름·설명(툴팁)·색·반짝임·손의 모델을 그립니다. 규칙은 다 id로만 읽고, 쓰면(먹기, 버리기 ...) 메타 있는 묶음에서 먼저 빠집니다.
메타는 묶음과 함께 갑니다: 상자에 넣고 꺼내기, 바닥에서 줍기(`World::ground_drop(&stack.key(), ..)`, `drop`), 편지, 플러그인
창(`Inventory::slot(i, &stack.key(), ..)`), `give(&stack.key(), n)`. `key()`는 `id#{메타 JSON}`(서버가 순서를 맞춤). 출하·판매는
그냥 id의 값으로 받습니다. 게임은 바닥의 것도 메타의 모델·색으로 그립니다.

```rust
let blade = ItemStack::new("kit_blade", 1).name("붉은 대검").tint("e04a3a").lore("가까이 붙어 크게 베어요.")
    .data("class", "전사").glow();
p.set_inventory(&[Some(blade), Some(ItemStack::new("health_tonic", 3))]);
p.inventory().set_held_slot(0);
```

`get_data(key)` → `Option<&str>`. 무기마다의 사거리·대기시간은 규칙 `tools`의 `reach`(m)·`cooldown`(초)
(`Registry::add("tools", id, r#"{"energy":0,"damage":2,"reach":7,"cooldown":1.2}"#)`; 하나라도 있으면 가방에 있어야 휘두름). 예: `plugins/kits`.

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
| `set_vanilla(feature, on)` → `bool` | 게임의 기능 하나 켜고 끄기, 월드에 저장 ([월드](world#월드-만들기)의 목록); `false`: 그런 기능 없음. 정하지 않으면 바닐라 마을이 있는 월드는 켜짐, 없는 월드는 `fishing` `crafting` `energy` `fall` `day_end`만 켜짐 |
| `is_vanilla(feature)` → `Option<bool>` | 그 기능이 켜졌는지 (이벤트가 시작될 때; `None` 그런 기능 없음) |
| `set_quit_warning(text)` | 자기 전에 나갈 때 게임이 띄우는 경고 (`""` 없음, 200자까지). server.properties `quit-warning`보다 우선 |

### 하루

| 메서드 | |
|---|---|
| `set_day(day)` | 날짜 (1이 첫날; 계절은 날짜에서). 월드의 게임에 바로 알림 |
| `set_morning_time(minute)` `clear_morning_time()` | 밤이 끝나는 시각 (해가 뜨고 몬스터가 사라짐, 6:30 = 390) / 계절의 해 뜨는 시각으로 |
| `set_night_time(minute)` `clear_night_time()` | 밤이 시작되는 시각 (해가 지고 몬스터가 나옴, 18:00 = 1080) / 계절의 해 지는 시각으로 |
| `set_dawn_time(minute)` `clear_dawn_time()` | 몬스터가 강해지는 시각 (2:00 = 120), 아침까지 / 기본값으로 |
| `set_day_end_time(minute)` `clear_day_end_time()` | 시계로 하루가 끝나는 시각 (자정부터 분, 26 * 60 = 다음 날 2:00, 48 * 60까지) / 규칙의 `day_end`로 |
| `end_day()` | 지금 하루를 끝냄, 모두 잔 것처럼 (먼저 `DayEnd` `"end_day"`) |
| `set_clock_rate(rate)` `clear_clock_rate()` | 이 월드의 시계가 규칙의 `rate`배 (0 멈춤, 100까지) / 규칙대로 |
| `set_rule(key, json)` → `bool` `clear_rules()` | rules.json의 값 하나를 이 월드에서만 (점으로 이은 키, `"null"` 서버의 것으로): 판정과 들어오는 게임의 콘텐츠 ([월드마다의 규칙](world#월드마다의-규칙가방시계-월드의-수명-미니게임-허브)) |
| `set_mode(mode)` → `bool` | `"arena"`: 농장 기능 전부 끔, 시계 멈춤, 그때그때 저장, HUD의 날짜·시간·퀘스트 숨김, 가방 그룹 `"arena"`(빈 키트), 행동 초당 30 / `"farm"`: 모두 서버의 것으로 ([경기장 모드](world#경기장-모드-농장이-아닌-게임을-한-번에)) |
| `set_action_rate(rate, burst)` `clear_action_rate()` | 이 월드의 행동 한도 (최대 60, 120; 서버 10, 30; 플러그인 패킷은 따로) |
| `hide_hud(part, hidden)` | 게임 HUD의 부분을 이 월드의 모두에게 숨김 |
| `set_inventory_group(name)` | 이 월드의 가방 그룹 (`""` 모두의 월드의 것): 다른 그룹에서 오면 자기 몫을 바꿔 받음 |
| `set_sync(tiers, chat)` | 위치를 거리별로 얼마나 자주 (`&[(m, ms)]`, 6개까지), 채팅이 닿는 거리 (`Some(0.0)` 월드 전체, `None` 48 m) |
| `set_sync_with(tiers, chat, full, send)` | 더해서 첫 구간을 받을 가까운 인원(1~64, `None` 10), 게임이 보내는 초당 위치 수(5~30, `None` 게임의 것) |

### 블록

| 메서드 | |
|---|---|
| `block(x, y, z)` → [`Block`](#block) | 그 블록 (아직 안 만든 청크는 바닐라 땅으로) |
| `top(x, z)` → `i64` | 기둥에서 가장 높은 단단한 블록의 y (없으면 `Block::LOWEST - 1`) |
| `set_block(x, y, z, b)` | 블록 놓기 (저장됨) |
| `fill(from, to, b)` | 상자 모양 채우기, 양 끝 포함, 한 번에 청크 넷까지 |
| `set_blocks(&[(x, y, z, Block)])` | 여러 블록을 한 번에 (65 536개까지). `ChunkGenerate` / `ChunkLoad`에서는 그 청크의 것만 |
| `set_block_rules(json)` | 이 월드에서 부수고 놓는 바닐라 블록 ([블록 규칙](world#바닐라-블록-부수기놓기)) |
| `block_data(x, y, z, key)` → `String` / `set_block_data(x, y, z, key, value)` | [블록 데이터](world#블록-데이터) ("" 없음 / 지움) |
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
| `path_blocks((x, y, z), (x, y, z), max)` → `Vec<(f64, f64, f64)>` | 어느 월드 어디서나 블록 위로 걷는 길: 첫 걸음부터 목적지까지 칸마다 `(x, 발 높이, z)`, 비어 있으면 길이 없음. 끝은 발 아래(조금 묻혀도) 가장 높은 설 수 있는 칸, 물속이면 물 위. 설 수 있는 칸: 단단한 블록 위에 몸 들어갈 두 칸(1.6 m)이 비었거나 물 맨 위(헤엄). 한 번에 한 칸 위로(플레이어 점프 1.5 m, 물에서 나올 때도), 네 칸까지 아래로, 여덟 방향, 모서리는 몸이 들어갈 때만. 플러그인의 단단하지 않은 블록은 지나감. `max`: 살필 칸 수(16384까지), 시작에서 가로세로 64칸 안; 두 끝이 그보다 멀거나 한쪽이 한 번도 만들어진 적 없는 청크면 찾지 않고 바로 빈 것. 엔진의 A*: 연료가 아니라 걸린 시간으로 셈 |
| `is_solid(x, y, z)` → `bool` | 그 칸이 단단한가: 블록, 또는 충돌층의 상자(구조물의 히트박스, 건물 벽, 울타리, 성벽, 단단한 엔티티) |
| `raycast(from, dir, most)` → `Option<f64>` | `from`에서 `dir`로 처음 닿는 단단한 칸까지 m (`most`, 256 m까지 안에서) |
| `room(name)` → `Option<Room>` | 건물 방(`"Farmhouse"` …): `x` `z` 가운데, `y` 바닥(땅 아래), `door` 안쪽 문 앞, `out` 바깥 문 앞, `size`. 엔티티를 `(door.0, y, door.1)`로 옮기면 방 안 |

### 구조물과 주민

| 메서드 | |
|---|---|
| `structures()` → `Vec<Structure>` | 월드에 선 것들 (건물, 울타리, 성벽, 성문, 정거장 …) |
| `put_structure(json)` → `Option<Structure>` | 세우기: `{"k": "building", "m": "house_Lv1", "x", "z", "yaw", "plot"}`, 칸 사각형 종류는 `{"k": "block", "cells": [x, z, w, d]}`, 히트박스 `"hit": [[x, z, w, d, y, h], …]` ([히트박스](world#히트박스와-충돌)) |
| `remove_plot(plot)` | 구획 통째로 치우기 (`"wall"`: 성벽·성문·바위 둑·암초, `"station"`, `"core"` 마을 한가운데 …) |
| `spawn_npc(json)` → `bool` | 주민 더하기 (`{"id", "name", "look", "home", "shop", "schedule": [[480, "square"]] …}`) |

[월드와 하루](world)에 자세히.

## Server

월드와 상관없는 서버의 값. `Server` (단위 구조체)로 씁니다.

| 메서드 | |
|---|---|
| `get(k)` → `f64` | 어느 이벤트에서나 읽음 |
| `set(k, v)` | `PlayerLogin`과 그 입력 창의 `Button`, `ServerTick`에서만 |
| `create_world(id)` → `bool` | 플러그인의 월드 하나 (바닐라 땅과 마을, 저만의 씨앗, 여느 월드처럼 저장; `id`는 영문·숫자·`_ - .` 32자까지, `false`: 쓸 수 없는 이름). 그 월드에서 `WorldCreate`·`ChunkGenerate`가 불림 ([플러그인의 월드](world#플러그인의-월드)). 서버가 함께 돌리는 월드는 16 + 접속 한도의 두 배(256까지): 넘으면 만들어지지 않음(서버 로그) |
| `create_world_with(id, generator, town)` → `bool` | 생성기를 골라: `"vanilla"` `"flat"` `"void"`, `town` false면 바닐라 땅에 마을 없이 ([월드 만들기](world#월드-만들기)) |
| `create_world_from(id, template)` → `bool` | 이 플러그인이 만든 월드 `template`의 지금 모습을 복사한 월드 ([월드마다의 규칙](world#월드마다의-규칙가방시계-월드의-수명-미니게임-허브)) |
| `reset_world(id, to)` / `remove_world(id, to)` → `bool` | 이 플러그인이 만든 월드를 만든 그대로 다시 / 지움; 안의 사람은 먼저 `to`로 (`""`: 모두의 월드, reset이면 다시 들어옴) |
| `worlds()` → `Vec<(String, usize)>` | 만들었거나 읽은 월드들과 사람 수 (아무도 없어 내린 월드도) |
| `world_loaded(id)` → `bool` | 지금 돌고 있는지 (아무도 없으면 `world-unload-seconds` 뒤 내려감) |
| `data_put(key, &[u8])` → `bool` | 서버 하나의 바이트: 어느 월드의 이벤트에서든 같은 것 (월드를 오가도 따라가야 하는 것: 서버 안 친구 목록, 순위). **넣는 즉시 디스크에** 저장 ([데이터 저장](#데이터-저장)) |
| `data_get(key)` → `Option<Vec<u8>>` | |
| `data_del(key)` | |
| `data_keys(prefix)` → `Vec<String>` | 이 플러그인의 서버 키 중 `prefix`로 시작하는 것 |
| `rank_set(board, key, score)` → `bool` | 순위표에 (로블록스의 OrderedDataStore): 높을수록 위, 넣는 즉시 디스크에. 플러그인마다 판 16개, 판마다 키 2000개(가득 차면 가장 높은 것만: 가장 낮은 것보다 낮은 새 키는 `false`), 이름 64바이트까지 |
| `rank_top(board, n)` → `Vec<(String, i64)>` | 높은 순 (같으면 키 순) |
| `rank_of(board, key)` → `Option<(u64, i64)>` | 등수(1이 가장 높음)와 점수 |
| `rank_remove(board, key)` | |
| `http_get(url, tag)` / `http_post(url, body, tag)` → `Option<i64>` | [바깥 요청](#바깥-요청) |

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
| `Server.set_whitelist(on)` `whitelist_on()` `whitelist_add(name)` `whitelist_remove(name)` `is_whitelisted(name)` `whitelist()` | 허용 목록 (server.properties `whitelist`, `whitelist.txt`; 운영자는 늘 들어옴) |
| `Server.ban(name, why)` `unban(name)` `is_banned(name)` `bans()` | 이름으로 차단 (접속하지 않은 사람도; `bans()`는 (이름, 이유, 때 ms)) |
| `Server.motd()` `set_motd(text)` `max_players()` `set_max_players(n)` `version()` | 서버 목록의 소개와 동시 접속 한도 (서버가 켜져 있는 동안; `""` / `-1` 파일의 것), 들여보내는 게임 버전 |

| 메서드 | |
|---|---|
| `name()` | 이름 |
| `has_played()` → `bool` | 저장된 게임이 있는지 |
| `gold()` `day()` | 골드, 그 사람 월드의 날짜 |
| `last_seen()` → `f64` | 마지막으로 나간 때 (1970년부터의 ms) |
| `first_seen()` → `f64` | 처음 들어온 때 (ms; 0: 기록 전부터의 게임, 다음에 나갈 때 정해짐) |
| `position()` → `Option<(x, y, z)>` `world()` | 마지막으로 나간 곳 (칸)과 그 월드 |
| `id()` | 어느 서버에서나 같은 id (이름의 해시; online-mode에서 이름은 중앙 계정 id라 별명이 바뀌어도 같음) |
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
| `set_interact_with(label, hold_secs, reach)` | `set_interact`인데 E를 `hold_secs`초 눌러야(0이면 누르기, 30초까지) `reach` m 안에서만(0이면 손 닿는 1.6 m, 16 m까지) 쓰임(로블록스의 ProximityPrompt): 게임이 「E 길게: label」과 차오르는 링을 그리고, **서버가 누르기 시작부터 시간을 잼**(그보다 이른 사용, 시작 없는 사용은 거절; 거리는 시작과 끝 둘 다) |
| `set_interact(label)` | 플레이어가 E로 쓸 수 있음: 가까이 가면 「E: label」, 누르면 [`EntityInteract`](events#entityinteract) (이 플러그인에만). `""` 끄기. 플러그인의 엔티티(`ModelEntity` `Avatar`)만 |
| `say(text)` | 머리 위 말풍선 (가까운 모두에게). 플러그인의 엔티티만 |
| `set_solid(on)` | 아무도 지나가지 못함: 서버의 걸음·길·몬스터와 게임의 몸이 그 히트박스에 부딪힘. 플러그인의 엔티티만 |

### ModelEntity

이 플러그인의 엔티티 (`World::spawn`). **저장되지 않습니다**: 서버를 다시 켜면 사라지니, 남길 것은 `World::set`에.

| 메서드 | |
|---|---|
| `get(k)` / `set(k, v)` | `"x"` `"y"` `"z"` `"yaw"`(라디안, 0이 +z) `"pitch"`(기수 들기) `"roll"`(오른쪽 내리기) `"scale"` (`get`은 `"alive"`도) |
| `set_rotation(yaw, pitch, roll)` | 통째로 돌림 (라디안: yaw, 그다음 pitch, 그다음 roll): 비행기의 선회, 비탈의 차. 게임은 그 사이를 부드럽게 |
| `text(k)` → `String` | `"model"` `"anim"` `"held"` `"name"` |
| `as_avatar()` → `Option<Avatar>` | 아바타면 그것으로 |
| `set_public(key, value)` | 모든 게임이 읽는 값 (`Player::set_public`처럼; 게임 쪽 `Entities::get(id).public(key)`) |
| `set_hitbox(&[[x, z, w, d, y, h]])` | 히트박스 (`set_solid`가 단단하게 하는 모양; [히트박스](world#히트박스와-충돌)) |
| `set_health(hp, max)` / `health()` | 체력 (0: 없음, 맞지 않음): 플레이어의 휘두름 → `ModelEntityDamage`, 0이면 `ModelEntityDeath` 뒤 사라짐 |

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
| `damage(amount)` | 피해: 0이면 쓰러지고 그 종류의 드롭(아무나 줍기)과 경험치(이벤트의 플레이어), [`MobDeath`](events#mobdeath)(`killer` 이벤트의 플레이어, `cause` 이 플러그인 이름) |
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

## 바깥 요청

`Server::http_get(url, tag)` / `Server::http_post(url, body, tag)`(로블록스의 HttpService): 답은 [`HttpDone`](events#httpdone).
`server.properties`의 [`http-allow`](server#serverproperties)에 적힌 호스트에만 보냅니다(기본은 없음: 모두 `None`).

- http와 https만, 리디렉션은 따라가지 않고, 프록시는 쓰지 않습니다.
- 이름으로 적은 호스트는 **공용 주소로만** 연결합니다(사설·루프백·링크 로컬로 풀리면 연결하지 않음). 사설 주소는 그 주소 자체를
  적었을 때만(`127.0.0.1:8080`, `localhost`), GreenHaven+ 24시간 서버에서는 그것도 안 됩니다.
- 보내는 본문 64 KB, 받는 본문 앞 64 KB, 10초. 플러그인마다 동시에 4개(넘으면 바로 `status` 0 "busy"), 1분에 60개.
- 본문이 `{`나 `[`로 시작하면 JSON, 아니면 글로 보냅니다. 헤더는 따로 붙일 수 없습니다.
- 거절된 행동 안의 요청은 보내지 않습니다. 게임의 자체 서버(혼자·LAN)에서는 언제나 실패합니다.

```rust
#[command("알림", "디스코드로 알리기")]
fn ping(c: Command) {
    Server.http_post("https://discord.com/api/webhooks/…", r#"{"content":"경기 시작!"}"#, "start");
}

#[on(HttpDone)]
fn done(e: HttpDone) {
    if !e.ok() { e.world().broadcast(&format!("알림 실패: {} {}", e.status(), e.error())); }
}
```

## 서버 사이 공유: 없음

서버끼리는 아무것도 주고받지 않습니다(남이 만든 플러그인이 다른 서버의 데이터를 건드리는 길이 되므로). 다른 서버로는
[`Player::transfer`](server#다른-서버로)로 플레이어와 짐 한 번만 보냅니다. 한 서버 안을 나누려면 월드(`Server::create_world`)나 채널
(예제 [`channels`](samples): `set_view_group`으로 사람만 나누거나, 설정 `mode` "worlds"로 채널마다 월드를 따로)을 씁니다.

## `sys` — 원본 함수

SDK가 감싸지 않은 것은 `greenhaven_plugin::sys`에 "gh" 함수 그대로 있습니다 ([목록](abi)).

## 상태 효과, 타이머, 쿨다운

서버의 `plugin_api/effects.rs`(Bukkit의 PotionEffect, BukkitScheduler, 아이템 쿨다운). 월드에 저장되고 서버가 월드의 스텝마다 합니다.

| 함수 | |
|---|---|
| `Player::add_effect(이름, 초, 세기, 아이콘) -> bool` | 효과 하나(같은 이름이면 새로; 한 사람 16개). 엔진이 하는 것: `speed`(세기마다 걸음 20 %, 서버의 판정도), `slow`(15 %씩), `jump`(세기마다 반만큼 더 높이), `invisible`(아무에게도 보내지 않음), `regen`(1초마다 세기만큼 회복), `poison`(1초마다 세기만큼, 마지막 1은 남김), `glow`(이름표가 벽 너머로). 다른 이름은 보이고 알리기만. `아이콘` `res://…` 또는 `""`(게임의 것) |
| `remove_effect(이름)`, `effect_left(이름) -> 초`, `has_effect(이름)`, `effects() -> [(이름, 초, 세기)]` | |
| `Player::cooldown(키, 초) -> bool`, `cooldown_left(키) -> 초` | 준비됐으면 true(지금부터 식음). 플러그인·사람·키마다, 서버가 판정 |
| `Scheduler::run_later(태그, 초)`, `run_every(태그, 초)`, `cancel(태그)` | [`Timer`](events#timer) 이벤트 |

그 사람의 게임에는 화면 위 가운데에 효과마다 아이콘과 남은 시간이 보입니다(끝나기 3초 전부터 깜박임). 이벤트
[`EffectStart` / `EffectEnd`](events#effectstart--effectend).

```rust
#[on(Packet)]
fn skill(e: Packet) {
    let p = e.player();
    if e.channel() == "haste" && p.cooldown("haste", 12.0) {
        p.hud().sweep("skill_haste", 12.0); // 버튼 위 쿨다운 부채꼴
        p.add_effect("speed", 6.0, 2.0, "");
    }
}
```

## 팀 채팅

플레이어가 채팅을 `!`로 시작하면 같은 팀에게만(월드 안 어디서나, 차단한 사람 빼고). 플러그인은 `World::team_chat(팀, 줄)`.
이름표는 팀 색입니다.

## 한 사람에게만, 장비, 기력, 월드 읽기, 팀 옵션

| | |
|---|---|
| `Player::title_with(title, sub, fade_in, stay, fade_out)` | 큰 글과 그 아래 줄 (초; NaN은 게임 기본 0, 2.5, 0.8) |
| `Player::action_bar(line)` | 단축바 위 한 줄, 2초 (`""`: 지움) |
| `Player::play_sound(name, x, y, z)` / `spawn_particle(...)` | 그 사람만 (이름은 `World::sound`·`particle`과 같음) |
| `Player::set_energy(n)` | 기력 (0~최대) |
| `PlayerInventory::equipment()` | `[(칸, Option<아이템>)]`, 규칙의 `equip_slots` 차례 |
| `PlayerInventory::set_equipment(칸, Some(id) \| None)` | 없던 것을 입힘 (가방에서 꺼내지 않음, 입던 것은 사라짐, `PlayerEquip` 없음) |
| `World::weather()` | 오늘의 날씨 |
| `World::spawn_location()` | `set_spawn`의 `(x, y, z, yaw)`, None: 바닐라 마을 |
| `World::mobs()` | 이벤트의 층의 몬스터 `[(EnemyEntity, x, z)]` |
| `World::set_minute(m)` | 월드의 시계 |
| `World::team_option(team, key, value)` | `"prefix"` `"suffix"` (16자), `"nametag"` `"all"` \| `"team"` \| `"others"` \| `"none"`, `"collide"` `"on"` \| `"off"` (끄면 단단한 엔티티가 지나감) |
