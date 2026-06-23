import random
import re
from game.avalon_game_helper import (
    askLLM, read_public_lib,
    read_private_lib, write_into_private
)

class Player:
    def __init__(self):
        # 初始化玩家状态。
        self.index = None
        self.player_index = None  # 玩家编号
        self.role_type = None  # 玩家角色类型
        self.role_sight = {}  # 夜晚视野信息
        self.map = None  # 地图数据
        self.player_positions = {}  # 所有玩家位置
        self.memory = {
            "speech": {},            # {player_index: [utterance1, utterance2, ...]}
            "team_history": [],      # [{"round":…, "leader":…, "team":[…], …}, …]
            "mission_results": []    # [True, False, ...]
        }
        # 角色身份标志
        self.is_merlin = False
        self.is_assassin = False
        self.is_persival = False
        self.is_mogana = False
        self.is_red_team = False
        # 推理辅助
        self.teammates = set()             # 可信任玩家
        self.suspected_red_players = []    # 怀疑的红方玩家
        self.suspected_merlin = []         # 帕西怀疑的梅林

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
            # 梅林直接知道所有红方玩家编号
            self.suspected_red_players = list(role_sight.values())
        if self.is_persival:
            # 派西维尔得到两个编号（梅林和莫甘娜之一）
            self.suspected_merlin = list(role_sight.values())

    def pass_map(self, map_data: list[list[str]]):
        # 接收地图数据
        self.map = map_data

    def pass_position_data(self, player_positions: dict[int, tuple]):
        # 接收所有玩家的位置信息
        self.player_positions = player_positions

    def pass_message(self, content: tuple[int, str]):
        # 接收其他玩家发言。
        player_id, speech = content
        self.memory["speech"].setdefault(player_id, []).append(speech)

    def pass_mission_members(self, leader: int, members: list[int]):
        # 记录本轮队长和队伍
        self.memory["team_history"].append({
            "round": len(self.memory["team_history"]) + 1,
            "leader": leader,
            "team": members,
            "included_me": self.player_index in members
        })

    def decide_mission_member(self, team_size: int) -> list[int]:
        # 队长提名决策；保留原逻辑，调整编号范围
        if self.is_merlin:
            # 梅林避免提名红方玩家
            candidates = [p for p in range(1, 8) if p not in self.suspected_red_players]
            return candidates[:team_size]
        elif self.is_red_team:
            # 红方尽量混入队伍
            others = [p for p in range(1, 8) if p != self.player_index]
            return [self.player_index] + random.sample(others, team_size - 1)
        else:
            # 其他蓝方玩家借助大模型选择
            full_history = read_public_lib()
            prompt = (
                f"作为蓝方成员（ID {self.player_index}），"
                f"请选择 {team_size} 名你信任的玩家加入队伍，"
                "只返回用逗号分隔的编号。\n"
                f"历史记录：{full_history}"
            )
            response = askLLM(prompt)
            # 解析返回的编号
            nums = [int(x) for x in re.findall(r'\b[1-7]\b', response)]
            # 填充或截断到 team_size
            while len(nums) < team_size:
                choice = random.choice([p for p in range(1, 8) if p not in nums])
                nums.append(choice)
            return nums[:team_size]

    def walk(self) -> tuple[str, ...]:
        # 假设你已经在 pass_position_data 中更新了 self.player_positions
        cur_x, cur_y = self.player_positions[self.player_index]
        occupied = set(self.player_positions.values())
        occupied.remove((cur_x, cur_y))  # 把自己当前位置从 occupied 中去掉

        # 让 LLM 给出一串逗号分隔的“Up,Down,Left,Right”
        prompt = f"…你的提示…当前坐标({cur_x},{cur_y})…"
        resp = askLLM(prompt)
        moves = [m.strip() for m in resp.split(",")]

        result = []
        for m in moves:
            if m == "Up":
                nx, ny = cur_x-1, cur_y
            elif m == "Down":
                nx, ny = cur_x+1, cur_y
            elif m == "Left":
                nx, ny = cur_x, cur_y-1
            elif m == "Right":
                nx, ny = cur_x, cur_y+1
            else:
                continue

            # 边界检查
            if not (0 <= nx < len(self.map) and 0 <= ny < len(self.map[0])):
                continue
            # 占用检查
            if (nx, ny) in occupied:
                continue

            # 如果合法，就接受这一步
            result.append(m)
            cur_x, cur_y = nx, ny
            occupied.add((nx, ny))  # 标记新位置也被占用
            if len(result) >= 3:
                break

        return tuple(result)


    def say(self) -> str:
        # 发言决策，为每个角色填充 prompt
        history = read_public_lib()
        if self.is_merlin:
            prompt = (
                f"你是梅林（ID {self.player_index}），已知红方编号 {self.suspected_red_players}，"
                "请生成一句帮助蓝方决策但不暴露自己身份的发言。"
            )
        elif self.is_persival:
            prompt = (
                f"你是派西维尔（ID {self.player_index}），"
                f"梅林可能是 {self.suspected_merlin} 中之一，"
                "请生成一句帮助蓝方推理的发言。"
            )
        elif self.is_mogana:
            prompt = (
                f"你是莫甘娜（ID {self.player_index}），"
                "请生成一句让蓝方误以为你是梅林的迷惑发言。"
            )
        elif self.is_red_team:
            prompt = (
                f"你是红方角色 {self.role_type}（ID {self.player_index}），"
                "请生成一句低调的发言，帮助红方隐藏身份。"
            )
        else:
            prompt = (
                f"你是普通蓝方骑士（ID {self.player_index}），"
                "请生成一句基于当前局势的发言，帮助蓝方完成任务。"
            )
        return askLLM(prompt)

    def mission_vote1(self) -> bool:
        # 公投阶段投票，分析队伍可疑程度
        last = self.memory["team_history"][-1]["team"] if self.memory["team_history"] else []
        if not self.is_red_team:
            # 蓝方分析队伍中是否有红方
            suspicious = any(p in self.suspected_red_players for p in last)
            return not suspicious
        # 简化：红方总同意
        return True

    def mission_vote2(self) -> bool:
        # 任务执行阶段：红方由 LLM 决定，蓝方总成功
        if self.role_type in {"Assassin", "Morgana", "Oberon"}:
            history = read_public_lib()
            prompt = (
                f"你是红方角色 {self.role_type}（ID {self.player_index}），"
                "请选择返回 True（成功）或 False（破坏）。\n"
                f"历史：{history}"
            )
            resp = askLLM(prompt).strip().lower()
            return "true" in resp
        return True

    def assass(self) -> int:
        # 刺客刺杀决策：LLM 输出最可能是梅林的编号
        history = read_public_lib()
        prompt = (
            f"你是刺客（ID {self.player_index}），"
            "请根据以下历史记录，仅返回最可能是梅林的玩家编号。\n"
            f"{history}"
        )
        resp = askLLM(prompt)
        ids = re.findall(r'\b[1-7]\b', resp)
        if ids:
            return int(ids[0])
        # 兜底：随机刺杀
        return random.choice([p for p in range(1, 8) if p != self.player_index])
