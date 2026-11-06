---
title: 플러그인
nav_order: 50
permalink: /plugins/
has_children: true
---

<div class="hero">
  <div class="cat-run" aria-hidden="true"></div>
  <div class="hero-inner">
    <h1 id="greenhaven-플러그인-api">GreenHaven 플러그인 API</h1>
    <p>폴더 하나로 서버의 규칙·모습·콘텐츠를 바꿔요. 접속하는 사람은 아무것도 설치하지 않아요.</p>
    <a class="btn btn-primary" href="#첫-플러그인-rust-sdk">첫 플러그인 만들기</a>
    <a class="btn btn-wood" href="events">이벤트 보기</a>
  </div>
</div>

서버 운영자가 **폴더 하나**를 넣어 서버의 규칙·모습·콘텐츠를 바꿉니다. 서버가 판정하고, 필요한 그림·소리·모델은
접속할 때 자동으로 받습니다.

<div class="cards">
  <a class="card" href="plugin-json"><strong>plugin.json</strong><span>이름, 버튼, 바, 명령어, 설정</span></a>
  <a class="card" href="events"><strong>이벤트</strong><span>행동, 수확, 몬스터, 하루, 월드 만들기</span></a>
  <a class="card" href="sdk"><strong>SDK 레퍼런스</strong><span>Player, World, Server, OfflinePlayer, Npc, Gui</span></a>
  <a class="card" href="rules"><strong>규칙 등록</strong><span>Enable에서 아이템·작물·블록·주민·스킬·땅 바꾸기</span></a>
  <a class="card" href="screen"><strong>화면</strong><span>HUD 요소, 미니맵, 키, 채널, 인벤토리 창</span></a>
  <a class="card" href="client"><strong>게임 쪽 코드</strong><span>client.wasm: 매 프레임 HUD, 카메라, 셰이더, 소리, 빠른 통신</span></a>
  <a class="card" href="moving"><strong>이동 방식 만들기</strong><span>비행, 탈것, 도구 동작, 서버의 이동 검사</span></a>
  <a class="card" href="models"><strong>커스텀 모델</strong><span>플레이어 모델과 감정 표현, 뼈대 규격과 검사 규칙</span></a>
  <a class="card" href="world"><strong>월드와 하루</strong><span>블록과 새 블록 종류, 청크, 구조물, 주민, 시계, 저장</span></a>
  <a class="card" href="chat"><strong>채팅과 음성, 명령어</strong><span>채널, 귓속말, 음성 묶음, 별칭·Tab 완성, 서식과 누르는 명령어</span></a>
  <a class="card" href="samples"><strong>샘플 플러그인</strong><span>스물다섯 개의 예제와 쓰는 기능</span></a>
</div>

