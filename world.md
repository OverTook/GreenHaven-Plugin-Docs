---
title: 월드와 하루
nav_order: 6
---

# 월드와 하루
{: .no_toc }

1. TOC
{:toc}

월드는 **처음 만들 때 한 번 생성되고, 그 뒤로는 저장된 것**입니다. 바닐라 생성기는 서버 코드이고,
플러그인은 만들어질 때([`WorldCreate`](events#worldcreate), [`ChunkGenerate`](events#chunkgenerate))와 그 뒤 어느 이벤트에서나
블록·구조물·주민을 바꿀 수 있습니다. 바뀐 것은 그 월드의 모두에게 바로 갑니다.

## 블록

- 청크는 32 × 32칸, 높이 64칸 (y −8 ~ 55). 블록 하나는 y−0.5 ~ y+0.5를 채웁니다: 마을 땅은 y 0의 블록, 윗면 0.5.
- 청크는 누가 처음 가까이 갈 때 만들어지고(바닐라 땅, 그다음 `chunk.generate`), `<data>/chunks/<월드>/<x>_<z>.bin`에
  저장되어 그 뒤로는 저장된 그대로입니다.
- 블록: `air` `grass` `sand` `snow` `stone` `dirt` `road` `bed`(물 밑 모래) `water` ([`Block`](sdk#block)).
- 서버의 이동 판정도 블록을 읽습니다: 블록을 쌓으면 그 위를 걸을 수 있고, 파내면 떨어집니다.

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
때의 인사, 말을 걸었을 때의 대답이 모두 대사 표(`client.VillagerLines` 등, [rules.json](rules)으로 더함)에서 나옵니다.

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
| `World::set_day_start(minute)` | 아침 시각 |
| `World::set_day_end(minute)` | 하루의 끝 시각 |
| `World::end_day()` | 지금 하루를 끝냄 |
| [`DayEnd`](events#dayend) | 끝나려는 하루를 막기 |
| [`DayChange`](events#daychange) | 날짜가 넘어가지 않게 |

이 설정들만 월드마다이고, rules.json의 다른 값을 코드에서 바꾸는 일반 API는 없습니다(규칙은 서버 전체가 함께 씀).

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

바닐라 규칙은 **모두가 월드 하나**입니다(`shared-world=true`, 기본). 그 월드는 **서버의 월드**(`@world`, 플레이어 이름으로는
못 씀)이고, 서버가 아무도 없어도 그 월드를 돌립니다(주민, `tick`, 밤, 시계). 어느 서버든 코드는 같습니다.

플러그인은 그 월드를 **서버를 연 호스트의 농장**으로 바꿀 수 있습니다: rules.json에 `{"world_owner": "host"}`. 게임 안의 서버(혼자
하기, 서버 개설로 연 LAN)에는 이 플러그인(`host_world`, 기본 제공)이 들어 있고 뺄 수 없습니다. 그래서 혼자 하기와 LAN에서는 호스트의
농장이 모두의 월드입니다.

들어오는 사람은 그 월드의 농장 일꾼입니다: 땅·블록·작물·마을·주민·몬스터는 함께, **돈**·가방·기력·스킬·호감도는 각자. 돈은 어느
서버에서나 각자의 것이고(바닐라), 출하 상자에 넣은 것은 넣은 사람에게 그 사람의 아침에 정산됩니다. 모두가 잠들거나 하루의 끝(기본
다음날 6:00)이면 그 월드의 하루가 끝나고 각자의 아침이 옵니다. 열기구 방문은 꺼집니다.

플레이어마다 자기 월드(자기 농장, 자기 시계, 열기구로 오감)로 하려면 server.properties의 `shared-world=false`입니다. 직접 연 서버는
파일을 고쳐 다시 켜고, GreenHaven+ 24시간 서버는 그 주인이 게임의 **GreenHaven+ › 구독 관리 › 서버 관리 › 일반**에서 끄고 다시 켜면
됩니다. 또는 플러그인이 `ServerTick`이나 `PlayerLogin`에서 `Server.set_shared_world(false)`를 부릅니다(플러그인 것이
server.properties보다 우선). 바뀐 뒤에 들어오는 사람부터 적용됩니다.

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
