def walk(self) -> tuple[str, ...]:
    """综合角色特性的移动决策"""
    try:
        origin_pos = self.player_positions[self.player_index]
        map_str = "\n".join([" ".join(row) for row in self.map])
        full_history = read_public_lib()

        # 生成角色特定策略
        if self.role_type == "Merlin":
            strategy = self._merlin_strategy(origin_pos)
        elif self.role_type == "Percival":
            strategy = self._percival_strategy(origin_pos, full_history)
        elif self.role_type == "Morgana":
            strategy = self._morgana_strategy(origin_pos, full_history)
        elif self.role_type == "Assassin":
            strategy = self._assassin_strategy(origin_pos)
        elif self.role_type == "Knight":
            strategy = self._knight_strategy(origin_pos)
        else: 
            strategy = self._oberon_strategy(origin_pos)


        prompt = f"""你当前在{origin_pos}，地图状态：{map_str}
其他玩家位置：{[f"{pid}:{pos}" for pid,pos in self.player_positions.items() if pid != self.player_index]}

作为{self.role_type}，移动策略：{strategy}
请用最多3个方向指令（Up/Down/Left/Right）响应，示例：("Up", "Left")"""

        raw_directions = askLLM(prompt)
        return self._process_directions(raw_directions, origin_pos)

    except Exception as e:
        write_into_private(f"移动异常：{str(e)}")
        return self._safe_default_move(origin_pos)

def _merlin_strategy(self, pos) -> str:
    #优化版在merlin strategy.py中
    """梅林移动策略（优化版在merlin strategy.py中）"""
    edge_dist = min(pos[0],8-pos[0],pos[1],8-pos[1])
    reds = [pid for pid in self.suspected_red_players if pid in self.player_positions]
    
    strategy = [
        f"与红方保持至少2格距离（当前最近红方距离：{self._closest_red_distance(pos)})",
        "优先停留在3-5坐标区间" if edge_dist <3 else "",
        "每三步改变移动方向避免规律性"
    ]
    return "\n".join(filter(None, strategy))

def _percival_strategy(self, pos, history) -> str:
    #思路是如果还没有确定谁是梅林，派西维尔尽量要同时听到梅林与莫甘娜的发言，如果无法完成，就至少听到一个人的；如果可以确定梅林身份，那么在确保前面的条件实现的情况下离梅林尽量远
    """派西维尔动态策略"""
    merlin_candidate = self._infer_merlin(history)
    
    if merlin_candidate:
        merlin_pos = self.player_positions.get(merlin_candidate)
        dist = abs(pos[0]-merlin_pos[0]) + abs(pos[1]-merlin_pos[1])
        return (
            f"已识别梅林在{merlin_pos}，保持至少3格距离\n"
            f"同时接近其他可疑目标（莫甘娜）"
        )
    return "寻找梅林与莫甘娜的中点区域"

def _morgana_strategy(self, pos, history) -> str:
    #思路是模仿梅林
    """莫甘娜伪装策略"""
    blue_candidates = self._infer_blue_players(history)
    red_candidates = self._infer_red_players(history) - {self.player_index}
    
    strategy = [
        "模仿梅林行为模式：",
        f"远离疑似红方：{red_candidates}",
        f"接近可信蓝方：{blue_candidates}",
        "保持与边缘至少1格距离",
        "每轮移动方向变化不超过90度"
    ]
    return "\n".join(strategy)

def _knight_strategy(self, pos: tuple) -> str:
    """骑士最大化监听范围策略"""
    audible_count = self._calculate_audible_players(pos, is_knight=True)
    best_move = self._find_optimal_position(pos, 
        lambda p: self._audible_score(p, role_type="Knight"),
        max_steps=3
    )
    
    return (
        f"当前可监听{audible_count}人\n"
        f"最优路径建议移动到{best_move}：\n"
        f"- 预估可监听人数：{self._audible_score(best_move, 'Knight')}\n"
        "优先覆盖蓝方关键角色（梅林/派西维尔）"
    )

def _oberon_strategy(self, pos: tuple) -> str:
    """奥伯伦最大化监听同时保持隐蔽策略"""
    safe_score = self._calculate_safety(pos)
    audible_score = self._audible_score(pos, role_type="Oberon")
    
    return (
        f"平衡隐蔽性与监听范围：\n"
        f"- 当前安全评分：{safe_score}/10\n"
        f"- 可监听玩家数：{audible_score}\n"
        "优先选择同时满足：\n"
        "1. 监听人数≥3\n"
        "2. 距离最近蓝方≥2格\n"
        "3. 不在直线走廊区域"
    )

