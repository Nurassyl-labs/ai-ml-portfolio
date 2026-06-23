import random
import re
from game.avalon_game_helper import (
    askLLM, read_public_lib,
    read_private_lib, write_into_private
)
  # 调用大语言模型

class Player:
    def __init__(self):

        # 初始化玩家状态。

        self.player_index = None  # 玩家编号
        self.role_type = None  # 玩家角色类型
        self.role_sight = {}  # 夜晚视野信息
        self.map = None  # 地图数据
        self.memory = {
            "speech": {},  # {player_index: [utterance1, utterance2, ...]}
            "votes": [],  # [(operators, {pid: vote})]
            "mission_results": []  # [True, False, ...]
        }
        self.is_merlin = False  # 是否为梅林
        self.is_assassin = False  # 是否为刺客
        self.is_persival = False  # 是否为派西维尔
        self.is_mogana = False  # 是否为莫甘娜
        self.is_red_team = False  # 是否为红方成员
        self.teammates = set()  # 推测的可信玩家编号
        self.suspected_red_players = []  # 怀疑的红方玩家列表
        self.suspected_merlin = []  # 怀疑的梅林

    def set_player_index(self, index: int):

        # 设置玩家编号。
        self.player_index = index

    def set_role_type(self, role_type: str):

        # 设置玩家角色。
        self.role_type = role_type
        if role_type == "Merlin":
            self.is_merlin = True
        elif role_type == "Assassin":
            self.is_assassin = True
            self.is_red_team = True
        elif role_type == "Percival":
            self.is_persival = True
        elif role_type == "Morgana":
            self.is_mogana = True
            self.is_red_team = True
        elif role_type == "Oberon":
            self.is_red_team = True

    def pass_role_sight(self, role_sight: dict[str, int]):

        # 接收夜晚视野信息。
        self.role_sight = role_sight
        if self.is_merlin:
            self.suspected_red_players = list(role_sight.keys())  # 梅林直接知道所有红方玩家
        if self.is_percival:
            self.suspected_merlin = list(role_sight.keys())  # 帕西二选一梅林            

    def pass_map(self, map_data: list[list[str]]):

        # 接收地图数据
        self.map = map_data

    def pass_message(self, content: tuple[int, str]):

        # 接收其他玩家发言。
        player_id, speech = content
        self.memory["speech"].setdefault(player_id, []).append(speech)


    def pass_mission_members(self, leader: int, members: list[int]):

        self.memory.setdefault("team_history", []).append({
            "round": len(self.memory.get("team_history", [])) + 1,
            "leader": leader,
            "team": members,
            "included_me": self.player_index in members
        })
        # 记录历史队伍和队长，用于后续的推理

    def decide_mission_member(self, team_size: int) -> list[int]:# 此处应当调用LLM（待完成）

        # （队长）选择任务成员。
        if self.is_merlin:
            # 梅林避免提名红方玩家
            return [p for p in range(7) if p not in self.suspected_red_players][:team_size]
        elif self.is_red_team:
            # 红方尽量混入队伍
            return [self.player_index] + random.sample([p for p in range(7) if p != self.player_index], team_size - 1)
        else:
            # 其他蓝方玩家借助大模型选择
            full_history = read_public_lib()
            promet = f"作为蓝方成员，请根据之前的对话、队伍信息与任务结果，选择{team_size}位你信任的玩家加入你的队伍，确保你回答的内容只有用逗号隔开的玩家编号，\n{full_history}"
            response = askLLM(promet)
            return list(map(int, response.split(',')))

    def walk(self) -> tuple[str, ...]:# 此处应当调用LLM（待完成）


        return tuple()

    def say(self) -> str:

        try:
            full_history = read_public_lib()  # 读取公有库：每轮队伍、队长信息+玩家发言记录+投票和任务执行结果等
            if self.is_merlin:
                promet = (f"身为梅林，你已知晓红方玩家编号{self.suspected_red_players}，"
                          f"请你根据之前的对话和任务结果，生成发言："
                          f"发言应保证在梅林身份不暴露的前提下，辅助蓝方决策，避免红方混入队伍\n{full_history}")
                reponse = askLLM(promet)
                return reponse
            elif self.is_persival:
                promet = (f"身为帕西维尔，你已知晓{self.suspected_merlin}两者中有一个是梅林"
                          f"请你根据之前的对话和任务结果，生成发言："
                          f"发言应保护梅林身份不暴露，辅助蓝方决策，避免红方混入队伍\n{full_history}")
                reponse = askLLM(promet)
                return reponse
            elif self.is_mogana:
                promet = f""
                reponse = askLLM(promet)
                return reponse
            elif self.is_red_team:
                promet = f""
                reponse = askLLM(promet)
                return reponse
            else:
                promet = f""
                reponse = askLLM(promet)
                return reponse

        except Exception as e:
            # write_into_private(f"round_say_error: {str(e)}")
            return "这轮信息太混乱，我还在观察。"

    def mission_vote1(self) -> bool:# 此处应当调用LLM（待完成）

        # 对队伍提案进行公投。
        # 分析队伍中是否有可疑红方玩家
        if not self.is_red_team:
            if not self.is_merlin:
                full_history = read_public_lib()
                promet = f"作为蓝方成员，请根据之前的对话、队伍信息与任务结果，选择至多三位你怀疑是红方的玩家，确保你回答的内容只有用逗号隔开的玩家编号，\n{full_history}"
                response = askLLM(promet)
                suspected_red_player = list(map(int, response.split(',')))
                suspicious = any(p in suspected_red_player for p in self.memory.get("team_history").get(-1).get("team"))
                return not suspicious  # 如果怀疑有红方玩家，投反对票
            else:
                suspicious = any(p in self.suspected_red_players for p in self.memory.get("team_history").get(-1).get("team"))
                return not suspicious  # 如果怀疑有红方玩家，投反对票
        return True # 红方直接同意（待定）

    def mission_vote2(self) -> bool:

        # 任务执行投票（决定成功/失败）。
        if self.is_red_team:
            # 红方根据策略决定是否隐藏身份
            # 此处应当调用LLM（待完成）
            return random.choice([True, False])
        return True  # 蓝方只能投成功票

    def assass(self) -> int:

        # 刺客刺杀梅林
        # 调用大语言模型分析梅林最可能的身份
        full_history = read_public_lib()  # 读取公有库：每轮队伍、队长信息+玩家发言记录+投票和任务执行结果等
        prompt = f"根据以下对话和任务结果，你觉得谁最可能是梅林？只返回数字编号。\n{full_history}"
        response = askLLM(prompt)
        target = re.findall(r'\b[1-7]\b', response) # 提取目标编号
        return int(target[0])
