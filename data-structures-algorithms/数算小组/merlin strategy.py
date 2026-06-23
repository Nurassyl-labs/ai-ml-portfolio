#如果梅林过于明显的远离红方角色，贴近边缘，这样会暴露身份。尝试加入限制条件，梅林的位置要使得尽量少的红方角色能听到自己的发言，
#且尽量多的蓝方角色能听到自己的发言，且自身位置不会紧邻9*9区域的边缘，考虑几个条件的权重进行评估，下面的分数构成是deepseek给出的示例，这一部分没有用到LLM。
#计算某个位置的红方可听玩家数量;计算某个位置的蓝方可听玩家数量;计算位置距离边缘的距离;生成所有可能的移动路径（最多三步），并评估最终位置的得分，最后返回一个可行的最高分的路径。
def _merlin_strategy(self, pos: tuple) -> str:
    """梅林智能平衡策略"""
    # 获取环境数据
    red_players = [pid for pid in self.suspected_red_players if pid in self.player_positions]
    blue_players = [pid for pid in self.player_positions if pid not in self.suspected_red_players]
    
    # 生成候选移动路径（最多3步）
    candidate_paths = self._generate_merlin_paths(pos)
    
    # 评估每条路径的最终位置
    best_score = -float('inf')
    best_path = []
    for path in candidate_paths:
        final_pos = path[-1][1]
        score = self._evaluate_merlin_position(final_pos, red_players, blue_players)
        if score > best_score:
            best_score = score
            best_path = path
    
    # 构建策略描述
    target_x, target_y = best_path[-1][1] if best_path else pos
    analysis = [
        f"目标位置：({target_x},{target_y})",
        f"红方监听风险：{self._red_audible_count(target_x, target_y)}人",
        f"蓝方覆盖人数：{self._blue_audible_count(target_x, target_y)}人",
        f"边缘距离：{min(target_x, 8-target_x, target_y, 8-target_y)}格"
    ]
    return "\n".join(analysis)

def _evaluate_merlin_position(self, pos: tuple, reds: list, blues: list) -> float:
    """梅林位置综合评分"""
    x, y = pos
    # 基础安全分（0-30）
    safe_score = 30 - (self._closest_red_distance(pos) * 3)  # 离最近红方越远分越高
    
    # 蓝方收益分（0-40）
    blue_score = sum(
        3 if self._is_key_blue(pid) else 1
        for pid in blues
        if self._in_blue_hearing_range(pos, self.player_positions[pid])
    ) * 2
    
    # 边缘惩罚分（0-30）
    edge_penalty = 0
    edge_dist = min(x, 8-x, y, 8-y)
    if edge_dist < 2:
        edge_penalty = 30 - (edge_dist * 15)  # 距离0格扣30分，1格扣15分
    elif edge_dist > 5:
        edge_penalty = 5  # 过于中心可能有异常
    
    # 自然移动分（0-10）
    natural_score = 5 if len(set(self.memory.get("last_moves", []))) > 1 else 0
    
    return safe_score + blue_score - edge_penalty + natural_score

def _generate_merlin_paths(self, start_pos: tuple) -> list:
    """生成梅林候选路径（考虑红方视线）"""
    paths = []
    queue = [ ([], start_pos, 0) ]  # (路径, 当前位置, 步数)
    
    for _ in range(3):
        new_queue = []
        for path, current_pos, steps in queue:
            for dir in ["Up", "Down", "Left", "Right"]:
                new_pos = self._calculate_new_pos(current_pos, dir)
                if self._is_valid_merlin_step(new_pos, path):
                    new_path = path + [(dir, new_pos)]
                    new_queue.append( (new_path, new_pos, steps+1) )
        queue = new_queue
        paths.extend(queue)
    
    return paths

def _is_valid_merlin_step(self, pos: tuple, existing_path: list) -> bool:
    """验证移动合理性"""
    # 不与他人位置冲突
    if pos in self.player_positions.values():
        return False
    
    # 避免直线移动超过2步
    if len(existing_path) >= 2:
        last_two_dirs = [p[0] for p in existing_path[-2:]]
        if len(set(last_two_dirs)) == 1 and last_two_dirs[0] == existing_path[-1][0]:
            return False
    
    # 至少保持1格红方安全距离
    return self._closest_red_distance(pos) >= 1

def _red_audible_count(self, x: int, y: int) -> int:
    """计算能听到梅林的红方人数（排除奥伯伦）"""
    return sum(
        1 for pid in self.suspected_red_players
        if pid in self.player_positions
        and self._role_type(pid) != "Oberon"
        and self._in_red_hearing_range((x,y), self.player_positions[pid])
    )

def _blue_audible_count(self, x: int, y: int) -> int:
    """计算能听到梅林的蓝方人数"""
    return sum(
        1 for pid in self.player_positions
        if pid not in self.suspected_red_players
        and self._in_blue_hearing_range((x,y), self.player_positions[pid])
    )

def _in_red_hearing_range(self, pos1: tuple, pos2: tuple) -> bool:
    """红方听力范围判断（3x3）"""
    return abs(pos1[0]-pos2[0]) <= 1 and abs(pos1[1]-pos2[1]) <= 1

def _in_blue_hearing_range(self, pos1: tuple, pos2: tuple) -> bool:
    """蓝方听力范围判断（骑士/派西维尔5x5）"""
    return abs(pos1[0]-pos2[0]) <= 2 and abs(pos1[1]-pos2[1]) <= 2