def mission_vote2(self) -> bool:
    """红方破坏决策（整合位置信息）"""
    if not self.is_red_team:
        return True  # 蓝方强制成功
    
    try:
        # 获取战略上下文
        current_round = len(self.memory["mission_results"]) + 1
        success_count = sum(self.memory["mission_results"])
        mission_members = self.memory["team_history"][-1]["team"] if self.memory.get("team_history") else []
        
        # 构建位置分析
        position_analysis = ""
        if self.player_positions:
            my_pos = self.player_positions[self.player_index]
            blue_players = [pid for pid in mission_members if not self._is_suspected_red(pid)]
            closest_blue = min(blue_players, key=lambda pid: self._distance(my_pos, self.player_positions[pid])) if blue_players else None
            position_analysis = f"你当前靠近玩家{closest_blue}" if closest_blue else "你处于孤立位置"
        
        prompt = f"""作为{self.role_type}（红方成员），请决定是否破坏本轮任务：
- 游戏阶段：第{current_round}轮（需{3-success_count}次失败阻止蓝方）
- 任务成员：{mission_members}
- 位置态势：{position_analysis}
- 队友可见性：{len(self.teammates)}名队友在任务中

策略建议：
{self._get_red_strategy(current_round, success_count)}
请用单个字母回答（Y=破坏/N=隐藏）："""
        
        # 调用LLM决策
        response = askLLM(prompt).strip().upper()
        
        # 决策逻辑（带战略保护）
        if "Y" in response:
            return self._validate_sabotage_decision(current_round, success_count)
        return random.random() < 0.2  # 默认低概率破坏
    
    except Exception as e:
        write_into_private(f"红方决策异常：{str(e)}")
        return False  # 异常时优先破坏

def _distance(self, pos1: tuple, pos2: tuple) -> int:
    """计算曼哈顿距离"""
    return abs(pos1[0]-pos2[0]) + abs(pos1[1]-pos2[1])

def _is_suspected_red(self, pid: int) -> bool:
    """判断是否为可疑红方"""
    if self.is_merlin:
        return pid in self.suspected_red_players
    return pid in self.teammates

def _get_red_strategy(self, current_round: int, success_count: int) -> str:
    """生成红方策略提示"""
    strategies = []
    if success_count >= 2:
        strategies.append("⚠️ 蓝方即将胜利，必须破坏本轮！")
    if current_round == 3 and success_count < 1:
        strategies.append("前三轮无失败，建议本轮破坏")
    if len(self.memory.get("mission_results", [])) >= 4:
        strategies.append("已进入终局阶段，谨慎使用破坏")
    return "\n".join(strategies) if strategies else "保持隐蔽，择机破坏"

def _validate_sabotage_decision(self, current_round: int, success_count: int) -> bool:
    """决策合理性"""
    if success_count >= 2 and current_round >= 3:
        return False  # 必须破坏
    if current_round == 5 and success_count == 2:
        return False  # 最终轮必须破坏
    return random.random() < 0.8  # 高概率执行破坏