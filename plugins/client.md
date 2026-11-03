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

`client!`에는 다섯 중 쓰는 것만 적습니다.

| 핸들러 | 언제 | |
|---|---|---|
| `load` → `Load` | 접속해서 이 플러그인을 불러왔을 때 한 번 | |
| `frame` → `Frame` | 게임이 그리는 매 프레임 | `dt()` 지난 프레임부터의 초, `time()` 로드된 뒤의 초 |
| `packet` → `Packet` | 서버 쪽이 이 플러그인의 채널로 보낸 것(`Hud::send_text` …, 빠른 패킷 `Hud::send_fast`), 게임의 `"window"` 패킷 | `channel()` `data()`, `fast()` 빠른 패킷으로 왔는지 |
| `input` → `Input` | 게임의 패널이 열려 있지 않을 때 키·마우스 버튼을 누르거나 뗌 | `key()` 이름(`"Q"` `"F5"` `"Space"` `"Shift"` `"Mouse1"`), `pressed()` |
| `click` → `Click` | 이 플러그인의 버튼·입력 칸을 누름 (HUD에서든 [월드 속 패널](#직접-그리는-ui)에서든; 같은 누름이 서버 쪽 `Packet`으로도 감) | `on()` 그 요소의 `on`, `data()` 입력 칸에 쓴 글 |

전역 변수(`static mut`)는 서버를 떠날 때까지 남습니다. 시간은 프레임 수가 아니라 `Frame::time()` / `dt()`로 재세요.

## 서버 쪽과 주고받기

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
| `num(k)` → `f64` | 이번 호출에 게임이 알려 준 숫자 (없으면 NaN): `dt` `time` `me.x` `me.y` `me.z`(이 플레이어, 칸) `me.yaw` `cam.x` `cam.y` `cam.z` `screen.w` `screen.h` `mouse.x` `mouse.y` `minute`(하루의 시각) `day` |
| `text(k)` → `String` | `me`(이 플레이어 이름) `server`(어디), 이벤트의 `channel` `data` `key` |
| `log(t)` | 게임의 로그에 한 줄 |
| `send(channel, data)` | 서버 쪽에 패킷 (위) |
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
| `Entities::play_anim(id, clip)` | 서버 쪽 엔티티의 클립을 이 게임에서만 (모두가 보는 것은 서버 쪽 `play_anim`) |
| `Me::play_anim(id)` | [감정 표현](models)을 자기 몸에 이 게임에서만 (서 있을 때; 모두가 보는 것은 서버 쪽 `Player::play_anim`) |

### World — 엔진에 묻기

스크립트가 하기엔 무거운 일은 엔진이 합니다.

| | |
|---|---|
| `World::raycast(from, to)` → `Option<(x, y, z)>` | 그 선이 처음 닿는 단단한 것 (칸) |
| `World::ground(x, z)` → `f64` | 게임이 가진 그곳의 땅 높이 (모르면 NaN) |
| `World::path(from, to)` → `Vec<(x, z)>` | 마을 길 (주민의 길찾기): 꺾이는 점들, 없으면 `[]` |

### Input과 Me

키를 넘겨받고 플레이어를 직접 움직이는 함수(`Input::capture`, `Me::set_velocity` …)는 [이동 방식 만들기](moving#게임-쪽에서-조작-넘겨받기)에 있습니다.

| | |
|---|---|
| `Me::position()` → `(x, y, z)` / `Me::yaw()` / `Me::name()` | 게임이 그리는 이 플레이어 (판정은 서버의 것) |
| `Me::velocity()` / `Me::on_ground()` | 게임이 움직이는 속도 (칸/초), 발이 땅에 닿았는지 |
| `Input::held(key)` → `bool` | 그 키를 지금 누르고 있는지 |

## 원본 함수 (`"ghc"`)

게임이 연결하는 것은 모듈 `"ghc"`의 함수 여섯뿐입니다. SDK의 함수는 모두 이것들을 감쌉니다. 글을 넘길 때 `(ptr, len)`, 받을 때
`(ptr, cap)`에 복사되고 전체 길이를 돌려줍니다(서버의 ["gh" 함수](abi#약속)와 같은 약속). 목록은 ["gh" 함수 › 게임 쪽](abi#게임-쪽-ghc).

## 예제

- `plugins/cutscene` 연출: G(서버 쪽 단축키)를 누르면 서버가 종 울리기를 판정(10초에 한 번, 마나석 하나)하고, 게임 쪽이 카메라를
  종으로 돌리고 번쩍이며 위쪽에 다음 종까지 남은 시간을 매 프레임 그립니다.
- `plugins/showcase` 화면 실험실: 앞에 셰이더로 빛나는 피라미드(실행 중 만든 메시)와 3D 글자, 그 위에 붙어 다니는 HUD, 오른쪽 위
  직접 그린 게이지, 월드 속 패널의 버튼(서버가 누름을 셈), 은은한 배경 소리, U로 화면 물결 효과, 서버와 빠른 패킷 왕복 횟수.
- `plugins/riding` 탈것과 지팡이, `plugins/flight` 비행: [이동 방식 만들기](moving).
