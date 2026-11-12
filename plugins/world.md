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

## 플러그인의 월드 생성기

`ChunkGenerate`는 바닐라 땅이 이미 깔린 청크를 고칩니다. 땅을 처음부터 만들려면 **생성기**를 씁니다(Bukkit의 ChunkGenerator;
2026-11-11, 예제 [`islands`](samples)). `ChunkGenerator`를 구현한 타입에 `#[generator("이름")]`을 붙이면 생성기
`"<플러그인>:<이름>"`(이름은 영문·숫자·`_ - .` 32자까지)이 생깁니다. 그것으로 만든 월드 — `Server.create_world_with(id, "islands:islands", "")`,
모두의 월드면 server.properties `level-type=islands:islands` — 의 청크가 처음 만들어질 때마다 `generate`가 불립니다.

```rust
use greenhaven_plugin::*;

#[generator("islands")]
struct Islands;

impl ChunkGenerator for Islands {
    fn generate(&self, c: &mut ChunkData) {
        let n = c.noise(); // 월드의 씨앗
        let ground = |x: i64, z: i64| (n.fbm2(x as f64 / 96.0, z as f64 / 96.0, 4) * 26.0 - 4.0) as i64;
        for (x, z) in c.columns() {
            let h = ground(x, z).clamp(Block::LOWEST + 2, 40);
            c.fill((x, Block::LOWEST, z), (x, h - 1, z), Block::STONE);
            c.set(x, h, z, if h <= 1 { Block::SAND } else { Block::GRASS });
            if h < 0 { c.fill((x, h + 1, z), (x, 0, z), Block::WATER); } // 바다
        }
        let trunk = Block::named("islands_trunk").unwrap_or(Block::DIRT);
        Trees::new(trunk, Block::GRASS).place(c, |x, z| Some(ground(x, z)).filter(|h| *h > 1 && *h < 40));
    }
}
```

| `ChunkData` | |
|---|---|
| `chunk()` / `first_cell()` / `size()` | 청크 번호 (x, z) / 첫 칸 (x0, z0: 칸은 x0..x0+32, z0..z0+32) / 32 |
| `seed()` / `noise()` | 월드의 씨앗 / `Noise::new(seed)` |
| `columns()` | 칸 기둥 `(x, z)` 하나씩 |
| `contains(x, z)` | 이 청크의 칸인지 |
| `set(x, y, z, b)` / `get(x, y, z)` | 블록 놓기 / 지금까지 놓은 것 (밖은 공기) |
| `fill(from, to, b)` | 상자 채우기 (두 끝 포함, 이 청크 안만) |
| `top(x, z)` → `Option<i64>` | 공기 아닌 가장 높은 칸 |

- 좌표는 월드의 칸, y는 `Block::LOWEST`(−8)부터 64칸. 놓지 않은 칸은 공기입니다.
- 블록마다 호스트 호출을 하지 않습니다: 핸들러가 끝나면 청크 하나가 버퍼 하나로 서버에 갑니다(호스트 함수 [`chunk_put`](abi)). 서버는
  그 플러그인에만, 그 생성기로 만든 월드에서만 이벤트 `"gen:<이름>"`을 보냅니다.
- **큰 블록**(여러 칸 종류)은 부품과 함께 놓입니다. 청크 **바로 밖**에 놓은 큰 블록이 이 청크로 들어오면 이 청크에도 그 부품이 놓이니,
  큰 블록이 닿는 청크마다 같은 `set`을 하세요. 그 밖의 청크 밖 칸은 무시됩니다.
- **같은 씨앗, 같은 땅**: 월드를 리셋하면 청크를 다시 만들므로, 땅은 씨앗과 좌표만으로 정해져야 합니다. `Noise::new(seed)`의
  `noise2(x, z)` `noise3(x, y, z)` `fbm2(x, z, 옥타브)`(약 −1~1; 좌표를 척도로 나눔: `x / 64.0`이면 64칸쯤에 언덕 하나).
- **나무**: `Trees::new(줄기, 잎)`(청크에 4그루, 줄기 4~6, 수관 2; 필드 `per_chunk` `height` `crown`)`.place(c, |x, z| 땅 높이 또는 None)`.
  청크마다 자기 나무와 이웃 청크 나무의 이 청크 부분을 놓아, 청크 경계에 선 나무도 온전합니다.
- 만든 청크는 여느 청크처럼 저장되고 그 뒤 `ChunkGenerate` / `ChunkLoad`도 그대로 옵니다. 생성기가 없거나(플러그인이 꺼짐) 아무것도
  만들지 못하면 빈 청크입니다.

## 새 블록 종류

