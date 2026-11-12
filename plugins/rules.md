---
title: 규칙 등록 (Registry)
nav_order: 5
parent: 플러그인
redirect_from:
  - /rules
  - /rules.html
---

# 규칙 등록 (Registry) — 아이템·작물·주민·스킬·땅 바꾸기
{: .no_toc }

1. TOC
{:toc}

**게임의 콘텐츠는 서버의 것**입니다.
서버는 자기 `data/rules.json`에 플러그인들이 등록한 것을 모두 덮은 결과를 접속하는 게임에 보내고(해시로 캐시되어 바뀌었을
때만 다시 받음), 게임은 자기 표 대신 그것으로 작물·아이템·퀘스트·주민·대사·마을 배치를 만듭니다. 그래서 등록 하나가 서버의
판정과 모든 접속자의 화면을 함께 바꿉니다.

## 코드로 등록하기 (`Enable`)

Bukkit의 `onEnable`처럼, 플러그인은 서버가 켜질 때 [`Enable`](events#enable) 이벤트에서 `Registry`로 규칙을 더하고 바꿉니다.
등록은 이 이벤트에서만 됩니다(다른 이벤트에서 부르면 아무것도 안 함). 월드도 플레이어도 없을 때입니다.

```rust
use greenhaven_plugin::*;
use greenhaven_vanilla::*; // Registry::crop (VanillaRegistry)

#[on(Enable)]
fn enable(_e: Enable) {
    // 엔진: 가방, 화면 글자, 아이템
    Registry::set("bag.slots", "48");                 // 값 하나: 경로와 JSON
    Registry::text("가방", "큰 가방");                 // 화면 글자
    Registry::item("golden_carrot", &ItemDef::new("황금 당근").icon("res://packs/golden_crops/golden_carrot.png").color("f2c14e"));
    // 바닐라(농장 모듈): 작물, 상점 가격, 먹으면 기력, 퀘스트 — 농장이 꺼진 서버·월드에서는 아무 일도 안 함
    Registry::crop("golden_carrot", r#"{"days": 8, "seasons": [0, 1, 2], "name": "황금 당근", "look": "carrot", "tint": "ffd23f"}"#);
    Registry::set("price.golden_carrot_seeds", "120");
    Registry::patch(r#"{"edible": {"golden_carrot": 150}, "progress": {"quests+": [["golden_harvest", "황금빛 수확", "황금 당근 3개를 가져다주세요.", {"deliver": {"golden_carrot": 3}}, 2000, "doyun"]]}}"#);
}
```

| 함수 | 규칙의 키 |
|---|---|
| `Registry::patch(json)` | JSON 객체 하나를 규칙 위에 덮음 |
| `Registry::set(path, json)` | `"bag.slots"` 같은 경로의 값 하나 (`"48"`, `"\"글\""`, `"[1, 2]"`) |
| `Registry::add(table, id, json)` | 표 `table`에 `id` 더하기·바꾸기 (`set("table.id", json)`) |
| `Registry::block(id, &BlockKind)` | `blocks_add` — [새 블록 종류](world#새-블록-종류) |
| `Registry::item(id, &ItemDef)` | `items` ([아래](#아이템)) |
| `Registry::model(id, &ModelDef)` `Registry::emote(id, &EmoteDef)` (JSON 문자열도) | `models_add` `emotes_add` ([커스텀 모델](models)) |
| `Registry::text(from, to)` | `texts` |

농장(바닐라 모듈)의 표는 `use greenhaven_vanilla::*;`의 트레잇 `VanillaRegistry`로 ([바닐라 모듈](sdk#바닐라-모듈-greenhaven_vanilla)):

| 함수 | 규칙의 키 |
|---|---|
| `Registry::crop(id, json)` | `crops` |
| `Registry::monster(id, json)` | `monsters_add` |
| `Registry::animal(id, json)` | `animals_add` |
| `Registry::villager(id, json)` | `villagers_add` |

`Registry::add("crops", id, json)`처럼 표 이름으로 부르면 들여오지 않아도 같습니다.

### 아이템

`Registry::item(id, &ItemDef)` (2026-11-11; 예전엔 JSON 글): `ItemDef::new(이름)` 위에 말한 것만 `items`의 그 아이템에 들어갑니다.

| `ItemDef` | |
|---|---|
| `new(name)` | 이름 |
| `.desc(text)` | 설명 (툴팁) |
| `.icon(path)` | 아이콘: 이 플러그인의 `res://….png`, 또는 게임의 아이템 id |
| `.color("e0115f")` | 아이콘이 없을 때의 색 |
| `.price(gold)` / `.sell(gold)` | 상점 값 / 파는 값 |
| `.kind(ItemKind::Tool \| Block \| Misc)` | 휘두르는 도구(`action`) / 놓는 블록 / 그 밖 (`"type"`) |
| `.usable()` | 단축바에서 사용 ([`Use`](events#use)) |
| `.model(path)` | 손에 든 모습 (`res://….glb`) |
| `.action("slash" \| "cast" \| "chop" …)` | 쓸 때의 몸짓 |
| `.with(key, json)` | 그 밖의 `items` 키, 값은 JSON (`.with("hit", "0.45")`, `.with("stack", "1")`) |

`ItemDef::default()`(이름 없이)는 게임의 아이템을 말한 것만 바꿉니다: `Registry::item("carrot", &ItemDef::default().price(50))`.

```rust
Registry::item("magic_staff", &ItemDef::new("마법 지팡이").kind(ItemKind::Misc).usable()
    .model("res://packs/riding/staff.glb").action("cast").icon("res://packs/riding/staff.png"));
```

이 문서의 JSON 예는 모두 `Registry::patch`에 넘기는 모양입니다. SDK 없이는 plugin.json `events`에 `"enable"`을 구독하고
`on_event`에서 "gh" [`register(ptr, len)`](abi#등록과-화면)를 부릅니다(샘플 `wild_fish`).

{: .note }
플러그인 폴더의 `rules.json`은 더 이상 읽지 않습니다(서버가 켜질 때 그렇다고 알림). 코드가 없는 플러그인은 규칙을 바꿀 수
없습니다. 그림·소리·모델은 플러그인이 아니라 [리소스 팩](#에셋)에 둡니다.

## 덮어쓰기 규칙

[RFC 7386](https://www.rfc-editor.org/rfc/rfc7386) JSON Merge Patch에 하나를 더했습니다.

- 객체는 키마다 합칩니다.
- `null`은 지웁니다.
- 나머지(숫자, 글, 목록)는 바꿉니다.
- **목록에 더하려면 키 뒤에 `+`**: `{"progress": {"quests+": [ … ]}}`는 원래 퀘스트 뒤에 붙입니다.
- 한 플러그인의 등록은 부른 차례로, 여러 플러그인은 폴더 이름 순서로 겹칩니다.
- 그 아래에 서버 자신의 패치가 먼저 깔립니다: `<data>/rules.d/*.json`(이름 순서). 운영자의 설정이고, 게임은 월드의 옵션을
  `rules.d/_world.json`에 씁니다. 플러그인이 아닙니다.

서버도 쓰는 표는 서버의 키 그대로, 게임만 쓰는 표는 `"client"` 아래 `{클래스: {표: …}}`로 있습니다. 무엇이 있는지는
서버의 `data/rules.json`을 열어 보세요.

## 키

| 키 | 바뀌는 것 |
|---|---|
| `price`, `sell` | 상점 값, 파는 값 (`{id: 골드}`; 새 아이템도 여기 값이 있으면 사고팔 수 있음) |
| `crops`, `trees` | 작물·과일나무 (`days` `regrow` `seasons` `name` `seed_price` `sell` …). 새 작물은 `look`(모델을 빌릴 작물) `tint`(`"rrggbb"`) `stages`(`res://` 모델 셋)로 그려지고, `<id>_seeds` 값이 있으면 그 계절 잡화점에 나옴 |
| `items` | 게임이 보여 줄 아이템: `{id: {name, desc, icon(아이템 id 또는 res:// png), color, type, model}}` — 원래 아이템 이름 바꾸기도 됨 |
| `items`의 `usable` `action` `hit` | 쓸 수 있는 플러그인 아이템과 그 동작 (`cast` `attack` … `emote:<id>`, 클립 경로), 동작의 몇 할에서 `Use`인지: [도구 동작](moving#도구-동작-플러그인-아이템) |
| `checks` | 서버의 이동 검사 `{"speed", "walls", "air", "teleport", "reach"}` (기본 모두 `true`): `Registry::set("checks.air", "false")` — [이동 방식 만들기](moving#서버의-이동-검사) |
| `edible` | 먹을 수 있는 것과 기력 `{id: 150}` |
| `texts` | 화면 글자 바꾸기 `{"가방": "큰 가방"}` (글자 전체가 같을 때) |
| `bag` | `{"slots": 48}` 가방 칸 수 (단축바 12 포함, 24~132) |
| `max_energy`, `seconds_per_minute`, `sleep_recovery` | 기력 최대, 게임 1분의 초 (0.7), 잠의 회복 |
| `starter`, `starter_tools` | 새 농장의 `gold`, `items`, 기본 도구 |
| `weather`, `debris`, `buildings` | 계절마다 날씨 확률, 야생 나무·바위, 목수가 짓는 건물 (값, 재료, 일수) |
| `town_plots`, `town_order`, `town_built`, `site_items` | 마을 배치 (구획과 그 안의 건물·소품, 놓는 순서) |
| `progress.quests` / `quests+` | 퀘스트 `[id, 제목, 설명, 조건, 보상 골드, 의뢰인]` (조건: `deliver` `level` `placed` `tier` `enchant` `fork` …) |
| `progress.tutorial` | 첫날을 마치면 받는 것 (`gold` `items` `letter`) |
| `progress.recipes` `equipment` `fish` `machines` `letters` `enchants` `placeables` `villagers` … | 제작법, 장비, 물고기, 가공기, 편지, 마법 부여, 설치물 |
| `progress.skills` `themes` `trees` … | [스킬과 스킬 트리](#스킬과-스킬-트리) |
| `progress.tutorial_tasks` | [첫날 할 일](#첫날-할-일) |
| `progress.fishing.reel` | [낚시의 손맛](#낚시의-손맛) |
| `monsters_add`, `animals_add` | [몬스터와 농장 동물 더하기](#몬스터와-농장-동물-더하기) |
| `models_add`, `emotes_add` | [커스텀 모델과 감정 표현](models) |
| `blocks_add` | [새 블록 종류](world#새-블록-종류) (`Registry::block`) |
| `villagers_add`, `villagers_remove`, `town_remove` | 주민·구획 더하기·빼기 (그 이름이 나오는 모든 표에서) |
| `places_add` | 주민이 가는 새 장소 |
| `terrain` | [땅](#땅-terrain) |
| `mine_layout` | [광산](#광산-mine_layout) |
| `dungeon` | [사막의 던전](#사막의-던전-dungeon) |
| `client.ItemData.*` | 도구·생산품·사료·재료·광물·설치물·가구·물약 … (이름, 색, 값, 모델) |
| `client.VillagerData.*` | 주민 (`PEOPLE` 이름·역할·색·생일·좋아하는 것·집·가게), `SCHEDULE` 하루 일정, `PLACES`, `SHOPS`(영업시간, `sells` 더 파는 것), `EVENTS`, `QUESTIONS`, `LINES`, `GOSSIP` |
| `client.VillagerLines.*` | 대사 (`TALK` 말 걸 때, `CHAT` 혼잣말·광장, `HELLO` 인사, `TOWN` 마을 소식, `PAIRS` 둘이 주고받는 말): `[누구, "조건,조건", "대사"]` (조건: 계절, 날씨, 시간대, 장소, 하트, 기분) |
| `client.VillagerMind.*` | 반응 대사 (`SAY` 본 일·소문·인사·혼잣말), `NATURE` 성격 (기분, 비, 친구, 라이벌), `SPECIAL` |
| `client.Intro.SCENES` | [오프닝](#오프닝) |
| `client.Music.TRACKS` | [음악](#음악) |
| `client.Interiors.ROOMS` | [건물 안의 방](#건물-안의-방) |
| `client.SkillNames.NAMES` | 3차 이후 전직 이름 |
| `client.Animalese.VOICES`, `client.TownBuilder.NPCS` | 주민의 목소리, 모델 |
| 그 밖의 키 | 서버가 쓰는 그대로 (몬스터, 밤, 동물, 도구 기력 …) — 서버 판정이 바뀌고 게임 화면의 숫자는 서버의 답을 따름 |

## 에셋

새 그림·소리·모델은 플러그인이 아니라 **리소스 팩**에 게임 경로로 넣습니다(플러그인의 `assets/`는 서버가 경고하고 건너뜀):
팩 폴더 `<data>/packs/golden_crops/`의 `packs/golden_crops/golden_carrot.png` → `res://packs/golden_crops/golden_carrot.png`.
팩의 `assets/...`에 게임의 것과 같은 경로로 넣으면 **바꿔치기**됩니다. 플러그인은 필요한 팩을 plugin.json `"packs": ["golden_crops"]`에
적습니다([리소스 팩](index#리소스-팩)).

- 쓸 수 있는 것: PNG / JPG / WebP, OGG / WAV, GLB. 실행되는 것은 하나도 쓰지 않습니다(게임이 원본에서 직접 리소스를 만듦).
- 모델(GLB)의 삼각형 수에는 한도가 없습니다(얼마나 무거워도 되는지는 서버 주인이 정함). LOD는 게임이 만들고, 옆에 `X_lod1.glb` `X_lod2.glb` `X_impostor.png`(먼 곳 그림)를
  두면 그걸 씁니다.
- 접속할 때 꼭 받아야 하는 파일로 알려집니다 (이름은 pack.json의 `title`, 버전은 `version`). 팩은 모두 받아야 들어갑니다.
- pack.json `"models"`에 id를 준 모델은 아이템의 `model`, `models_add` / `emotes_add`에서 `"pack:<팩>/<id>"`로 불러도 됩니다
  ([팩의 모델](index#팩의-모델)). 게임의 씬(`.tscn`)은 팩의 `assets/.../x.tscn.glb`가 바꿔치기합니다.

## 스킬과 스킬 트리

특성(perk)은 서버와 게임이 같은 정의에서 똑같이 만듭니다. 정의만 고치면 서버의 판정과 가방 › 스킬 화면이 함께 바뀝니다.
모두 `progress` 아래:

| 키 | |
|---|---|
| `skills` | 스킬 목록 `["farming", …]`. `[]`이면 레벨이 오르지 않고 가방의 스킬 탭이 사라짐. 빠진 스킬은 경험치도 특성도 없음 |
| `themes` | 스킬 → 테마 → `[효과, 이름, 한 단계 값, 설명("%d")]`. 효과 `k`: `energy`(tool, %) `power`(tool) `sell`/`price`(type, %) `extra`(on, %) `xp`(skill, %) `max_energy` `soil` `quality` `bar_ore` `enchant_stones` `fish_zone` `bite` |
| `trees` | 스킬 → `{"base": [Lv 1~4의 테마], "paths": [[id, 이름, [테마 넷], [[2차 id, 이름, [테마]], …]]], "draw": [3차부터 자동으로 만드는 갈래가 고르는 테마, 차례대로]}` |
| `fork_every`, `max_level` | 전직 간격 (5), 만렙 (30). 트리 화면의 줄 수도 따라감 |
| `choices`, `one_off` | 레벨 칸의 후보 수 (3), 한 칸에만 나오는 테마 `{"farming.base.2": "soil"}` |
| `xp_base`, `xp_cross` | 레벨업 경험치 (50 + 25L + 2L²) × (100 + 3 × 다른 스킬 레벨 합) / 100 |
| `xp_from` | 무엇이 어느 스킬에 경험치를 주나: `harvest`(n + 작물 일수) `fruit`(열매당 n) `forage` `product`(동물 생산물) `enchant`(마력석당 n) `fish` `release`(물고기 경험치의 n%) — `{"forage": ["mining", 12]}` |
| `debris_xp` | 나무·바위·광맥을 부수면 `[스킬, 경험치]` |

## 첫날 할 일

`progress.tutorial_tasks`는 할 일 목록이고, 서버가 같은 목록으로 보상(`progress.tutorial`)을 판정합니다.

```json
{
  "id": "fence",
  "title": "울타리 만들기",
  "act": "craft",
  "n": 2,
  "item": "",
  "text": ["PC 안내", "PC 둘째 줄", "폰 안내", "폰 둘째 줄"]
}
```

- 게임이 아는 `id`: `move` `look` `till` `plant` `water`(n칸) `chop` `mine` `ship` `talk` `sleep` — 원래의 감지, 카드 그림,
  키 안내가 그대로.
- 다른 `id`: `act` 종류의 행동을 `n`번 하면 완료 (서버도 셈). 카드는 그 `item`(핫바 칸)이 깡충 뛰는 그림.
- 서버는 `till` `plant` `water` `ship` `sleep`과 `act` 할 일을 확인합니다. `move` `look` `chop` `mine` `talk`는 게임의 말을 믿음.
- 바꾸기, 빼기, 순서 바꾸기, 더하기(`"tutorial_tasks+"`) 모두 됩니다. `[]`이면 튜토리얼도 첫날 보상도 없음.

## 오프닝

`client.Intro.SCENES`: 새 농장을 만들 때의 오프닝 장면들. `[]`이면 오프닝 없이 바로 캐릭터 만들기.

```json
{
  "title": "새 마을",
  "caption": "자막",
  "stage": 7,
  "image": "res://packs/my/scene.png",
  "music": "lovely_town",
  "speaker": "raon",
  "name": "라온",
  "role": "마을 마법사",
  "lines": ["대사 하나", "대사 둘"],
  "wave": "doyun",
  "letter": {
    "tag": "",
    "no": "",
    "title": "",
    "lines": [],
    "sign": "",
    "stub": ["1인", "새벽 첫 비행"]
  }
}
```

- `stage`: 게임의 장면 (0 도시의 밤 … 8 도착: 움직이는 인물·비·열기구가 그림 위에). 없으면 `image` 한 장만.
- `music`: 그 장면부터 (게임의 `assets/music` 이름이나 `res://….ogg`).
- `lines`: 자막 뒤에 `speaker`의 얼굴·목소리로. `wave`: PC에서 옆에서 손 흔드는 주민.
- 오프닝은 서버에 들어가기 전에 나옵니다: 혼자 하기는 그 월드의 플러그인들의 `Enable`을 서버를 켜기 전에 돌려 등록한 것을
  쓰고, 온라인은 마지막으로 그 서버에 들어갔을 때 받아 둔 것(처음이면 게임의 것)을 씁니다.

## 음악

`client.Music.TRACKS`:

```json
[{"id": "곡", "hours": [6, 18], "seasons": [2], "weather": ["Rain"], "where": ["outdoors"]}]
```

지금 맞는 것 중에서 무작위 (두 번 넣으면 두 배 자주). `where`: `"outdoors"` `"indoors"` `"mine"` 또는 방 id. `id`는
`assets/music`의 이름이나 리소스 팩의 `res://….ogg`. 코드에서는 [`Audience`](sdk#audience)의 `music(track)` /
`music_with(&Music { track, fade, volume, looped })` / `stop_music()` (`Player` 그 사람, `World` 월드의 모두, `Server` 서버의 모두).

## 몬스터와 농장 동물 더하기

```json
{
  "monsters_add": {
    "ice_slime": {
      "like": "slime",
      "name": "얼음 버섯",
      "level": 1,
      "weight": 2,
      "hp": 5,
      "drops": [["stone", 2, 0.6]],
      "xp": 3,
      "skill": "mining",
      "look": {"kind": "mushroom_cute", "variant": 1, "scale": 0.95, "tint": "8fd8ff"}
    },
    "wisp": {
      "like": "firefly",
      "level": 2,
      "mine": 2,
      "script": true,
      "look": {
        "model": "res://packs/my/wisp.glb",
        "scale": 1.0,
        "clips": {"idle": "Idle", "move": "Fly", "attack": "Bite", "hit": "Hit", "die": "Die"},
        "tiers": ["8ad8ff", "ffb35c"]
      }
    }
  },
  "animals_add": {
    "goat": {
      "like": "sheep",
      "name": "염소",
      "house": "barn",
      "price": 2500,
      "product": "goat_milk",
      "every": 2,
      "product_item": {"name": "염소 젖", "sell": 260, "color": "f4efe2"},
      "feed": {"name": "염소 사료", "price": 50, "sell": 25},
      "foods": ["hay", "wheat"],
      "grow": 3,
      "breed": 5,
      "scale": 1.2,
      "tint": "c9b28f"
    }
  }
}
```

### 몬스터 (`monsters_add`)

| 키 | |
|---|---|
| `like` | 빠진 값을 빌릴 기존 종류: `slime` `bat` `skeleton` `shadow` `ember` `gem_bug` `pot` `firefly` `biter` `vine` `golem` `minotos` |
| `name` | 이름 |
| `level` | 밤에 얼마나 드문지 (1 가장 흔함, 높을수록 드묾; 1000이면 밤엔 안 나옴) |
| `mine` | 그 층부터 광산에 (30층 아래로는 물러남; 0이면 광산엔 안 나옴) |
| `weight` | 뽑히는 비율 (기본 1) |
| `size` `hp` `damage` `speed` | |
| `move` | `hop` `flutter` `walk` `charge` `zigzag` |
| `fly` | 뜬 높이 |
| `drops` | 쓰러뜨리면 `[아이템, 개수, 확률]` |
| `xp`, `skill` | 경험치와 그 스킬 (기본 `mining`) |
| `script` | `true`: [`MobStep`](events#mobstep) 이벤트로 움직임 |
| `look` | 모습: `[모델 종류, 색 번호, 크기]` 또는 `{"kind", "variant", "scale", "tint"}`로 게임의 몬스터를 다른 색·크기로, 또는 `{"model": GLB, "clips"}`로 플러그인의 모델. `tint`은 밝기는 두고 그 색으로 다시 칠함, `tiers`는 층 단계마다의 색. 사전 꼴의 두 모습 다 `"death"`: 쓰러질 때 `"dissolve"`(기본: 타서 사라짐), `"fade"`(투명해지며 사라짐), `"none"`(`die` 클립 뒤에도 몸이 남아 플러그인의 게임 쪽이 나머지를 그리고 치움: [게임 쪽 › 몬스터의 죽음](client#몬스터의-죽음); 치우지 않으면 60초 뒤 저절로 사라짐) |

서버가 내보내고 움직이고 판정하며, 모든 접속자는 서버가 보낸 대로 그립니다.

### 동물 (`animals_add`)

| 키 | |
|---|---|
| `like` | 빠진 값과 모델을 빌릴 동물: `chicken` `cow` `sheep` `pig` |
| `house` | 사는 건물: `barn` `coop` (기본은 `like`의 건물) |
| `price` | 목장에서 사는 값 |
| `product`, `product_item` | 생산품 아이템, 새 생산품이면 `{name, sell, color, icon}` |
| `every` | 며칠에 한 번 생산 (기본 1) |
| `feed` | 잡화점에서 파는 `<id>_feed` |
| `foods` | 그 밖에 먹는 것 |
| `grow`, `breed` | 먹이를 다 먹은 날 수로 자라기·새끼 |
| `size`, `scale`, `tint` | 충돌 상자, 모델 크기, 색 |
| `model`, `young_model` | GLB (클립 `idle` `walk` `eat` `sit`) |

새 건물 종류는 아직 없습니다: 헛간·닭장 중 하나에 삽니다.

## 건물 안의 방

`client.Interiors.ROOMS`(방 이름 = 건물의 `n`)를 고치면 서버의 방(바닥 크기, 문, 문 앞, 침대, 가구를 놓는 방과 그 막힌
칸, 방 안의 주민)도 그것으로 만들어집니다.

| 키 | |
|---|---|
| `w` `d` | 칸 |
| `door` | 앞벽 위 문의 가운데 |
| `out` | 밖의 문 앞 (건물 기준) |
| `style` | `wood` / `stone` |
| `windows`, `rugs`, `lights` | |
| `things` | `[조각, x, z, yaw, y, scale]` — 바닥(y 0.9 미만)에 놓인 것은 단단함. 조각: Tavern 조각 이름, `farm:` `rts:` `mine:` `blk:<종류>/<이름>` |
| `bed`, `mirror` | |
| `keepers` | `[주민, x, z, yaw, [장소 …]]` |
| `uses`, `shop`, `night`, `furnish`, `title` | |

```json
{
  "client": {
    "Interiors": {
      "ROOMS": {
        "Farmhouse": {
          "w": 10,
          "things+": [["table", 3.5, -2.0, 90]]
        },
        "Bakery": {
          "w": 7,
          "d": 6,
          "door": 0.0,
          "out": [0.0, 5.7],
          "style": "wood",
          "windows": [],
          "things": [],
          "lights": [],
          "keepers": [["doyun", 0.0, 1.0, 180, ["bakery"]]]
        }
      }
    }
  },
  "town_plots": {
    "bakery": {
      "w": 9,
      "d": 13,
      "items": [
        {"k": "building", "n": "Bakery", "m": "emily", "x": 4.5, "z": 5.3, "yaw": 180, "s": "빵집"},
        {"k": "door", "x": 4, "z": 0},
        {"k": "clear", "x": 0, "z": 0, "w": 9, "d": 13}
      ]
    }
  },
  "town_order+": ["bakery"]
}
```

새 건물은 새 구획(`town_plots` + `town_order+`, 기존 모델 `m`)에 새 이름 `n`으로, 그 방을 같은 이름으로 넣으면 됩니다(처음
보는 구획은 마을 한가운데 가까이 놓임). `room_order`는 바꾸지 마세요(게임은 자기 순서로 셈). 없는 주민의 `keepers`는 빠집니다.

## 낚시의 손맛

낚시 미니게임의 숫자는 `progress.fishing.reel`이고, 물고기마다 `progress.fish.<id>.reel`로 그 위에 덮습니다.

| 키 | |
|---|---|
| `bar`, `fish_h` | 물 높이 (300), 물고기 (40) |
| `zone`, `zone_level` | 초록 칸 (78), 레벨마다 −6 |
| `fish_start` `zone_start` `meter_start` | 시작 값 |
| `reach`, `reach_level` | 한 번에 움직이는 거리 |
| `wait` `wait_rand` `pace` `pace_level` | 쉬는 시간 |
| `speed`, `speed_level` | |
| `leap_level`, `leap_chance` | 전설의 도약 |
| `lift` `gravity` `bounce` | 누를 때 오름, 뗄 때 내려감, 튕김 |
| `fill`, `drain`, `drain_level` | 칸 안에서 차오름, 밖에서 줄어듦 |
| `max_ticks` | |
| `plugin` | 아래 |

`"plugin": "<플러그인 이름>"`이면 그 플러그인이 물고기의 움직임을 짭니다. 던질 때 **서버가** 그 플러그인의 내보내기

```rust
#[no_mangle]
pub extern "C" fn reel(tick: i64, fish_y: f64, level: f64, roll: f64) -> f64
```

를 20틱(1/3초)마다 불러 물고기의 길(최대 1000점, 0.01 단위)을 만들고 게임에 보냅니다. 게임은 그 점들을 이어 그리고,
서버의 판정도 그 길로 합니다. `fish_y`는 앞 점, `roll`은 그 점의 0..1 난수, 돌려준 값은 물 안(0..`bar - fish_h`)으로
잘립니다(숫자가 아니면 제자리). 호출 한 번에 연료 200 000. 물고기는 플레이어의 입력에 반응하지 않습니다(미리 모르므로).
예: `plugins/wild_fish`.

## 땅 (`terrain`)

바닐라 생성기가 청크를 처음 만들 때 쓰는 숫자입니다(이미 만들어진 청크는 그대로). 땅을 통째로 다르게 만들려면
[`ChunkGenerate`](events#chunkgenerate)를 쓰세요. 원래 값은 서버의 `data/rules.json`에.

| 키 | |
|---|---|
| `height` `mount` `temp` `forest` `detail` `grain` | 노이즈 `{"seed": 월드 시드에 더할 값, "octaves", "period": 칸}` — 높이, 산맥, 기온, 숲, 지형 결 |
| `coast` `coast_waves` `pull` | 바다가 시작하는 곳 (마을 북쪽 끝에서 몇 칸), 만과 곶 `[[x 배율, 줄, 진폭], …]`, 마을 양옆 몇 칸에 걸쳐 마을 해안선으로 돌아오는지 |
| `beach` `beach_wave` `beach_rise` `notch` | 모래사장 폭과 흔들림, 땅이 해변으로 내려오는 폭, 해안선의 들쭉날쭉 `[x 배율, 줄, 진폭, 칸마다의 난수 폭, 뺄 값]` |
| `height_amp` `mount_amp` `detail_amp` `grain_amp` `inland` | 높이 = 높이 노이즈 × amp + smoothstep(mount_amp[0], [1], 산맥) × [2] × 내륙 + … (산과 추위는 `inland` [시작, 끝] 칸만큼 들어가야) |
| `flat` `ground` `near_town` | 마을 둘레 평지 `[몇 칸부터, 몇 칸까지 거칠어짐]`, 평지 높이, 마을 둘레 몇 칸엔 나무·바위 없음 |
| `lake` `level_from` `level_step` `top_level` | 호수 (높이가 이 아래), 층 = (높이 − level_from) × level_step, 가장 높은 층 (최대 9) |
| `snow_level` `stone_level` `desert` `cold` | 눈 덮인 봉우리, 바위산, 사막 `[높이 아래, 기온 위]`, 추운 언덕 `[기온 아래, 층 이상, 내륙 위]` |
| `scatter` | 칸 위에 서는 것들 (아래) |
| `town` | 마을 땅 `{"noise_scale", "water", "sand"}` |

`scatter`는 **위에서부터 처음 맞는 하나**가 섭니다:

| 키 | |
|---|---|
| `on` | `"grass"` 풀밭·낮은 눈, `"beach"` 바다 앞 모래, `"rough"` 바위·사막 |
| `h` | `[이상, 미만]` 칸의 난수 (1000 중) |
| `wild` | 마을 둘레 제외 |
| `even` | x+z 짝수 칸만 |
| `forest` | `[초과, 이하]` 숲 노이즈 |
| `top` | `[블록]` |
| `back` | 해변 뒤쪽 몇 칸 안 |
| `models` | `res://` 경로들 (플러그인 assets의 모델도) |
| `pick` | 0: `h`로, 아니면 그 솔트의 난수로 모델 고르기 |
| `scale` | `[곱, 더함, h % m, ÷]` → 곱 × (더함 + (h % m) ÷ ÷) |
| `solid` | `[반지름, 높이]` 부딪히는 줄기 (없으면 지나감) |

`"scatter+"`로 더한 것은 원래 것들이 안 맞는 난수 칸에서만 나옵니다. 원래 것을 바꾸려면 목록 전체를 주세요.

## 광산 (`mine_layout`)

| 키 | |
|---|---|
| `lift` `rest` `rest_size` | 승강기가 서는 층 간격, 쉼터 층 간격 (몬스터·바위 없음), 쉼터 크기 |
| `w` `d` | 층의 폭·깊이 `[기본, 난수, 상한, ÷]` → 기본 + 2×난수 + 2×min(층, 상한)÷÷ |
| `clumps` `radius` | 바위벽 덩어리 수 `[기본, 난수, 상한, ÷]`, 덩어리 반지름 1 + 난수(radius) |
| `dense` | 빈 칸 중 바위가 놓이는 비율(%) `[기본, 상한]` → 기본 + min(층, 상한) |
| `kinds` `late` | 바위 종류 `[[id(debris의 것), 무게, 몇 층부터, late층부터의 무게], …]` |

층마다 바위를 코드로 바꾸려면 [`MineFloor`](events#minefloor).

## 사막의 던전 (`dungeon`)

사막의 던전은 **끝없는 한 층짜리 미로**로, 입구에서 안으로 들어갈수록 깊어집니다(아래로 내려가는 계단은 없음). 매일 아침 월드의
운명으로 새로 짜입니다. 방은 입구(칸 (0, 0), 사막으로 올라가는 사다리, 유일한 출구)를 둘러싼 끝없는 격자의 칸이고, **깊이**는 입구까지의
거리(|x| + |z|: 문은 늘 한 칸 깊이 또는 한 칸 얕게)입니다. 입구 말고는 모든 방이 입구 쪽 이웃 하나(부모)와 이어져 어느 방이든 닿을 수 있고,
아무도 부모로 고르지 않은 방은 막다른 곳입니다. 방마다 자기 굴림만으로 만들어지므로 아무리 깊어도 됩니다. 깊을수록 상자의 보상이
좋아지고 몬스터가 강해지고 진해집니다. 방 번호(광산 층 번호)는 `10000 + 칸의 번호`(입구 0, 그다음 깊이 1의 4칸, 깊이 2의 8칸 …).

| 키 | |
|---|---|
| `loops` | 옆에 붙었지만 부모 관계가 아닌 두 방에 문을 더 낼 확률(/100) |
| `size` | 방의 칸 수 `[x, z, 굴림]` → 각각 + 2 × 난수(굴림) |
| `chest` | 방(입구·쉼터 빼고)에 상자가 있을 확률(/100) |
| `loot` `picks` | 깊이마다의 보상 표 `[[이 깊이부터, [[아이템, 최소, 최대, 무게], …]], …]`, 상자 하나의 물건 수 `[기본, 난수]` |
| `rest` | **쉼터** `[확률(/100), 이 깊이부터, 한 변의 칸 수]` (x와 z가 모두 짝수인 칸에서만: 둘이 붙지 않음): 몬스터도 상자도 없고 모닥불·집·우물·탁자와 떠돌이 상인의 노점 |
| `camp` | 쉼터 상인이 파는 것 (게임의 상점 `camp`, 그 아이템의 값에) |
| `kinds_every` `tier_every` | 깊이 d의 방에 광산 `d × kinds_every`층의 몬스터 종류, 등급 `(d − 1) ÷ tier_every` |
| `at` `station` `y` | 던전 입구, 사막의 열기구 정거장 (월드 칸 `[x, z]`), 방들의 바닥 높이 |

```rust
#[on(Enable)]
fn bigger(_e: Enable) {
    Registry::patch(r#"{"dungeon": {"loops": 15, "rest": [70, 3, 21]}}"#); // 길을 더 잇고, 쉼터를 자주
}
```

### 간이 침대

설치물(`progress.placeables`)의 `"at"`은 놓을 수 있는 곳입니다: `"farm"`(땅 위; 없으면 이것만), `"rest"`(광산·던전의 쉼터),
`"below"`(광산·던전 어디든). `"sleep": true`면 그 위에서 잘 수 있습니다. 바닐라의 간이 침대(`cot`)는 `"at": ["rest"]`라 쉼터에만 놓입니다.
간이 침대에서 자면 그 층(던전의 방)은 다음 날에도 그날 짜인 그대로 남고(크기·캠프·입구 쪽 길; 다른 문은 새 미로로), 자던 사람은 아침에
그 자리에서 깨어납니다. 간이 침대는 한 번 펴면 다시 접을 수 없고, 한 번 자면 아침에 사라집니다. 남지 않는 층에 둔 것은 그 층과 함께 사라집니다.

```rust
Registry::patch(r#"{"progress": {"placeables": {"cot": {"at": ["farm", "below"]}}}}"#); // 어디서든 펴고 자기
```
