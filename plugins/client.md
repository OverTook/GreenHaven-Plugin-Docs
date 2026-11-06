---
title: 게임 쪽 코드
nav_order: 6.3
parent: 플러그인
redirect_from:
  - /client
  - /client.html
---

# 게임 쪽 코드 (`client.wasm`, `greenhaven-client`)
{: .no_toc }

1. TOC
{:toc}

로블록스의 LocalScript처럼, 플러그인은 **접속한 게임 안에서 도는 코드**를 함께 가질 수 있습니다. 매 프레임 바뀌는 HUD,
카메라 연출, 화면 번쩍임, 자기에게만 보이는 파티클, 키 입력, 새 이동 방식처럼 서버를 오가면 늦거나(온라인이면 수십 ms)
너무 잦은 것들을 게임이 바로 그립니다. 그러면서도 **결과를 정하는 권한은 모두 서버에 남습니다**: 게임 쪽 코드에는 상태를
바꾸는 함수가 아예 없습니다.

## 두 부분

플러그인 하나가 크레이트 하나에서 두 부분으로 빌드됩니다.

| | `server.wasm` (`greenhaven-plugin`) | `client.wasm` (`greenhaven-client`) |
|---|---|---|
| 어디서 | 서버에서만 | 접속한 모든 게임 안의 샌드박스에서 |
| 하는 일 | 결과를 정함: 아이템, 돈, 이동 판정, 전투, 저장, 월드 | 보이고 느껴지는 것만: 자기 화면의 HUD(매 프레임), 직접 그리는 UI, 카메라, 화면 페이드·번쩍임·셰이더, 자기에게만 보이는 파티클·소리·음악, 키·마우스, 자기에게만 보이는 물체(`Local`: 모델, 실행 중 만든 메시, 3D 글자), 셰이더 재질, 엔진에 묻기(레이캐스트, 땅 높이, 길), 이동 넘겨받기, 빠른 패킷 |
| 상태 바꾸기 | 됨 | **함수가 아예 없음**: 쓰면 컴파일이 안 되고, 게임도 연결하지 않음 |

게임 쪽은 **요청만** 하고, 서버가 판정한 결과를 그립니다. 게임 쪽 코드를 고친 사람이 할 수 있는 것은 자기 화면을 바꾸는
것뿐입니다: 아이템도 돈도 위치 판정도 서버의 것입니다([이동 방식 만들기](moving)의 예측도 서버가 다시 판정함).

`client.wasm`이 없는 플러그인(지금까지의 플러그인)은 그대로 서버 쪽만으로 동작합니다.

## 크레이트 모양

`src/shared.rs`(채널 이름과 데이터 형식, 두 쪽이 함께 쓰는 규칙), `src/server.rs`, `src/client.rs`를 두고 Cargo.toml에 feature
둘을 둡니다.

```toml
[lib]
crate-type = ["cdylib"]

[features]
default = ["server"]
server = ["dep:greenhaven-plugin"]
client = ["dep:greenhaven-client"]

[dependencies]
greenhaven-plugin = { path = "../../sdk/plugin", optional = true }
greenhaven-client = { path = "../../sdk/client", optional = true }
```

```rust
// src/lib.rs
mod shared;
#[cfg(feature = "server")] mod server;
#[cfg(feature = "client")] mod client;
```

HUD 요소 `El`과 `Anchor`는 두 SDK가 같은 것을 씁니다(`greenhaven-common`: 데이터뿐인 공통 크레이트). 서버 쪽에서 쓰던 요소를
그대로 게임 쪽에서 매 프레임 그릴 수 있습니다.

## 빌드

GreenHaven-Server의 `plugins/` 아래에서 `python tools/build_plugins.py <이름>`이 두 번 빌드합니다.

| 결과 | 빌드 |
|---|---|
| `server.wasm` | `cargo build --release --target wasm32-unknown-unknown` (기본 feature `server`) |
| `client.wasm` | 크레이트에 `client` feature가 있을 때: `--no-default-features --features client`로 한 번 더 (`src/server.rs`는 컴파일되지 않음) |

빌드한 뒤 각 파일이 **무엇을 가져다 쓰는지**(import) 검사합니다. `client.wasm`이 게임의 `"ghc"` 말고 다른 것(서버의 `"gh"`)을
가져다 쓰면, `server.wasm`이 `"ghc"`를 가져다 쓰면 빌드가 실패합니다. 클라이언트 빌드에는 서버 SDK 크레이트가 아예 없으므로
`client.rs`에서 `Player::give` 같은 것을 쓰면 컴파일 오류입니다.

`code.wasm`은 `server.wasm`의 예전 이름입니다. 서버는 그것도 계속 읽고, `build_plugins.py`는 새로 빌드할 때 옛 `code.wasm`을 지웁니다.

## 게임이 받고 돌리는 법

- **받기**: `client.wasm`은 플러그인 zip(`assets/`와 함께, 서버의 `<data>/.plugins/<이름>.zip`)에 들어가 리소스 팩과 같은 길로
  접속할 때 받습니다(제공 목록, sha256 확인, 끊기면 이어 받기).
