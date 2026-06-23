import random
import re
from game.avalon_game_helper import (
    askLLM, read_public_lib,
    read_private_lib, write_into_private
)


class Player:
    def __init__(self):
        self.index = None
        self.role = None
        self.role_info = {}
        self.map = None
        self.memory = {
            "speech": {},         # {player_index: [utterance1, utterance2, ...]}
            "votes": [],          # [(operators, {pid: vote})]
            "mission_results": [] # [True, False, ...]
        }
        self.teammates = set()   # 推测的可信玩家编号
        self.suspects = set()    # 推测的红方编号

    def set_player_index(self, index: int):
        self.index = index

    def set_role_type(self, role_type: str):
        self.role = role_type

    def pass_role_sight(self, role_sight: dict[str, int]):
        self.sight = role_sight
        self.suspects.update(role_sight.values())

    def pass_map(self, map_data: list[list[str]]):
        self.map = map_data

    def pass_message(self, content: tuple[int, str]):
        player_id, speech = content:
        self.memory["speech"].setdefault(player_id, []).append(speech)
        if "任务失败" in speech or "破坏" in speech:
            self.suspects.add(player_id)  # 简化的推理：谁喊破坏谁可疑

    def decide_mission_member(self, team_size: int) -> list[int]:
        """
        选择任务队员：
        - 自己一定上
        - 优先选择不在嫌疑列表的人
        """
        candidates = [i for i in range(1, 8) if i != self.index and i not in self.suspects]
        random.shuffle(candidates)
        chosen = [self.index] + candidates[:team_size - 1]
        return chosen[:team_size]

    def pass_mission_members(self, leader: int, members: list[int]):
        self.last_leader = leader # 储存本轮的队长编号
        self.last_team = members # 储存本轮将执行任务的队员编号列表
        self.is_chosen = self.index in self.last_team # 是否被选为任务执行者
        self.memory.setdefault("team_history", []).append({
            "round": len(self.memory.get("team_history", [])) + 1,
            "leader": self.last_leader,
            "team": self.last_team.copy(),
            "included_me": self.is_chosen
        })
        # 记录历史队伍和队长，用于后续的推理

    def walk(self) -> tuple:
        """
        TODO 现在就是随便走
        """
        return "Left", "Up", "Right"

    def say(self) -> str:
        # 使用大模型来判断谁最可能是梅林，演示自然语言+正则+推理
        try:
            full_history = read_public_lib() # 读取公有库：每轮队伍、队长信息+玩家发言记录+投票和任务执行结果等
            prompt = f"根据以下对话和任务结果，你觉得谁最可能是梅林？只返回数字编号。\n{full_history}"
            reply = askLLM(prompt)
            match = re.findall(r'\b[1-7]\b', reply) # 使用正则表达式提取LLM回复中的第一个数字编号（可以优化）
            if not match:
                return "我还在观察。"
            merlin_id = int(match[0])
            write_into_private(f"round_say: suspect_merlin={merlin_id}") # 写入私有库，记录这轮判断

            if merlin_id == self.index:
                return f"我觉得我知道谁是梅林，但我不方便多说。"
            else:
                return f"我怀疑{merlin_id}号是梅林，理由稍后详谈。"
        except Exception as e:
            write_into_private(f"round_say_error: {str(e)}")
            return "这轮信息太混乱，我还在观察。"

    def mission_vote1(self) -> bool:
        """
        投票策略：
        - 如果队伍中全是可信玩家则通过
        - 否则按概率通过
        """
        if all(pid not in self.suspects for pid in self.last_team):
            return True
        return random.random() > 0.3

    def mission_vote2(self) -> bool:
        """
        执行任务投票：
        - 红方一定投False（破坏）
        - 蓝方一定True（成功）
        """
        return self.role not in ["Morgana", "Assassin", "Oberon"]

    def assass(self) -> int:
        """刺杀"""
        possible_targets = [i for i in range(1, 6) if i != self.player_id]
        return random.choice(possible_targets)