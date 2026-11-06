---
title: 이동 방식 만들기
nav_order: 6.4
parent: 플러그인
redirect_from:
  - /moving
  - /moving.html
---

# 이동 방식 만들기 — 비행, 탈것, 도구 동작
{: .no_toc }

1. TOC
{:toc}

비행, 탈것 물리, 대시, 벽 타기처럼 게임의 이동 자체를 바꾸는 법입니다. [게임 쪽 코드](client)가 플레이어를 즉시 움직이고(예측),
서버 쪽 코드가 같은 규칙으로 검사해 막습니다. 예: `plugins/flight`(비행), `plugins/riding`(탈것과 지팡이).

## 규칙은 한 번만 (`shared.rs`)

규칙(최대 빠르기, 최고 높이, 키가 만드는 속도)은 `src/shared.rs`에 **한 번** 씁니다. 게임 쪽은 그 규칙으로 움직이고, 서버 쪽은
`PlayerMove`에서 같은 규칙으로 검사합니다. 서버와 게임의 샌드박스 모두 NaN을 정규화하므로 `shared.rs`의 계산은 양쪽에서 같습니다.

```rust
// shared.rs
pub const SPEED: f64 = 9.0;   // 가로 최대 칸/초
pub const CLIMB: f64 = 5.0;   // 위아래
pub const CEILING: f64 = 40.0; // 발의 최고 높이
pub const SLACK: f64 = 1.35;  // 서버의 여유 (늦은 보고, 긴 프레임)

pub fn velocity(ahead: f64, up: f64, yaw: f64) -> (f64, f64, f64) {
    (yaw.sin() * ahead * SPEED, up * CLIMB, yaw.cos() * ahead * SPEED)
}

pub fn allowed(from: (f64, f64), to: (f64, f64, f64), dt: f64) -> Result<(), &'static str> {
    if (to.0 - from.0).hypot(to.2 - from.1) > SPEED * SLACK * dt.max(0.0) + 0.5 { return Err("너무 빨리 날았어요") }
    if to.1 > CEILING { return Err("너무 높이 날았어요") }
    Ok(())
}
```

## 서버의 이동 검사

서버는 기본으로 다섯 가지를 검사합니다. 새 이동 방식이 그중 하나에 걸리면(날면 `air`, 빨리 날면 `speed`, 지붕 위로 날면
`walls`) 그것을 끕니다.

| 검사 | 막는 것 |
|---|---|
| `speed` | 빠르기 (걸음, 행동 사이의 이동 시간) |
| `walls` | 벽·건물 통과 (그리고 돌아가야 하는 길이). 블록도: 점프로 못 넘는(두 칸 높이) 단단한 블록 벽을 곧장 지나간 걸음은 돌아가는 길로 잼 (마을 밖, 마을 없는 월드에서도; `air`가 켜져 있을 때만) |
| `air` | 공중·물 위·땅속에 2초 넘게 |
| `teleport` | 걷기가 시작될 수 있는 곳(집 앞, 침대, 정류장)에서 먼 데 나타나기, 다른 사람에게 순간이동으로 보이기 |
| `reach` | 도구의 칸이 손 닿는 거리 밖 |

