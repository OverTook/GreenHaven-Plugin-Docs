---
title: 플러그인끼리
nav_order: 6.6
parent: 플러그인
---

# 플러그인끼리 (다른 플러그인의 API 쓰기)
{: .no_toc }

1. TOC
{:toc}

Bukkit에서 경제·권한 플러그인의 API를 다른 플러그인이 가져다 쓰듯, GreenHaven 플러그인도 다른 플러그인의 함수를 부를 수
있습니다. 예제: `plugins/economy`(코인을 맡는 플러그인과 그 API 크레이트 `economy/api`), `plugins/bounty`(그 API를 쓰는 플러그인).

## 한눈에

| 하는 사람 | 하는 일 |
|---|---|
| API를 주는 플러그인 | 부를 수 있게 할 함수에 `#[export]`. API 크레이트를 같이 배포(`api!` 한 덩어리) |
| API를 쓰는 플러그인 | Cargo.toml에 그 API 크레이트, plugin.json에 `depend`(또는 `soft_depend`). 그 함수를 그냥 부름 |
| 서버 | `depend` 순서로 로드, 호출을 상대 플러그인의 샌드박스로 넘기고 결과를 돌려줌 |

## API를 주는 쪽

```rust
use greenhaven_plugin::*;

/// The player's coins.
#[export]
fn balance(player: String) -> i64 {
    World.get(&format!("c:{player}")) as i64
}

#[export]
fn deposit(player: String, amount: i64) -> i64 { ... }
```

- `#[export]` 함수는 평소처럼 자기 안에서도 부를 수 있는 보통 함수입니다. 다른 이름으로 내보내려면 `#[export("이름")]`.
- 인자와 결과로 쓸 수 있는 것: `i32 i64 u32 u64 f32 f64 bool String`, `Vec<T>`, `Option<T>`, 튜플(6개까지).
  넘길 때는 `&str`, `&[T]`도 됩니다. 값은 복사되어 건너가며 메모리를 나누지 않습니다.
- 서비스 이름을 plugin.json `"provides": ["economy"]`에 적으면 다른 플러그인이 이 이름으로 찾습니다(Vault처럼: 같은 이름을
  주는 다른 플러그인으로 바꿔 끼워도 쓰는 쪽 코드는 그대로). 둘 이상이 같은 서비스를 주면 먼저 로드된 쪽이 받습니다.
- 누가 불렀는지는 `caller()`(플러그인 이름, 이벤트로 불렸으면 `""`). 아무나 돈을 빼 가지 못하게 할 때 씁니다.

### API 크레이트

쓰는 사람의 자동완성과 타입 검사는 이 크레이트에서 나옵니다. 몸통은 `api!` 하나입니다.

```toml
# economy/api/Cargo.toml
[package]
name = "economy-api"
version = "0.1.0"
edition = "2021"

[dependencies]
greenhaven-plugin = { path = "../../../sdk/plugin" }
```

```rust
// economy/api/src/lib.rs
greenhaven_plugin::api! { "economy";
    /// The player's coins.
    fn balance(player: &str) -> i64;
    /// `amount` more coins: the player's coins after.
    fn deposit(player: &str, amount: i64) -> i64;
    fn withdraw(player: &str, amount: i64) -> bool;
}
```

`api!`의 첫 줄은 플러그인 이름이나 서비스 이름입니다. 함수마다 `Result<결과, CallError>`를 돌려주는 함수가 생기고,
`available()`은 그 플러그인이 지금 있는지 알려 줍니다. 함수 이름은 `#[export]`의 이름과 같아야 합니다.

## API를 쓰는 쪽

```toml
[dependencies]
greenhaven-plugin = { path = "../../sdk/plugin" }
economy-api = { path = "../economy/api" }
```

```json
{ "name": "bounty", "depend": ["economy"] }
```

```rust
#[on(Harvest)]
fn reward(e: Harvest) {
    let p = e.player();
    match economy_api::deposit(&p.name(), 1) {
        Ok(n) => p.say(&format!("코인 {n}개")),
        Err(why) => p.say(&format!("보상 없음: {why}")),
    }
}
```

API 크레이트 없이 직접 부를 수도 있습니다: `find("economy", "deposit")`가 `Option<Func>`을 주고,
`f.call::<_, i64>((name, 10))`로 부릅니다. 이름으로 찾는 것은 처음 한 번이고(`api!`가 기억해 둠) 그 뒤로는 번호로 부릅니다.

## depend, soft_depend

