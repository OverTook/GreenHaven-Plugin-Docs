---
title: 서버 운영
nav_order: 8
---

# 서버 운영
{: .no_toc }

1. TOC
{:toc}

## server.properties

전용 서버는 데이터 폴더의 `server.properties`(처음 켤 때 기본값으로 만들어짐)를 읽습니다. Bukkit처럼 `키=값` 줄입니다.

```
name=봄바람 마을 서버
motd=봄 축제 진행 중! 매일 저녁 7시 낚시 대회
max-players=40
password=
address=0.0.0.0:7777
visits=true
online-mode=true
listed=true
tags=초보 환영,농사
region=한국
```

| 키 | |
|---|---|
| `name`, `motd` | 게임의 서버 목록에 보이는 이름과 소개 |
| `max-players` | 동시 접속 (0: 제한 없음) |
| `password` | 서버 전체의 비밀번호 |
| `address` | 명령줄에 주소가 없을 때 들을 곳 |
| `visits` | 플레이어 월드 사이의 열기구 방문 |
| `online-mode` | 접속자를 공식 중앙 서버로 확인 (기본 켬). 끄면 이름을 말하는 대로 믿음: 시험, 닫힌 LAN |
| `listed` | (online-mode일 때) 중앙 서버의 서버 목록에 1분마다 알려 멀티플레이 › 서버 찾기에 보임 |
| `tags` | 쉼표로: 초보 환영, 농사, 낚시, 축제, 느긋하게, 롤플레이 |
| `region` | 한국, 일본 … |
| `shared-world` | 모두의 월드 ([월드와 하루](world#모두의-월드)); 플러그인의 `Server::set_shared_world`가 우선 |
| `save-mode` | `sleep`(아침에만, 기본) / `live`(1분마다·나갈 때); 플러그인의 `World::set_live_saving`이 우선 |
| `resume-seconds` | 끊긴 플레이어를 그날 상태로 기다리는 초 (30) |
| `quit-warning` | 자기 전에 나갈 때의 경고; 플러그인의 `World::set_quit_warning`이 우선 |

접속할 때 서버는 받을 파일을 알립니다: `<data>/packs/*.zip`(리소스 팩: 골라 받을 수 있음)과 플러그인의 `assets/`(꼭 받아야
함). 게임은 받을지 묻고, 끊기면 받던 곳부터 이어 받습니다.

## 샌드박스

- wasmtime (Cranelift). NaN 정규화와 연료로 **결정적**입니다: 같은 입력이면 늘 같은 결과.
- 이 문서의 ["gh" 함수](abi) 말고는 아무것도 못 합니다: 파일·네트워크·시간·난수 원천 없음. 시각은 `now()`, 난수는 `roll(k)`.
- 이벤트 한 번에 연료 5 000 000 명령, 메모리 16 MB (낚시의 `reel`은 한 번에 200 000).
- 끝나지 않는 반복이나 오류(panic, trap)는 **그 플러그인의 몫만** 없던 일이 되고 게임은 계속됩니다.
- 코드는 서버에서만 돌고 게임에는 가지 않습니다. `assets/`도 그림·소리·모델 원본만 씁니다.
- 휴대폰(안드로이드) 게임의 자체 서버는 코드를 돌리지 않습니다: `rules.json`과 `assets/`만. 코드가 든 플러그인은
  plugin.json에 `"mobile": true`가 있어야 그렇게라도 쓰입니다.
- 이벤트 한 번에 1~2 µs (모듈은 월드마다 만들어 둔 채로 씀).

## 한계

- 게임은 아침(또는 `save_now`)에만 저장됩니다: 그 사이에 서버가 꺼지면 그날 일은 사라집니다 (`set_live_saving`이면 1분마다).
- 엔티티는 저장되지 않습니다. 오래 남길 것은 `World::set` / `Player::set`이나 데이터 저장에.
- 주민의 기억(본 일, 소문, 어제 받은 선물)은 서버가 켜져 있는 동안만 남습니다.
- 동물용 새 건물 종류는 아직 없습니다 (헛간·닭장).
- 광산 층은 바위만 코드로 바꿀 수 있습니다 (벽과 사다리는 `mine_layout`).
- rules.json의 값을 코드에서 바꾸는 일반 API는 없습니다. 월드마다 바꿀 수 있는 것은 날짜와 하루의 시각뿐입니다.