- **모두에게**: [`Enable`](events#enable)에서 `Registry::set("checks.air", "false")`. 서버가 켜질 때 꺼진 검사가 로그에 한 줄로 나옵니다.
- **한 사람에게만**: `player.set_check("air", false)` / `set_check("air", true)`. 저장되지 않으니 필요하면 `Join`에서 다시 부릅니다.
- 위치 보고의 검사와 행동 사이 이동 시간의 검사가 같은 스위치를 따르므로 둘이 어긋나지 않습니다.

{: .warning }
검사를 끄면 그만큼 부정 이동이 열립니다. 끈 검사는 **반드시 `PlayerMove`에서 `shared.rs`의 규칙으로 다시 막으세요**
(최대 빠르기, 최고 높이 …). 모두에게보다 한 사람에게만 끄고, 그 이동이 끝나면(착지) 다시 켜세요. `plugins/flight`는 땅에
닿았을 때, 늦어도 내려오기 시작하고 3초 뒤에 다시 켭니다.

## 밀기

`player.push(vx, vy, vz)`(m/s, 칸 기준, 축마다 30까지): 넉백, 점프대, 돌진. 게임의 `PlayerController`가 속도로 받습니다(옆으로는
초당 3배로 줄어 `v / 3` m를 가고, 위로는 그 속도의 점프). 검사를 끌 필요가 없습니다: 서버가 게임에 보내기 전에 **그만큼의 허용**을
적어 두고(몬스터에 밀린 것과 같은 것) 걸음 검사가 그것을 뺍니다.

| 허용 | 크기 |
|---|---|
| 땅을 따라 | `v / 3 + 1` m, 걸어서 갈 수 있는 것보다 더 간 만큼씩 써서 없어짐 (겹쳐도 24 m까지) |
| 더 높이 | `v² / 2g` (g = 20 × 그 사람의 중력 배율) |
| 더 오래 공중에 | `2v / g`초 |
| 동안 | 공중 시간 + 1초 + 1.5초 |

얼어 있거나 관전자면 게임이 무시합니다. 게임 쪽 코드로 운전 중(`drive`)이면 그 속도에 더해집니다.

## 구역과 월드 보더

`World::zone(id, min, max)`(칸, 발 높이; 다시 부르면 옮김)에 들어가고 나갈 때 [`ZoneEnter` / `ZoneLeave`](events#zoneenter--zoneleave)
(그 플러그인에만). `World::keep_in(id, min, max)`는 월드 보더: 안에서 밖으로 가는 걸음을 서버가 되돌립니다(바깥에서 순간이동으로
온 사람은 들어올 때까지 자유). `World::keep_out(id, min, max)`는 들어가는 걸음을 되돌립니다. `remove_zone(id)`, `zones_at(점)`.
월드와 함께 저장되고 한 월드에 256개, 다른 플러그인의 id는 건드리지 못합니다.

```rust
#[command("경기장", "")]
fn arena(c: Command) {
    let ((x, z), y) = (c.player().position(), c.player().y());
    c.world().keep_in("arena", (x - 12.0, y - 8.0, z - 12.0), (x + 12.0, y + 40.0, z + 12.0));
    c.world().zone("pad", (x + 3.5, y - 1.0, z - 1.0), (x + 5.5, y + 1.0, z + 1.0));
}
#[on(ZoneEnter)]
fn came(e: ZoneEnter) {
    if e.zone() == "pad" { e.player().push(0.0, 14.0, 0.0) } // 5 m쯤 위로
}
```

## PlayerMove로 판정하기

[`PlayerMove`](events#playermove)는 플레이어가 가로나 위아래로 움직일 때마다 옵니다(서버가 걷기를 검사하는 0.19초마다 한 번까지:
플레이어당 초당 약 5번). `cancel`이면
있던 곳으로 되돌려 보냅니다.

| | |
|---|---|
| `from()` → `(x, z)` / `from_y()` | 지난 걸음의 자리와 발 높이 |
| `to()` → `(x, y, z)` | 이번 자리 (y는 발) |
| `dt()` | 지난 걸음부터의 초 |
| `on_ground()` | 서버가 본 발밑에 무언가 있는지 (땅, 지붕, 갑판) |
| `mode()` | 게임 쪽이 알린 이동 모드 (`Me::set_move_mode`; `""` 게임 그대로). **주장일 뿐**: 믿지 말고 판단의 근거로만 |
| `mount()` | 탄 엔티티 (0 없음) |

```rust
// server.rs
#[on(Packet)]
fn asked(e: Packet) {                       // Y: 날기 / 내려오기
    if e.channel() != TOGGLE { return }
    let p = e.player();
    let on = p.get("flying") == 0.0;
    for c in ["air", "speed", "walls"] { p.set_check(c, !on) }
    p.set("flying", on as i64 as f64);
    p.hud().send_text(FLYING, if on { "1" } else { "0" });
}

#[on(PlayerMove)]
fn stepped(e: PlayerMove) {
    if e.player().get("flying") != 0.0 {
        if let Err(why) = allowed(e.from(), e.to(), e.dt()) { e.cancel(why) }
    }
}
```

(실제 샘플은 내려올 때 바로 검사를 켜지 않고, 땅에 닿거나 3초가 지날 때까지 같은 규칙으로 판정합니다.)

**비용**: `plugins/flight`의 `PlayerMove` 핸들러 한 번에 약 5 µs(초당 30번이면 플레이어 한 명에 0.15 ms/초). 야생·땅의 아이템·방을
읽는 함수까지 가져다 쓰는 플러그인은 이벤트마다 그 사본을 만들어 약 100 µs가 됩니다. 걸음마다 오는 이벤트이니 핸들러를 가볍게,
읽기 함수는 꼭 필요한 것만 쓰세요.

## 게임 쪽에서 조작 넘겨받기

| | |
|---|---|
| `Input::capture(&["W", "A", "S", "D", "Space", "Shift"])` | 그 키를 게임에서 가져옴: 게임은 그 키로 아무것도 안 하고(WASD면 걷기, Space면 점프, `Mouse1`/`Mouse2`면 도구가 꺼짐) 이 플러그인의 `input`으로만 옴 |
| `Input::release()` | 모든 키를 게임에 돌려줌 |
| `Input::held(key)` | 지금 누르고 있는지 (가져간 키도) |
| `Me::set_position(x, y, z)` | 지금 그 자리로 (칸; 이 게임의 예측) |
| `Me::set_yaw(yaw)` | 그쪽으로 돌림 (라디안, 0이 +z) |
| `Me::set_velocity(x, y, z)` | 게임의 물리로 그 속도로 움직임 (칸/초; 벽과 바닥이 막음), `release_drive`까지 게임의 걷기는 꺼짐 |
| `Me::release_drive()` | 게임의 걷기를 되돌림 |
| `Me::set_gravity(on)` | 중력 (끄면 놓인 곳에 머묾: 공중에도) |
| `Me::set_jump(on)` | 점프 |
| `Me::set_move_mode("fly")` | 서버에 알리는 이동 모드 (서버 쪽 `PlayerMove::mode()`; `""` 게임 그대로) |
| `Me::velocity()` / `Me::on_ground()` | 게임이 움직이는 속도, 발이 땅에 닿았는지 |

서버로 가는 위치 보고와 판정은 그대로입니다. 서버가 막은 걸음(검사나 `PlayerMove`의 `cancel`)은 되돌려지는데, 서버는 마지막으로
받아들인 곳의 **높이**도 함께 보내므로(`{"t":"back","y"}`) 날던 사람은 땅바닥이 아니라 그 높이로 돌아갑니다.

카메라는 `Camera::set`(매 프레임 위치·바라볼 곳) `follow` `orbit` `first_person` `mouse_look` `yaw` `release`([게임 쪽 코드 › Camera](client#camera)).
플러그인이 내려놓거나 서버를 떠나면 키·이동·중력·점프·카메라가 모두 게임으로 돌아옵니다.

```rust
// client.rs
fn heard(p: Packet) {
    if p.channel() != FLYING { return }
    if p.data() == "1" {
        Input::capture(&["W", "A", "S", "D", "Space", "Shift"]);
        Me::set_gravity(false);
        Me::set_move_mode("fly");
        Camera::follow(0.0, 2.2, -5.5, 1.0, true);
        unsafe { (ON, YAW) = (true, Me::yaw()) };
    } else {
        Input::release();
        Me::release_drive();
        Me::set_gravity(true);
        Me::set_move_mode("");
        Camera::release(0.5);
        unsafe { ON = false };
    }
}

fn axis(plus: &str, minus: &str) -> f64 { (Input::held(plus) as i64 - Input::held(minus) as i64) as f64 }

fn frame(f: Frame) {
    if !unsafe { ON } { return }
    let yaw = unsafe { YAW } + axis("A", "D") * TURN * f.dt();
    unsafe { YAW = yaw };
    Me::set_yaw(yaw);
    let (vx, vy, vz) = velocity(axis("W", "S"), axis("Space", "Shift"), yaw); // shared.rs의 규칙
    Me::set_velocity(vx, vy, vz);
}
```

## 탈것

서버 쪽 `Player::mount(&엔티티, 빠르기, 앉는 높이)` / `dismount()` — 그 사람이 한 일의 이벤트에서(엔티티를 E로 쓴
[`EntityInteract`](events#entityinteract), 명령어, 버튼, `Packet`).

- 탄 동안 모든 게임이 그 엔티티를 탄 사람 아래에 그리고(카메라가 흐리게 하지 않음) 탄 사람을 앉힙니다. 나중에 들어온 사람도
  누가 무엇을 탔는지 받습니다.
- 걸음은 `빠르기`배로 서버가 판정합니다(`set_walk_speed`와 같은 길). 그래서 탈것에는 검사를 끌 필요가 없습니다.
- 내리면 엔티티는 그 자리에 남고 걸음은 전과 같아집니다. 저장되지 않습니다(다시 접속하면 걸어서).
- 서버가 내려 주기도 합니다: 건물 문으로 들어감(방 안에는 탈것 없음), 다른 월드로 감(`Player::move_world`), 서버를 나감. 그때
  [`Dismount`](events#dismount) 이벤트가 옵니다(`reason()` `"door"` `"world"` `"quit"`, `mount()`). 플러그인이 부른
  `dismount()`에는 오지 않습니다.

```rust
#[on(EntityInteract)]
fn ride(e: EntityInteract) {
    e.player().mount(&e.entity(), 2.0, 0.55);   // 두 배 빠르게, 0.55 m 위에 앉음
    e.entity().set_interact("");                // 그동안 다른 사람은 못 탐
}

#[on(Dismount)]
fn taken_off(e: Dismount) {
    e.mount().set_interact("소 타기");           // 문으로 들어가 내렸으면 다시 탈 수 있게
}
```

## 도구 동작 (플러그인 아이템)

[등록](rules)하는 아이템에 이 필드를 주면, 쓸 때 게임이 그 동작을 하고(다른 사람에게도 보임) 그 순간 [`Use`](events#use)
이벤트를 보냅니다.

| 필드 | |
|---|---|
| `"usable": true` | 쓸 수 있는 아이템 |
| `"model"` | 손에 드는 모델 `res://plugins/<이름>/x.glb` (자기 재질 그대로; 다른 사람의 아바타에도) |
| `"action"` | 동작: `cast` 시전, `attack` `thrust` 공격, `block` 막기, `cheer` 환호, `slash` `chop` `swing` `sweep` `throw` 도구들의 동작, `emote:<id>` 플러그인의 [감정 표현](models), 또는 클립의 `res://` 경로 |
| `"hit"` | 동작의 몇 할에서 쓰이는지 (기본 0.5): 이때 `Use` |

서버 쪽은 결과를 정하고(`World::strike`, `give`), 게임 쪽은 연출을 그립니다(`Local`, `Camera::shake`). 서버가 그 아이템을 알도록
값도 함께 등록하세요(`Registry::set("price.<id>", ..)`).

```rust
// server.rs
#[on(Enable)]
fn enable(_e: Enable) {
    Registry::set("price.magic_staff", "300");
    Registry::item("magic_staff", r#"{"name": "마법 지팡이", "usable": true, "type": "misc",
        "icon": "res://plugins/riding/staff.png", "model": "res://plugins/riding/staff.glb", "action": "cast", "hit": 0.45}"#);
}

#[on(Use)]
fn cast(e: Use) {
    if e.id() != "magic_staff" { return }
    let p = e.player();
    let ((x, z), (fx, fz)) = (p.position(), p.facing());
    let (tx, tz) = (x + fx * 7.0, z + fz * 7.0);
    e.world().strike(tx, tz, 1.8, 12);                                    // 결과: 서버
    p.hud().send_text("bolt", &format!("{x:.2},{z:.2},{tx:.2},{tz:.2}")); // 연출: 게임 쪽에
}

// client.rs: 구슬이 손에서 날아감 (이 플레이어에게만)
let id = Local::spawn("res://plugins/riding/orb.png", v[0], y, v[1]);
Local::glide_to(id, v[2], y, v[3], 0.35);
```

## 예제

- `plugins/flight` 비행: Y로 날기 시작하고 다시 Y로 내려옴. W/S 앞뒤, A/D 돌기, Space 위로, Shift 아래로. 규칙은 `shared.rs` 하나,
  나는 동안 그 사람의 `air` `speed` `walls` 검사를 끄고 `PlayerMove`에서 그 규칙으로 판정.
- `plugins/riding` 탈것과 지팡이: 마을 소에 E로 올라타면 두 배 빨리 달림(서버가 그 빠르기로 판정), J로 내림, `/소`로 옆에 부름.
  `/지팡이`로 받는 마법 지팡이를 쓰면 시전 동작과 함께 앞쪽에 번개 구슬이 날아가 몬스터를 침.
