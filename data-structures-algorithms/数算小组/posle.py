import random
import re
from collections import Counter
from game.avalon_game_helper import askLLM, read_public_lib, write_into_private

class Player:
    def __init__(self):
        # 基本状态
        self.player_index = None
        self.role_type = None
        self.role_sight = {}
        self.map = None
        self.player_positions = {}
        # 对局记忆
        self.memory = {
            "speech": {},            # {pid: [msg, ...]}
            "team_history": [],      # [{"round": n, "leader": x, "team": [...]}]
            "mission_results": []    # [True/False,...]
        }
        # 身份标志
        self.is_merlin = False
        self.is_persival = False
        self.is_mogana = False
        self.is_red = False
        # 推理集合
        self.trusted = set()         # 多次成功的可信玩家
        self.suspected = Counter()   # 发言和投票可疑度计数
        self.seen_votes = []         # 记录每轮投票详情

    def set_player_index(self, index: int):
        self.player_index = index

    def set_role_type(self, role_type: str):
        self.role_type = role_type
        if role_type == "Merlin":
            self.is_merlin = True
        elif role_type == "Percival":
            self.is_persival = True
        elif role_type in {"Morgana", "Assassin", "Oberon"}:
            self.is_red = True
            if role_type == "Morgana":
                self.is_mogana = True

    def pass_role_sight(self, role_sight: dict[str, int]):
        self.role_sight = role_sight
        if self.is_merlin:
            # 梅林直接知道邪恶列表
            self.suspected.update(role_sight.values())
        if self.is_persival:
            # 派西得知两名候选
            for pid in role_sight.values():
                self.suspected[pid] += 0.5

    def pass_map(self, map_data: list[list[str]]):
        self.map = map_data

    def pass_position_data(self, pos: dict[int, tuple]):
        self.player_positions = pos

    def pass_message(self, content: tuple[int, str]):
        pid, msg = content
        self.memory["speech"].setdefault(pid, []).append(msg)
        # 简单关键词计数
        for word in ("fail", "betray", "sabotage"):
            if word in msg.lower():
                self.suspected[pid] += 1

    def pass_mission_members(self, leader: int, members: list[int]):
        self.memory["team_history"].append({
            "round": len(self.memory["team_history"]) + 1,
            "leader": leader,
            "team": members
        })

    def decide_mission_member(self, team_size: int) -> list[int]:
        # 优先：队伍中出现次数最多的可信玩家
        rounds = self.memory["team_history"]
        success_cnt = Counter()
        for res, info in zip(self.memory["mission_results"], rounds):
            if res:
                success_cnt.update(info["team"])
        # 信任度高的前 team_size
        trusted = [pid for pid, _ in success_cnt.most_common() if pid != self.player_index]
        # 如果我是梅林——绝不选红
        if self.is_merlin:
            avail = [p for p in range(1,8) if p not in self.suspected]
            return avail[:team_size]
        # 红方保持原有策略
        if self.is_red:
            others = [p for p in range(1,8) if p != self.player_index]
            return [self.player_index] + random.sample(others, team_size-1)
        # 蓝方使用混合策略
        pick = []
        # 先加自己
        pick.append(self.player_index)
        # 再加最可信的人
        for pid in trusted:
            if len(pick) < team_size and pid not in pick:
                pick.append(pid)
        # 补充至足够人数
        candidates = [p for p in range(1,8) if p not in pick]
        while len(pick) < team_size:
            pick.append(random.choice(candidates))
        return pick

    def walk(self) -> tuple[str, ...]:
        # Путаемся с LLM, но фильтруем по карте и занятым позициям
        x,y = self.player_positions[self.player_index]
        occupied = set(self.player_positions.values()) - {(x,y)}
        prompt = f"你是{self.role_type}({self.player_index})，请给出0–3个移动方向Up/Down/Left/Right"
        resp = askLLM(prompt)
        moves = [m.strip() for m in resp.split(",") if m.strip() in {"Up","Down","Left","Right"}]
        result = []
        for m in moves:
            dx,dy = {"Up":(-1,0),"Down":(1,0),"Left":(0,-1),"Right":(0,1)}[m]
            nx,ny = x+dx, y+dy
            if 0<=nx<len(self.map) and 0<=ny<len(self.map) and (nx,ny) not in occupied:
                result.append(m); x,y=nx,ny; occupied.add((x,y))
                if len(result)==3: break
        return tuple(result)

    def say(self) -> str:
        if self.is_merlin:
            prompt = (f"你是梅林({self.player_index})，知道红方{list(self.suspected.elements())}，"
                      "生成一句不暴露身份但引导蓝方的发言。")
        elif self.is_persival:
            prompt = (f"你是派西维尔({self.player_index})，"
                      f"梅林在{list(self.suspected.elements())}中，"
                      "生成一句帮助蓝方推理的发言。")
        elif self.is_red:
            prompt = (f"你是红方{self.role_type}({self.player_index})，"
                      "生成一句谨慎隐藏身份的发言。")
        else:
            prompt = (f"你是骑士({self.player_index})，"
                      "生成一句帮助蓝方完成任务的发言。")
        return askLLM(prompt)

    def mission_vote1(self) -> bool:
        last_team = self.memory["team_history"][-1]["team"]
        # 如果 в команде есть подозрительные, голосуем против
        for pid in last_team:
            if self.suspected[pid] > 1:
                return False
        return True

    def mission_vote2(self) -> bool:
        # Красные саботируют не каждый раз
        if self.is_red:
            # 70% шанс сломать по key-раундам
            return random.random() > 0.7
        return True

    def assass(self) -> int:
        # Статистический выбор Мерлина
        history = read_public_lib()
        prompt = f"你是刺客({self.player_index})，谁最可能是梅林？只返回编号"
        resp = askLLM(prompt)
        ids = re.findall(r'\b[1-7]\b', resp)
        if ids:
            return int(ids[0])
        # случайный
        return random.choice([p for p in range(1,8) if p!=self.player_index])
