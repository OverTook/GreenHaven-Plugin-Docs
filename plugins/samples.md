---
title: 샘플 플러그인
nav_order: 9
parent: 플러그인
redirect_from:
  - /samples
  - /samples.html
---

# 샘플 플러그인

GreenHaven-Server의 `plugins/` 아래에 있습니다. `wild_fish` 말고는 모두 Rust SDK로 쓰여 있고, 규칙을 바꾸는 것은 모두
`#[on(Enable)] fn enable`의 `Registry`로 합니다([규칙 등록](rules)). 몇몇은 게임에도 zip으로 들어 있어 월드 선택 › 편집 › 플러그인에서
켤 수 있습니다(PC).

| 샘플 | 하는 일 | 보여 주는 것 |
|---|---|---|
| `example` | 마나 바, 화염구 버튼(날아가는 엔티티), 물 주면 섬유, 나무가 한 번에 5분의 1씩 자람, `/신속` | `ui` 버튼·바, `Button`, `Tick`, 엔티티, `set_walk_speed`, `assets/` |
| `big_backpack` 큰 가방과 긴 하루 | 가방 48칸, 기력 최대 +100, 하루 1.5배, 새 농장 1000골드, "가방" 글자 바꾸기 | `Enable`의 `Registry::set` `text`만 |
| `harvest_festival` 풍년 축제 | 비 오는 밤엔 작물이 이틀치 자람, 계절의 7·14·21·28일은 수확 두 배·파는 값 1.25배, 그날 아침 알림, `/축제` | `Grow` `Harvest` `Sell` `Morning` `Command` |
| `golden_crops` 황금 작물 | 새 작물 황금 당근(잡화점 씨앗, 아이콘, 금빛 당근 모델), 먹으면 기력, 새 퀘스트, 거두면 반짝임, `/황금씨앗` | `Registry::crop` `item` `patch`, `assets/`, `Harvest` |
| `new_start` 새 출발 | 짧은 오프닝, 첫날 할 일 넷과 보상 1000골드, 마법 스킬 없음, 3레벨마다 전직(만렙 15), 채집 경험치 두 배, 집 안·광산의 음악, `/노래 곡` | `client.Intro.SCENES` `progress.tutorial_tasks` `progress.skills` `client.Music.TRACKS`, `play_music` |
| `new_creatures` 새 생물 | 밤의 얼음 버섯(돌을 떨굼), 둘레를 돌다 덤비는 도깨비불(광산 2층부터도), 헛간의 염소(이틀에 한 번 염소 젖) | `monsters_add` `animals_add`, `MobStep`, `Mob::set` `attack` |
| `new_neighbor` 새 이웃 하늘 | 새 주민 하늘(소율의 모습, 하루 일정, 대사), 말을 걸면 선택지 창, 이야기, `/하늘`로 부르면 걸어옴 | `WorldCreate`의 `spawn_npc`, `Words`, `Gui`, `Npc::say` `go_to`, 대사 패치 |
| `woodcutter` 나무꾼 | `/나무꾼`: 곁에 나타난 나무꾼(아바타, 머리 위 이름)이 가장 가까운 나무로 걸어가 한 번씩 도끼질해(나무가 흔들림) 자기 쪽으로 베어 쓰러뜨리고, 떨어진 나무 하나를 먹고 하나는 모이를 쪼는 닭으로 꾸미며(나머지는 누구나 주움), 가까운 건물 방에 들렀다 나옴 | `spawn_avatar` `Avatar::set_look` `hold` `set_name` `play_anim` `debris_at` `debris_damage` `items_near` `ItemEntity::consume_by` `set_model` `play_anim` `room`, `Tick` |
| `flat_world` 탁 트인 평지 | 성벽·성문·바위 둑·암초 없는 마을, 마을 밖은 나무 없는 평평한 풀밭 (새 월드에만) | `WorldCreate`의 `remove_plot`, `ChunkGenerate`의 `fill` `clear_props` |
| `deep_mines` 거친 땅과 깊은 광산 | 성벽 밖 땅이 더 높고 험해짐(산, 눈, 큰 바위), 광산 층이 넓어지고 금이 일찍, 층마다 도착한 곳 근처에 금광석 | `terrain` `mine_layout`, `MineFloor::set_rock` |
| `server_password` 서버 비밀번호 | 처음 들어올 때 비밀번호를 정하고, 그 뒤로는 들어올 때마다 물어봄 (세 번 틀리면 돌려보냄) | `PlayerLogin`의 입력 창, `Gui::secret`, `Server` 값 |
| `server_clock` 서버 공통 시계 | 모든 월드의 시각을 서버 시계 하나로 (하루 길이는 설정), `/시계` | `Tick`, `now()`, `Player::set_time`, `settings` |
| `keep_day` 하루 이어서 하기 | 자지 않고 나가도 그날이 남음 (1분마다·나갈 때 저장) | `World::set_live_saving` |
| `rpg` RPG: 모험가 서버 | 전사 / 마법사 직업과 스킬 트리, 기술 버튼(Q), 마나·투지 바, 모두의 월드 하나, 서버 하나의 시계, 농사와 잠 막기(설정), `/직업` | `ServerTick`, `Server::set_shared_world`, `PlayerSleep`·`PlayerTill` … 막기, `MobDeath` 경험치, `progress.skills`, `settings` |
| `town_helper` 마을 도우미 | 귀환 주문서(쓰면 집 앞으로), 체력 150, 고운 말 채팅, 환영 인사, 광산 층 이름 '지하 n층', `/비` `/맑음` | `Use`, `Chat::replace`, `Join`, `where_text`, `set_weather` |
| `second_wind` 기절과 긴 밤 | 쓰러져도 물건을 지키고 10초 뒤 일어남, `/기절`, `/긴밤` | `PlayerDeath`, `death`, `respawn`, `set_night_time` |
| `custom_model` 커스텀 모델 | `/변신`으로 파란 고양이가 되고 `/인사`로 손을 흔듦 | [`models_add`, `emotes_add`](models), `set_model`, `play_anim` |
| `wild_fish` 거친 물고기 | 잉어는 느긋하게, 참치는 빠르게, 비단잉어는 물결처럼 오르내리다 갑자기 내달림 | `progress.fish.<id>.reel`, `reel` 내보내기, "gh" `register` (SDK 없이) |
| `screen` 화면 꾸미기 | 오른쪽 아래 마나 바와 화염 버튼, 왼쪽 위 둥근 미니맵(M으로 켜고 끄기), H로 시계 숨기기, 마나 상점 창(가방의 물건을 마나로), 가방 대신 자기 보따리 창(K로 원래 가방) | [화면](screen): `Hud` `El` `Anchor`, `World::columns_raw` + `send_png`, `Hud::hide` `key` `replace` `restore`, `Packet`, `Inventory`, `InventoryClick` |
| `townsfolk` 엔티티 주민 | 주민 기능 없이 엔티티만으로 만든 주민 새봄: 시간표대로 마을 길을 걷고, 가까이 오면 인사, E로 이야기·선물, 플레이어마다 하트(`/새봄`) | `spawn_avatar`, `Entity::set_interact` `say`, [`EntityInteract`](events#entityinteract), `World::path`, `Player::get/set` |
| `blocks` 새 블록 | 루비 블록, 고유 텍스처의 벽돌, 비쳐 보이는 유리, 이어지는 나무 울타리(모델), 3×3×3칸 오두막(모델), `/블록`으로 받아 놓고 곡괭이로 부숨, 이미 있는 청크에도 처음 불러올 때 한 번 루비 기둥 | `Registry::block` (`BlockKind::textured` `model`), `BlockPlace` `BlockBreak`, `ChunkLoad`, `World::set_blocks` `chunk_mark` |

빌드 (GreenHaven-Server에서):

```sh
python tools/build_plugins.py                 # 모두
python tools/build_plugins.py rpg keep_day    # 몇 개만
python tools/build_plugins.py --zip out rpg   # out/rpg.zip 으로도 묶기
```
