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
`#[on(Enable)] fn enable`의 `Registry`로 합니다([규칙 등록](rules)). `cutscene` `riding` `flight` `showcase` `friend_lands` `camera_modes` `arcade` `hide_blocks` `fx_demo`는 서버 쪽과 [게임 쪽 코드](client)를
함께 가집니다(`src/shared.rs` `server.rs` `client.rs`). 몇몇은 게임에도 zip으로 들어 있어 월드 선택 › 편집 › 플러그인에서
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
| `hitboxes` 히트박스 | `/벽세우기`: 동쪽 3칸에 히트박스(1 × 9칸, 3블록 높이)를 가진 상자 구조물, 서쪽 3칸에 같은 히트박스의 단단한 바위 엔티티: 서버의 걸음 판정과 게임의 몸이 둘 다 막음. `/벽치우기`로 치움 | `put_structure`의 `"hit"`, `set_hitbox` `set_solid` |
| `void_arena` 허공 경기장 | 미니게임: 빈 월드(server.properties `level-type=void`) 한가운데 떠 있는 9×9 블록 발판, 마을·주민·농사·상점·밤 없이 발판 위에서 시작, 경기장 블록을 쌓고 곡괭이로 부숨, 떨어지면 가방 그대로 발판에서 다시 | `WorldCreate`의 `fill` `World::set_spawn` `set_vanilla` `set_live_saving`, `Join`의 `set_check("air")`, `PlayerMove`의 `death`, `PlayerDeath`의 `keep_inventory` |
| `minigame_hub` 미니게임 허브 | 허브(빈 월드 `level-type=void`의 광장)에서 `/참가`로 대기, 틀 `arena_tpl`에서 복사한 경기장(`arena1`, `arena2`)으로 옮겨 그곳의 가방(칼·샐러드, 돈 없음)과 규칙(체력 60, 멈춘 시계, PvP, 위치 자주·채팅 월드 전체)으로 겨룸; 떨어지면 탈락, 15초나 한 사람 남으면 끝: 경기장은 틀의 모습으로, 모두 허브의 가방으로 | `World::set_mode` `set_rule` `set_sync`, `Server::create_world_from` `reset_world`, `Player::reset`, `Server::data_*` |
| `arena_mode` 경기장 모드 | 마을 있는 월드를 `set_mode("arena")` 한 번으로 경기장으로: 농장 기능·기력·하루 끝 없음, 멈춘 시계, HUD의 날짜·시간·퀘스트 숨김, 칼 한 자루 키트, 초당 30 행동; `/농장` 원래대로, `/경기장` 다시 | `World::set_mode` `set_rule` |
| `flat_world` 탁 트인 평지 | 성벽·성문·바위 둑·암초 없는 마을, 마을 밖은 나무 없는 평평한 풀밭 (새 월드에만) | `WorldCreate`의 `remove_plot`, `ChunkGenerate`의 `fill` `clear_props` |
| `deep_mines` 거친 땅과 깊은 광산 | 성벽 밖 땅이 더 높고 험해짐(산, 눈, 큰 바위), 광산 층이 넓어지고 금이 일찍, 층마다 도착한 곳 근처에 금광석 | `terrain` `mine_layout`, `MineFloor::set_rock` |
| `server_password` 서버 비밀번호 | 처음 들어올 때 비밀번호를 정하고, 그 뒤로는 들어올 때마다 물어봄 (세 번 틀리면 돌려보냄) | `PlayerLogin`의 입력 창, `Gui::secret`, `Server` 값 |
| `server_clock` 서버 공통 시계 | 모든 월드의 시각을 서버 시계 하나로 (하루 길이는 설정), `/시계` | `Tick`, `now()`, `Player::set_time`, `settings` |
| `keep_day` 하루 이어서 하기 | 자지 않고 나가도 그날이 남음 (1분마다·나갈 때 저장) | `World::set_live_saving` |
| `stay_up` 밤새기 | 새벽 2시에 기절하지 않음: 아침 6시에 하루가 저절로 넘어가고 그 자리에서 이어서 함, 자지 않은 아침엔 정산 화면 대신 출하 대금 한마디 | 규칙 `day_end` `pass_out` `summary_awake` |
| `rpg` RPG: 모험가 서버 | 전사 / 마법사 직업과 스킬 트리, 기술 버튼(Q), 마나·투지 바, 서버 하나의 시계, 농사와 잠 막기(설정), `/직업` | `ServerTick`, `PlayerSleep`·`PlayerTill` … 막기, `MobDeath` 경험치, `progress.skills`, `settings` |
| `town_helper` 마을 도우미 | 귀환 주문서(쓰면 집 앞으로), 체력 150, 고운 말 채팅, 환영 인사, 광산 층 이름 '지하 n층', `/비` `/맑음` | `Use`, `Chat::replace`, `Join`, `where_text`, `set_weather` |
| `second_wind` 기절과 긴 밤 | 쓰러져도 물건을 지키고 10초 뒤 일어남, `/기절`, `/긴밤` | `PlayerDeath`, `death`, `respawn`, `set_night_time` |
| `blaster` 물총 놀이 | 1인칭 FPS(손 뷰모델 `hands.glb`: 벽을 뚫지 않는 층, 쏘기·장전 클립, F 조준경): `/물총`(PvP, 모두 체력·탄 가득) `/물총 연습`(PvP 없이) `/물총 끄기` `/물총 엄폐`·`치우기`(앞에 돌벽). 왼쪽 클릭 물총(12발, R 장전, 25 피해), 오른쪽 클릭 돌 대포(서버가 날리는 발사체, 60과 둘레 반), 십자선, 반동, 탄도선, 맞힘 표시, 쓰러뜨림 알림, 남은 탄. 모든 사격을 서버가 쏜 사람이 본 그대로(되감아) 다시 판정 | 두 쪽: `World::cast_for` `World::projectile` `ProjectileHit` `FastPacket`; 게임 쪽 `Camera::forward` `kick` `sensitivity` `fov` `Crosshair` `hit` `World::cast` `Local::attach`(`Viewmodel`) `play_anim_with` `anim_end` `Viewmodel::arms` `beam` |
| `kits` 직업 장비 | `/직업 [전사\|궁수]`(패널): 가방이 그 직업 장비로 바뀜(이름·설명·색·반짝임·데이터 붙은 무기, 회복약), 든 칸 0, 첫 칸 무기는 옮길 수 없음; 무기마다 사거리·대기시간 | `ItemStack`, `set_inventory`, `set_held_slot`, `InventoryClick` 취소, 규칙 `tools`의 `reach`·`cooldown` |
| `tag` 술래잡기 | `/술래 [초]`: 시작한 사람이 술래(팀), 나머지는 도망자. 술래가 E로 건드리거나 치면(그 판 동안 PvP, 피해 없음) 술래가 바뀜; 시간이 다 되면 도망자에게 30골드 | `PlayerInteractPlayer`, `PlayerDamage`, `World::team`, `set_pvp`, `Server::player`, Tick에서 남에게 `add_gold` |
| `custom_model` 커스텀 모델 | `/변신`으로 파란 고양이가 되고 `/인사`로 손을 흔듦 | [`models_add`, `emotes_add`](models), `set_model`, `play_anim` |
| `wild_fish` 거친 물고기 | 잉어는 느긋하게, 참치는 빠르게, 비단잉어는 물결처럼 오르내리다 갑자기 내달림 | `progress.fish.<id>.reel`, `reel` 내보내기, "gh" `register` (SDK 없이) |
| `screen` 화면 꾸미기 | 그림이 든 환영 창, 설정에 나오는 단축키(하나는 게임 키와 겹쳐 꺼짐: 접속 때 알림), 오른쪽 아래 마나 바와 화염 버튼, 왼쪽 위 둥근 미니맵(M으로 켜고 끄기), H로 시계 숨기기, 마나 상점 창(가방의 물건을 마나로), 가방 대신 자기 보따리 창(K로 원래 가방) | [화면](screen): `Hud` `El` `Anchor`, `World::columns_raw` + `send_png`, `Hud::hide` `key` `replace` `restore`, `Packet`, `WindowOpen`, `Inventory`, `InventoryClick` |
| `townsfolk` 엔티티 주민 | 주민 기능 없이 엔티티만으로 만든 주민 새봄: 시간표대로 마을 길을 걷고, 가까이 오면 인사, E로 이야기·선물, 플레이어마다 하트(`/새봄`) | `spawn_avatar`, `Entity::set_interact` `say`, [`EntityInteract`](events#entityinteract), `World::path`, `Player::get/set` |
| `builder` 건축가 | 마인크래프트처럼: 바닐라 블록(흙·풀·모래·눈, 돌은 곡괭이) 부수고 놓기, `/건축`, 빈손으로 여닫는 문, 글을 쓰는 표지판(`/표지판 글`), `/미리보기`로 내 화면에만 보이는 돌집 → `/짓기` / `/취소` | `World::set_block_rules`, `PlayerInteract`, `set_block_data` `block_data`, `Player::show_block` `clear_fake_blocks` |
| `portal` 포탈 | 두 서버 사이: `/이동 <주소 또는 GS-아이디> [표]`로 표를 들고 다른 서버로(허브에서 경기장으로), 그 서버의 포탈이 어디서 왔는지와 표(서명 확인됨 / 안 됨)를 말하고, `/돌아가기`로 온 곳으로 | `Player::transfer`, `Join::transfer_from` `transfer_data` `transfer_trusted`, `data_put` |
| `channels` 채널 | 한 서버를 채널 두 개로 (메이플스토리처럼): 들어올 때 사람이 적은 채널로, 같은 채널끼리만 서로 보이고 채팅·목소리도 그 채널에만. `/채널` 채널마다 몇 명, `/채널 2` 옮기기. 설정 `mode`: "people"(기본, 월드 하나에 사람만 나눔: 블록·드롭·몬스터·주민은 함께) / "worlds"(채널마다 월드: `ch1`과 그 사본) | `Player::set_view_group`, `join_channel`, `Server::channel_members`, `create_world_from`, `move_world` |
| `grenades` 수류탄 | H 파편(튕기고 구르다 2.2초 뒤 펑: 가까울수록 크게, 벽 뒤는 안전, 밀려남), J 섬광(정면으로 본 사람일수록 오래 하얗게), N 연막(큰 연기 구름); 휴대폰은 버튼, `/수류탄 파편\|섬광\|연막 [x,y,z]` | 두 쪽: `World::projectile_with` `ProjectileExpire` `EntityBump` `World::explode` `World::seen_from`; 게임 쪽 `Input::bind` `Screen::fade` `Particles::emit` |
| `tycoon` 컨베이어 타이쿤 | `/타이쿤`: 내 부지(남은 밀려남), 드로퍼의 부품이 컨베이어로 수집기에 들어가면 돈, E 버튼으로 드로퍼·부품 값 사기(산 것이 지어짐), 컨베이어에 서면 실려 감, 돈은 다시 들어와도·다시 켜도 그대로 | `World::conveyor` `watch_entities` `ZoneEntityEnter` `ModelEntity::set_body` `Player::set` `World::set_live_saving` |
| `zones` 구역과 밀기 | `/경기장`: 내 둘레에 밖으로 못 나가는 울타리(월드 보더), 밟으면 하늘로 튀는 점프대, E를 2초 눌러 여는 보물 상자(50골드); `/폭발`: 둘레 4 m의 사람을 밀어내고 몬스터에 피해 | `World::keep_in` `zone`, `ZoneEnter` `ZoneLeave`, `Player::push`, `World::overlap`, `set_interact_with` |
| `blocks` 새 블록 | 루비 블록, 고유 텍스처의 벽돌, 비쳐 보이는 유리, 이어지는 나무 울타리(모델), 3×3×3칸 오두막(모델), `/블록`으로 받아 놓고 곡괭이로 부숨, 이미 있는 청크에도 처음 불러올 때 한 번 루비 기둥 | `Registry::block` (`BlockKind::textured` `model`), `BlockPlace` `BlockBreak`, `ChunkLoad`, `World::set_blocks` `chunk_mark` |
| `cutscene` 연출 | G를 누르면 게임이 서버에 '종 울리기'를 요청하고, 서버가 판정(10초에 한 번, 마나석 하나)한 뒤 결과를 보내면 게임이 카메라를 종으로 돌리고 화면을 번쩍이며 위쪽에 다음 종까지 남은 시간을 매 프레임 그림 | [게임 쪽 코드](client): `client!` `Frame` `Packet`, `Camera::look_at` `shake` `release`, `Screen::flash`, 게임 쪽 `Hud`; 서버 쪽 `Hud::key_action` `send_text` |
| `plane_demo` 비행기 | `/비행기`로 부르고 E로 앞자리(조종)·뒷자리(승객)에 탐; 돌면 그쪽으로 기울고 오르면 기수가 들림, 모두의 게임에서. `/조종`: 비행 시뮬레이터(평평한 월드의 활주로에서 Shift 출력, S로 이륙, A/D 기울이기, Q/E 방향타, C 조종석 시점; 기체와 함께 기우는 카메라, 계기판, 실속·추락) | [탈것](moving#탈것): `Player::mount_seat`, `ModelEntity::set_rotation`, `set_check("air")`, `Registry::tick_rate`; [서버가 움직이는 탈것](moving#서버가-움직이는-탈것-차와-비행기-sdkphysics): `Plane` `Driven` `Predicted`, `Camera::set_oriented`, `Me::set_pose`, `Draw` |
| `racing` 레이스 | `/레이스`: 평평한 월드의 블록 트랙에서 차(W A S D, Space 드리프트), 길·모래·풀의 마찰, 체크포인트 넷을 차례로 지나 3바퀴(랩 기록), 미니맵, rpm에 맞춰 높아지는 엔진 소리, 다음 체크포인트 위에서 도는 표시 | [서버가 움직이는 탈것](moving#서버가-움직이는-탈것-차와-비행기-sdkphysics): `Car` `Driven` `Predicted`, `Entities::predict`, `World::zone` + `ZoneEnter`, `Draw`, `Sound::play` `set`, `Local::tween` `set_rotation` |
| `riding` 탈것과 지팡이 | 마을 소에 E로 올라타면 두 배 빨리 달림(서버가 그 빠르기로 판정), J로 내림, `/소`로 옆에 부름; `/지팡이`로 받는 마법 지팡이를 쓰면 시전 동작과 함께 앞쪽에 번개 구슬이 날아가 몬스터를 침 | [탈것](moving#탈것): `Player::mount` `dismount`, `Dismount`, `glide_to`; [도구 동작](moving#도구-동작-플러그인-아이템): 아이템의 `action` `model` `hit`, `Use`; 게임 쪽 `Local` `World::ground` `Camera::fov` |
| `showcase` 화면 실험실 | 앞에 셰이더로 빛나는 피라미드(실행 중 만든 메시)와 3D 글자, 그 위에 붙어 다니는 HUD, 오른쪽 위 직접 그린 게이지, 월드 속 패널의 버튼(서버가 누름을 세어 보냄), 은은한 배경 소리, U로 화면 물결 효과, 서버와 빠른 패킷 왕복 횟수 | [게임 쪽 코드](client): `mesh` `Material::create` `Local::set_material` `spawn_text`, `pin`, `Draw`, `Local::spawn_panel` `set_panel` + `click`, `Sound::play`, `Screen::shader`, `send_fast` + `FastPacket` + `Hud::send_fast` |
| `fx_demo` 연출 물리와 소리 | B: 서버가 앞쪽에 폭발 자리를 정해 모두에게. 게임마다 파편이 튀고, 연막이 피어오르고(안에 들면 화면이 뿌옇게), 근처 사람은 래그돌로 쓰러지고, 소리가 붙은 상자가 날아가고, 귀가 멍멍해짐. 말풍선도 이 서버의 모양 | [게임 쪽 코드](client): `Physics::debris` `ragdoll`, `Local::physics`, `Particles::smoke`, `Sound::effect` `duck` `attach`, `Chat::bubble_style` |
| `arcade` 오락실 | K(부스트)와 O(빛) 액션(휴대폰에선 화면 버튼, 설정 › 조작키에서 키 바꾸기), 누를 때마다 서버에 요청하고 답을 HUD에, 마우스 이동량·이동 축·장치·고정 스텝을 HUD에, 어두운 공포 조명, 자기 외곽선, 머리 위 반짝이, 부스트 불꽃, 따라오는 별의 궤적 | [게임 쪽 코드](client): `Input::bind` `Action` `Step` `axis` `mouse_delta` `device`, `request` + 서버 쪽 `split_request` `reply_data`, `Lighting::set` `reset`, `Highlight::add`, `Particles::emit`, `Local::trail` |
| `friend_lands` 친구 땅 | 플레이어마다 자기 땅(플러그인의 월드)이 생기고, 서버 안 친구 기능(신청·수락·거절·끊기: 열기구 창의 「친구 관리」나 `/친구`)을 더함. 열기구 창은 친구 목록(내 땅, 모두의 월드, 게임의 사막 노선도)이 되어, 친구를 고르면 열기구가 떠오르는 동안(열기구 앞 시점) 서버가 뒤에서 그 친구의 땅으로 옮기고, 다 오르면 그 땅 바로 위 상공에서 가만히 내려다보며 「착륙하기」(하늘에서 그 땅의 정거장으로 내려앉는 장면, 열기구 앞 시점) / 「돌아가기」(떠나온 곳으로 옮겨져 거기 내려앉음) | `Server::create_world`, `Player::move_world`, `Server::data_*`(친구 목록), `Hud::replace("balloon")` `open`, `WindowOpen`, `Gui`; 게임 쪽 `Balloon::lift_off` `land` `state`, `World::id` `ready`, `Camera::set` |
| `camera_modes` 카메라 시점 | F5로 시점 바꾸기: 기본 → 영화처럼(천천히 도는 시점) → 내려다보기 → 옆에서(횡스크롤) → 어깨 너머 → 1인칭 → 드론(W A S D, Q / E로 나는 자유 카메라) | [게임 쪽 코드](client): 매 프레임 `Camera::set` `follow` `first_person` `release` |
| `economy` 코인 경제 | 서버의 코인: 잔고·넣기·빼기를 다른 플러그인에 내보냄, `/코인` | [플러그인끼리](interop): `#[export]`, `caller()`, `provides`, API 크레이트(`economy/api`: `api!`) |
| `bounty` 수확 보상 | 수확마다 코인 1개, `/씨앗사기`(코인 5개로 순무 씨앗). 코인 경제가 필요 | `depend`, 다른 플러그인의 API(`economy_api::deposit` `withdraw`) |
| `hide_blocks` 블록 숨바꼭질 | `/숨바꼭질 [숨는 초]`: 친 사람이 술래(빨간 이름표, 멈추고 눈가림), 나머지는 블록으로 변장해 숨음(가만히 있으면 칸에 맞춰 섬). 숨는 동안 술래의 게임에는 숨는 사람의 위치도 블록도 아예 가지 않고, 그다음 가짜 블록 8개 사이에서 E로 때려 찾음(가짜를 때리면 2초 멈춤). 찾힌 사람은 관전자, 모두 찾거나 3분이 지나면 끝 | `Player::disguise` `set_body` `hide_from` `freeze` `set_spectator` `set_nametag` `set_public`, `"block:<kind>"` 엔티티, `EntityInteract`; 게임 쪽 `Players::list` `public_text`, `public` 이벤트, `Screen::fade` |
| `rpg_ui` RPG 화면 | R 화염구 · F 치유 · H 신속 버튼과 재사용 대기 부채꼴, 버프 아이콘과 남은 시간, 몬스터와 플레이어 머리 위 체력 바, 떠오르는 피해 숫자, 스크롤되는 퀘스트 목록, P를 누르는 동안 파티 점수판, 처치 소식, `/보스`: 보스 바와 그 머리 위 막대, 천천히 회복. `!`로 팀 채팅 | [화면](screen#레이아웃-머리-위-트윈-점수판): `El::list` `rich` `boss_bar`, `Hud::sweep` `tween` `pin_to` `feed` `float_text` `board`; [상태 효과](sdk#상태-효과-타이머-쿨다운): `add_effect`, `cooldown`, `Scheduler`, `Timer`; 게임 쪽 `Mobs::near` `Players::near` `Local::fade` |
| `flight` 비행 | Y로 날기 시작하고 다시 Y로 내려옴. W/S 앞뒤, A/D 돌기, Space 위로, Shift 아래로. 비행 규칙(최대 빠르기, 높이)은 `src/shared.rs` 하나에 있어 게임은 그대로 움직이고 서버는 그대로 검사 | [이동 방식 만들기](moving): `Player::set_check`, `PlayerMove`(`dt` `on_ground`), `Tick::dt`; 게임 쪽 `Input::capture` `Me::set_velocity` `set_gravity` `set_move_mode`, `Camera::follow` |

빌드 (GreenHaven-Server에서):

```sh
python tools/build_plugins.py                 # 모두
python tools/build_plugins.py rpg keep_day    # 몇 개만
python tools/build_plugins.py --zip out rpg   # out/rpg.zip 으로도 묶기
```

크레이트에 `client` feature가 있으면 `server.wasm`과 함께 `client.wasm`도 빌드하고, 각각 가져다 쓰는 것을 검사합니다
([게임 쪽 코드 › 빌드](client#빌드)).
