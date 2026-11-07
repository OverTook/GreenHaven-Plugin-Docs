---
title: 채팅과 음성, 명령어
nav_order: 6.7
parent: 플러그인
---

# 채팅과 음성, 명령어 (예제 `plugins/party`)
{: .no_toc }

1. TOC
{:toc}


누가 누구의 말을 듣는지 플러그인이 정합니다. 숨기기 규칙은 그대로입니다: 이름으로 숨긴 사람(`hide_from`)에게는 채팅도 음성도
가지 않습니다. 보기 그룹(`Player::set_view_group`)이 다른 사람에게도 채팅·음성·팀 채팅이 가지 않습니다. 같은 채널·같은 음성 묶음 안에서는 전체 숨김(투명, 관전, 변장)이 서로를 막지 않습니다(관전자끼리 말하기).

```rust
#[on(Chat)]
fn party_chat(e: Chat) {
    if let Some(rest) = e.line().strip_prefix('@') {
        e.set_channel("party:kim");            // 그 채널에 든 사람들에게만 (쓴 사람도), 채널 이름과 함께
        e.replace(&escape_rich(rest));         // 플러그인의 줄은 BBCode로 그려짐: 친 그대로 보이게
    }
    // e.set_recipients(&["kim", "lee"]);      // 그 사람들에게만 (서버 어디에 있든)
}
p.join_channel("party:kim");                   // 서버에 있는 동안 (16개까지); leave_channel, channels()
Server.channel_members("party:kim");           // 접속한 사람만
p.chat_to(&["lee"], "귓속말");                  // p의 이름으로 그 사람들에게만 (p도 봄)
p.set_talk_group("red");                       // 같은 묶음끼리만 목소리가, 월드 어디서든; ""는 다시 거리대로
w.set_talk_range(0.0);                         // 묶음 없는 사람의 목소리가 닿는 거리 (0 월드 전체, 음수 서버 기본 48 m)
p.lang(); p.device(); p.ping_ms();             // "ko", "pc" / "phone" / "pad", 왕복 ms (되감기가 쓰는 값, 1초마다)
```

- 채팅의 서식: 플러그인이 쓴 줄(`Chat::replace`, `chat_to`, `message`, `broadcast`)은 게임이 `El::rich`와 같은 화이트리스트로
  그립니다(`[b] [i] [u] [s] [color=#7fd0ff] [size=16]`, `[[`는 `[` 그대로) — 그리고 `[cmd=/party accept kim]수락[/cmd]`: 누르면
  그 명령어를 친 것처럼. 플레이어가 친 말은 친 그대로이고, 플러그인의 줄에 넣을 때는 `escape_rich`.
- 명령어: `#[command("party", "파티", aliases = "파티 p", usage = "<invite|accept|leave> [이름]", args = "invite accept leave")]`.
  별칭으로 쳐도 핸들러는 이름으로 불림(`c.label()`이 친 이름). 인자: `c.arg(i)`, `c.arg_num(i)`, `c.arg_player(i)`, `c.rest(i)`,
  `c.arg_list()`("따옴표 안"은 한 낱말), `c.usage_error()`(「사용법: /p <invite|…>」). `/help`에 사용법과 별칭이 나옴.
- Tab 완성: 게임이 `{"t":"complete","text":"/party in"}`을 보내면 서버가 `{"t":"complete","text","l":[줄 전체]}`로 답합니다
  (1초에 10번까지): 명령어 이름과 별칭(쓸 권한이 있는 것), 첫 인자는 `args`의 낱말(`<player>`는 접속한 사람들), 그 밖은 그
  플러그인의 `CommandComplete`(`e.arg_list()`의 마지막이 아직 치는 중인 낱말; `e.suggest(&[..])`). 친 것으로 시작하는 것만 남깁니다.
- 게임: `{"t":"chat","name","text"}`에 `"channel"`(채널의 줄), `"rich"`(플러그인의 BBCode). join에 `"device"`.

