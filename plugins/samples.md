---
title: 샘플 플러그인
nav_order: 9
parent: 플러그인
redirect_from:
  - /samples
  - /samples.html
---

# 샘플 플러그인

GreenHaven-Server의 `plugins/` 아래에 있습니다. `wild_fish` 말고는 모두 Rust SDK로 쓰여 있고, 게임에도 zip으로 들어 있어
월드 선택 › 편집 › 플러그인에서 켤 수 있습니다.

| 샘플 | 하는 일 | 보여 주는 것 |
|---|---|---|
| `example` | 마나 바, 화염구 버튼(날아가는 엔티티), 물 주면 섬유, 나무가 한 번에 5분의 1씩 자람, `/신속` | `ui` 버튼·바, `Button`, `Tick`, 엔티티, `set_walk_speed`, `assets/` |
| `big_backpack` 큰 가방과 긴 하루 | 가방 48칸, 기력 최대 +100, 하루 1.5배, 새 농장 1000골드, "가방" 글자 바꾸기 | `rules.json`만 (코드 없음) |
| `harvest_festival` 풍년 축제 | 비 오는 밤엔 작물이 이틀치 자람, 계절의 7·14·21·28일은 수확 두 배·파는 값 1.25배, 그날 아침 알림, `/축제` | `Grow` `Harvest` `Sell` `Morning` `Command` |
| `golden_crops` 황금 작물 | 새 작물 황금 당근(잡화점 씨앗, 아이콘, 금빛 당근 모델), 먹으면 기력, 새 퀘스트, 거두면 반짝임, `/황금씨앗` | `rules.json` + `assets/` + 코드 |
| `new_start` 새 출발 | 짧은 오프닝, 첫날 할 일 넷과 보상 1000골드, 마법 스킬 없음, 3레벨마다 전직(만렙 15), 채집 경험치 두 배, 집 안·광산의 음악, `/노래 곡` | `client.Intro.SCENES` `progress.tutorial_tasks` `progress.skills` `client.Music.TRACKS`, `play_music` |
| `new_creatures` 새 생물 | 밤의 얼음 버섯(돌을 떨굼), 둘레를 돌다 덤비는 도깨비불(광산 2층부터도), 헛간의 염소(이틀에 한 번 염소 젖) | `monsters_add` `animals_add`, `MobStep`, `Mob::set` `attack` |
| `new_neighbor` 새 이웃 하늘 | 새 주민 하늘(소율의 모습, 하루 일정, 대사), 말을 걸면 선택지 창, 이야기, `/하늘`로 부르면 걸어옴 | `WorldCreate`의 `spawn_npc`, `Words`, `Gui`, `Npc::say` `go_to`, 대사 패치 |
| `flat_world` 탁 트인 평지 | 성벽·성문·바위 둑·암초 없는 마을, 마을 밖은 나무 없는 평평한 풀밭 (새 월드에만) | `WorldCreate`의 `remove_plot`, `ChunkGenerate`의 `fill` `clear_props` |
| `deep_mines` 거친 땅과 깊은 광산 | 성벽 밖 땅이 더 높고 험해짐(산, 눈, 큰 바위), 광산 층이 넓어지고 금이 일찍, 층마다 도착한 곳 근처에 금광석 | `terrain` `mine_layout`, `MineFloor::set_rock` |
| `server_password` 서버 비밀번호 | 처음 들어올 때 비밀번호를 정하고, 그 뒤로는 들어올 때마다 물어봄 (세 번 틀리면 돌려보냄) | `PlayerLogin`의 입력 창, `Gui::secret`, `Server` 값 |
| `server_clock` 서버 공통 시계 | 모든 월드의 시각을 서버 시계 하나로 (하루 길이는 설정), `/시계` | `Tick`, `now()`, `Player::set_time`, `settings` |
| `keep_day` 하루 이어서 하기 | 자지 않고 나가도 그날이 남음 (1분마다·나갈 때 저장) | `World::set_live_saving` |
| `rpg` RPG: 모험가 서버 | 전사 / 마법사 직업과 스킬 트리, 기술 버튼(Q), 마나·투지 바, 모두의 월드 하나, 서버 하나의 시계, 농사와 잠 막기(설정), `/직업` | `ServerTick`, `Server::set_shared_world`, `PlayerSleep`·`PlayerTill` … 막기, `MobDeath` 경험치, `progress.skills`, `settings` |
| `town_helper` 마을 도우미 | 귀환 주문서(쓰면 집 앞으로), 체력 150, 고운 말 채팅, 환영 인사, 광산 층 이름 '지하 n층', `/비` `/맑음` | `Use`, `Chat::replace`, `Join`, `where_text`, `set_weather` |
| `custom_model` 커스텀 모델 | `/변신`으로 파란 고양이가 되고 `/인사`로 손을 흔듦 | [`models_add`, `emotes_add`](models), `set_model`, `play_anim` |
| `wild_fish` 거친 물고기 | 잉어는 느긋하게, 참치는 빠르게, 비단잉어는 물결처럼 오르내리다 갑자기 내달림 | `progress.fish.<id>.reel`, `reel` 내보내기 (SDK 없이) |

빌드 (GreenHaven-Server에서):

```sh
python tools/build_plugins.py                 # 모두
python tools/build_plugins.py rpg keep_day    # 몇 개만
python tools/build_plugins.py --zip out rpg   # out/rpg.zip 으로도 묶기
```
