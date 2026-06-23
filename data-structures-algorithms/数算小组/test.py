# player.py
import random
import re
from game.avalon_game_helper import (
    askLLM, read_public_lib,
    read_private_lib, write_into_private
)

# 把你自己在 walk.py、vote2.py 里的实现引入进来
from walk import custom_walk    # 自定义的 walk 实现
from vote2 import custom_mission_vote2  # 自定义的 mission_vote2 实现

class Player:
    def __init__(self):
        # ---- 基础属性 ----
        self.index = None               # 玩家编号
        self.role = None                # 角色类型字符串
        self.role_sight = {}            # 夜晚视野信息
        self.map = None                 # 地图数据
        self.player_positions = {}      # 每轮更新时由平台注入
        # ---- 记忆与推理 ----
        self.memory = {
            "speech": {},               # {player_id: [utterance,…]}
            "team_history": [],         # 每轮的 {round, leader, team, included_me}
            "votes": [],                # [(phase, votes_dict)]
            "mission_results": []       # [True/False,…]
        }
        # ---- 身份判断 ----
        self.is_merlin = False
        self.is_assassin = False
        self.is_percival = False
        self.is_morgana = False
        self.is_oberon = False
        self.is_red = False
        # ---- 推理集合 ----
        self.suspected_red = set()
        self.percival_candidates = []  # “两选一”可能的梅林候选

    def set_player_index(self, index: int):
        self.index = index

    def set_role_type(self, role_type: str):
        self.role = role_type
        if role_type == "Merlin":
            self.is_merlin = True
        elif role_type == "Assassin":
            self.is_assassin = True
            self.is_red = True
        elif role_type == "Percival":
            self.is_percival = True
        elif role_type == "Morgana":
            self.is_morgana = True
            self.is_red = True
        elif role_type == "Oberon":
            self.is_oberon = True
            self.is_red = True

    def pass_role_sight(self, role_sight: dict[str,int]):
        # 夜晚视野：Merlin 看红方三人，Percival 看两人（Merlin/Morgana）
        self.role_sight = role_sight
        if self.is_merlin:
            self.suspected_red.update(role_sight.values())
        if self.is_percival:
            # Percival 得到两个 ID，存为候选
            self.percival_candidates = list(role_sight.values())

    def pass_map(self, map_data: list[list[str]]):
        self.map = map_data

    def pass_position_data(self, player_positions: dict[int,tuple[int,int]]):
        self.player_positions = player_positions

    def pass_message(self, content: tuple[int,str]):
        pid, text = content
        self.memory["speech"].setdefault(pid, []).append(text)

    def pass_mission_members(self, leader:int, members:list[int]):
        rec = {
            "round": len(self.memory["team_history"])+1,
            "leader": leader,
            "team": members,
            "included_me": self.index in members
        }
        self.memory["team_history"].append(rec)

    def decide_mission_member(self, team_size:int) -> list[int]:
        # 梅林避免提名红方
        if self.is_merlin:
            good = [i for i in range(1,8) if i not in self.suspected_red]
            return good[:team_size]
        # 红方成员优先带上自己并混入
        if self.is_red:
            others = [i for i in range(1,8) if i!=self.index]
            return [self.index] + random.sample(others, team_size-1)
        # 其他蓝方调用 LLM
        hist = read_public_lib()
        prompt = (
            f"你是蓝方玩家{self.index}号，历史记录：{hist}\n"
            f"请选择{team_size}名你最信任的玩家编号，用逗号分隔返回。"
        )
        resp = askLLM(prompt)
        return list(map(int, resp.split(',')))

    def walk(self) -> tuple[str,...]:
        # 委托给你在 walk.py 中写好的策略函数
        return custom_walk(self)

    def say(self) -> str:
        # 以 Merlin 为例 :contentReference[oaicite:0]{index=0}
        if self.is_merlin:
            prompt = (
                f"身为梅林，你知道红方编号{sorted(self.suspected_red)}，"
                f"请生成一句话模糊指引蓝方，但不暴露具体名单。\n"
                f"{read_public_lib()}"
            )
            return askLLM(prompt)
        if self.is_percival:
            prompt = (
                f"身为派西维尔，你知道两位梅林候选{self.percival_candidates}，"
                f"请生成一句话帮助蓝方，但不泄露哪位是真梅林。\n"
                f"{read_public_lib()}"
            )
            return askLLM(prompt)
        # Morgana 或其他角色可仿照补充
        return "我还在思考。"

    def mission_vote1(self) -> bool:
        # 蓝方若队伍中无明显嫌疑，则同意；否则否决
        last = self.memory["team_history"][-1]
        if not self.is_red:
            if any(m in self.suspected_red for m in last["team"]):
                return False
            return True
        # 红方一律同意
        return True

    def mission_vote2(self) -> bool:
        # 真正投票阶段委托给 vote2.py 中的策略
        return custom_mission_vote2(self)

    def assass(self) -> int:
        # 刺杀阶段用 LLM 或简单统计推理
        hist = read_public_lib()
        prompt = f"谁最可能是梅林？只返回编号。\n{hist}"
        resp = askLLM(prompt)
        m = re.findall(r"\b[1-7]\b", resp)
        return int(m[0]) if m else random.choice([i for i in range(1,8) if i!=self.index])
