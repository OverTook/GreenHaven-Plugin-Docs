---
title: 화면
nav_order: 6.2
parent: 플러그인
redirect_from:
  - /screen
  - /screen.html
---

# 화면 — HUD, 미니맵, 키, 인벤토리 창
{: .no_toc }

1. TOC
{:toc}

Bukkit의 커스텀 GUI·스코어보드·보스 바·지도처럼, 플러그인이 플레이어의 화면에 자기 것을 그립니다. 게임은 플러그인의 코드를
돌리지 않습니다: 서버가 보낸 **데이터**(요소, 채널의 값)를 그리고, 누르면 서버에 패킷을 보냅니다. 서버 쪽은
`src/plugin_api/ui.rs`, 게임 쪽은 `PluginHud`. 예: `plugins/screen`.

```rust
#[on(Join)]
fn came(e: Join) {
    let hud = e.player().hud();
    hud.add("mana", &El::panel("wood").anchor(Anchor::BottomRight).pos(-130.0, -120.0).size(220.0, 64.0)
        .child(El::bar(50.0, 100.0).pos(10.0, 10.0).size(130.0, 20.0).color("4f7bff").label("마나").bind("mana"))
        .child(El::button("화염", "cast").anchor(Anchor::TopRight).pos(-8.0, 8.0).size(64.0, 44.0)));
    hud.key("H", "clock");          // H를 누르면 채널 "clock"의 패킷
    hud.send_text("mana", "50/100"); // 바가 이 값을 보여 줌
}

#[on(Packet)]
fn packet(e: Packet) {
    match e.channel().as_str() {
        "cast" => { /* 화염 버튼 */ }
        "clock" => e.player().hud().hide("clock"),
        _ => {}
    }
}
```

## Hud

`Player::hud()`는 그 사람의 화면, `World::hud()`는 월드 모두의 화면입니다(같은 요소를 모두에게, 채널의 값도 모두에게).

| 메서드 | |
|---|---|
| `add(id, &El)` | 이 플러그인의 요소 (`id`는 플러그인마다 따로; 같은 id가 있으면 바꿈) |
| `set(id, &El)` | 준 필드만 바꿈 (자식을 주면 자식은 통째로) |
| `remove(id)` | |
| `clear()` | 이 플러그인의 요소와 키를 모두 없애고, 숨긴 게임 HUD를 다시 보임 |
| `hide(part)` / `show(part)` | 게임 자신의 HUD 부분 숨기기 / 다시 보이기 (아래) |
| `key(key, on)` | 키(`"M"` `"F5"` `"Tab"`)를 누르면 채널 `on`의 패킷 (패널이 열려 있지 않을 때; `""` 풀기) |
| `replace(window)` / `restore(window)` | 게임의 창을 열면 이 플러그인에 `"window"` 패킷이 대신 감 / 게임의 창으로 되돌림 (아래 「게임의 창 바꾸기·꾸미기」) |
| `send(chan, &[u8])` `send_text(chan, text)` | 이 플러그인의 채널 `chan`에 값 (256 KB까지). 게임은 마지막 값을 갖고 있고, 그 채널에 묶인 요소가 보여 줌 |
| `send_png(chan, w, h, &rgba)` → `i32` | RGBA8 픽셀(`w` × `h`, 512 × 512까지)을 PNG로 만들어 채널에: 묶인 이미지가 보여 줌. PNG의 바이트 수, 픽셀이 `w × h × 4`가 아니면 0 |

플러그인 하나의 요소는 자식까지 세어 200개까지입니다. 서버를 떠나면 그 서버의 플러그인이 띄운 것은 모두 사라집니다.

### 게임 HUD의 부분

`hide` / `show`의 이름: `clock`(날짜, 시각, 날씨, 골드) `status`(그 아래의 알약과 버튼) `nearby`(가까운 사람) `chat` `hotbar`
`bars`(체력과 기력) `quests` `prompt`(E가 하는 일) `toasts` `plugins`(plugin.json의 버튼과 바) `menu`(휴대폰의 메뉴 버튼).
여러 플러그인이 숨기면 모두 `show`해야 다시 보입니다.

## 요소 (`El`)

| 만들기 | |
|---|---|
| `El::panel(style)` | 다른 요소를 담는 상자: `"wood"`(HUD의 나무 틀) `"parch"`(양피지) `"dark"`(어두운 알약) `"none"` |
| `El::text(t)` | 글 (묶으면 채널의 글) |
| `El::image(src)` | `res://` 그림 (게임의 것, 팩·플러그인 `assets/`의 것). `""`에 `bind`: 채널의 PNG |
| `El::bar(value, max)` | 바 (묶으면 채널의 `"30"` 또는 `"30/100"`) |
| `El::button(label, on)` | 누르면 채널 `on`의 패킷 (데이터 `""`) |
| `El::input(placeholder, on)` | 한 줄 입력: Enter면 채널 `on`의 패킷 (데이터: 쓴 글) |