플러그인은 [`Enable`](events#enable)에서 블록 종류를 등록합니다. 그려지는 모습은 셋 중 하나입니다(앞의 것이 있으면 그것):
자기 **모델**(GLB), 자기 **텍스처**의 큐브(PNG, 비쳐 보이게도), 바닐라 블록의 모델에 **색**을 입힌 것. 여러 칸을 차지할 수도 있습니다.

```rust
#[on(Enable)]
fn enable(_e: Enable) {
    Registry::block("ruby_block", &BlockKind::new("루비 블록", "stone", "e0405a"));
    Registry::block("brick", &BlockKind::textured("벽돌", "res://packs/blocks/brick.png"));
    Registry::block("glass", &BlockKind { alpha: true, ..BlockKind::textured("유리", "res://packs/blocks/glass.png") });
    Registry::block("fence", &BlockKind { side: "res://packs/blocks/fence_rail.glb".into(),
        ..BlockKind::model("나무 울타리", "res://packs/blocks/fence_post.glb", [1, 1, 1]) });
    Registry::block("hut", &BlockKind::model("오두막", "res://packs/blocks/hut.glb", [3, 3, 3]));
}
```

그림과 모델은 리소스 팩(폴더 `<data>/packs/<팩>/packs/<팩>/`, 또는 zip)에 넣고 `res://packs/<팩>/…`로 부릅니다. 플러그인은
plugin.json `"packs"`에 그 팩을 적습니다(접속할 때 게임이 받아 감; [리소스 팩](index#리소스-팩)).

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
- 큰 블록의 한 칸 위에 다른 블록을 놓으면(`set_block` `set_blocks` `fill`) **그 큰 블록 전체가 먼저 사라집니다**: 반쪽 조각상이나 부서지지
  않는 부품이 남지 않습니다. 큰 종류로 `fill`하면 그 크기 간격으로, 상자 안에 다 들어가는 것만 온전히 놓입니다.
- **충돌**은 칸 단위입니다: 단단한 종류는 모양과 상관없이 그 칸 전체가 막힙니다(서버의 걷기 판정과 같게).
- 비쳐 보이거나 모델이거나 지나다니는 종류 옆의 블록 면은 그려집니다.

- 번호는 서버가 9부터 매기고 `<data>/blocks.json`에 남겨, 저장된 청크가 늘 같은 블록을 뜻합니다. 코드에서는
  `Block::named("ruby_block")`으로 찾아 `set_block` / `set_blocks`로 놓습니다. 접속하는 게임은 레지스트리의 `"blocks"`로 그립니다.
- `item`이 있으면 플레이어가 그 아이템을 손에 들고 사용 버튼으로 앞 칸에 놓고(닿는 곳, 빈 칸, 옆에 단단한 블록이 있어야),
  곡괭이로 부숴 가방에 돌려받습니다: [`BlockPlace` / `BlockBreak`](events#blockplace--blockbreak). 바닐라 땅의 블록은
  월드의 블록 규칙이 허락할 때만 부서지고 놓입니다(아래).
- 예: `plugins/blocks`.

## 바닐라 블록 부수기·놓기

`World::set_block_rules(json)` (월드와 함께 저장; 서버 전체는 규칙 키 `"block_rules"`): 어느 바닐라 블록(`grass` `sand`
`snow` `stone` `dirt` `road` `bed`; 공기·물은 안 됨)을 사용 버튼으로 부술지, 무엇을 손에 들어야 하는지(`tool`, ""는 빈손이나
동작이 없는 아이템), 무엇을 땅에 떨굴지(`drop`, ""는 없음, 안 쓰면 블록 이름의 아이템: 서버가 아는 것일 때만), 어느 아이템이
어느 블록을 놓는지. 규칙이 없으면(바닐라 농장) 아무것도 부서지지 않습니다.

```rust
#[on(Join)]
fn joined(e: Join) {
    e.world().set_block_rules(r#"{"break": {"*": {}, "stone": {"tool": "pickaxe"}}, "place": ["dirt", "stone"]}"#);
}
```

`"break": ["grass", "dirt"]`(이름만), `"place": {"cobble": "stone"}`(아이템 → 블록)도 됩니다. `"{}"`는 서버의 규칙으로
돌아갑니다. 놓기·부수기는 플러그인 종류와 같은 검사(닿는 곳, 빈 칸, 옆의 단단한 블록, 사람 몸)를 거치고
[`BlockPlace` / `BlockBreak`](events#blockplace--blockbreak)가 불립니다. 놓인 블록은 걷기 판정·길 찾기에 다른 블록과 똑같이 쓰입니다.

## 블록 데이터

`World::block_data(x, y, z, key)` / `set_block_data(x, y, z, key, value)` (""는 지움): 블록 하나에 짧은 값 몇 개(키 8개, 키
32바이트, 값 256바이트, 청크마다 1024블록까지; 공기에는 없음). 청크와 함께 저장되고 보는 게임에 갑니다. 블록이 다른 것으로
바뀌면 사라집니다(바꾼 뒤 다시 쓰기). 이벤트 안에서 쓴 값은 이벤트가 끝난 뒤에 들어갑니다. 게임이 그리는 키:

| 키 | |
|---|---|
| `open` = `"1"` | 플러그인 종류의 모델을 모서리를 축으로 90° 돌려 그림 (문; 지나다닐지는 종류가 정하니 닫힌 문 / 열린 문 두 종류로) |
| `text` | 블록 위에 글 (표지판) |

## 가짜 블록

`Player::show_block(x, y, z, block)` / `clear_fake_blocks()` (Bukkit의 sendBlockChange): 그 사람의 게임에만 그려지는 블록
(미리보기, 힌트). 월드의 블록이 아니어서 서버는 판정에 쓰지 않습니다. 지우거나, 다른 월드로 가거나, 그 칸에 진짜 블록이
놓이면 사라집니다. 예: `plugins/builder`의 `/미리보기` → `/짓기`.

## 구조물

마을의 건물·울타리·밭·데크·장소·성벽(`wall`)·탑(`tower`)·성문(`gate`, 레버 포함)·바위 둑(`ruins`)·암초(`reef`)·열기구
정거장(`station`)·막힌 칸(`block`) … 이 모두 구조물이고, 각각 번호와 구획(`plot`)이 있습니다. 서버의 판정(벽 안에 서 있음,
성벽은 성문으로만 넘음, 정거장 내리는 곳, 레버)과 게임의 그림이 모두 이 목록에서 나옵니다: **성벽 구조물을 빼면 성벽
판정도 사라집니다.**

구조물은 [`Entity`](sdk#structure)입니다(`location` `move_to` `remove`; 혼자 움직이지 않고 체력이 없음). 세울 것은 [`Placement`](sdk#placement)
빌더로 줍니다(2026-11-11; 예전엔 JSON 글, `Structure`의 글 키 `get` `text`도 타입 있는 메서드로 바뀜).

```rust
#[on(WorldCreate)]
fn open(e: WorldCreate) {
    e.world().remove_plot("wall"); // 성벽·성문·바위 둑·암초
    for s in e.world().structures() {
        if s.plot() == "station" { let (x, y, z) = s.location(); s.move_to(x + 4.0, y, z); }
    }
    e.world().put_structure(&Placement::building("house_Lv1").at(40.0, 60.0).plot("my_house"));
    e.world().put_structure(&Placement::prop("res://packs/deco/lamp.glb").at(12.0, 5.0).turned(1.57).scaled(1.2).plot("deco"));
}
```

`Placement::prop(model)`(서 있는 것: 플러그인의 GLB나 게임의 모델 이름) `building(model)`(게임의 건물: 문과 방) `blocked(x, z, w, d)`(아무도
못 서는 칸) 위에 `.at(x, z)` `.raised(y)` `.turned(yaw 라디안)` `.scaled(s)` `.plot(name)` `.hitbox(..)`. 목수가 짓는 건물도 구조물로 들어갑니다.

## 히트박스와 충돌

블록이 아닌 것도 부딪힙니다. 구조물과 단단한 엔티티는 **히트박스**를 가지고, 서버는 월드마다 그 상자들을 청크별로
모아 둡니다(충돌층). 걸음 판정, `path_blocks`·`path`, 밤의 몬스터, `World::is_solid` / `cast_blocks`가 블록과 함께 이 상자를
단단한 것으로 보고, 게임도 같은 상자로 몸을 만듭니다(부딪히고, 게임 쪽 코드의 `World::cast_to` 질의에 닿음). 마을의 건물 벽,
헛간, 울타리, 성벽 선도 같은 층에 있습니다.

히트박스는 상자 목록 `[[x, z, w, d, y, h], ...]`(32개까지)입니다: 그 물건의 칸에서 (x, z)칸 떨어진 곳부터(방향 0일 때,
x·z는 월드의 칸) 가로 w × 세로 d칸, 바닥 블록(땅 위에 섰을 때 발이 있는 블록)에서 y블록 위부터 h블록 높이. 물건의
방향을 90도 단위로 반올림해 함께 돕니다.

- 구조물: `Placement::hitbox(&[[x, z, w, d, y, h]])`. 바닥은 그 칸의 가장 높은 단단한 블록 바로 위(+ `y`). 적지 않은 `prop`·`building`은
  놓을 때 서버가 정합니다: 리소스 팩의 GLB면 그 크기, 아니면 발자국에 2블록 높이.
- 엔티티: `set_solid(true)`(기본은 지나감), 모양은 `set_hitbox(&[[x, z, w, d, y, h]])`(없으면 GLB 크기, 아니면 한 칸 두 블록).
  움직이면 따라가고, 지우면 빠집니다. 플레이어가 타고 있는 탈것은 그 플레이어의 걸음에서는 빼고 봅니다. yaw가 직각이면 상자째
  90°씩, 아니면 어느 각도로든 돕니다(돌린 상자가 가운데를 덮는 칸들). pitch·roll은 상자를 기울이지 않습니다.
- 바닐라 구조물은 종류대로: 건물 벽 12블록, 울타리 4블록(가늘게: 옆에 선 몸은 그 칸에 들어가도 됨), 성벽 선(성문으로만).

```rust
w.put_structure(&Placement::prop("res://packs/arena/pillar.glb").at(10.0, 4.0).hitbox(&[[0, 0, 2, 2, 0, 4]]));
let gate = w.spawn("res://packs/arena/gate.glb", 12.0, 0.5, 4.0).unwrap();
gate.set_hitbox(&[[0, -1, 1, 3, 0, 3]]);
gate.set_solid(true);
if w.is_solid(11.0, 1.0, 4.0) { /* 블록이나 상자 */ }
let d = w.cast_blocks((0.0, 1.0, 4.0), (1.0, 0.0, 0.0), 30.0); // 처음 닿는 단단한 칸까지 m
```

### 메시 충돌: 완성된 맵

칸 상자로는 경사로, 얇은 벽, 난간, 계단을 만들 수 없습니다. 맵을 GLB로 만들었다면 그 삼각형 그대로 충돌시키세요(한 번에 하려면
아래 [맵 월드](#맵-월드)).

```rust
// 빈 월드(server.properties level-type=void, 또는 create_world_with(id, "void", ..))의 Enable이나 world.create에서
let map = w.spawn("res://packs/arena/map.glb", 0.0, 0.0, 0.0).unwrap();   // 그리는 모델
map.set_collision_mesh("res://packs/arena/map_col.glb");                 // 충돌용(같은 GLB여도 됨)
map.set_persistent(true);
w.set_view(&View { curve: false, fog: 300.0, sight: 400.0, occlusion: true }); // 평평하게, 멀리까지, 벽 뒤는 안 그림
w.set_spawn(0.0, 1.0, 0.0, 0.0);
```

- 충돌 GLB는 어느 리소스 팩의 것이든(팩이 바꿔치기한 게임의 모델도) 됩니다. 삼각형 수에는 한도가 없습니다(얼마나 무거워도 되는지는
  서버 주인이 정함). 충돌 메시 엔티티는 월드에 256개까지.
  GLB의 노드 위치·회전·크기를 모두 반영하고, 엔티티의 자리·회전·크기대로 놓입니다.
- 서버의 걷기 검사: 위치 보고마다 직전 위치와 이은 걸음이 벽을 앞면에서 뚫으면 되돌립니다. 바닥, 경사로, 계단, 2층을 발밑 땅으로
  봅니다. 총알(`World::cast` / `cast_for`), `cast_blocks`, 투사체, 폭발의 엄폐, `seen_from`도 면에 막힙니다(맞은 것은 `"entity"`, 그 id).
- 게임도 같은 삼각형으로 몸을 만들어 플레이어가 부딪힙니다.
- 걷기 판정의 엄격함: 기본(`line`)은 무릎·가슴 높이 선 두 줄만 봐서 정상 플레이어를 잘못 되돌리는 일이 없지만, 조작된 게임이 몸보다
  좁은 틈이나 낮은 창, 벽 뒷면을 지나가는 건 못 잡습니다. 경쟁 맵이면 `w.set_mesh_check(true, 0.25)`(몸 반지름 0.05~0.5 m, 게임 캡슐은
  0.54)로 몸 크기 구까지 대 보게 하세요. 네트워크가 나쁜 플레이어는 모서리에서 가끔 되돌려질 수 있습니다. `clear_mesh_check()`는 서버
  기본값(server.properties `mesh-walk-check=line|body`, `mesh-walk-radius=0.25`).
- 길찾기(`path_blocks`)와 몬스터는 칸 단위라 메시를 모릅니다. FPS 맵에는 `World::set_mode("none")`로 몬스터를 끄세요.
- 충돌 메시가 있는 엔티티(맵 같은)는 거리와 상관없이 보입니다(2026-11-11부터; 다른 엔티티는 원점에서 150 m 안). 월드에 256개까지(server.properties `max-collision-meshes`로 4096개까지).
- 게임은 큰 팩 메시를 32 m 조각으로 나눠 화면 밖의 조각을 그리지 않고(frustum culling), 월드의 `View`가 `occlusion`이면 충돌
  메시로 가리개(occluder)를 만들어 벽 뒤를 그리지 않습니다.

### 맵 월드

빈 월드(`Server.create_world_with(id, "void", "")`)의 `WorldCreate`에서 맵 GLB를 `World::spawn`으로 세웁니다. 맵, 문, 소품이
모두 같은 `ModelEntity`입니다(2026-11-11 잠깐 있던 `create_map_world` / 생성기 `"map"`은 이것과 같아 없앴습니다).

- `set_persistent(true)`: 월드와 함께 저장 (`WorldCreate`는 월드가 처음 만들어질 때 한 번만).
- `set_collision_mesh(glb)`: 그 삼각형으로 단단하게(`pack:<팩>/<id>`도). 같은 모양의 더 단순한 메시가 쌉니다. 거리와 상관없이 보이고 월드에 256개까지(server.properties `max-collision-meshes`로 4096개까지).
- **충돌 없는 것**(수풀, 풀, 장식): 충돌 메시를 주지 않으면 됩니다. `spawn`한 엔티티는 기본으로 통과합니다(`set_solid`도 꺼짐).
  많으면 맵 GLB에 그려 넣고 충돌 GLB에서만 빼는 편이 쌉니다(엔티티 하나가 그리기 한 번, 월드에 1024개까지, 150 m 안에서만 보임).
- `World::set_spawn`, `World::set_view(&View { curve: false, occlusion: true, .. })`: 평평하게, 벽 뒤는 그리지 않음.

```rust
// 맵 하나 = 빈 월드 + WorldCreate에서 세운 모델 (World::spawn 하나로: 맵, 소품 모두 같은 ModelEntity)
#[command("경기장", "")]
fn arena(c: Command) {
    Server.create_world_with("arena", "void", "");   // 처음 한 번만 만들어짐
    c.player().move_world("arena");
}

#[on(WorldCreate)]
fn build(e: WorldCreate) {
    let w = e.world();
    if w.id() != "arena" { return }
    if let Some(map) = w.spawn("res://packs/arena/arena.glb", 0.0, 0.0, 0.0) {
        map.set_persistent(true);                                   // 월드와 함께 저장
        map.set_collision_mesh("res://packs/arena/arena_col.glb"); // 단단하게 (없으면 통과)
    }
    if let Some(bush) = w.spawn("res://packs/arena/bush.glb", 12.5, 0.0, -3.2) {
        bush.set_persistent(true);                                  // 충돌 메시 없음: 보이기만 하고 통과
    }
    w.set_spawn(0.0, 2.0, -20.0, 0.0);
    w.set_view(&View { curve: false, occlusion: true, ..View::default() }); // 평평하게, 벽 뒤는 안 그림
}
```

#[command("경기장", "")]
fn arena(c: Command) {
    Server.create_map_world("arena", "res://packs/arena/arena.glb", Some("res://packs/arena/arena_col.glb"), (0.0, 2.0, -20.0, 0.0));
    c.player().move_world("arena");
}
```

## 주민

주민은 바닐라 모듈의 것입니다(`use greenhaven_vanilla::*;`: `VanillaWorld::spawn_npc` `npcs`, [`Npc`](sdk#npc)).

바닐라 주민 10명이 월드를 만들 때 들어가고, 그 목록이 서버의 주민 AI·대사·선물·의뢰와 게임의 주민 표가 됩니다. 주민은
서버가 걷게 하고 말도 서버가 합니다: 광장의 잡담, 둘이 만나 나누는 말과 소문, 플레이어가 하는 일을 보고 하는 말, 지나갈
때의 인사, 말을 걸었을 때의 대답이 모두 대사 표(`client.VillagerLines` 등, [등록](rules)으로 더함)에서 나옵니다.

```rust
use greenhaven_vanilla::*;

#[on(WorldCreate)]
fn neighbor(e: WorldCreate) {
    e.world().spawn_npc(r#"{"id": "haneul", "name": "하늘", "look": "soyul", "home": "library",
        "schedule": [[480, "square"], [660, "library"]]}"#);
}
```

- `look`: 모습·얼굴·목소리·일정을 빌려 올 기존 주민 id.
- 장소(`home`, `schedule`, `rain`): 마을의 장소 키 (`square` `library` `dock` `general` …, 각 주민의 집, 또는 구조물 `place`의 `key`).
- 이미 있는 주민은 [`Npc`](sdk#npc)의 `set` `go_to` `say`, 그리고 `Entity`로서 `location` `move_to`(걸어감) `remove`.

## 하루

각 월드는 자기 시계를 갖고(아무도 없으면 멈춤), 마을·주민·밤 몬스터는 그 시계를 따릅니다.

| 바꾸는 것 | |
|---|---|
| `World::set_minute(minute)` / `minute()` | 지금 시각 (예전 `Player::set_time`) |
| `World::set_day(n)` | 날짜 |
| `World::set_morning_time(minute)` `clear_morning_time()` | 밤이 끝나는 시각 |
| `World::set_night_time(minute)` `clear_night_time()` | 밤이 시작되는 시각 |
| `World::set_dawn_time(minute)` `clear_dawn_time()` | 몬스터가 강해지는 시각 (바닐라 모듈: `VanillaWorld`) |
| `World::end_day()` | 지금 하루를 끝냄 |
| [`DayEnd`](events#dayend) | 끝나려는 하루를 막기 |
| [`DayChange`](events#daychange) | 날짜가 넘어가지 않게 |

세 시각은 하늘과 몬스터에 함께 적용되고, 계절과 상관없이 하나의 값입니다. 월드에 저장되고 `clear_*`로 규칙 값으로 돌아갑니다. 밤이 하루 안에 있어도 됩니다(1:00~5:00). 새 날의 시작은 6:00으로 고정이고, 더 일찍 끝내려면 `Tick`에서 시각을 보고 `end_day()`를 부릅니다.

이 설정들만 월드마다이고, 규칙의 다른 값은 서버가 켜질 때([`Enable`](events#enable))만 바꿉니다(규칙은 서버 전체가 함께 씀).

### 서버 하나의 시계

`tick`에서 벽시계 `now()`로 서버 시각을 계산해 `World::set_minute`으로 맞추면 모든 월드가 한 시계를 씁니다. 아무도 없는
동안에도 벽시계는 흐르니 들어오면 그 시각부터입니다. 예: `plugins/server_clock`.

```rust
#[on(Tick)]
fn keep_to_the_server(e: Tick) {
    let per_day = setting_num("day_real_minutes", 14.0) * 60_000.0;
    let want = 360 + ((now() % per_day) / per_day * 1200.0) as i64;
    if (e.world().minute() - want).abs() > 2 { e.world().set_minute(want) }
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

월드를 더 두려면 플러그인이 만듭니다(Bukkit처럼): `Server.create_world("garden")`은 서버의 생성기(server.properties `level-type`, 기본 바닐라 땅과 마을)로 된 새 월드(`@garden`,
저만의 씨앗; `id`는 영문·숫자·`_ - .` 32자까지)를 만들어 서버가 돌리고 저장하며, 그 월드에서 `world.create`와 `chunk.generate`가
불립니다(`World::id()`가 "garden": 그 월드만의 땅이나 구조물을 거기서; 모두의 월드는 "world"). `Player::move_world("garden")`은
그 플레이어를 그 월드의 스폰으로 옮기고, `move_world_at("garden", "station")`은 게임 모듈이 아는 자리로(바닐라: `"station"` 그 월드의
열기구 정거장, `"desert"` 사막의 정거장; `""`이나 모르는 이름은 스폰) 옮깁니다(`""` 월드는 모두의 월드; 떠난 월드에서 `leave`, 간
월드에서 `join`; 가방과 게임 모듈의 몫(돈·스킬)은 함께). 한 서버가 함께 돌리는 월드는 16 + 접속 한도의 두 배(256까지)까지: 넘으면 새 월드는 만들어지지
않고(서버 로그에 남음) 그리로 옮기는 `move_world`도 그대로 머뭅니다. 예제 [`friend_lands`](samples)(친구 땅).

## 월드 파일

`<data>/worlds/<id>/world.json`은 월드 하나의 설정과 소품입니다. `world`는 모두가 들어오는 월드, 다른 id는 플러그인이 만들거나
플레이어를 옮기는 월드(`create_world` / `move_world`) 또는 시작 월드([`start-world`](server#serverproperties))입니다.

- 서버는 그 월드를 돌릴 때 파일을 읽어 설정을 정하고, 소품을 **어느 플러그인의 것도 아닌 엔티티**(`owner()`가 `"@world"`)로 직접 놓습니다.
- 어느 플러그인이든 여느 엔티티처럼 옮기거나 지울 수 있습니다([열린 엔티티](sdk#엔티티는-모두에게-열려-있음)).
- 소품은 월드와 함께 저장되고, 파일이 바뀌었을 때만 다시 놓입니다.
- GreenHaven Studio가 프로젝트의 월드마다 이 파일을 씁니다.

```json
{"spawn": [x, y, z, yaw], "pvp": false, "clock_rate": 1.0,
 "props": [{"model": "res://...", "x": 0, "y": 0, "z": 0, "yaw": 0, "scale": 1,
            "collision": "box", "solid": true, "hit": [[0, 0, 1, 1, 0, 2]]}]}
```

| 키 | |
|---|---|
| `spawn` | `[x, y, z, yaw]` 들어오는 곳 |
| `pvp` | PvP |
| `clock_rate` | 시계 빠르기 |
| `props[].model` | `res://` 경로 (게임의 것이나 리소스 팩의 것), 또는 팩의 모델 `pack:<팩>/<id>` ([팩의 모델](index#팩의-모델)) |
| `props[].x` `y` `z` `yaw` `scale` | 자리, 방향(라디안), 크기 |
| `props[].collision` | `"box"` \| `"mesh"` \| `"none"` |
| `props[].solid` | 단단한가 |
| `props[].hit` | 상자 칸 `[[x, z, w, d, y, h], ...]` (`ModelEntity::set_hitbox`와 같음, [히트박스](#히트박스와-충돌)); 없으면 모델에서 잼 |

## 월드 만들기

서버는 Minecraft처럼 **엔진**(블록, 엔티티, 플레이어, 월드, 이벤트)과 **바닐라 콘텐츠**(마을, 주민, 농사, 상점, 밤의 몬스터 …)로
나뉩니다. 월드는 처음 만들어질 때 한 번 **생성기**를 고릅니다:

| 생성기 | 땅 | 마을 |
|---|---|---|
| `vanilla` (기본) | 바닐라 땅 | 바닐라 마을 (옵션 `{"town": false}`면 없이: 마을 자리는 평평한 풀밭, 마을에 묶인 기능은 꺼짐) |
| `flat` | 어디나 높이 0의 풀 (그 밑 흙 셋, 그 밑 돌) | 없음 |
| `void` | 아무것도 없음: 플러그인이 `WorldCreate`·`ChunkGenerate`로 지음 | 없음 |
| `<플러그인>:<이름>` | 그 플러그인의 [생성기](#플러그인의-월드-생성기) (예: `islands:islands`) | 없음 |

- 모두의 월드: server.properties `level-type=vanilla|flat|void|<플러그인>:<이름>` (처음 만들 때만, [서버](server)).
- 플러그인의 월드: `Server.create_world_with("arena", "void", "")` (세 번째는 그 생성기의 옵션 JSON 객체, `""` 없음; 처음 만들 때만 셈).
  `create_world(id)`는 서버의 생성기(`level-type`)로. 바닐라 땅에 마을 없이: `create_world_with("wild", "vanilla", r#"{"town": false}"#)`.
- 마을이 없는 월드에는 구조물·성벽·방·주민·가축이 없고, 게임도 아무것도 짓지 않습니다(나침반, 우편함, 집터 고르기도 없음).
- **스폰** `World::set_spawn(x, y, z, yaw)`: 들어오는 곳 (칸, 발 높이: 높이 y 블록의 윗면은 y + 0.5; yaw 라디안, 0이 +z). 정하지 않으면 마을의 농가 문 앞,
  마을이 없으면 (0, 0)의 가장 높은 블록 위(거기 아무것도 없는 `void` 월드면 서버가 (0, 0, 0)에 돌 한 칸을 놓아 그 위). 침대·의료실·열기구 정거장이 없는 월드에서는 아침에도, 쓰러진 뒤에도, 내릴 때도 여기입니다.
- **바닐라 기능** `World::set_vanilla(feature, on)` (바닐라 모듈의 `VanillaWorld`; 월드에 저장; 모르는 이름이면 `false`, `is_vanilla`로 읽기): `villagers`(주민),
  `night`(땅 위 밤의 몬스터), `farming`(밭 갈기·심기·물 주기·수확·동물), `wild`(아침마다 나는 나무·바위·채집물), `tutorial`(첫날 할 일),
  `shops`(사고팔기, 출하, 목공소·대장간·마법사), `sleep`(침대), `mining`(광산), `dungeon`(사막의 던전), `balloon`(열기구), `quests`(퀘스트와
  주민의 의뢰), `mail`(편지), `love`(연애·결혼), `festivals`(축제), `furniture`(가구), 그리고 마을이 없어도 켜지는 `fishing`(낚시),
  `crafting`(제작), `energy`(끄면 도구가 기력을 쓰지 않음, 게임은 기력 바를 숨김), `fall`(끄면 쓰러져도 잃는 것 없이 스폰에서 일어남),
  `day_end`(끄면 시계로는 하루가 끝나지 않고 끝 시각에 하루의 시작으로 돌아감). 정하지 않은 것은 바닐라 마을이 있으면 켜짐, 없으면
  마을에 묶인 것은 꺼짐. 꺼진 기능의 행동은 서버가 거절합니다. 낮에도 플러그인의 몬스터(`spawn_mob`)는 남아 움직이고 칠 수 있습니다. 하루의 끝과 저장은
  규칙(`day_end`, `pass_out`), [`DayEnd`](events), `set_live_saving`이 정합니다.

```rust
use greenhaven_vanilla::*; // set_vanilla

#[on(WorldCreate)]
fn made(e: WorldCreate) {
    let w = e.world();
    let b = Block::named("arena_block").unwrap();
    w.fill((-4, 20, -4), (4, 20, 4), b); // 허공에 떠 있는 발판
    w.set_spawn(0.0, 20.5, 0.0, 0.0);
    w.set_vanilla("farming", false);     // (빈 월드는 이미 다 꺼짐: 평지·바닐라 월드에서도 미니게임이 되게)
}
```

예제 [`void_arena`](samples)(허공 경기장).

### 월드마다의 규칙·가방·시계, 월드의 수명 (미니게임 허브)

Multiverse처럼 월드마다 다르게 (예제 [`minigame_hub`](samples)):

- **규칙** `World::set_rule("max_health", "60")`: rules.json의 값 하나를 그 월드에서만 (그 키의 값을 통째로; 점으로 이은 키 `"starter.items"`,
  `"sell.carrot"`, `"checks.air"`; `"null"`이면 서버의 것으로, `clear_rules()` 전부). 그 월드의 행동·걸음·밤·하루는 그 규칙으로 판정되고,
  들어오는 게임은 그 규칙의 콘텐츠(레지스트리)를 받습니다. 같은 패치의 월드들은 규칙 하나를 함께 씁니다. 블록 종류(`blocks_add`)는 안 됨.
  규칙은 바뀔 때만 다시 만들어지며(약 0.1초) 보통 `WorldCreate`에서 한 번 정합니다.
- **시계** `World::set_clock_rate(f)`: 규칙의 f배 (0 멈춤: 시계로는 하루가 끝나지 않음), `clear_clock_rate()`.
- **가방 그룹** `World::set_inventory_group("arena")`: 다른 그룹의 월드에서 오면 자기 몫(가방·돈·기력·체력·스킬·호감도·장비)은 떠난
  그룹에 맡겨지고 이 그룹의 것을 받음 (지난번 그대로, 처음이면 이 월드 규칙의 `starter`로 새로). `""`은 모두의 월드의 그룹.
  `Player::reset()`: 지금 그룹의 몫을 새 손으로 (경기마다 새 장비).
- **동기화** `World::set_sync(&[(30.0, 0), (80.0, 50)], Some(0.0))`: 다른 사람의 위치를 거리별로 얼마나 자주 (m, ms; 6개까지, ms 0~1000),
  채팅이 닿는 거리 (0이면 월드 전체, `None` 48 m).
  `World::set_sync_with(tiers, chat, full, send)`: 더해서 `full` 각자 가장 가까운 몇 명에게 첫 구간을 줄지(1~64, 없으면 10: 그 너머는
  초당 15번보다 자주 안 보냄), `send` 이 월드의 게임이 가까운 사람과 상관없이 초당 몇 번 위치를 보낼지(5~30, 없으면 게임의 것: 48 m 안에
  누가 있으면 30, 아니면 5; 마을의 `"send"`로 실려 감). 경기(FPS): `set_sync_with(&[(400.0, 0)], Some(0.0), Some(16), Some(30.0))`.
- **수명** (그 월드를 만든 플러그인만, 모두의 월드는 안 됨): `Server::create_world_from(id, template)` 틀의 지금 모습(블록, 구조물,
  주민, 플러그인 데이터, 위의 설정들, 지금의 엔티티)을 복사; `Server::reset_world(id, to)` 만든 그대로 다시 (안의 사람은 `to`로, `""`이면
  모두의 월드로 갔다 다시 들어옴); `Server::remove_world(id, to)` 지움. 아무도 없는 플러그인 월드는 server.properties
  `world-unload-seconds`(기본 300, 0 안 내림) 뒤 저장하고 내렸다가, 누가 오면 다시 읽습니다. `Server::worlds()`, `Server::world_loaded(id)`.

```rust
#[on(WorldCreate)]
fn made(e: WorldCreate) {
    let w = e.world();
    if w.id() == "arena_tpl" {
        w.set_mode("none"); // 농장 기능 전부 끔, 시계 멈춤, 가방 그룹 "arena" (아래 「경기장 모드」)
        w.set_pvp(true);
        w.set_rule("starter", r#"{"gold": 0, "items": {"sword": 1, "salad": 3}}"#);
    }
}
// 경기 시작: Server.create_world_from("arena1", "arena_tpl"); p.move_world("arena1");  (Join에서 p.reset())
// 경기 끝: Server.reset_world("arena1", "world");  모두 허브로(허브의 가방 그대로), 경기장은 틀의 모습으로
```

### 경기장 모드: 농장이 아닌 게임을 한 번에

`World::set_mode("none")` 한 번이 (예제 [`arena_mode`](samples); `WorldCreate`, `Enable`, `PlayerJoin` 어디서든, 월드와 함께 저장):

- 바닐라 기능 20개 전부 끔 (`set_vanilla`: 주민, 밤, 농사, 상점, 잠, 튜토리얼 … **기력**, **쓰러짐의 비용**, **하루 끝**), 마을 있는 월드에서도.
- 시계 멈춤 (`set_clock_rate(0)`; 하늘이 돌게 하려면 뒤에 `set_clock_rate(1.0)`: 하루 끝이 꺼져 있어 시계로 끝나지 않음).
- 그때그때 저장 (`set_live_saving(true)`).
- HUD의 날짜·시간·날씨(`"time"`)와 퀘스트(`"quests"`)를 이 월드의 모두에게 숨김 (`hide_hud`).
- 가방 그룹 `"arena"`, 시작 키트는 빔 (돈 0, 물건 없음): 키트는 뒤에 `set_rule("starter.items", r#"{"sword": 1}"#)` 또는 `Player::set_inventory`.
- 행동 한도 초당 30, 한 번에 60 (`set_action_rate`).

`set_mode("vanilla")`은 모두 서버의 것으로 되돌립니다. 하나씩도:

- `World::set_action_rate(rate, burst)`: 이 월드의 행동 한도 (최대 60, 120; 서버는 10, 30), `clear_action_rate()`. 플러그인의 패킷(게임 쪽
  `send`, 버튼, 키)은 따로 초당 30이라 행동 한도를 쓰지 않습니다.
- `World::hide_hud(part, hidden)`: 게임 HUD의 부분([이름들](screen#게임-hud의-부분))을 이 월드의 모두에게 숨김 (들어오는 사람도).
- `World::set_view(&View { curve, fog, sight, occlusion })`: [이 월드를 그리는 법](#월드를-그리는-법).

```rust
#[on(WorldCreate)]
fn made(e: WorldCreate) {
    let w = e.world();
    w.set_mode("none");
    w.set_rule("starter.items", r#"{"sword": 1}"#);
}
```

저장되지 않은 하루가 버려져도 플러그인 모듈의 메모리(전역 변수, [`Global`](sdk#global))는 남습니다. 월드를 디스크에서 다시 읽을 때만 새로 만들어집니다.

### 월드를 그리는 법

`World::set_view(&View { curve, fog, sight, occlusion })` / `clear_view()` (월드와 함께 저장; 2026-11-11 전에는 인자 셋):

- `curve`: 세계가 지평선 아래로 휘는지 (농장의 모습). false면 평평 (FPS 맵: 안개까지 그대로 보임).
- `fog`: 안개가 다 가리는 거리 m, `sight`: 그 너머는 안 그리는 거리 m (16~2000, sight ≥ fog).
- `occlusion`: 벽에 가려진 것을 그리지 않음. 가리개는 플러그인 엔티티의 충돌 메시입니다: 방과 거리가 많은 맵은 이득, 위에서
  내려다보는 농장은 비용뿐이라 기본 꺼짐 ([맵 월드](#맵-월드)는 `set_view`로 켬).
- `View::default()`와 `clear_view()`는 server.properties의 `world-curve=true`, `fog-distance=112`, `view-distance=150`, occlusion 꺼짐.
  블록 땅은 플레이어 둘레 ~112 m만 지어지니, 블록 월드에서 안개를 그보다 멀리 두면 땅 끝이 보입니다.

```rust
w.set_view(&View { curve: false, fog: 300.0, sight: 400.0, ..View::default() });
```

## 영역 복사·붙여넣기 (스키매틱)

`World::copy(min, max, structures)` → `Option<Vec<u8>>`: 상자(두 모서리 포함, 26만 2144블록까지)의 블록, 블록 데이터, `structures`면
그 안에 선 구조물. `World::paste(at, &bytes, turns, structures)` → `bool`: 낮은 모서리를 `at`에, y축으로 `turns`번 4분의 1 회전(돌아가는
블록 종류와 구조물도), 공기도 붙여서. 바이트는 원하는 곳에 두세요(`Server::data_put`, 월드 데이터). 복사는 이벤트가 시작될 때의
블록을 읽으므로, 같은 이벤트에서 쌓은 것은 타이머로 다음 스텝에 복사합니다. 예제 `plugins/arena_stats`.

```rust
let arena = w.copy((0, 0, 0), (20, 6, 20), false).unwrap();   // 처음 모양
Server.data_put("arena", &arena);
// 판이 끝나면
w.paste((0, 0, 0), &Server.data_get("arena").unwrap(), 0, false);
```

## 저장

- **바닐라 규칙: 자고 일어난 아침에만 저장됩니다.** 그 전에 주인이 나가거나 서버가 꺼지면 그날 한 일(블록, 플러그인 값과
  데이터까지)은 사라집니다.
- 그 자리에서 남겨야 하면 `World::save_now()`: 월드(게임, 블록, 데이터)를 아침처럼 지금 저장 (날은 그대로 이어짐).
- 잠이 없는 서버(RPG 등)는 `World::set_live_saving(true)`: 1분마다와 플레이어가 나갈 때 블록까지 저장합니다.
- 연결이 끊긴 플레이어는 `resume-seconds`(기본 30초) 안에 돌아오면 그날 상태 그대로 이어집니다.
- 나가기 전 경고는 `World::set_quit_warning("...")` (`""`: 띄우지 않음; 실시간 저장이면 기본으로 안 띄움).
- 주민의 기억(본 일과 소문, 플레이어와 마지막으로 나눈 말과 받은 선물, 최근에 한 말)은 월드와 함께 저장됩니다. 주민이 서 있는
  곳과 하던 일은 저장하지 않고, 월드가 열릴 때 그 시각의 일정대로 다시 놓입니다.
- 엔티티는 저장되지 않습니다(`ModelEntity::set_persistent(true)`면 저장됨). [월드 파일](#월드-파일)의 소품은 월드와 함께 저장됩니다.
