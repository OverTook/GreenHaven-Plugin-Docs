---
title: 월드와 하루
nav_order: 6
parent: 플러그인
redirect_from:
  - /world
  - /world.html
---

# 월드와 하루
{: .no_toc }

1. TOC
{:toc}

월드는 **처음 만들 때 한 번 생성되고, 그 뒤로는 저장된 것**입니다. 바닐라 생성기는 서버 코드이고,
플러그인은 만들어질 때([`WorldCreate`](events#worldcreate), [`ChunkGenerate`](events#chunkgenerate)), 청크를 불러올 때([`ChunkLoad`](events#chunkload))와 그 뒤 어느 이벤트에서나
블록·구조물·주민을 바꿀 수 있습니다. 바뀐 것은 그 월드의 모두에게 바로 갑니다.

## 블록

- 청크는 32 × 32칸, 높이 64칸 (y −8 ~ 55). 블록 하나는 y−0.5 ~ y+0.5를 채웁니다: 마을 땅은 y 0의 블록, 윗면 0.5.
- 청크는 누가 처음 가까이 갈 때 만들어지고(바닐라 땅, 그다음 `chunk.generate`), `<data>/chunks/<월드>/<x>_<z>.bin`에
  저장되어 그 뒤로는 저장된 그대로입니다.
- 블록: `air` `grass` `sand` `snow` `stone` `dirt` `road` `bed`(물 밑 모래) `water` ([`Block`](sdk#block)), 그리고 플러그인이
  등록한 [새 블록 종류](#새-블록-종류).
- 서버의 이동 판정도 블록을 읽습니다: 블록을 쌓으면 그 위를 걸을 수 있고, 파내면 떨어집니다.
- 많이 바꿀 때는 `World::set_blocks(&[(x, y, z, Block)])`: 한 번에 65 536개까지, `set_block`을 여러 번 부르는 것보다 훨씬 쌉니다.
  `ChunkGenerate` / `ChunkLoad`에서는 그 청크의 것만 받습니다.
- 청크 표시: `World::chunk_mark(x, z, name)` → `i64`(0: 없음) / `set_chunk_mark(x, z, name, v)`. 청크마다 이 플러그인의 숫자로,
  월드와 함께 저장됩니다. 이미 만들어진 청크에 새 블록을 한 번씩 넣을 때 씁니다([`ChunkLoad`](events#chunkload)).

```rust
#[on(ChunkGenerate)]
fn flat(e: ChunkGenerate) {
    let (x0, z0) = e.first_cell();
    let n = e.size() - 1;
    e.world().fill((x0, Block::LOWEST, z0), (x0 + n, -1, z0 + n), Block::DIRT);
    e.world().fill((x0, 0, z0), (x0 + n, 0, z0 + n), Block::GRASS);
    e.world().fill((x0, 1, z0), (x0 + n, Block::LOWEST + 63, z0 + n), Block::AIR);
    e.clear_props();
}
```

## 새 블록 종류

플러그인은 [`Enable`](events#enable)에서 블록 종류를 등록합니다. 그려지는 모습은 셋 중 하나입니다(앞의 것이 있으면 그것):
자기 **모델**(GLB), 자기 **텍스처**의 큐브(PNG, 비쳐 보이게도), 바닐라 블록의 모델에 **색**을 입힌 것. 여러 칸을 차지할 수도 있습니다.

```rust
#[on(Enable)]
fn enable(_e: Enable) {
    Registry::block("ruby_block", &BlockKind::new("루비 블록", "stone", "e0405a"));
    Registry::block("brick", &BlockKind::textured("벽돌", "res://plugins/blocks/brick.png"));
    Registry::block("glass", &BlockKind { alpha: true, ..BlockKind::textured("유리", "res://plugins/blocks/glass.png") });
    Registry::block("fence", &BlockKind { side: "res://plugins/blocks/fence_rail.glb".into(),
        ..BlockKind::model("나무 울타리", "res://plugins/blocks/fence_post.glb", [1, 1, 1]) });
    Registry::block("hut", &BlockKind::model("오두막", "res://plugins/blocks/hut.glb", [3, 3, 3]));
}
```

그림과 모델은 플러그인의 `assets/plugins/<이름>/`에 넣고 `res://plugins/<이름>/…`로 부릅니다(접속할 때 게임이 받아 감).

| `BlockKind` | |
|---|---|
| `name` | 이름 (아이템 이름도) |
| `look` | 그려질 바닐라 블록: `"grass"` `"sand"` `"snow"` `"stone"` `"dirt"` |
| `tint` | 그 위에 입힐 색 `"rrggbb"` |
| `solid` | 단단함 (`false`: 지나다님). 기본 `true` |
| `item` | 놓는 아이템이 따로 있음 (아이템 id는 블록 id, `"type": "block"`, 아이콘은 `texture`). 기본 `true` |
| `texture` | 여섯 면의 PNG: 자기 텍스처의 큐브 (픽셀 그대로) |
| `top` / `bottom` | 위·아래 면만 다른 PNG (없으면 `texture`) |
| `alpha` | PNG의 알파대로 비쳐 보임 (유리, 잎) |
| `model` | 자기 GLB 모델: 원점은 차지하는 칸들의 바닥 가운데, 1 유닛 = 한 칸 |
| `side` | +x를 향한 GLB: 같은 종류나 불투명하고 단단한 블록이 있는 옆(네 방향)마다 그쪽으로 돌려 붙임 (울타리의 가로대) |
| `size` | `[x, y, z]` 차지하는 칸 (각 1~16, 놓은 칸에서 +x +y +z로). 기본 `[1, 1, 1]` |
| `rotate` | 마인크래프트처럼 놓는 사람 쪽을 보게 90°씩 돌려 놓음: 모델의 +z가 플레이어 쪽, 홀수 회전이면 `size`의 x와 z가 바뀜 (`BlockKind::model`은 기본 켬). [`BlockPlace`](events#blockplace--blockbreak)의 `turn()` |

`BlockKind::new(name, look, tint)`, `BlockKind::textured(name, png)`, `BlockKind::model(name, glb, size)`로 시작해
`{ alpha: true, ..BlockKind::textured(…) }`처럼 나머지를 정합니다.

- **여러 칸**: 놓은 칸에 그 종류, 나머지 칸은 그려지지 않는 부품 블록이 되어 건물처럼 그 칸들 모두 막힙니다(`solid`가 꺼져
  있으면 모두 지나다님). 놓을 때 모든 칸이 비어 있어야 하고, 어느 칸을 부숴도 전체가 사라져 아이템 하나로 돌아옵니다.
  `set_block` / `set_blocks`로 놓아도 부품까지 채워집니다(청크 이벤트 안에서는 그 청크의 칸만).
- **충돌**은 칸 단위입니다: 단단한 종류는 모양과 상관없이 그 칸 전체가 막힙니다(서버의 걷기 판정과 같게).
- 비쳐 보이거나 모델이거나 지나다니는 종류 옆의 블록 면은 그려집니다.

- 번호는 서버가 9부터 매기고 `<data>/blocks.json`에 남겨, 저장된 청크가 늘 같은 블록을 뜻합니다. 코드에서는
  `Block::named("ruby_block")`으로 찾아 `set_block` / `set_blocks`로 놓습니다. 접속하는 게임은 레지스트리의 `"blocks"`로 그립니다.
- `item`이 있으면 플레이어가 그 아이템을 손에 들고 사용 버튼으로 앞 칸에 놓고(닿는 곳, 빈 칸, 옆에 단단한 블록이 있어야),
  곡괭이로 부숴 가방에 돌려받습니다: [`BlockPlace` / `BlockBreak`](events#blockplace--blockbreak). 바닐라 땅의 블록은
  부서지지 않습니다.
- 예: `plugins/blocks`.

## 구조물

마을의 건물·울타리·밭·데크·장소·성벽(`wall`)·탑(`tower`)·성문(`gate`, 레버 포함)·바위 둑(`ruins`)·암초(`reef`)·열기구
정거장(`station`)·막힌 칸(`block`) … 이 모두 구조물이고, 각각 번호와 구획(`plot`)이 있습니다. 서버의 판정(벽 안에 서 있음,
성벽은 성문으로만 넘음, 정거장 내리는 곳, 레버)과 게임의 그림이 모두 이 목록에서 나옵니다: **성벽 구조물을 빼면 성벽
판정도 사라집니다.**

```rust
#[on(WorldCreate)]
fn open(e: WorldCreate) {
    e.world().remove_plot("wall"); // 성벽·성문·바위 둑·암초
    for s in e.world().structures() {
        if s.plot() == "station" { s.move_to(s.get("x") + 4.0, s.get("z"), s.get("yaw")) }
    }
    e.world().put_structure(r#"{"k": "building", "m": "house_Lv1", "x": 40, "z": 60, "yaw": 0, "plot": "my_house"}"#);
}
```

목수가 짓는 건물도 구조물로 들어갑니다.

## 주민

바닐라 주민 10명이 월드를 만들 때 들어가고, 그 목록이 서버의 주민 AI·대사·선물·의뢰와 게임의 주민 표가 됩니다. 주민은
서버가 걷게 하고 말도 서버가 합니다: 광장의 잡담, 둘이 만나 나누는 말과 소문, 플레이어가 하는 일을 보고 하는 말, 지나갈
때의 인사, 말을 걸었을 때의 대답이 모두 대사 표(`client.VillagerLines` 등, [등록](rules)으로 더함)에서 나옵니다.

```rust
#[on(WorldCreate)]
fn neighbor(e: WorldCreate) {
    e.world().spawn_npc(r#"{"id": "haneul", "name": "하늘", "look": "soyul", "home": "library",
        "schedule": [[480, "square"], [660, "library"]]}"#);
}
```

- `look`: 모습·얼굴·목소리·일정을 빌려 올 기존 주민 id.
- 장소(`home`, `schedule`, `rain`): 마을의 장소 키 (`square` `library` `dock` `general` …, 각 주민의 집, 또는 구조물 `place`의 `key`).
- 이미 있는 주민은 [`Npc`](sdk#npc)의 `set` `go_to` `say` `remove`.

## 하루

각 월드는 자기 시계를 갖고(아무도 없으면 멈춤), 마을·주민·밤 몬스터는 그 시계를 따릅니다.

| 바꾸는 것 | |
|---|---|
| `Player::set_time(minute)` | 지금 시각 |
| `World::set_day(n)` | 날짜 |
| `World::set_morning_time(minute)` `clear_morning_time()` | 밤이 끝나는 시각 |
| `World::set_night_time(minute)` `clear_night_time()` | 밤이 시작되는 시각 |
| `World::set_dawn_time(minute)` `clear_dawn_time()` | 몬스터가 강해지는 시각 |
| `World::end_day()` | 지금 하루를 끝냄 |
| [`DayEnd`](events#dayend) | 끝나려는 하루를 막기 |
| [`DayChange`](events#daychange) | 날짜가 넘어가지 않게 |

세 시각은 하늘과 몬스터에 함께 적용되고, 계절과 상관없이 하나의 값입니다. 월드에 저장되고 `clear_*`로 규칙 값으로 돌아갑니다. 밤이 하루 안에 있어도 됩니다(1:00~5:00). 새 날의 시작은 6:00으로 고정이고, 더 일찍 끝내려면 `Tick`에서 시각을 보고 `end_day()`를 부릅니다.

이 설정들만 월드마다이고, 규칙의 다른 값은 서버가 켜질 때([`Enable`](events#enable))만 바꿉니다(규칙은 서버 전체가 함께 씀).

### 서버 하나의 시계

`tick`에서 벽시계 `now()`로 서버 시각을 계산해 `Player::set_time`으로 맞추면 모든 월드가 한 시계를 씁니다. 아무도 없는
동안에도 벽시계는 흐르니 들어오면 그 시각부터입니다. 예: `plugins/server_clock`.

```rust
#[on(Tick)]
fn keep_to_the_server(e: Tick) {
    let per_day = setting_num("day_real_minutes", 14.0) * 60_000.0;
    let want = 360 + ((now() % per_day) / per_day * 1200.0) as i64;
    if (e.num("minute") as i64 - want).abs() > 2 { Player::default().set_time(want) }
}
```

## 모두의 월드

바닐라 규칙은 **모두가 월드 하나**입니다. 그 월드는 **서버의 월드**(`@world`, 플레이어 이름으로는 못 씀)이고, 서버가 아무도
없어도 그 월드를 돌립니다(주민, `tick`, 밤, 시계). 게임 안의 서버(혼자 하기, 서버 개설로 연 LAN)도 같습니다: 혼자 하기의 월드도
그 서버의 `@world`이고, 연 사람도 들어온 사람도 그 안의 플레이어입니다. 어느 서버든 코드는 같습니다.

들어오는 사람은 그 월드의 농장 일꾼입니다: 땅·블록·작물·마을·주민·몬스터는 함께, **돈**·가방·기력·스킬·호감도는 각자. 돈은 어느
서버에서나 각자의 것이고(바닐라), 출하 상자에 넣은 것은 넣은 사람에게 그 사람의 아침에 정산됩니다. 모두가 잠들거나 하루의 끝(기본
다음날 6:00)이면 그 월드의 하루가 끝나고 각자의 아침이 옵니다.

바닐라의 열기구는 마을 해변의 정거장과 사막(던전 입구 옆)의 정거장을 오갑니다(같은 월드 안: 행동 `balloon`, `why` "desert" / "town").

### 플러그인의 월드

월드를 더 두려면 플러그인이 만듭니다(Bukkit처럼): `Server.create_world("garden")`은 바닐라 땅과 마을로 된 새 월드(`@garden`,
저만의 씨앗; `id`는 영문·숫자·`_ - .` 32자까지)를 만들어 서버가 돌리고 저장하며, 그 월드에서 `world.create`와 `chunk.generate`가
불립니다(`World::id()`가 "garden": 그 월드만의 땅이나 구조물을 거기서; 모두의 월드는 "world"). `Player::move_world("garden", true)`는
그 플레이어를 그 월드의 열기구 정거장으로 옮깁니다(`false`면 농장 집 앞으로, `""`는 모두의 월드; 떠난 월드에서 `leave`, 간 월드에서
`join`; 가방·돈·스킬은 함께). 예제 [`friend_lands`](samples)(친구 땅).

## 저장

- **바닐라 규칙: 자고 일어난 아침에만 저장됩니다.** 그 전에 주인이 나가거나 서버가 꺼지면 그날 한 일(블록, 플러그인 값과
  데이터까지)은 사라집니다.
- 그 자리에서 남겨야 하면 `World::save_now()`: 월드(게임, 블록, 데이터)를 아침처럼 지금 저장 (날은 그대로 이어짐).
- 잠이 없는 서버(RPG 등)는 `World::set_live_saving(true)`: 1분마다와 플레이어가 나갈 때 블록까지 저장합니다.
- 연결이 끊긴 플레이어는 `resume-seconds`(기본 30초) 안에 돌아오면 그날 상태 그대로 이어집니다.
- 나가기 전 경고는 `World::set_quit_warning("...")` (`""`: 띄우지 않음; 실시간 저장이면 기본으로 안 띄움).
- 주민의 기억(본 일과 소문, 플레이어와 마지막으로 나눈 말과 받은 선물, 최근에 한 말)은 월드와 함께 저장됩니다. 주민이 서 있는
  곳과 하던 일은 저장하지 않고, 월드가 열릴 때 그 시각의 일정대로 다시 놓입니다.
- 엔티티는 저장되지 않습니다.