| 필드 | |
|---|---|
| `anchor(Anchor::…)` | 화면의 어디: `TopLeft` `Top` `TopRight` `Left` `Center` `Right` `BottomLeft` `Bottom` `BottomRight` (자식은 부모 안에서) |
| `pos(x, y)` `size(w, h)` | 앵커에서 안쪽으로, HUD의 디자인 픽셀(PC 1280 × 720 기준으로 늘림) |
| `color(hex)` | 바의 채움, 글의 색, 패널의 바탕 |
| `font_size(n)` `label(t)` `set_text(t)` `value(v, max)` `visible(on)` | |
| `bind(chan)` | 이 플러그인의 채널 값을 보여 줌 |
| `follow(x0, z0, per_cell)` | 이미지를 월드 지도의 창으로: 픽셀 (0, 0)이 칸 (x0, z0), 한 칸에 `per_cell` 픽셀. 게임이 매 프레임 플레이어 자리를 가운데에 둠 (걸을 때마다 다시 보낼 필요 없음) |
| `zoom(z)` | 따라가는 이미지를 몇 배로 |
| `rotate(on)` | 카메라를 따라 돌림 (위가 카메라가 보는 쪽) |
| `round(on)` | 둥글게 자름 |
| `marker(on)` | 가운데에 플레이어 표시 (바라보는 쪽으로 도는 화살표) |
| `child(El)` | 자식 |
| `raw(k, json)` | 그 밖의 필드를 JSON 그대로 |

### 미니맵

`World::columns_raw(x0, z0, w, d)`는 위에서 본 땅을 기둥마다 두 바이트(가장 높은 단단한 블록의 번호(위에 물이면 물),
높이 − `Block::LOWEST`)로 줍니다(256 × 256까지). 픽셀은 **블록 번호로 표를 찾아** 만드세요: 이벤트 한 번의 연료(5 000 000)로
128 × 128 지도가 넉넉합니다(칸마다 함수를 부르면 모자람). `columns()`는 같은 것을 `(Block, 높이)`로.

```rust
const MAP: i64 = 128;

fn draw_map(w: &World, p: &Player) {
    let (x, z) = p.position();
    let (x0, z0) = (x.round() as i64 - MAP / 2, z.round() as i64 - MAP / 2);
    let mut colour = [[60u8, 60, 60]; 16];
    for (b, c) in [(Block::WATER, [64, 132, 196]), (Block::SAND, [222, 205, 150]), (Block::GRASS, [104, 168, 76])] {
        colour[b.0 as usize] = c;
    }
    let raw = w.columns_raw(x0, z0, MAP, MAP);
    let mut px = vec![255u8; raw.len() * 2];
    for (i, c) in raw.chunks_exact(2).enumerate() {
        px[i * 4..i * 4 + 3].copy_from_slice(&colour[(c[0] & 15) as usize]);
    }
    p.hud().set("map", &El::default().follow(x0 as f64, z0 as f64, 1.0));
    p.hud().send_png("map", MAP as i32, MAP as i32, &px);
}

// Join에서: 둥글고 카메라를 따라 도는 지도
// hud.add("map", &El::image("").anchor(Anchor::TopLeft).pos(16.0, 16.0).size(176.0, 176.0).bind("map")
//     .follow(0.0, 0.0, 1.0).zoom(2.0).round(true).rotate(true).marker(true));
```

플레이어가 지도 가운데에서 멀리 걸어갔을 때만(`Tick`에서) 다시 그리면 됩니다.

## 패킷 (`Packet`)

