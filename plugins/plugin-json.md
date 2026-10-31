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
  "mobile": false,
  "conflicts": ["other_plugin"],
  "ui": {
    "buttons": [{"id": "fireball", "label": "화염구", "icon": "res://plugins/example/fireball.png", "key": "Q", "cooldown": 1.5}],
    "bars": [{"id": "mana", "label": "마나", "max": 100, "color": "4f7bff"}]
  },
  "settings": [
    {"key": "power", "label": "화염구 세기", "kind": "range", "min": 1, "max": 10, "step": 1, "default": 3}
  ]
}
```

| 키 | |
|---|---|
| `name` | 플러그인 이름 (폴더 이름과 같게). 데이터·값이 이 이름으로 나뉩니다 |
| `title`, `description` | 게임의 플러그인 목록과 서버 접속 때 받을 파일 목록에 보이는 이름과 설명 |
| `version` | 버전 (접속 때 받을 파일 목록에 표시) |
| `mobile` | 휴대폰에서 코드를 뺀 채로 써도 되는지 ([아래](#휴대폰-mobile)) |
| `conflicts` | 같이 켜면 안 되는 플러그인 이름들. 새 월드 만들기에서 둘 중 하나를 끌 때까지 만들 수 없음 |
| `ui` | 화면의 버튼과 바 (아래) |
| `settings` | 서버 주인이 바꾸는 값 (아래) |
| `events` | (SDK 없이 쓸 때) 구독할 이벤트 → 우선순위 `{"action.after": 0, "tick": 0}`. 모듈의 `on_event`가 받음 |
| `commands` | (SDK 없이 쓸 때) 채팅 명령어 `[{"name": "축제", "desc": "…"}]` |

## 휴대폰 (`mobile`)

휴대폰(안드로이드) 게임 안의 서버는 WebAssembly를 돌리지 못합니다. 그래서 혼자 하기·LAN 농장을 휴대폰에서 열면
`code.wasm`이 든 플러그인을 어떻게 할지 이 값으로 정합니다.

| | PC·전용 서버 | 휴대폰의 자체 서버 |
|---|---|---|
| 코드 없음 (`rules.json`·`assets/`만) | 모두 적용 | 모두 적용 |
| 코드 있음, `mobile` 없음 (기본) | 모두 적용 | **통째로 빠짐**: `rules.json`·`assets/`도 안 씀. 플러그인 목록에 "휴대폰에서는 코드가 든 플러그인을 쓸 수 없어요" |
| 코드 있음, `"mobile": true` | 모두 적용 | `rules.json`·`assets/`만 적용, `code.wasm`은 무시 |

`"mobile": true`는 "코드가 없어도 망가지지 않는다"는 약속입니다. 예를 들어 새 작물을 `rules.json`으로 더하고 코드로는 거둘 때
반짝임만 내는 플러그인이면 붙여도 됩니다. 반대로 `rules.json`의 콘텐츠가 코드에 기대는 플러그인(코드가 움직이는 `script`
몬스터, 코드가 여는 창이 있어야 진행되는 퀘스트 …)에는 붙이지 마세요. 휴대폰에서 반쪽짜리로 돌게 됩니다.

휴대폰이 **온라인 서버**에 들어갈 때는 상관없습니다. 그때는 그 서버(PC)가 코드를 돌리고 휴대폰은 결과만 받습니다.

## 버튼 (`ui.buttons`)

화면에 버튼이 생깁니다. 누르면(또는 PC에서 `key`) 플레이어가 바라보는 방향과 함께 [`Button`](events#button) 이벤트가
`id`로 옵니다. `cooldown`(초)은 서버가 플레이어마다 지킵니다.

| 키 | |
|---|---|
| `id` | 버튼 id (`Button::button()`) |
| `label` | 글자 |
| `icon` | `res://` png (플러그인 `assets/`의 것도) |
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
"settings": [
  {"key": "on", "label": "서버 시계 쓰기", "kind": "toggle", "default": true},
  {"key": "day_real_minutes", "label": "하루의 길이 (실제 분)", "kind": "range", "min": 5, "max": 60, "step": 1,
   "unit": "분", "default": 14, "hint": "6시부터 새벽 2시까지가 실제로 몇 분인지 (게임 기본 14분)"},
  {"key": "seasons", "label": "축제 계절", "kind": "chips", "choices": ["봄", "여름", "가을", "겨울"], "default": ["봄"]}
]
```