| plugin.json | |
|---|---|
| `"depend": ["economy"]` | 꼭 있어야 함. 없으면 이 플러그인은 켜지지 않고 서버 로그에 `bounty: needs economy (depend)` |
| `"soft_depend": ["perms"]` | 있으면 먼저 로드. 없어도 켜지고, 부르면 `CallError::Missing` |
| `"provides": ["economy"]` | 이 플러그인이 맡는 서비스 이름. `depend`에 서비스 이름을 적어도 됨 |

- 서버는 이것으로 로드 순서를 정합니다: 필요한 플러그인의 `Enable`이 먼저 끝납니다. 이벤트의 우선순위가 같으면 순서도 이것을 따릅니다.
- 서로가 서로를 `depend`하면(고리) 둘 다 켜지지 않습니다. `soft_depend`끼리의 고리는 적힌 순서대로 켜집니다.
- 필요한 플러그인이 꺼져 있으면(서버 관리 › 플러그인) 그것을 필요로 하는 플러그인도 켜지지 않습니다.

## 호출이 어떻게 도는지

- 불린 플러그인은 **자기 샌드박스, 자기 값**으로 돕니다. `World::set`, `Player::set`, 데이터는 그 플러그인 이름 아래에 남습니다:
  economy의 잔고는 economy만 직접 바꿀 수 있고, 다른 플러그인은 economy의 함수를 거쳐야 합니다.
- 불린 쪽은 부른 쪽과 **같은 이벤트 안에서** 돕니다: 같은 플레이어(`Player`), 같은 월드. 그 안에서 한 일(아이템 주기, 말하기,
  `cancel`)은 그 이벤트에 한 것과 같습니다.
- 비용: 한 번에 약 1~2 µs(측정 1.3 µs). 매 틱 수백 명에게 여러 번 부를 일이면 여럿을 한 번에 받는 함수를 내보내세요.
- CPU 예산: 불린 쪽이 쓴 시간은 **불린 쪽의 몫**에서 나갑니다(부른 쪽에 이중으로 세지 않음). 불린 쪽이 예산을 다 썼으면
  `CallError::Busy`. 한 호출에도 연료 5 000 000과 약 50 ms의 상한이 따로 있고, 부른 쪽의 시간 상한에는 기다린 시간이 들어갑니다.
- 불린 쪽이 오류(panic, trap, 연료·시간 초과)로 끝나면 `CallError::Failed`이고, 그 호출에서 한 일은 없던 일이 됩니다. 부른 쪽은 계속 돕니다.

| `CallError` | |
|---|---|
| `Missing` | 그런 플러그인·서비스·함수가 없음, 꺼짐, 또는 `Enable` 중(규칙 등록 때는 부를 수 없음) |
| `Busy` | 불린 쪽이 CPU 예산을 다 씀 |
| `Failed` | 불린 쪽이 오류로 끝남, 또는 인자를 읽지 못함(타입이 안 맞음) |
| `Loop` | 이미 이 호출 사슬에 있는 플러그인을 다시 부름(A → B → A), 자기 자신, 또는 사슬이 4개를 넘음 |

## 플러그인의 이벤트 (`Server::fire`, `#[on_custom]`)

함수를 부르는 대신 이벤트를 내고 듣는 쪽이 알아서 받게 할 수도 있습니다 (Bukkit의 사용자 `Event`와 `callEvent`).
내는 쪽은 듣는 쪽을 몰라도 됩니다.

```rust
// 미니게임 허브: 판이 끝나면
let cancelled = Server.fire("hub.game_end", "{\"winner\":\"민수\"}");

// 업적 플러그인 (depend가 없어도 됨)
#[on_custom("hub.game_end", priority = 5)]
fn ended(e: Custom) {
    let data = e.data(); // 낸 쪽이 준 글. e.from(): 낸 플러그인, e.player(): 낸 이벤트의 플레이어
    if data.is_empty() { e.cancel(""); } // fire()가 true를 돌려받음
}
```

- 듣는 쪽마다 호출처럼 자기 샌드박스에서, 낸 쪽의 이벤트 안에서 우선순위 순으로 돕니다. 한 일은 그 이벤트의 것, CPU는 각자의 몫.
- 낸 플러그인 자신, 호출 사슬에 이미 있는 플러그인은 불리지 않습니다. 깊이는 호출과 같이 4개까지(넘으면 아무도 못 듣고 `false`).
  누가 취소하면 거기서 멈춥니다. `Enable` 중에는 낼 수 없습니다.

## 원본 ABI

SDK 없이 쓰려면 [`"gh"` 함수](abi#플러그인끼리)의 `call_*`와, 커스텀 섹션 `gh`의 `export\t<이름>\t<내보내기>\n` 줄을 씁니다.
