---
title: 여러 언어 (lang/)
nav_order: 6.8
parent: 플러그인
---

# 여러 언어 (`lang/`, 예제 `plugins/example`)
{: .no_toc }

1. TOC
{:toc}

플러그인이 쓰는 말을 언어마다 따로 둡니다. 서버는 문장 대신 **키와 값**을 보내고, 게임이 플레이어가 고른 언어로
문장을 만듭니다. 한 서버에 한국어로 하는 사람과 영어로 하는 사람이 같이 있어도 각자 자기 말로 봅니다.

## 카탈로그

플러그인 폴더의 `lang/<언어>.json`(`ko.json`, `en.json` ...). 접속할 때 플러그인의 zip(`assets/`, `client.wasm`과 함께)에
담겨 게임에 갑니다.

```
<data>/plugins/example/
  plugin.json
  server.wasm
  lang/ko.json
  lang/en.json
```

```json
{
  "tree.huge": {"one": "The tree grew huge!", "other": "The tree grew {n} times as big!"},
  "haste.on": "Your feet feel light!"
}
```

- 값은 문장 하나 전체입니다. 조각을 이어 붙이지 말고, 언어마다 어순대로 문장 전체를 씁니다.
- `{이름}`: 그 자리에 들어갈 값.
- 개수에 따라 모양이 바뀌면 `{"one": ..., "other": ...}`: 값 `n`으로 그 언어의 규칙(CLDR)대로 골라요. 영어는 1이면
  `one`, 한국어·일본어·중국어는 늘 `other`, 러시아어·폴란드어는 `one` / `few` / `many`, 프랑스어는 0과 1이 `one`.
- 숫자가 둘 이상인 문장은 단어마다 바로 앞 숫자에 맞춰요: `"{f} [friend|friends] · {r} [request|requests]"`
  (`[one|other]`, 네 가지면 `[one|few|many|other]`).
- 게임의 언어가 카탈로그에 없으면 `en.json`, 그것도 없으면 첫 파일, 키가 없으면 키 그대로 보입니다.

## `t!`로 쓰기

```rust
use greenhaven_plugin::*;

p.say(&t!("haste.on"));
p.say(&t!("tree.huge", n = 4));
p.refuse(&t!("too_far", who = name, n = cells));
e.replace(&t!("welcome", who = p.name()));
```

`t!(키, 이름 = 값, ...)`가 만드는 것은 그냥 `String`입니다. 말·거절·채팅·HUD의 글자·제목·말풍선 어디에나 그대로 넣을 수
있고, 다른 `t!`의 값으로 넣어도 됩니다(`t!("got", what = t!("prize.gold"))`). 값은 글자나 숫자입니다. 게임의
아이템 이름(예: `"당근"`)을 값으로 넣으면 게임이 그 이름도 플레이어의 언어로 바꾸고, `n`이 있으면 개수에 맞는 모양으로
씁니다(`Carrots`).

게임 쪽 코드(`client.wasm`, `greenhaven_client`)도 같은 `t!`를 씁니다: 같은 플러그인의 `lang/`에서 찾습니다.

## 안에서 일어나는 일

`t!`는 `U+E000 @ U+E001 키 U+E001 {값 JSON} U+E002` 모양의 글자를 만듭니다. 서버는 플러그인이 넘긴 글자 속 `@`를 그
플러그인의 이름으로 바꿔 보내고(`said_stamp`), 게임은 받은 메시지의 모든 글자에서 이 표시를 찾아 그 플러그인의
카탈로그로 바꿉니다(`Net.plugin_said`). 플레이어의 언어는 접속할 때 서버에 가고(게임에서 바꾸면 `{"t":"lang"}`로 다시)
`p.lang()`으로 읽을 수 있습니다. 언어를 바꾸면 이미 보인 채팅과 HUD도 새 언어로 다시 그려집니다.
