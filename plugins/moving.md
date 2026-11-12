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
  이름은 `checks::SPEED` `WALLS` `AIR` `TELEPORT` `REACH` 상수로도 씁니다(오타는 컴파일에서 걸림).
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
    p.hud().send_text(FLYING, &pack(&on));
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
#[on(Packet)]
fn heard(p: Packet) {
    if p.channel() != FLYING { return }
    if p.read::<bool>() == Some(true) {
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

#[on(Frame)]
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
  [`Dismount`](events#dismount) 이벤트가 옵니다(`reason()` `"door"` `"world"` `"quit"`, 게임 모듈의 것: 농장의 `"balloon"` `"home"`; `mount()`). 플러그인이 부른
  `dismount()`에는 오지 않습니다.

- 서버도 그 엔티티를 탄 사람의 걸음이 허락된 자리로 옮겨 둡니다(위치와 yaw): 탄 사람을 못 보는 사람에게도 그 자리에 보입니다.
- **여러 자리**: `Player::mount_seat(&엔티티, 자리, 빠르기, (오른쪽, 위, 앞))`. 자리 0은 운전석(`mount`와 같음: 그 사람의 걸음이
  탈것을 움직임), 나머지는 승객: 그 자리(엔티티 가운데에서 m, 엔티티와 함께 돎)에 실려 가고, 걸음은 판정하지 않고 탈것 근처인지만
  봅니다(자리까지의 거리 + 4 m). 누가 어느 자리인지(운전석은 하나)는 플러그인이 지킵니다. 하늘을 나는 탈것은 운전자에게
  `set_check("air", false)`. 예제 `plane_demo`.
- **기울기**: `ModelEntity::set_rotation(yaw, pitch, roll)`(라디안: yaw, 그다음 기수 들기, 그다음 오른쪽 내리기). 모든 게임이 그렇게
  기울여 그리고, 탄 사람의 게임은 그 기울기를 자기 자세로 보내 다른 게임에서 아바타도 같이 기웁니다.

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

## 서버가 움직이는 탈것: 차와 비행기 (`sdk/physics`)

빠른 차·비행기는 "빨리 걷는 사람"(`mount`)으로는 판정이 안 됩니다. 대신 **서버가 탈것을 움직이고, 게임은 같은 코드로 미리 그립니다**.
규칙은 순수 Rust crate `greenhaven-physics`(서버 SDK의 `sdk/physics`: 호스트 함수 없음, 1/60초 고정 걸음, `f64`만: 같은 입력이면 두 쪽의
결과가 비트까지 같음)에 있습니다.

```toml
[dependencies]
greenhaven-physics = { path = "../../sdk/physics" }
```

- `Car`: 바퀴 넷이 땅을 밟음(`Surface { height, grip }`: 길 1, 풀 0.6, 모래 0.4), 가속·브레이크·후진, 타이어 마찰 한계(넘으면 미끄러짐),
  사이드 브레이크로 드리프트, 높은 땅은 벽, 경사와 쏠림으로 차체가 기움, 기어와 rpm.
- `Plane`: 6자유도, 추력, 받음각의 양력과 실속, 항력, 피치·롤·요(속도가 붙어야 듣는 조종면), 바퀴로 이륙·착륙(세게 닿으면 추락).
- 서버 쪽 `Driven<S>`: 조작을 번호째 받아(`take`) 서버 시계대로만 걸음(`run(dt, 땅)`: 조작을 더 보내도 빨라지지 않음), 이벤트 사이에는
  `to_bytes` / `load`로 `World::data_put`에, 매 틱 엔티티를 그 자리·자세로(`move_to` + `set_rotation(entity_turn(..))`), 운전자에게
  `state_packet()`을 `send_fast`로.
- 게임 쪽 `Predicted<S>`: `step` 이벤트마다 한 걸음(`step(Controls, 땅)`), 두 걸음마다 `packet(4)`를 `send_fast`, 서버 상태가 오면
  `heard`(같으면 그대로, 다르면 서버의 것으로 바꾸고 다시 걸음), 그리기는 `Entities::predict`.
- 타는 사람은 `mount_seat(&탈것, 1, 1.0, 좌석)`: 0이 아닌 자리라 누구의 걸음도 탈것을 움직이지 않고, 그 사람의 자리는 탈것 곁인지만 봅니다.
- 땅은 두 쪽이 똑같이 아는 함수로: 평평한 월드(`Server.create_world_with(id, "flat", "")`, 풀 꼭대기 0.5)에 플러그인이 깐 길.

```rust
// shared.rs: 두 쪽이 같은 땅
pub fn ground(x: f64, z: f64) -> Surface { Surface::new(0.5, if on_road(x, z) { 1.0 } else { 0.65 }) }

// server.rs: 매 틱
let mut d = Driven::new(Car::new(CarSpec::default(), [0.0; 3], 0.0));
if w.data_get(&key).is_some_and(|b| d.load(&b)) && d.run(t.dt(), &ground) > 0 {
    w.data_put(&key, &d.to_bytes());
    let (pos, turn) = d.sim.pose();
    car.move_to(pos[0], pos[1], pos[2]);
    let (y, p, r) = entity_turn(turn);
    car.set_rotation(y, p, r);
    player.hud().send_fast("st", &d.state_packet());
}

// client.rs: 고정 스텝마다
car.step(Controls { throttle: axis("W", "S"), steer: axis("D", "A"), ..Default::default() }, &ground);
send_fast("in", &car.packet(4));
```

예제 `racing`(트랙, 체크포인트, 랩, 미니맵, rpm 엔진 소리), `plane_demo`의 `/조종`(활주로, 추적·조종석 카메라, 계기판).

### 차끼리 부딪히기

엔진은 탈것끼리 서로를 모릅니다. 대신 `greenhaven-physics`가 두 차를 부딪히게 하는 함수를 줍니다: `Car::body()`(바퀴 자리로 만든
캡슐), `Car::collide(&mut a, &mut b, 반발, &땅)`(겹친 만큼 반씩 밀어내고 법선으로 충격: 같은 질량, 운동량 보존, 맞은 자리만큼 돎;
밀려날 자리의 땅이 `step_up`보다 높으면, 즉 벽이면 그 차는 밀지 않음). 두 반쪽이 비트까지 같은 결과를 냅니다.

- 서버: 모든 차를 한 걸음씩 번갈아 걷고 걸음마다 모든 쌍을 부딪힘 (`Driven::owe(dt)`로 걸을 수만큼 정하고 `step_once(땅)`으로 한 걸음:
  늦게 온 조작을 몰아서 따라잡는 걸음에서도 서로 지나치지 않게).
- 게임: 내 차의 예측은 남의 차를 그려진 자리 + 속도 × (왕복 시간 + 50 ms)에 두고 부딪힘 (`Predicted::after_step`, 다시 걷는
  `heard_with`에서도 같게); 내 차 꼬리 뒤의 것은 빼서 나란히 달릴 때 떨지 않음. 닿는 동안은 서버 상태로 고쳐질 수 있음.

예제 `racing`이 이렇게 합니다.

## 탈것 말고 아무 규칙이나: 예측과 되감기 (`sdk/predict`)

`Driven` / `Predicted`는 탈것 전용이 아닙니다. `greenhaven-predict`(`sdk/predict`)에 있고, `greenhaven-physics`는 그 위에 차와 비행기를
얹은 것입니다. 대시, 차지 공격, 갈고리, 미니게임의 말처럼 **즉시 반응해야 하지만 결과는 서버가 정해야 하는** 규칙이면 무엇이든 씁니다.
게임은 누르는 즉시 같은 코드로 한 걸음 가고, 서버는 번호 붙은 입력으로 자기 시계대로 걸어 상태를 돌려주며, 다르면 게임이 서버의 상태로
바꾸고 그 뒤 걸음을 다시 걷습니다. 두 쪽이 같은 코드로 걸으니 패킷이 다 오면 고칠 일이 없고, 서버만 아는 것(게임이 모르는 감속 구역,
다른 플레이어)이 있으면 그만큼만 고쳐집니다.

```toml
[dependencies]
greenhaven-predict = { path = "../../sdk/predict" }
```

규칙 하나 = `Rollback`(상태, 걸음, 숫자로 쓰기·읽기) + 그 입력 `Input`(바이트로 쓰기·읽기: `put` / `get`). 비트까지 같으려면 1/60초 고정 걸음(`DT`),
시계·난수·호스트 함수 없이 `f64` 산술만(난수가 필요하면 상태 안에 시드를 두고). 입력은 플레이어가 보내는 것이니 `get`에서 범위를 자르세요.
패킷(`packet`, `state_packet`)은 그 바이트를 `pack`과 같은 base64 글로 보냅니다(2026-11-11 전에는 `"seq|1,0|..."` 글; 차의 입력 하나 5바이트).

```rust
// shared.rs: 두 쪽이 같은 규칙
#[derive(Clone, Copy, Debug, Default, PartialEq)]
pub struct Keys { pub dir: i8, pub dash: bool }
impl Input for Keys {
    fn put(&self, b: &mut Vec<u8>) { b.extend([self.dir as u8, self.dash as u8]); }
    fn get(r: &mut Reader) -> Option<Keys> {
        let [d, b] = r.take::<2>()?;
        Some(Keys { dir: (d as i8).clamp(-1, 1), dash: b != 0 })
    }
}

#[derive(Clone, Debug, PartialEq)]
pub struct Dasher { pub x: f64, pub stamina: f64 }
impl Rollback for Dasher {
    type Input = Keys;
    type Env<'e> = (); // 걸음이 읽는 바깥 것(땅, 트랙: `dyn Fn(f64, f64) -> Surface + 'e`), 없으면 ()
    fn step(&mut self, k: &Keys, _: &()) {
        let dashing = k.dash && self.stamina > 0.0;
        self.x += if dashing { 12.0 } else { 4.0 } * k.dir as f64 * DT;
        self.stamina = (self.stamina + if dashing { -2.0 } else { 0.5 } * DT).clamp(0.0, 1.0);
    }
    fn values(&self) -> Vec<f64> { vec![self.x, self.stamina] }
    fn set_values(&mut self, v: &[f64]) -> bool {
        let [x, s] = v else { return false };
        (self.x, self.stamina) = (*x, s.clamp(0.0, 1.0));
        true
    }
    fn pose(&self) -> ([f64; 3], [f64; 3]) { ([self.x, 0.0, 0.0], [0.0; 3]) } // 고쳐질 때 그리는 자리를 부드럽게
}
```

서버 쪽 `Driven<Dasher>`(`take`, `run(dt, &())`, `to_bytes` / `load`, `state_packet`), 게임 쪽 `Predicted<Dasher>`(`step`, `packet`,
`heard`, `drawn`)는 위의 탈것과 똑같이 씁니다. 통계: `Predicted`의 `agreed` / `corrections` / `missed`, `Driven`의 `filled`(입력이 늦어
마지막 것으로 걸은 걸음) / `dropped`(시계보다 많이 보내 버린 입력).

### 플레이어 몸을 시뮬로 움직이기 (`Player::drive`)

위의 `Dasher`처럼 시뮬이 플레이어 몸 자체라면(대시, 갈고리, 몸이 곧 탈것), 걷기 검사가 대시를 "너무 빠르다"고 되돌리지 않게 서버에 그 시뮬의
자리를 알려 주세요. 걸려 있는 동안 서버는 **자기 시뮬의 자리를 진짜로** 삼고, 게임이 보고한 자리는 그 근처(`slack` m 안)인지만 봅니다.
속도·벽·공중은 보지 않으니(시뮬이 판정) 시뮬이 벽을 알아야 하면 `Env`에 넣으세요.

```rust
// 서버 반쪽: 걸음(Tick)마다
d.run(dt, &());
let (p, _) = d.sim.pose();
player.drive(p[0], p[1], p[2], 12.0 * 0.3 + 1.0); // 속도 × 왕복 시간 정도 + 1 m (최대 16)
// 끝나면
player.release_drive(); // 시뮬의 마지막 자리부터 다시 걷기로 판정
```

```rust
// 게임 반쪽: 프레임마다
pred.step(keys, &());
let (p, _) = pred.drawn();
Me::set_position(p[0], p[1], p[2]);
```

- 보고가 시뮬 자리에서 `slack`보다 멀면 시뮬 자리로 돌려보냅니다(MoveRefused의 check `"drive"`).
- 0.5초 동안 `drive`를 다시 부르지 않으면 저절로 풀리고, 시뮬의 마지막 자리부터 걷기 검사를 다시 합니다(플러그인이 멈춰도 몸이 풀린 채로 남지 않음).
- 걸려 있는 동안 그 자리는 속도 제한 없이 다른 플레이어에게 전달됩니다.

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
    Registry::item("magic_staff", &ItemDef::new("마법 지팡이").usable().kind(ItemKind::Misc).icon("res://plugins/riding/staff.png")
        .model("res://plugins/riding/staff.glb").action("cast").with("hit", "0.45"));
}

#[on(Use)]
fn cast(e: Use) {
    if e.id() != "magic_staff" { return }
    let p = e.player();
    let ((x, z), (fx, fz)) = (p.position(), p.facing());
    let (tx, tz) = (x + fx * 7.0, z + fz * 7.0);
    e.world().strike(tx, tz, 1.8, 12);                                    // 결과: 서버 (vanilla::VanillaWorld)
    p.hud().send_text("bolt", &pack(&((x, z), (tx, tz))));               // 연출: 게임 쪽에
}

// client.rs: 구슬이 손에서 날아감 (이 플레이어에게만)
let Some(((x, z), (tx, tz))) = p.read::<((f64, f64), (f64, f64))>() else { return };
let id = Local::spawn("res://plugins/riding/orb.png", x, y, z);
Local::glide_to(id, tx, y, tz, 0.35);
```

몸의 크기도 판정됩니다: `Player::set_body(반폭, 키)`(게임의 캡슐과 서버의 걸음 판정이 함께).

## 예제

- `plugins/flight` 비행: Y로 날기 시작하고 다시 Y로 내려옴. W/S 앞뒤, A/D 돌기, Space 위로, Shift 아래로. 규칙은 `shared.rs` 하나,
  나는 동안 그 사람의 `air` `speed` `walls` 검사를 끄고 `PlayerMove`에서 그 규칙으로 판정.
- `plugins/riding` 탈것과 지팡이: 마을 소에 E로 올라타면 두 배 빨리 달림(서버가 그 빠르기로 판정), J로 내림, `/소`로 옆에 부름.
  `/지팡이`로 받는 마법 지팡이를 쓰면 시전 동작과 함께 앞쪽에 번개 구슬이 날아가 몬스터를 침.