플러그인은 코드와 에셋으로 되어 있습니다. 코드는 크레이트 하나에서 **두 부분**으로 빌드됩니다: 모든 것을 정하는 서버 쪽
`server.wasm`과, 원하면 접속한 게임 안에서 보이고 느껴지는 것만 다루는 게임 쪽 `client.wasm`. 규칙(가격, 작물, 아이템, 블록, 주민, 대사, 스킬, 몬스터, 땅 …)도 코드에서
등록합니다(Bukkit의 `onEnable`처럼 [`Enable`](events#enable) 이벤트에서 `Registry`로).

| 무엇 | 파일 | 하는 일 | 문서 |
|---|---|---|---|
| 서버 쪽 코드 | `server.wasm` | 켜질 때 규칙 등록, 이벤트를 받아 값을 바꾸거나 막고, 아이템·골드·이동 판정·창·화면·엔티티·블록… 을 다룸 (서버에서만 돎) | [이벤트](events), [SDK](sdk), [규칙 등록](rules), [화면](screen), ["gh" 함수](abi) |
| 게임 쪽 코드 (없어도 됨) | `client.wasm` | 접속한 게임 안의 샌드박스에서: 매 프레임 HUD, 카메라, 화면 효과, 자기에게만 보이는 파티클·소리, 키, 이동 넘겨받기. 상태를 바꾸는 함수는 없음 | [게임 쪽 코드](client), [이동 방식 만들기](moving) |
| 에셋 | `assets/` | 접속자에게 보낼 그림·소리·모델 (게임의 `res://` 경로 그대로; 없어도 됨) | [규칙 등록 › 에셋](rules#에셋) |

## 넣는 곳

- 전용 서버: `<data>/plugins/<이름>/`
- 게임 자체 서버로 여는 오프라인·LAN 농장: 월드마다 고름 (월드 선택 › 편집 › 플러그인). PC에서는 직접 만든 플러그인을
  `user://plugins`에 넣으면 목록에 나옵니다.

```
<data>/plugins/my_plugin/
  plugin.json   이름, 버전, 화면(버튼·바), 설정
  server.wasm   규칙 등록(Enable)과 이벤트 핸들러 (WebAssembly; 예전 이름 code.wasm도 읽음)
  client.wasm   게임 쪽 코드 (없어도 됨; assets/와 함께 접속자에게 감)
  assets/       접속자에게 보낼 그림·소리·모델
```

`rules.json`은 더 이상 읽지 않습니다. 서버 운영자가 규칙을 바꾸려면 플러그인이 아니라 `<data>/rules.d/*.json`(이름 순서로
덮음)에 둡니다.

## 첫 플러그인 (Rust SDK)

준비: Rust와 `rustup target add wasm32-unknown-unknown`.

`Cargo.toml`

```toml
[package]
name = "my_plugin"
version = "0.1.0"
edition = "2021"

[lib]
crate-type = ["cdylib"]

[profile.release]
opt-level = "s"
lto = true
panic = "abort"

[dependencies]
greenhaven-plugin = { path = "../../sdk/plugin" }   # GreenHaven-Server의 sdk/plugin
```

`src/lib.rs`

```rust
use greenhaven_plugin::*;

#[on(Harvest)]                       // 이 이벤트마다 불림
fn bigger(e: Harvest) {
    if e.crop() == "pumpkin" { e.set_count(e.count() * 2.0) }
}

#[on(ActionBefore, priority = -10)]  // 낮은 숫자가 먼저 (다른 플러그인들 사이에서도)
fn no_night_fishing(e: ActionBefore) {
    if e.kind() == "cast" && e.num("minute") > 22.0 * 60.0 { e.cancel("밤엔 낚시 금지예요") }
}

#[command("신속", "걸음이 1.5배 빨라져요")] // 채팅 /신속, /help 목록에도
fn haste(c: Command) {
    c.player().set_walk_speed(1.5);    // 게임의 걸음과 서버의 이동 판정이 함께 바뀜
    c.player().title("발이 가벼워졌어요!");
}
```

`plugin.json`

```json
{"name": "my_plugin", "title": "내 플러그인", "version": "1.0", "description": "호박 두 배, 밤낚시 금지, /신속"}
```

이벤트와 명령어는 코드의 속성(`#[on]`, `#[every]`, `#[command]`)에서 선언되므로 plugin.json에 적지 않아도 됩니다. 서버가 모듈의
"gh" 커스텀 섹션을 읽습니다.

빌드:

```sh
cargo build --release --target wasm32-unknown-unknown
cp target/wasm32-unknown-unknown/release/my_plugin.wasm server.wasm
```

GreenHaven-Server 안의 `plugins/` 아래에 두었다면 `python tools/build_plugins.py my_plugin`이 위 두 줄을 대신하고,
`--zip <폴더>`는 서버가 받는 모양 그대로 zip으로 묶습니다. 크레이트에 `client` feature가 있으면 `client.wasm`도 함께 빌드하고,
두 파일이 저마다 가져다 쓰는 것을 검사합니다([게임 쪽 코드 › 빌드](client#빌드)).

폴더째(`plugin.json`, `server.wasm`, 있으면 `client.wasm`과 `assets/`) 서버의 `plugins/`에 넣고 서버를 켜면 됩니다.

## 알아 둘 것

- **결과는 서버가 정합니다.** `server.wasm`은 서버에서만 돌고 게임에 가지 않습니다. 플러그인의 결과는 서버 대답(온라인이면
  수십 ms) 뒤에 보입니다.
- **게임 쪽 코드는 보이는 것만.** `client.wasm`은 로블록스의 LocalScript처럼 접속한 게임 안에서 돌아, 기다림 없이 매 프레임
  그리고 키를 받고 새 이동 방식을 예측합니다. 아이템·돈·위치 같은 상태를 바꾸는 함수는 아예 없어서(쓰면 컴파일되지 않음)
  권한은 서버에 남습니다. 게임은 접속할 때 그런 플러그인이 있다고 알립니다. [게임 쪽 코드](client) 참고.
- **휴대폰의 자체 서버는 플러그인을 쓰지 않습니다.** 휴대폰에서 연 혼자 하기·LAN 농장에는 플러그인이 하나도 없습니다.
  플러그인이 있는 서버에는 휴대폰으로도 들어갈 수 있고, 그 서버의 코드가 돌아 휴대폰에서도 그대로 보입니다.
  게임 쪽 코드(`client.wasm`)는 PC에서 확인했습니다. Android(Cranelift JIT)와 iOS(Pulley 인터프리터)는 네이티브 라이브러리 설정만 되어 있고 아직 빌드해 확인하지 않았습니다.
- **모듈은 월드마다 하나 만들어져 계속 쓰입니다.** 전역 변수가 다음 이벤트에도 남아 캐시로 써도 되지만, 자고 일어나지
  않은 하루가 버려질 때 새로 만들어집니다. 오래 남길 것은 `World::set` / `Player::set`이나 [데이터 저장](sdk#데이터-저장)에.
- **저장은 바닐라 규칙**: 자고 일어난 아침에만 저장됩니다. [저장](world#저장) 참고.
- 정해진 난수는 `e.roll(k)`: 같은 이벤트를 다시 돌려도 같은 값. `rand`는 쓰지 마세요(샌드박스에 시간·난수 원천이 없습니다).