버튼·입력 칸의 `on`, `key`로 묶은 키는 그 플러그인에게만 [`Packet`](events#packet) 이벤트로 옵니다: `channel()`, `data()`(4 KB까지),
`player()`. 플레이어의 행동처럼 판정되므로 여기서 `give` `take` `add_gold` …가 됩니다.

## 인벤토리 창

플러그인의 칸 창(Bukkit의 커스텀 인벤토리). 칸에 무엇이 있는지는 플러그인이 정하고, 누르면 [`InventoryClick`](events#inventoryclick)이
옵니다. **아무것도 저절로 옮겨지지 않습니다.**

```rust
fn shop() -> Inventory {
    Inventory::new("shop", "마나 상점", 1, 5)          // id, 제목, 줄, 칸 (각 1~12)
        .slot(0, "wood", 5, "나무 다섯", "마나 30")     // 칸, 아이템(아이콘), 개수, 이름, 설명 ("": 아이템의 것)
        .with_bag()                                    // 옆에 그 사람의 가방
}

#[on(InventoryClick)]
fn click(e: InventoryClick) {
    let p = e.player();
    match e.side().as_str() {
        "top" if e.slot() == 0 => p.give("wood", 5),
        "bag" if !e.bag_item().is_empty() => p.take(&e.bag_item(), 1),
        _ => return,
    }
    p.open_inventory(&shop()); // 가방이 바뀐 대로 다시 보임
}
```

`Player::open_inventory(&inv)`(이미 열려 있으면 지금 칸으로), `Player::close_inventory(id)`. 서버는 열린 창을 기억해 그 창의 칸만
받습니다.

## 게임의 창 바꾸기·꾸미기

**바꾸기** — `Hud::replace(window)`: 플레이어가 그 창을 열면 게임은 열지 않고 이 플러그인에 채널 `"window"`의 패킷을 보냅니다.
플러그인은 자기 것(인벤토리 창, HUD 요소, `gui`)을 보여 주면 됩니다. 아무것도 안 하면 그 창은 막힌 셈입니다.
`restore(window)`로 게임의 창이 돌아옵니다.

| 창 | 패킷 데이터 (JSON) |
|---|---|
| `bag` | 가방의 모든 탭: `{"window": "bag", "tab": "bag"}` (`bag` `skills` `relations` `map` `craft` `quests`) |
| `shop` | 가게: `"shop"` (`general` `clinic` `furniture` `ranch` …), `"selling"` |
| `smith` / `enchant` | 대장간 / 마법사의 마법 부여대 |
| `chest` | 상자: `"x"` `"z"` |
| `build` | 서연의 건축 |
| `letter` | 우편함 편지: `"from"` `"text"` `"items"` |
| `bundles` / `library` / `festival` | 꾸러미 / 도서관 / 축제 (`"festival"`) |
| `dialogue` | 주민과의 대화: `"who"` `"text"` `"choices"` (선택지 글). 플러그인이 `Hud::choose(n)`으로 고름 |
| `settings` / `friends` | 설정(`"tab"`) / 친구 |
| `balloon` / `visit_book` | 열기구 / 방문 노트 |
| `sleep` | 잠자기 물음 (`Hud::open("sleep", "{}")`이면 눕기) |
| `summary` | 아침 결산: `"lines"` `"total"` |
| `mirror` | 거울(모습 바꾸기) |
| `catch` | 잡은 물고기 카드: `"id"` `"q"` … |

`Hud::open(window, data)`: 바꾼 창이라도 게임의 것을 지금 엶 (플러그인 자기 화면 다음에, 예: 확인을 받은 뒤 `sleep`).

```rust
#[on(Join)]
fn came(e: Join) {
    e.player().hud().replace("bag");
}

#[on(Packet)]
fn packet(e: Packet) {
    if e.channel() == "window" && e.data().contains("\"bag\"") {
        e.player().open_inventory(&Inventory::new("bag", "보따리", 1, 3).with_bag());
    }
}
```

판정은 그대로 서버의 행동입니다: 가방 창을 바꿔도 아이템은 서버의 것이고, 플러그인이 주고 가져갑니다.

**꾸미기** — `Registry::ui_theme(json)`([`Enable`](events#enable)에서): 게임의 모든 창과 HUD가 그 모습으로 그려집니다.
서버를 떠나면 게임의 모습으로 돌아옵니다.

```rust
#[on(Enable)]
fn enable(_e: Enable) {
    Registry::ui_theme(r#"{"colors": {"ink": "1d2433", "parch": "e2e9f4", "wood": "34446c"},
        "frame": {"texture": "res://plugins/screen/frame.png", "margin": 12, "pad": 4},
        "parchment": {"texture": "res://plugins/screen/parchment.png", "margin": 12}}"#);
}
```

| 키 | |
|---|---|
| `colors` | 색 `"rrggbb"`: `ink`(글자) `sub`(작은 글자) `brown` `wood` `wood_light`(틀) `parch` `parch_shade`(종이) `cream` `cream_shade`(버튼) `line` `green` `green_dark` `red` `gold` `hp` `en` `shade` `veil` |
| `frame` | 나무 틀 대신의 그림 |
| `parchment` | 양피지 대신 |
| `slot` / `slot_selected` | 아이템 칸 / 고른 칸 (없으면 `slot`을 밝게) |
| `button` / `button_go` / `button_red` | 보통 / 확인 / 위험 버튼 (올리면 밝게, 누르면 어둡게) |

그림은 `{"texture": 플러그인 assets의 PNG, "margin": 나인 슬라이스 가장자리 픽셀 (또는 [왼, 위, 오른, 아래]), "pad": 안쪽 여백}`:
가장자리는 그대로, 가운데는 늘어납니다. 예: `plugins/screen`의 남색 테마(`make_assets.py`).

## SDK 없이

"gh" 함수 `hud(json)` `hud_all(json)`의 JSON:

```json
{"op": "add", "id": "mana", "el": {"type": "bar", "anchor": "bottom_right", "pos": [-130, -120], "size": [130, 20], "bind": "mana"}}
{"op": "set", "id": "mana", "el": {"visible": false}}
{"op": "remove", "id": "mana"}
{"op": "clear"}
{"op": "hide", "part": "clock"}
{"op": "show", "part": "clock"}
{"op": "key", "key": "M", "on": "map"}
```

요소의 키: `type`(`panel` `text` `image` `bar` `button` `input`) `anchor` `pos` `size` `color` `style` `text` `label` `placeholder`
`value` `max` `src` `bind` `on` `follow` `zoom` `rotate` `round` `marker` `font_size` `visible` `children`. 인벤토리는
`inv_open({"id", "title", "rows", "cols", "slots": [{"item", "n", "name", "lore"} 또는 null, …], "bag": true})`, 닫기
`{"id", "close": true}`. 함수의 모양은 ["gh" 함수](abi#등록과-화면).