- **알림**: 서버의 플러그인 중 게임 안에서 코드를 돌리는 것이 있으면 접속할 때 알립니다("이 서버의 플러그인 N개는 이 게임
  안에서도 코드를 실행해요. 화면·카메라·효과만 다루는 격리된 환경에서만 돌아요.").
- **샌드박스**: 게임의 네이티브 `PluginRuntime`(wasmtime)이 플러그인마다 따로 돌립니다.
  - 호출 한 번에 연료 5 000 000 (끝나지 않는 반복은 그 플러그인만 멈추고 게임은 계속), 메모리 32 MB.
  - 호출 한 번에 게임에 남기는 작업(HUD, 카메라 …) 256개까지, 작업이나 글 하나 64 KB까지 (메시는 4 MB까지).
  - `"ghc"` 함수 말고는 아무것도 연결되지 않습니다. 다른 것을 가져다 쓰는 모듈은 로드되지 않습니다. 파일·네트워크도 없습니다.
- PC에서 확인했습니다. Android(Cranelift JIT)와 iOS(Pulley 인터프리터)는 네이티브 라이브러리 설정만 되어 있고 아직 빌드해 확인하지 않았습니다. 게임 쪽 코드가 돌지 않는 게임에서는 서버 쪽의 결과만 보입니다.
- 서버를 떠나면 그 서버의 플러그인이 띄운 것, 넘겨받은 키·이동·카메라가 모두 게임으로 돌아옵니다.

## 핸들러

```rust
// src/client.rs
use crate::shared::*;
use greenhaven_client::*;

greenhaven_client::client! { load => loaded, frame => frame, packet => heard, input => key }  // 그리고 click => …

fn loaded(_: Load) { log("내 플러그인: 게임 쪽 로드됨"); }

fn frame(f: Frame) {   // 매 프레임 (f.dt(), f.time())
    Hud::add("t", &El::text(&format!("{:.1}", f.time())).anchor(Anchor::Top));
}

fn heard(p: Packet) {  // 서버 쪽이 보낸 것
    if p.channel() == "boom" { Camera::shake(0.3, 0.5); Screen::flash("ffffff", 0.2); }
}

fn key(i: Input) {     // 패널이 열려 있지 않을 때의 키·마우스
    if i.key() == "Q" && i.pressed() { send("cast", ""); }
}
```

`client!`에는 여덟 중 쓰는 것만 적습니다.

| 핸들러 | 언제 | |
|---|---|---|
| `load` → `Load` | 접속해서 이 플러그인을 불러왔을 때 한 번 | |
| `frame` → `Frame` | 게임이 그리는 매 프레임 | `dt()` 지난 프레임부터의 초, `time()` 로드된 뒤의 초 |
| `packet` → `Packet` | 서버 쪽이 이 플러그인의 채널로 보낸 것(`Hud::send_text` …, 빠른 패킷 `Hud::send_fast`), 게임의 `"window"` 패킷 | `channel()` `data()`, `fast()` 빠른 패킷으로 왔는지 |
| `input` → `Input` | 게임의 패널이 열려 있지 않을 때 키·마우스 버튼을 누르거나 뗌 | `key()` 이름(`"Q"` `"F5"` `"Space"` `"Shift"` `"Mouse1"`), `pressed()` |
| `click` → `Click` | 이 플러그인의 버튼·입력 칸을 누름 (HUD에서든 [월드 속 패널](#직접-그리는-ui)에서든; 같은 누름이 서버 쪽 `Packet`으로도 감) | `on()` 그 요소의 `on`, `data()` 입력 칸에 쓴 글 |
| `action` → `Action` | [액션](#액션과-터치-버튼)(`Input::bind`)의 키·마우스·패드·터치 버튼을 누르거나 뗌 | `name()` 액션 이름, `pressed()` |
| `step` → `Step` | 고정 스텝, 1초에 60번 (게임의 물리 틱): 서버와 같은 코드(`src/shared.rs`)로 미리 계산할 것. 그리기는 `frame`에서 | `n()` 몇 번째, `dt()` 한 스텝의 초 |
| `chat` → `ChatLine` | 이 게임의 채팅 상자가 보여 주는 줄 하나 (다른 사람의 들린 줄, 이 플레이어가 보낸 줄, 서버의 알림; 채팅 필터의 별표 그대로) | `text()`, `sender()` 채팅에 보이는 이름 (내 것은 `text("me")`, 알림은 `""`), `channel()` (`""` 근처, 팀 이름, 플러그인의 채널, `"sys"` 알림), `rich()` |

전역 변수(`static mut`)는 서버를 떠날 때까지 남습니다. 시간은 프레임 수가 아니라 `Frame::time()` / `dt()`로 재세요.

## 서버 쪽과 주고받기

**요청과 답** (로블록스의 RemoteFunction 흉내, 엔진 변경 없이): 게임 쪽 `request(채널, 데이터)`는 번호를 붙여(`"<번호>|<데이터>"`)
보내고 그 번호를 돌려줍니다. 서버 쪽은 `split_request(&e.data())`로 번호와 데이터를 꺼내 판정하고, 답을 `reply_data(번호, 답)`으로
써서 자기 채널로 보냅니다. 게임 쪽 `packet`에서 `p.reply()`가 `Some((번호, 답))`이면 그 요청의 답입니다. 기다리는 함수는 없습니다
(게임 쪽은 멈추지 않음): 짝은 번호로 맞추세요. 예: `plugins/arcade`.

로블록스의 RemoteEvent와 같습니다.

| 방향 | 보내는 쪽 | 받는 쪽 |
|---|---|---|
| 게임 → 서버 | 게임 쪽 `send(채널, 데이터)` | 서버 쪽 [`Packet`](events#packet) 이벤트 (`channel()` `data()` 4 KB까지 `player()`) |
| 서버 → 게임 | 서버 쪽 `player.hud().send_text(채널, 데이터)` (`World::hud()`면 월드 모두) | 게임 쪽 `packet` |

- 게임 쪽은 플러그인 하나가 **1초에 8개까지** 보냅니다(더 보낸 것은 버려짐). 서버의 자동화 한도(플레이어의 행동 1초에 10개)도 그대로입니다.
- 서버 쪽 `Packet`은 플레이어의 행동처럼 판정되므로 거기서 `give` `add_gold` …가 됩니다. 받은 데이터는 믿지 말고 판단의 근거로만 쓰세요.
- 서버 쪽에서 등록한 단축키(`Hud::key_action`)도 그대로 서버 쪽 `Packet`으로 갑니다: 키는 서버 쪽에 두고 결과만 게임 쪽이 그려도 됩니다(샘플 `cutscene`).
- 채널 이름과 데이터 형식은 `shared.rs`에 상수와 함수로 두면 두 쪽이 어긋나지 않습니다.

```rust
// shared.rs
pub const RING: &str = "ring";   // 게임 → 서버: 울려 주세요
pub const RANG: &str = "rang";   // 서버 → 게임: "x,y,z" 울린 곳
// server.rs
#[on(Packet)]
fn asked(e: Packet) {
    if e.channel() != RING { return }
    let p = e.player();
    p.give("mana_stone", 1);                       // 결과는 서버가
    p.hud().send_text(RANG, "3.00,1.50,4.00");
}
// client.rs
fn heard(p: Packet) {
    if p.channel() == RANG {                       // 연출은 게임이
        Camera::look_at(3.0, 1.5, 4.0, 0.4);
        Screen::flash("fff4c0", 0.35);
    }
}
```

## 빠른 통신

많이, 자주 오가는 것(스틱의 방향, 조준, 실시간 게임의 입력)은 데이터그램으로 보냅니다.

| 방향 | 보내는 쪽 | 받는 쪽 |
|---|---|---|
| 게임 → 서버 | 게임 쪽 `send_fast(채널, 데이터)` | 서버 쪽 [`FastPacket`](events#fastpacket) 이벤트 (`channel()` `data()` `player()`; 그 플러그인에만) |
| 서버 → 게임 | 서버 쪽 `player.hud().send_fast(채널, 데이터)` (`World::hud()`면 월드 모두) | 게임 쪽 `packet` (`Packet::fast()`가 `true`) |

- 플레이어 한 명에 **1초에 60개까지**, 데이터는 **1000바이트까지**.
- 순서를 지키지 않고, 잃은 것은 다시 보내지 않습니다: 늘 최신 값을 보내는 것(지금의 방향)에 쓰세요.
- **행동이 아닙니다**: 서버 쪽 `FastPacket`에서는 아이템·골드 같은 플레이어의 것을 바꾸지 못합니다. 꼭 가야 하는 것, 결과가
  있는 요청은 `send` / `send_text`로.

```rust
// client.rs: 매 프레임 조준 방향을
fn frame(_: Frame) { send_fast("aim", &format!("{:.3}", Camera::yaw())); }
// server.rs
#[on(FastPacket)]
fn aim(e: FastPacket) {
    if e.channel() == "aim" { e.player().set("aim", e.data().parse().unwrap_or(0.0)); }
}
```

## 소리

이 플레이어에게만 들리는 소리와 음악입니다(모두가 듣는 것은 서버 쪽 `World::sound` / `play_music`). `id`는 플러그인이 붙이는
이름이고, 경로는 게임의 것이나 플러그인 `assets/`의 `res://….ogg` / `.wav`.

| | |
|---|---|
| `Sound::play(id, path, volume_db, pitch, looped, at, music)` | 틀기: `volume_db` dB(0 그대로), `pitch`(1 그대로), `looped` 반복, `at` 월드의 자리 `Some((x, y, z))`(칸) 또는 `None`(어디서나), `music`이면 음악 버스로 (그동안 게임의 음악은 조용히) |
| `Sound::set(id, volume_db, pitch, secs)` | 소리 크기와 피치를 `secs`초에 걸쳐 바꿈 |
| `Sound::move_to(id, x, y, z)` | 월드의 소리를 옮김 |
| `Sound::stop(id, secs)` | `secs`초에 걸쳐 줄이며 멈춤 |

```rust
Sound::play("hum", "res://plugins/my_plugin/hum.ogg", -12.0, 1.0, true, Some((x, y, z)), false);
```

플러그인이 내려놓거나 서버를 떠나면 모두 멈춥니다.

소리 효과와 붙이기 (로블록스의 SoundService 효과, 소리를 파트에 넣기):

| | |
|---|---|
| `Sound::effect(key, bus, effect)` / `clear_effect(key)` | 버스에 효과: `Effect::LowPass { hz, q }` `HighPass { hz, q }` `Reverb { room, wet }` `Distort { drive }` `Echo { ms, feedback }`. `Bus::Plugin` 플러그인 소리만 (`Sound::play`의 것은 모두 이 버스로), `Bus::All` 들리는 모든 것 (섬광탄의 멍멍함, 물속), `Bus::Music`, `Bus::Sfx`. 모든 플러그인 합쳐 8개 |
| `Sound::duck(bus, db, secs)` | 그 버스 소리를 `db`(0 그대로, -60까지)로 `secs`초에 걸쳐 줄였다가, 0으로 되돌림. 플레이어의 음량 설정은 건드리지 않음 |
| `Sound::attach(id, target)` | 그 소리가 대상을 따라감 (1 m 위; 남의 차의 엔진 소리, 날아가는 상자의 소리). 자리 없이 튼 소리는 그 자리부터 3D로 |

```rust
// 섬광탄: 2초 동안 귀가 멍멍하게, 그 뒤 1초에 걸쳐 돌아옴 (frame에서 시간을 재서)
Sound::effect("deaf", Bus::All, Effect::LowPass { hz: 400.0, q: 0.3 });
Sound::duck(Bus::All, -14.0, 0.1);
// ... 2초 뒤
Sound::clear_effect("deaf");
Sound::duck(Bus::All, 0.0, 1.0);
```

서버를 떠나면 효과와 줄인 음량이 모두 게임의 것으로 돌아옵니다.

## 직접 그리는 UI

`El`로 모자라면 캔버스에 직접 그립니다: 게이지, 레이더, 그래프 … 원하는 위젯을 무엇이든. 매 프레임 다시 그려도 됩니다.
좌표는 캔버스 자신의 픽셀(왼쪽 위가 0, 0)입니다.

| `Draw::new()` 다음에 | |
|---|---|
| `.rect(x, y, w, h, color, fill, width)` | 사각형 (`fill` false면 `width` px 테두리) |
| `.line(x0, y0, x1, y1, color, width)` | 선 |
| `.circle(x, y, r, color)` | 채운 원 |
| `.arc(x, y, r, a0, a1, color, width)` | 호 (라디안, 0이 오른쪽, 화면에서 시계 방향) |
| `.polygon(&[x, y, x, y, …], color)` | 채운 다각형 |
| `.text(x, y, t, color, size)` | 글 |
| `.image(path, x, y, w, h)` | `res://` 그림 |
| `.show(id, anchor, (x, y), (w, h))` | 이 플러그인의 캔버스 `id`에 그림 (처음이면 그 앵커·자리·크기로 만듦) |

```rust
fn frame(f: Frame) {
    let t = (f.time() % 3.0) / 3.0;
    Draw::new()
        .circle(40.0, 40.0, 36.0, "00000088")
        .arc(40.0, 40.0, 30.0, 0.0, t * std::f64::consts::TAU, "4fd1ff", 6.0)
        .text(24.0, 46.0, &format!("{:.0}%", t * 100.0), "ffffff", 16)
        .show("gauge", Anchor::TopRight, (-20.0, 90.0), (80.0, 80.0));
}
```

**월드에 붙이기**: `pin(id, Some((x, y, z)))`는 이 플러그인의 HUD 요소(`Hud::add`)를 월드의 한 점 위에 붙여 둡니다(머리 위 바,
물건 위 이름표; 카메라 뒤로 가면 숨김). `pin(id, None)`이면 앵커의 자리로 돌아갑니다.

**월드 속 UI 패널**: `Local::spawn_panel(&El, x, y, z, width_m, (px_w, px_h), face_camera)` → id. 어떤 HUD 요소든(패널·글·그림·바·
버튼·입력 칸·캔버스, 자식까지) `(px_w, px_h)` 픽셀로 그려 월드에 선 너비 `width_m` m의 판에 붙입니다(`face_camera`면 늘 카메라를 봄).
그 버튼은 마우스로 누르고 입력 칸에는 씁니다: HUD에서처럼 동작하고, 그 클릭은 게임의 도구로 가지 않습니다.
`Local::set_panel(id, &El)`로 다시 그리고, `Local::remove(id)`로 없앱니다.

버튼이나 입력 칸을 누르면(HUD에서든 월드 속 패널에서든) 서버 쪽에는 그 `on` 채널의 [`Packet`](events#packet)이, 게임 쪽에는
`click` 이벤트(`Click::on()` `data()`)가 함께 옵니다. 게임 쪽은 바로 반응하고(흔들림, 소리), 결과는 서버 쪽이 정해 보냅니다.

```rust
// shared.rs
pub const PRESS: &str = "press";     // 패널의 버튼
pub const PRESSED: &str = "pressed"; // 서버 → 게임: 센 횟수

// client.rs
greenhaven_client::client! { load => loaded, packet => heard, click => clicked }
static mut PANEL: i64 = 0;

fn board(n: &str) -> El {
    El::panel("parch").anchor(Anchor::TopLeft).size(360.0, 220.0)
        .child(El::text(&format!("서버가 센 누름: {n}")).anchor(Anchor::Top).pos(0.0, 40.0).font_size(20))
        .child(El::button("눌러 보세요", PRESS).anchor(Anchor::Bottom).pos(0.0, -20.0).size(200.0, 56.0))
}
fn loaded(_: Load) {
    let (x, y, z) = Me::position();
    unsafe { PANEL = Local::spawn_panel(&board("0"), x + 3.0, y + 1.6, z, 1.8, (360.0, 220.0), true) };
}
fn clicked(c: Click) {
    if c.on() == PRESS { Camera::shake(0.05, 0.2) }   // 바로 (서버의 답보다 먼저)
}
fn heard(p: Packet) {
    if p.channel() == PRESSED { Local::set_panel(unsafe { PANEL }, &board(&p.data())) }
}

// server.rs
#[on(Packet)]
fn asked(e: Packet) {
    if e.channel() == PRESS {
        let p = e.player();
        let n = p.get("presses") + 1.0;
        p.set("presses", n);
        p.hud().send_text(PRESSED, &format!("{n}"));
    }
}
```

## 그래픽

**셰이더 재질**: Godot 셰이딩 언어로 이 플러그인의 재질을 만듭니다.

| | |
|---|---|
| `Material::create(id, kind, code)` | `kind` `"spatial"`(월드의 물체) / `"canvas_item"`(화면). 코드는 16 KB까지, 게임이 컴파일하기 전에 검사함 (아래 「셰이더 검사」) |
| `Material::set(id, name, v)` | uniform 숫자 |
| `Material::set_vec(id, name, &[..])` | uniform 벡터·색 (숫자 2~4개) |
| `Local::set_material(local_id, id)` | 자기에게만 보이는 물체에 (`""` 원래대로) |
| `Entities::set_material(entity_id, id)` | 서버 쪽 엔티티를 이 게임에서만 그 재질로 (`""` 원래대로) |
| `Screen::shader(id)` | 화면 전체를 `"canvas_item"` 재질로 (셰이더에서 `uniform sampler2D screen : hint_screen_texture;`로 화면을 읽음; `""` 끄기) |

**셰이더 검사**: 플러그인의 셰이더가 게임을 멈추지 못하게, 게임은 컴파일하기 **전에** 코드를 검사하고 걸리면 그 재질을 만들지
않습니다(게임의 로그에 이유가 한 줄).

| 안 되는 것 | 까닭 |
|---|---|
| 반복문 `for` `while` `do` | GLSL에는 재귀가 없으니, 반복만 없으면 한 픽셀의 계산이 코드 길이로 묶입니다: 셰이더가 GPU를 멈출 수 없음 |
| 텍스처 읽기 16번 넘게 | (`texture…` `texelFetch`) 한 픽셀의 비용을 묶음 |
| `#` (`#include` `#define` …) | 다른 파일·매크로 없음 |
| 자기 `shader_type` | 게임이 `kind`로 붙임 |
| (`spatial`만) `POSITION`, `render_mode`의 `skip_vertex_transform` `world_vertex_coords`, `vertex()` 안의 `return` | 월드 곡률을 벗어남 (아래) |

**월드 곡률**: `spatial` 셰이더에는 게임이 월드의 곡률을 넣습니다. 곡률 함수를 포함하고 `vertex()`의 끝에 꼭짓점을 휘게 하는 줄을
붙이며, `vertex()`가 없으면 그 줄만 든 `vertex()`를 줍니다. 그래서 플러그인이 그린 물체도 다른 것처럼 멀리서 지평선 아래로
내려갑니다. 위 표의 마지막 줄이 막히는 것은 이 줄을 건너뛰거나 무효로 만들기 때문입니다.

**실행 중 감시**: 플러그인 재질이 쓰이는 동안 GPU의 한 프레임이 80 ms를 넘는 것이 30프레임 이어지면, 게임은 플러그인의 재질을
**모두** 떼고(자기에게만 보이는 것, 서버 엔티티의 재질, 화면 셰이더) 플레이어에게 "서버 플러그인의 셰이더가 너무 무거워서
껐어요."라고 알립니다.

**실행 중 메시**: `mesh(id, vertices, normals, colors, indices)` — 삼각형(인덱스 셋마다 하나), 꼭짓점 x y z(m), 법선과 색(r g b a)은
없어도 되고 있으면 꼭짓점 수만큼, 65536 꼭짓점까지. `Local::spawn("mesh:<id>", x, y, z)`로 세웁니다.

**3D 글자와 변형**: `Local::spawn_text(글, x, y, z, color, size)` → id(늘 카메라를 보는 글자, `size` px), `Local::set_text(id, 글)`,
`Local::set_transform(id, yaw, scale)`(y축 회전 라디안, 크기).

```rust
const GLOW: &str = "uniform vec4 tint : source_color = vec4(0.4, 0.8, 1.0, 1.0);
void fragment() { ALBEDO = COLOR.rgb * tint.rgb; EMISSION = tint.rgb * (0.6 + 0.4 * sin(TIME * 3.0)); }";

fn loaded(_: Load) {
    let (b, h) = (0.6, 1.2);
    let v = [-b, 0.0, -b, b, 0.0, -b, b, 0.0, b, -b, 0.0, b, 0.0, h, 0.0];
    mesh("pyramid", &v, &[], &[], &[0, 1, 4, 1, 2, 4, 2, 3, 4, 3, 0, 4]);
    Material::create("glow", "spatial", GLOW);
    let (x, y, z) = Me::position();
    let id = Local::spawn("mesh:pyramid", x, y, z + 3.0);
    Local::set_material(id, "glow");
}
```

예: `plugins/showcase`(화면 실험실).

## 함수

### 읽기

| | |
|---|---|
| `num(k)` → `f64` | 이번 호출에 게임이 알려 준 숫자 (없으면 NaN): `dt` `time` `me.x` `me.y` `me.z`(이 플레이어, 칸) `me.yaw` `cam.x` `cam.y` `cam.z` `screen.w` `screen.h` `mouse.x` `mouse.y` `minute`(하루의 시각) `day`, 입력의 `mouse.dx` `mouse.dy` `wheel` `move.x` `move.y` `look.x` `look.y` ([액션과 터치 버튼](#액션과-터치-버튼)) |
| `text(k)` → `String` | `me`(이 플레이어 이름) `server`(어디), 이벤트의 `channel` `data` `key` |
| `log(t)` | 게임의 로그에 한 줄 |
| `send(channel, data)` | 서버 쪽에 패킷 (위) |
| `request(channel, data)` → `u32` | 번호를 붙인 요청 ([서버 쪽과 주고받기](#서버-쪽과-주고받기)) |
| `send_fast(channel, data)` | 서버 쪽에 빠른 패킷 ([빠른 통신](#빠른-통신)) |

### Hud

이 플레이어의 화면에만, 서버를 거치지 않고 그립니다(매 프레임 바꿔도 됨). 요소는 [화면](screen#요소-el)의 `El`과 같습니다.

| | |
|---|---|
| `Hud::add(id, &El)` / `set(id, &El)` / `remove(id)` | 이 플러그인의 요소 |
| `Hud::hide(part)` / `show(part)` | 게임 HUD의 부분: `clock` `status` `nearby` `chat` `hotbar` `bars` `quests` `prompt` `toasts` `plugins` `menu` |

### Camera

이 플레이어의 시야만 바꿉니다. 플러그인이 `release`하거나 서버를 떠나면 게임이 되찾습니다.

| | |
|---|---|
| `Camera::shake(세기, 초)` | 흔들기: 최대 `세기` m, `초`에 걸쳐 잦아듦 |
| `Camera::look_at(x, y, z, 초)` | 그곳을 보게 돌림, `release`까지 |
| `Camera::move_to(x, y, z, lx, ly, lz, 초)` | 그 자리로 옮겨 (lx, ly, lz)를 봄 (컷신의 한 장면), `release`까지 |
| `Camera::set(x, y, z, lx, ly, lz)` | 이번 프레임에 바로 그 자리 (매 프레임 부르면 플러그인의 카메라) |
| `Camera::follow(ox, oy, oz, look_up, turn)` | 매 프레임 플레이어를 오프셋에서 따라감 (`turn`이면 몸 방향으로 돌림), 발에서 `look_up` 위를 봄 |
| `Camera::orbit(x, y, z, distance, yaw, pitch, spin)` | 그 둘레를 돌기 (라디안, `spin` 초당 라디안) |
| `Camera::fov(도, 초)` | 화각 (0: 게임의 것) |
| `Camera::first_person(bool)` | 1인칭 / 3인칭 |
| `Camera::mouse_look(bool)` | 마우스가 카메라를 돌릴지 (끄면 플러그인만 돌림) |
| `Camera::yaw()` → `f64` | 카메라가 보는 방향 (땅 위의 라디안, 0이 +z): W 같은 키의 "앞" |
| `Camera::release(초)` | 게임의 카메라로 되돌림 |
| `Camera::pitch()` `forward()` → `(x, y, z)` `position()` | 위아래 각(라디안), 보는 방향(단위 벡터, 칸), 자리: 히트스캔의 시작과 방향 |
| `Camera::screen_ray(px, py)` → `Option<(from, dir)>` `to_screen(x, y, z)` → `Option<(sx, sy)>` | 화면의 점 → 광선, 세계의 점 → 화면 (뒤면 `None`) |
| `Camera::kick(위 도, 옆 도, 돌아오는 초)` | 반동: 게임 카메라를 돌렸다 서서히 되돌림 (30도까지 쌓임, `forward`에도 들어감) |
| `Crosshair::show(글자, 색, 크기)` `hide()` | 화면 가운데 십자선 (HUD 요소 `aim.crosshair`) |

### Screen, 파티클, 소리

| | |
|---|---|
| `Screen::fade(색, 불투명도, 초)` | 화면을 그 색(`"000000"`)으로 덮음 (0 투명 ~ 1 가득), 그대로 남음 |
| `Screen::flash(색, 초)` | 번쩍임, `초`에 걸쳐 사라짐 |
| `particle(name, x, y, z)` | 이 플레이어에게만 보이는 파티클 (`"fire"` `"smoke"` `"sparkle"` `"splash"` `"leaf"` `"hit"` 또는 `res://….png`) |
| `sound(name, x, y, z)` | 이 플레이어에게만 들리는 소리 (`"hit"` `"pickup"` `"click"` … 또는 `res://….ogg`) |

모두가 보고 들어야 하는 것은 서버 쪽 `World::particle` / `sound`입니다.

### Local — 자기에게만 보이는 것

요청의 결과를 답이 오기 전에 미리 그리거나(손에서 바로 날아가는 화염구: 서버의 엔티티가 오면 그것이 이어받음), 연출용
물체를 둡니다. 모델은 서버 쪽 엔티티와 같습니다(`res://….glb`, 그림이면 늘 카메라를 보는 스프라이트).

| | |
|---|---|
| `Local::spawn(model, x, y, z)` → `i64` | 만들고 id |
| `Local::glide_to(id, x, y, z, 초)` | 그곳으로 `초`에 걸쳐 (0: 바로) |
| `Local::play_anim(id, clip)` | 클립 |
| `Local::remove(id)` | 없앰 |
| `Local::spawn_text` `set_text` `set_material` `set_transform` | 3D 글자, 재질, 회전·크기 ([그래픽](#그래픽)) |
| `Local::spawn_panel(&El, x, y, z, width_m, (px_w, px_h), face_camera)` → `i64` / `Local::set_panel(id, &El)` | 월드에 선 UI 패널 (마우스로 누르고 씀), 다시 그리기 ([월드 속 UI 패널](#직접-그리는-ui)) |
| `Local::attach(id, &AttachTo::Camera \| AttachTo::Bone(Target, "RightHand"), offset, rot)` `detach(id)` | 카메라(뷰모델: x 오른쪽, y 위, −z 앞)나 무언가의 뼈에 들려 매 프레임 따라감 |
| `Local::beam(from, to, 색, 굵기, 초)` | 탄도선·레이저: 사라지며 (64개까지) |
| `Entities::play_anim(id, clip)` | 서버 쪽 엔티티의 클립을 이 게임에서만 (모두가 보는 것은 서버 쪽 `play_anim`) |
| `Me::play_anim(id)` | [감정 표현](models)을 자기 몸에 이 게임에서만 (서 있을 때; 모두가 보는 것은 서버 쪽 `Player::play_anim`) |
| `Me::play_clip(clip, upper, looped, speed)` `Me::stop_clip()` | 걷는 몸 위에 겹치는 클립을 자기 몸에 이 게임에서만 (장전을 답 전에 바로; 모두가 보는 것은 서버 쪽 `Player::play_clip`) |
| `PlayerView::play_clip(clip, upper, looped, speed)` `stop_clip()` | 그 사람의 아바타에 이 게임에서만 |

### World — 엔진에 묻기

스크립트가 하기엔 무거운 일은 엔진이 합니다.

| | |
|---|---|
| `World::raycast(from, to)` → `Option<(x, y, z)>` | 그 선이 처음 닿는 단단한 것 (칸) |
| `World::cast(from, dir, len)` → `Option<Hit>` | 이 게임이 그린 블록, 단단한 것, 다른 플레이어의 히트박스(폭 0.8 m, 1.6 m: 서버의 몸과 같음), 그려진 몬스터(`HitKind::Mob`, `id` 그 번호: 서버가 재는 몸), 서버의 단단한 엔티티 가운데 처음 닿는 것 (`kind`, `id`, `at`, `normal`, `distance`; 자신은 빼고). 그리기 예측: 맞힘은 서버 쪽 `World::cast_for` |
| `World::overlap(lo, hi)` → `Vec<(HitKind, id)>` | 그 상자(한 변 16 m까지) 안의 것 (32개까지) |
| `World::ground(x, z)` → `f64` | 게임이 가진 그곳의 땅 높이 (모르면 NaN) |
| `World::path(from, to)` → `Vec<(x, z)>` | 마을 길 (주민의 길찾기): 꺾이는 점들, 없으면 `[]` |

이것들은 엔진이 메인 스레드에서 하는 일이라 연료에 잡히지 않아요. 그래서 핸들러 한 번에 32번까지만 답하고, 그 뒤는 모르는 것처럼
답해요(`None`, `NaN`, `[]`). 한 번의 op 전체 크기도 8 MB까지예요(mesh 하나는 4 MB).
| `World::id()` → `String` | 지금 있는 월드 (`"world"` 모두의 것, 아니면 서버 쪽 `Server::create_world`로 만든 id) |
| `World::ready()` → `bool` | 월드가 오고 주변 땅이 다 그려졌는지 (서버가 다른 월드로 옮긴 뒤, 보여 줄 때) |

### Balloon — 열기구

게임의 열기구 여행 그대로의 장면입니다(플레이어에게 가장 가까운 정거장의 열기구). 보이는 것뿐이고, 플레이어를 옮기는 것은 서버
쪽(`Player::move_world(.., true)`)입니다: 오르는 동안 옮기면 새 월드의 땅이 그 뒤에서 들어옵니다(이륙하는 열기구는 정거장에서 떼어
두어, 마을이 다시 지어져도 그대로 날아감).

| | |
|---|---|
| `Balloon::lift_off()` | 이륙: 열기구 앞에서 올려다보는 시점, 바구니에 탄 플레이어, HUD는 숨김. 다 오르면 하늘에 둔 채 멈춤 (그동안 카메라는 플러그인 것: `Camera::set` …) |
| `Balloon::land()` | 그때 있는 월드의 가장 가까운 정거장으로 하늘에서 내려앉는 장면 (열기구 앞 시점). 갑판에 내려서면 HUD가 돌아옴 |
| `Balloon::state()` → `i64` | 0 땅, 1 오르는 중, 2 하늘, 3 내려오는 중 |

### 액션과 터치 버튼

키 하나에 직접 묶지 말고 **액션**을 만드세요(로블록스의 ContextActionService). 한 액션에 키보드 키 하나, 마우스 버튼, 패드 버튼,
휴대폰 화면 버튼을 같이 묶고, 무엇으로 누르든 `action` 핸들러가 받습니다.

```rust
greenhaven_client::client! { load => loaded, action => act }

fn loaded(_: Load) {
    Input::bind("boost", &Bind { label: "부스트", keys: &["K"], pad: &["RB"],
        touch: Some(TouchButton { label: "부스트", icon: "" }) });
}

fn act(a: Action) {
    if a.name() == "boost" && a.pressed() { request("boost", ""); }   // 판정은 서버 쪽
}
```

| | |
|---|---|
| `Input::bind(name, &Bind { label, keys, pad, touch })` | 액션 만들기 (다시 부르면 바꿈; 플러그인 하나에 16개까지). `keys`: 키보드 키 하나(`"K"`)와 마우스 버튼(`"Mouse1"` …), `pad`: `"A"` `"B"` `"X"` `"Y"` `"LB"` `"RB"` `"L2"` `"R2"` `"LS"` `"RS"` `"Up"` `"Down"` `"Left"` `"Right"` (Start·Back은 메뉴의 것이라 안 됨), `touch`: 휴대폰 화면 버튼 (`label` 6자까지, 또는 `icon`에 `res://` 그림) |
| `Input::unbind(name)` | 액션 지우기 |
| `Input::axis("move")` → `(x, y)` | 걷기 방향: 화면 조이스틱, W A S D, 패드 왼쪽 스틱 (x 오른쪽, y 앞, -1..1) |
| `Input::axis("look")` → `(x, y)` | 시선: 마우스, 화면 드래그, 패드 오른쪽 스틱 (이번 프레임의 픽셀, x 오른쪽, y 아래) |
| `Input::mouse_delta()` → `(dx, dy)` / `Input::wheel()` | 이번 프레임의 마우스 이동량 (픽셀), 휠 (위로 +) |
| `Input::lock_mouse(bool)` | 마우스 포인터를 가두고 숨김 (FPS 조준: `mouse_delta`를 읽음). 게임의 창이 열리면 풀리고, 놓거나 서버를 떠나면 돌아옴 |
| `Input::device()` → `"kbm"` `"touch"` `"pad"` | 마지막으로 쓴 장치 (HUD를 그에 맞게) |

- **키 바꾸기**: 액션은 서버 쪽 단축키(`Hud::key_action`)처럼 설정 › 조작키에 `label`로 보라색 칩으로 나오고, 플레이어가 다른 키로
  바꿀 수 있습니다(서버마다 저장). 게임이 쓰는 키나 다른 단축키가 먼저 가진 키는 묶이지 않고 접속할 때 알려 줍니다. Esc는 언제나
  게임의 것입니다(`Input::capture`로도 못 가져감).
- **터치 버튼**은 게임의 버튼들 위의 한 줄에 게임이 놓습니다(모든 플러그인 합쳐 8개). 플러그인이 자리를 정하지 않으므로 게임의 버튼·메뉴를
  가리지 못합니다. 화면 버튼과 손가락 탭은 마우스 버튼으로 치지 않습니다(휴대폰에선 터치 버튼이 그 몫).
- 액션으로 묶어도 마우스 버튼의 게임 동작은 그대로입니다: 막으려면 `Input::capture`(예: `"Mouse1"` 도구 사용)를 같이 쓰세요.
- 채팅에 글을 쓰는 중이나 게임의 창이 열려 있을 때는 누름이 오지 않습니다(떼는 것은 옴: 눌린 채로 남지 않음).

### Input과 Me

키를 넘겨받고 플레이어를 직접 움직이는 함수(`Input::capture`, `Me::set_velocity` …)는 [이동 방식 만들기](moving#게임-쪽에서-조작-넘겨받기)에 있습니다.

| | |
|---|---|
| `Me::position()` → `(x, y, z)` / `Me::yaw()` / `Me::name()` | 게임이 그리는 이 플레이어 (판정은 서버의 것) |
| `Me::velocity()` / `Me::on_ground()` | 게임이 움직이는 속도 (칸/초), 발이 땅에 닿았는지 |
| `Me::health()` / `Me::max_health()` | 서버가 마지막으로 알린 체력과 최대 체력 |
| `Me::slot()` / `Me::held()` | 고른 단축바 칸 (0부터), 그 칸의 아이템 id (`""` 없음) |
| `Me::data(key)` → `f64` | 이 플러그인의 서버 쪽이 이 플레이어에게 `Player::set(key, …)`한 값 (마지막으로 온 것; 없으면 NaN) |
| `Input::held(key)` → `bool` | 그 키를 지금 누르고 있는지 |

### 세상 읽기

이 게임에 **온 것만** 읽습니다. 서버가 이 플레이어에게 숨긴 사람(서버 쪽 `hide_from` `set_invisible` `disguise`, `set_spectator`)은
위치도 번호도 오지 않으므로 어떤 게임 쪽 코드로도 알 수 없습니다(그리지 않는 것이 아니라 보내지 않음). 하나하나가 게임의 답이라
한 호출에 32번까지.

| | |
|---|---|
| `Players::list()` / `get(id)` / `near(r)` → `PlayerView { id, pos, yaw, doing }` | 이 게임이 그리는 다른 플레이어 (그려진 자리, 칸; `doing` 0 서기, 1 걷기, 2 달리기, 3 잠, 4 도구, 5 수영, 6 점프, 7 떨어짐) |
| `PlayerView::name()` / `public(key)` → `f64` / `public_text(key)` | 이름, 서버 쪽이 공개한 값 (서버 쪽 `Player::set_public`; 없으면 NaN / `""`) |
| `Entities::list()` / `get(id)` / `near(r)` → `EntityView { id, pos, yaw, pitch, roll }`, `model()`, `public(key)` | 서버 쪽 엔티티 (`"block:stone"` 같은 블록 모습도; 기울기는 서버 쪽 `set_rotation`) |
| `Mobs::near(r)` → `MobView { n, pos, hp }`, `kind()` | 이 층의 몬스터 (`hp` 남은 체력 0-1) |
| `Me::id()` | 이 월드에서 내 번호 (`PlayerView::id`와 같은 것) |
| `Net::ms()` / `Net::rtt()` | 서버 시계 (unix ms), 왕복 시간 (ms) |
| 이벤트 `public` (`PublicChanged::who()` `id()`) | 누군가의 공개 값이 바뀜: `client! { public => f }` |
| `Target::Player(id)` | 외곽선·파티클·궤적의 대상으로 다른 플레이어 |

### 연출: 빛, 외곽선, 파티클, 궤적

모두 이 플레이어의 화면에서만입니다. 서버를 떠나면 게임의 것으로 돌아옵니다. 대상(`Target`)은 `Target::Me`(자기),
`Target::Local(id)`(자기 `Local` 물체), `Target::Entity(id)`(서버 쪽 엔티티가 이 게임에 그려진 것).

| | |
|---|---|
| `Lighting::set(&Light { fog_end, fog_color, ambient, ambient_energy, exposure, glow, saturation, brightness, contrast }, 초)` | 빛 덮어쓰기: `Some`인 것만, 나머지는 게임의 것 (낮밤·날씨는 그 밑에서 계속). `fog_end` 안개 끝 (m), `ambient` 사방의 빛 색, `exposure` 노출 (1 그대로), `glow` 번짐 (0 없음), `saturation` `brightness` `contrast` (1 그대로). `초`에 걸쳐 바뀜 |
| `Lighting::reset(초)` | 게임의 빛으로 되돌림 |
| `Highlight::add(key, target, fill, outline, width, through_walls)` / `remove(key)` | 외곽선과 채움 (로블록스의 Highlight, 모든 플러그인 합쳐 16개): 색 `"rrggbb"` 또는 `"rrggbbaa"` (채움은 알파만큼: `"ff000040"`), `width` m, `through_walls` 벽 너머로도 |
| `Particles::emit(&Emitter { at, on, offset, texture, color, color_end, size, life, rate, count, speed, dir, spread, gravity })` → `i64` / `stop(id)` | 파티클 (로블록스의 ParticleEmitter): `count`개 한 번에 (`life` 뒤 사라짐) 또는 `rate` 초당 (`stop`까지; 이때 `count: 0`), `at` 그 자리 (칸) 또는 `on` 대상에 붙어 `offset`만큼, `texture` `res://` 그림 (`""` 부드러운 점), `color`에서 `color_end`로, `size` m, `speed` m/초로 `dir` 쪽 `spread`도 안에서, `gravity` 아래로 m/초². 모든 플러그인 합쳐 32개, 입자 4096개 |
| `Local::trail(id, color, width, 초)` / `Trail::on(key, target, color, width, 초)` | 지나간 자리에 남는 띠 (로블록스의 Trail): 점마다 `초` 동안 (0: 없앰), 모든 플러그인 합쳐 32개 |

| `Particles::smoke(at, radius, secs, color)` → `i64` | 연막 프리셋: `radius` m 둘레에 부드러운 연기가 `secs`초(60까지) 천천히 오르고 퍼짐, 카메라가 그 안에 들어가면 화면이 그 색으로 뿌옇게 (휴대폰 렌더러에는 볼륨 안개가 없어서). `color` `""` 회색. `stop(id)`로 일찍 끝냄; 파티클 수에 같이 셈 |

### 연출 물리: 파편, 놓아 준 물체, 래그돌

이 게임에서만 도는 물리입니다 (로블록스에서 클라이언트가 계산하는 연출 물리와 같음): 게임마다 조각이 다르게 떨어지고, 서버는
모릅니다. 폭발이 무엇을 했는지는 서버 쪽이 정합니다.

| | |
|---|---|
| `Physics::debris(&Debris { at, count, size, color, model, speed, up, spin, mass, life })` | 파편: `count`개(한 번에 32)의 큐브(`size` m, `color`) 또는 `model`(`res://` 장면)의 사본이 `at`에서 `speed` m/초까지 튀어 나감 (`up` 0-1 그중 위쪽, `spin` 초당 바퀴), `life`초(30까지) 뒤 줄어들며 사라짐. 땅·건물·서로에 튕기고 플레이어와는 안 부딪힘. 모든 플러그인 합쳐 64개: 넘으면 가장 오래된 것부터 |
| `Local::physics(id, vel, spin, mass, life)` | `Local` 하나를 놓아 줌: 그것을 감싼 상자로 강체가 되어 `vel` m/초로 던져짐. 그 뒤 `glide_to`는 안 먹고 `remove`는 먹음; 그 Local을 가리키는 `Target`과 `Sound::attach`는 그대로 따라감. 파편과 같이 셈 |
| `Physics::ragdoll(target, push, secs)` / `unragdoll(target)` | 축 늘어짐: `Target::Me`, `Target::Player(id)`, 아바타 엔티티 (`Target::Entity`)의 몸이 `push` m/초로 밀려 쓰러지고 `secs`초(0이면 `unragdoll`까지) 뒤 클립으로 돌아옴. 게임의 휴머노이드 뼈대(플레이어 동물, 주민, 그 뼈대의 플러그인 모델)만. 그려지는 모양만이라 그 사람의 자리는 서버의 것: 죽음 연출이면 서버 쪽에서 `freeze`. 동시에 8명 |

```rust
Physics::debris(&Debris { at: (x, y + 0.3, z), count: 24, size: 0.2, color: "6b5a48", speed: 7.0, life: 5.0, ..Default::default() });
Particles::smoke((x, y, z), 3.5, 6.0, "");
for o in Players::near(6.0) { Physics::ragdoll(Target::Player(o.id), (0.0, 4.0, 5.0), 2.5); }
```

`Fx::vibrate(ms)`: 휴대폰을 짧게 떨게 함 (로블록스의 HapticService; 500 ms까지, 모든 플러그인 합쳐 1초에 4번; PC에서는 아무것도 안 함).

### Chat — 채팅

`Chat::say(text)`: 플레이어가 채팅 상자에 친 것처럼 이 플레이어의 이름으로 한 줄 (근처에, `!`로 시작하면 팀에게; 서버의 채팅 제한은
플레이어의 것 그대로). 명령어(`/`로 시작)는 보내지 않고, 플러그인마다 2초에 한 줄, 80자까지. 다른 사람의 이름으로는 보낼 수 없습니다.
`Chat::system(text)`: 이 게임에만 보이는 알림 한 줄 (앞에 `[플러그인 이름]`; 1초에 4줄까지). 줄을 읽는 것은 `chat` 핸들러로.
`Chat::bubble_style(player, &Bubble { bg, text, edge, size })`: 플레이어 채팅 말풍선의 모양 (로블록스의 BubbleChatConfiguration):
`player` `Some(id)` 그 사람(`PlayerView::id`, `Me::id`) 또는 `None` 모두, `bg` 카드 색, `text` 글자 색, `edge` 글자 테두리 색
(`""` 게임의 것), `size` 글자 px (0 게임의 것). 모두 비우면 게임의 모양으로.

```rust
greenhaven_client::client! { chat => asked }
fn asked(l: ChatLine) {
    if l.text().trim() == "점수?" && l.channel() != "sys" {
        Chat::system(&format!("내 점수 {}", Me::data("score")));
        if l.sender() != text("me") { Chat::say("저는 3점이에요"); }
    }
}
```

`Emitter`는 `..Default::default()`로 필요한 것만 쓰세요. 값이 이상하면(범위 밖, 글자 대신 숫자 …) 게임은 범위 안으로 줄이거나
무시하고, 멈추지 않습니다.

## 원본 함수 (`"ghc"`)

게임이 연결하는 것은 모듈 `"ghc"`의 함수 여섯뿐입니다. SDK의 함수는 모두 이것들을 감쌉니다. 글을 넘길 때 `(ptr, len)`, 받을 때
`(ptr, cap)`에 복사되고 전체 길이를 돌려줍니다(서버의 ["gh" 함수](abi#약속)와 같은 약속). 목록은 ["gh" 함수 › 게임 쪽](abi#게임-쪽-ghc).

## 예제

- `plugins/cutscene` 연출: G(서버 쪽 단축키)를 누르면 서버가 종 울리기를 판정(10초에 한 번, 마나석 하나)하고, 게임 쪽이 카메라를
  종으로 돌리고 번쩍이며 위쪽에 다음 종까지 남은 시간을 매 프레임 그립니다.
- `plugins/showcase` 화면 실험실: 앞에 셰이더로 빛나는 피라미드(실행 중 만든 메시)와 3D 글자, 그 위에 붙어 다니는 HUD, 오른쪽 위
  직접 그린 게이지, 월드 속 패널의 버튼(서버가 누름을 셈), 은은한 배경 소리, U로 화면 물결 효과, 서버와 빠른 패킷 왕복 횟수.
- `plugins/friend_lands` 친구 땅: 친구를 고르면 `Balloon::lift_off`로 떠오르는 동안 서버에 이동을 청하고, `World::id` `ready`로 친구의
  땅이 그려지길 기다려 그 위 상공에서 내려다보다가(`Camera::set`) 「착륙하기」로 `Balloon::land`. `plugins/camera_modes`: F5로 시점 바꾸기.
- `plugins/riding` 탈것과 지팡이, `plugins/flight` 비행: [이동 방식 만들기](moving).
- `plugins/hide_blocks` 블록 숨바꼭질: 술래의 눈가리개와 남은 시간, 숨는 사람에게는 `Players::list`와 술래의 공개 값 `role`로 술래까지의 거리.
- `plugins/arena_stats` 경기장 기록: 서버의 순위표와 경기장(서버 쪽), 내 점수와 체력을 HUD에, 점수마다 휴대폰 진동, 채팅에 "점수?"가 보이면
  내 점수를 알림으로, 이웃이 물었으면 대신 답함(`chat`, `Chat::system`, `Chat::say`).
- `plugins/arcade` 오락실: K(부스트)와 O(빛) 액션(휴대폰에선 화면 버튼, 설정에서 키 바꾸기), 누를 때마다 서버에 `request`하고 답을 HUD에,
  마우스 이동량·이동 축·장치·고정 스텝을 HUD에, 어두운 공포 조명(O로 켜고 끔), 자기 외곽선, 머리 위 반짝이, 부스트 불꽃, 발자국 궤적.

## 화면의 새 것 (G5)

`Hud::tween` `pin_to` `sweep` `push` `float_text` `board`와 `El::list` `grid` `rich` `viewport` `boss_bar`는 서버 쪽과 같습니다([화면 ›
레이아웃](screen#레이아웃-머리-위-트윈-점수판)). 게임 쪽에서 쓰면 왕복 없이 바로: 예를 들어 근처 몬스터마다 체력 바를 붙이기.

```rust
for m in Mobs::near(25.0) {
    Hud::add(&format!("mob{}", m.n), &El::bar(m.hp, 1.0).size(56.0, 7.0).color("d9483b"));
    Hud::pin_to(&format!("mob{}", m.n), Some(&PinTo::Mob(m.n)), 1.7, 25.0);
}
```

`Local::fade(id, alpha, 초, then_remove)`: 글·패널·모델이 그 투명도로 서서히(`then_remove`면 끝나면 사라짐). 피해 숫자:

```rust
let id = Local::spawn_text("20!", x, y + 1.5, z, "ffd84a", 64);
Local::glide_to(id, x, y + 3.2, z, 0.9);
Local::fade(id, 0.0, 0.9, true);
```

