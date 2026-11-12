---
title: plugin.json
nav_order: 2
parent: 플러그인
redirect_from:
  - /plugin-json
  - /plugin-json.html
---

# plugin.json
{: .no_toc }

1. TOC
{:toc}

```json
{
  "name": "example",
  "title": "예제",
  "version": "1.0",
  "description": "마나 바, 화염구 버튼, /신속",
  "conflicts": ["other_plugin"],
  "packs": ["example"],
  "ui": {
    "buttons": [
      {
        "id": "fireball",
        "label": "화염구",
        "icon": "res://packs/example/fireball.png",
        "key": "Q",
        "cooldown": 1.5
      }
    ],
    "bars": [{"id": "mana", "label": "마나", "max": 100, "color": "4f7bff"}]
  },
  "settings": [
    {
      "key": "power",
      "label": "화염구 세기",
      "kind": "range",
      "min": 1,
      "max": 10,
      "step": 1,
      "default": 3
    }
  ]
}
```

| 키 | |
|---|---|
| `name` | 플러그인 이름 (폴더 이름과 같게). 데이터·값이 이 이름으로 나뉩니다 |
| `title`, `description` | 게임의 플러그인 목록과 서버 접속 때 받을 파일 목록에 보이는 이름과 설명 |
| `version` | 버전 (접속 때 받을 파일 목록에 표시) |
| `conflicts` | 같이 켜면 안 되는 플러그인 이름들. 새 월드 만들기에서 둘 중 하나를 끌 때까지 만들 수 없음 |
| `packs` | 이 플러그인이 쓰는 [리소스 팩](#리소스-팩) 이름들. 하나라도 없으면 그 플러그인은 빠짐 |
| `ui` | 화면의 버튼과 바 (아래) |
| `settings` | 서버 주인이 바꾸는 값 (아래) |
| `events` | (SDK 없이 쓸 때) 구독할 이벤트 → 우선순위 `{"enable": 0, "action.after": 0, "tick": 0}`. 모듈의 `on_event`가 받음 (규칙 등록은 `"enable"`) |
| `depend` | 꼭 있어야 하는 플러그인(또는 서비스) 이름들: 그것들 뒤에 로드, 없으면 켜지지 않음 ([플러그인끼리](interop#depend-soft_depend)) |
| `soft_depend` | 있으면 먼저 로드할 것들 (없어도 켜짐) |
| `provides` | 이 플러그인이 맡는 서비스 이름들 (`"economy"`): 다른 플러그인이 이 이름으로 찾아 부름 |
| `commands` | (SDK 없이 쓸 때) 채팅 명령어 `[{"name": "축제", "desc": "…", "permission": "축제.시작"}]` (`permission`: 없는 사람은 서버가 거절; SDK는 `#[command("축제", "…", "축제.시작")]`) |
| `permissions` | 플러그인의 권한 `{"축제.시작": {"description": "…", "default": "op"}}` (`default`: `op` 운영자만(기본), `true`(`all`) 모두, `false`(`none`) 준 사람만, `notop` 운영자 아닌 사람); 줄여서 `{"축제.시작": "op"}`. `Player::permissions()`가 목록을, `is_permission_set(p)`이 정해 준 것인지를 읽음 |

## 리소스 팩

플러그인은 코드만 담습니다(`plugin.json`, `server.wasm`, `client.wasm`, `lang/`, 설정). 그림·소리·모델은 리소스 팩에 두고
`"packs"`에 그 이름을 적습니다. 플러그인 폴더의 `assets/`는 게임에 보내지 않습니다(서버가 경고하고 건너뜀).

```
<data>/packs/example/
  pack.json                       {"title": "예제", "version": "1.0", "description": "화염구 그림과 모델"}
  packs/example/fireball.png      res://packs/example/fireball.png
  packs/example/fireball.glb      res://packs/example/fireball.glb
  assets/...                      게임의 같은 경로 파일을 바꿔치기
```

- 팩 이름은 a-z 0-9 `_` `-`, 64자까지. 폴더 안에서는 `packs/<이름>/...`(팩의 새 것)과 `assets/...`(게임의 것을 바꿔치기)만
  쓰고, 그 밖의 파일은 빠집니다. `pack.json`은 없어도 됩니다.
- `pack.json`의 `"models"`는 팩의 모델에 id와 언어마다의 이름을 줍니다(`title`도 언어마다 줄 수 있음). 플러그인은 그 모델을
  `"pack:<팩>/<id>"`로 부르고, 엔티티의 이름으로 주면 플레이어의 언어로 보입니다([팩의 모델](index#팩의-모델)).
- 게임의 씬(`.tscn`)은 옆의 GLB로 바꿔치기: `assets/.../x.tscn.glb`가 `res://assets/.../x.tscn`을 대신합니다.
- 폴더 대신 zip `<data>/packs/<이름>.zip`(`res://` 경로의 미디어, `pack.json`은 맨 위; 마켓이 설치하는 모양)도 됩니다.
- **팩은 모두 받아야 접속할 수 있습니다.** 골라 받거나 건너뛰는 팩은 없습니다.
- `python tools/build_plugins.py --zip DIR`는 플러그인(코드와 `lang/`)을 `DIR`에, 필요한 팩을 `DIR/../packs/<팩>.zip`으로 묶습니다.

## 휴대폰

휴대폰(안드로이드) 게임 안의 서버는 WebAssembly를 돌리지 못하고, 규칙도 코드가 등록하므로 플러그인을 하나도 쓰지 않습니다.
휴대폰에서 연 혼자 하기·LAN 농장의 플러그인 목록에는 "휴대폰에서는 플러그인을 쓸 수 없어요"가 나옵니다.

휴대폰이 **플러그인이 있는 서버**에 들어갈 때는 상관없습니다. 그때는 그 서버(PC)가 코드를 돌리고 휴대폰은 결과만 받습니다.
플러그인의 [게임 쪽 코드](client)(`client.wasm`)는 PC에서 확인했습니다. Android(Cranelift JIT)와 iOS(Pulley 인터프리터)는 네이티브 라이브러리 설정만 되어 있고 아직 빌드해 확인하지 않았습니다. 게임 쪽 코드가 돌지 않는 게임에서는 서버 쪽의 결과만 보입니다.
예전의 `"mobile"` 키는 더 이상 쓰이지 않습니다.

## 버튼 (`ui.buttons`)

화면에 버튼이 생깁니다. 누르면(또는 PC에서 `key`) 플레이어가 바라보는 방향과 함께 [`Button`](events#button) 이벤트가
`id`로 옵니다. `cooldown`(초)은 서버가 플레이어마다 지킵니다.

| 키 | |
|---|---|
| `id` | 버튼 id (`Button::button()`) |
| `label` | 글자 |
| `icon` | `res://` png (리소스 팩의 것도) |
| `key` | PC 단축키 |
| `cooldown` | 다시 누를 수 있기까지의 초 |

## 바 (`ui.bars`)

플레이어 값 하나(`Player::get` / `set`의 키)를 보여 주는 바입니다. 값을 바꾸면 게임의 바도 따라갑니다.

| 키 | |
|---|---|
| `id` | 플레이어 값의 키 |
| `label` | 글자 |
| `max` | 가득 찬 값 |
| `color` | `"rrggbb"` |

```rust
#[on(Tick)]
fn regen(e: Tick) {
    for p in e.players() {
        p.set("mana", (p.get("mana") + 1.0).min(100.0));
    }
}
```

## 명령어

SDK에서는 `#[command("이름", "설명")]`. 채팅에 `/이름 뭐든`을 치면 그 핸들러가 [`Command`](events#command)를 받고
(`args()`가 나머지), `/help`가 설명과 함께 목록을 보여 줍니다. 대답은 `c.player().say(..)`나 `message(..)`.

## 설정 (`settings`)

서버 주인이 바꿀 수 있는 값입니다. 서버는 값을 플러그인 폴더의 `settings.json`에 둡니다. 게임 자체 서버에서는 월드마다
따로(월드 선택 › 편집 › 플러그인의 설정), 전용 서버는 `settings.json`을 직접 고칩니다.

코드에서는 어느 이벤트에서나:

```rust
let on = setting_bool("on", true);
let minutes = setting_num("day_real_minutes", 14.0);
let mode = setting("mode").unwrap_or_default();   // 글자 그대로 ("12.5", "true", …), 없으면 None
```

| 키 | |
|---|---|
| `key` | 값의 키 |
| `label` | 설정 화면의 이름 |
| `kind` | 아래 표 |
| `default` | 기본값 |
| `hint` | 이름 아래의 설명 |
| `min` `max` `step` `unit` | `range` |
| `choices` | `select` `seg` `chips`의 후보 |
| `shortcut` | `toggle` 옆에 보일 PC 단축키 |

| `kind` | 모양 | 값 |
|---|---|---|
| `range` (`number`) | 슬라이더 | 숫자 (`min`~`max`) |
| `toggle` (`bool`) | 켜기/끄기 | `true` / `false` |
| `select` | 목록 | `choices` 중 하나 |
| `seg` (`choice`) | 버튼 줄 (후보가 셋 넘으면 목록) | `choices` 중 하나 |
| `chips` | 여럿 고르기 | `choices` 중 여럿 (목록) |
| `text` | 한 줄 글 | 글 (500자까지) |
| `warn` / `note` | 값 없이 `label`만: 주의 / 안내 | — |

```json
{
  "settings": [
    {"key": "on", "label": "서버 시계 쓰기", "kind": "toggle", "default": true},
    {
      "key": "day_real_minutes",
      "label": "하루의 길이 (실제 분)",
      "kind": "range",
      "min": 5,
      "max": 60,
      "step": 1,
      "unit": "분",
      "default": 14,
      "hint": "6시부터 새벽 2시까지가 실제로 몇 분인지 (게임 기본 14분)"
    },
    {
      "key": "seasons",
      "label": "축제 계절",
      "kind": "chips",
      "choices": ["봄", "여름", "가을", "겨울"],
      "default": ["봄"]
    }
  ]
}
```