def _audible_score(self, pos: tuple, role_type: str) -> int:
    """计算当前位置的监听价值"""
    x, y = pos
    score = 0
    for pid, (px, py) in self.player_positions.items():
        if pid == self.player_index:
            continue
        
        # 不同角色的听力范围
        if role_type in ["Knight", "Oberon"]:
            if abs(x-px) <= 2 and abs(y-py) <= 2:  # 5x5范围
                score += 1
                # 对关键角色额外加分，各权重的具体数值有待商榷，下面的10分制是deepseek给出的示例
                if role_type == "Knight" and self._is_key_blue(pid):
                    score += 2
        else:
            if abs(x-px) <= 1 and abs(y-py) <= 1:  # 3x3范围
                score += 1
    return score

def _calculate_safety(self, pos: tuple) -> float:
    """奥伯伦安全评分（0-10）"""
    blue_positions = [p for pid,p in self.player_positions.items() if not self._is_red(pid)]
    min_blue_dist = min((abs(pos[0]-x)+abs(pos[1]-y) for (x,y) in blue_positions)) if blue_positions else 5
    
    edge_dist = min(pos[0], 8-pos[0], pos[1], 8-pos[1])
    corridor_penalty = 2 if (pos[0] in [2,6] or pos[1] in [2,6]) else 0
    
    return min(
        (min_blue_dist * 2) + 
        (edge_dist * 0.5) - 
        corridor_penalty, 
    10)

def _find_optimal_position(self, start_pos: tuple, 
                          score_func: Callable[[tuple], int], 
                          max_steps: int) -> tuple:
    """寻找最优移动位置"""
    from collections import deque
    
    visited = {}
    queue = deque([(start_pos, [], 0)])  # (position, path, step)
    best_score = -1
    best_path = []
    
    while queue:
        current_pos, path, steps = queue.popleft()
        current_score = score_func(current_pos)
        
        if current_score > best_score:
            best_score = current_score
            best_path = path
        
        if steps >= max_steps:
            continue
            
        # 生成下一步候选
        for dx, dy, dir in [(-1,0,"Left"), (1,0,"Right"), (0,-1,"Up"), (0,1,"Down")]:
            new_x = current_pos[0] + dx
            new_y = current_pos[1] + dy
            if 0 <= new_x <9 and 0 <= new_y <9:
                new_pos = (new_x, new_y)
                if new_pos not in self.player_positions.values():
                    new_path = path + [dir]
                    if new_pos not in visited or len(new_path) < visited[new_pos]:
                        visited[new_pos] = len(new_path)
                        queue.append((new_pos, new_path, steps+1))
    
    # 返回最佳路径终点（若存在）
    return best_path[-1] if best_path else start_pos

def _is_key_blue(self, pid: int) -> bool:
    """判断是否为蓝方关键角色"""
    return self.role_sight.get(pid, "") in ["Merlin", "Percival"]

def _is_red(self, pid: int) -> bool:
    """判断玩家阵营（奥伯伦视角）"""
    return pid in self.teammates or pid == self.player_index


def _process_directions(self, raw: str, origin_pos) -> tuple:
    #deepseek给的补充
    """带物理验证的路径处理"""
    valid_dirs = []
    current_pos = origin_pos
    occupied = set(self.player_positions.values())
    
    for dir in re.findall(r"Up|Down|Left|Right", raw)[:3]:
        new_pos = self._calculate_new_pos(current_pos, dir)
        if new_pos not in occupied and 0<=new_pos[0]<9 and 0<=new_pos[1]<9:
            valid_dirs.append(dir)
            current_pos = new_pos
            occupied.add(new_pos)
        else:
            break
    return tuple(valid_dirs) or ("Up",)

def _infer_merlin(self, history) -> int:
    """派西维尔身份推断逻辑"""
    prompt = f"""分析游戏历史判断梅林身份：
{history}
请用1个数字回答最可能是梅林的玩家编号："""
    #思路是调用历史来判断，不确定在这里应用LLM的写法
    response = askLLM(prompt)
    return int(re.search(r"\d", response).group()) if response else None

def _infer_blue_players(self, history) -> set:
        #思路是调用历史来判断，不确定在这里应用LLM的写法
    """莫甘娜的蓝方推断"""
    prompt = f"""根据以下信息推断可信蓝方玩家（返回数字编号逗号分隔）：
{history}
你怀疑的红方玩家是："""
    response = askLLM(prompt)
    return set(int(n) for n in re.findall(r"\d", response))

def _closest_red_distance(self, pos) -> int:
    """计算最近红方距离"""
    return min(
        abs(pos[0]-p[0])+abs(pos[1]-p[1]) 
        for pid,p in self.player_positions.items() 
        if pid in self.suspected_red_players
    ) if self.suspected_red_players else 99