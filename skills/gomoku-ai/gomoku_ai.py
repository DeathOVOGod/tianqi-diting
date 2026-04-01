#!/usr/bin/env python3
"""
五子棋 AI - v21 (修复威胁检测bug + 进攻优先 + 新评分)
"""

import sys
import random

BOARD_SIZE = 15
EMPTY = '.'
BLACK = 'X'
WHITE = 'O'

# 威胁等级常量
THREAT_FIVE = 10000000
THREAT_LIVE_FOUR = 9500000
THREAT_RUSH_FOUR = 8500000
THREAT_LIVE_THREE = 750000
THREAT_SLEEP_THREE = 300000
THREAT_LIVE_TWO = 200000

class GomokuAI:
    def __init__(self, board_str=None):
        if board_str:
            self.board = self.parse_board(board_str)
        else:
            self.board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
    
    def parse_board(self, board_str):
        """解析棋盘字符串，返回15x15的2D列表"""
        board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        lines = board_str.strip().split('\n')
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            # 跳过列头行
            if 'A B C D' in stripped or stripped.startswith('   A'):
                continue
            parts = stripped.split()
            if len(parts) < 2:
                continue
            # 第一部分是行号
            row_text = parts[0]
            try:
                row_num = int(row_text)
                row_idx = row_num - 1  # 转为0索引
            except ValueError:
                continue
            if not (0 <= row_idx < BOARD_SIZE):
                continue
            # 剩余部分是棋盘数据（过滤空字符串，处理末尾多余空格）
            row_data = [p for p in parts[1:] if p]
            for col_idx, ch in enumerate(row_data):
                if col_idx >= BOARD_SIZE:
                    break
                if ch in ['.', '·']:
                    board[row_idx][col_idx] = EMPTY
                elif ch in ['X', '●']:
                    board[row_idx][col_idx] = BLACK
                elif ch in ['O', '○']:
                    board[row_idx][col_idx] = WHITE
        return board
    
    def get_threat_level(self, row, col, player):
        """
        评估在(row, col)落子后的威胁等级
        row, col 是0索引
        """
        if self.board[row][col] != EMPTY:
            return 0
        
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        max_threat = 0
        
        for dr, dc in directions:
            # 统计落子点顺方向的连续己方棋子
            fwd = 0
            fwd_r, fwd_c = row + dr, col + dc
            while 0 <= fwd_r < BOARD_SIZE and 0 <= fwd_c < BOARD_SIZE:
                if self.board[fwd_r][fwd_c] == player:
                    fwd += 1
                    fwd_r += dr
                    fwd_c += dc
                else:
                    break
            
            # 统计落子点逆方向的连续己方棋子
            bwd = 0
            bwd_r, bwd_c = row - dr, col - dc
            while 0 <= bwd_r < BOARD_SIZE and 0 <= bwd_c < BOARD_SIZE:
                if self.board[bwd_r][bwd_c] == player:
                    bwd += 1
                    bwd_r -= dr
                    bwd_c -= dc
                else:
                    break
            
            total = fwd + bwd  # 落子后该方向总连接数
            
            # 延伸空间检查
            fwd_empty = (0 <= fwd_r < BOARD_SIZE and 0 <= fwd_c < BOARD_SIZE and 
                        self.board[fwd_r][fwd_c] == EMPTY)
            bwd_empty = (0 <= bwd_r < BOARD_SIZE and 0 <= bwd_c < BOARD_SIZE and 
                        self.board[bwd_r][bwd_c] == EMPTY)
            
            # total == 4: 落子后5连
            if total == 4:
                max_threat = max(max_threat, THREAT_FIVE)
            # total == 3: 落子后4连
            elif total == 3:
                if fwd_empty and bwd_empty:
                    max_threat = max(max_threat, THREAT_LIVE_FOUR)
                elif fwd_empty or bwd_empty:
                    max_threat = max(max_threat, THREAT_RUSH_FOUR)
                else:
                    max_threat = max(max_threat, THREAT_RUSH_FOUR)
            # total == 2: 落子后3连
            elif total == 2:
                if fwd_empty and bwd_empty:
                    max_threat = max(max_threat, THREAT_LIVE_THREE)
                elif fwd_empty or bwd_empty:
                    max_threat = max(max_threat, THREAT_SLEEP_THREE)
            # total == 1: 落子后2连
            elif total == 1:
                if fwd_empty and bwd_empty:
                    max_threat = max(max_threat, THREAT_LIVE_TWO)
        
        return max_threat
    
    def find_all_threats(self, player):
        """返回所有威胁位置，按威胁等级降序"""
        threats = []
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self.board[r][c] != EMPTY:
                    continue
                level = self.get_threat_level(r, c, player)
                if level > 0:
                    threats.append((r, c, level))
        threats.sort(key=lambda x: -x[2])
        return threats
    
    def find_defense_point(self, opponent):
        """找到对手的最高威胁点（用于防守）
        
        遍历所有空位，模拟对手落子后计算威胁等级。
        只考虑眠三及以上的威胁。
        """
        threats = []
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self.board[r][c] != EMPTY:
                    continue
                level = self.get_threat_level(r, c, opponent)
                if level >= THREAT_SLEEP_THREE:
                    threats.append((r, c, level))
        
        if not threats:
            return None
        threats.sort(key=lambda x: -x[2])
        return threats[0][0], threats[0][1], threats[0][2]
    
    def find_double_threat(self, player):
        """检测双威胁（一步形成两个冲四或更强的威胁）"""
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self.board[r][c] != EMPTY:
                    continue
                
                count = 0
                for dr, dc in [(0,1), (1,0), (1,1), (1,-1)]:
                    fwd = 0
                    fwd_r, fwd_c = r + dr, c + dc
                    while 0 <= fwd_r < BOARD_SIZE and 0 <= fwd_c < BOARD_SIZE:
                        if self.board[fwd_r][fwd_c] == player:
                            fwd += 1
                            fwd_r += dr
                            fwd_c += dc
                        else:
                            break
                    
                    bwd = 0
                    bwd_r, bwd_c = r - dr, c - dc
                    while 0 <= bwd_r < BOARD_SIZE and 0 <= bwd_c < BOARD_SIZE:
                        if self.board[bwd_r][bwd_c] == player:
                            bwd += 1
                            bwd_r -= dr
                            bwd_c -= dc
                        else:
                            break
                    
                    total = fwd + bwd
                    fwd_empty = (0 <= fwd_r < BOARD_SIZE and 0 <= fwd_c < BOARD_SIZE and 
                                self.board[fwd_r][fwd_c] == EMPTY)
                    bwd_empty = (0 <= bwd_r < BOARD_SIZE and 0 <= bwd_c < BOARD_SIZE and 
                                self.board[bwd_r][bwd_c] == EMPTY)
                    
                    # 冲四或更强的威胁
                    if total >= 4:
                        count += 2
                    elif total == 3:
                        if fwd_empty or bwd_empty:
                            count += 1
                    elif total == 2:
                        if fwd_empty and bwd_empty:
                            count += 1
                
                if count >= 2:
                    return r, c
        return None
    
    def find_four_attacks(self, player):
        """找到所有冲四及以上进攻机会"""
        fours = []
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self.board[r][c] != EMPTY:
                    continue
                level = self.get_threat_level(r, c, player)
                if level >= THREAT_RUSH_FOUR:
                    fours.append((r, c, level))
        fours.sort(key=lambda x: -x[2])
        return fours
    
    def can_defend_four(self, player, r, c):
        """检查对手能否有效防守冲四"""
        opponent = WHITE if player == BLACK else BLACK
        for dr, dc in [(0,1), (1,0), (1,1), (1,-1)]:
            fwd = 0
            fwd_r, fwd_c = r + dr, c + dc
            while 0 <= fwd_r < BOARD_SIZE and 0 <= fwd_c < BOARD_SIZE:
                if self.board[fwd_r][fwd_c] == player:
                    fwd += 1
                    fwd_r += dr
                    fwd_c += dc
                else:
                    break
            
            bwd = 0
            bwd_r, bwd_c = r - dr, c - dc
            while 0 <= bwd_r < BOARD_SIZE and 0 <= bwd_c < BOARD_SIZE:
                if self.board[bwd_r][bwd_c] == player:
                    bwd += 1
                    bwd_r -= dr
                    bwd_c -= dc
                else:
                    break
            
            total = fwd + bwd
            fwd_empty = (0 <= fwd_r < BOARD_SIZE and 0 <= fwd_c < BOARD_SIZE and 
                        self.board[fwd_r][fwd_c] == EMPTY)
            bwd_empty = (0 <= bwd_r < BOARD_SIZE and 0 <= bwd_c < BOARD_SIZE and 
                        self.board[bwd_r][bwd_c] == EMPTY)
            
            if total == 3 and (fwd_empty or bwd_empty):
                return False
        return True
    
    def find_vcf(self, player, depth=4):
        """VCF（连续冲四）搜索"""
        if depth <= 0:
            return None
        
        opponent = WHITE if player == BLACK else BLACK
        
        for r, c, level in self.find_four_attacks(player):
            self.board[r][c] = player
            
            if level >= THREAT_FIVE:
                self.board[r][c] = EMPTY
                return r, c
            
            if self.can_defend_four(player, r, c):
                self.board[r][c] = EMPTY
                continue
            
            opp_fours = self.find_four_attacks(opponent)
            opp_has_four = any(f[2] >= THREAT_RUSH_FOUR for f in opp_fours)
            
            if opp_has_four:
                self.board[r][c] = EMPTY
                continue
            
            next_move = self.find_vcf(player, depth - 1)
            if next_move:
                self.board[r][c] = EMPTY
                return r, c
            
            self.board[r][c] = EMPTY
        
        return None
    
    def count_nearby(self, r, c, player, radius=2):
        count = 0
        for dr in range(-radius, radius + 1):
            for dc in range(-radius, radius + 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE:
                    if self.board[nr][nc] == player:
                        count += 1
        return count
    
    def find_best_move(self, player=BLACK):
        """找到最佳落子位置 - v21 进攻优先版
        
        决策顺序（确保"有四下四"）：
        1. 我能赢（五连）→ 直接下
        2. 对手要赢（五连）→ 必须堵
        3. VCF → 连续冲四获胜
        4. 我冲四 → 直接下（修复"有四不下四"bug）
        5. 对手冲四/活四 → 必须堵
        6. 双威胁 → 必胜
        7. 我活三 → 进攻
        8. 对手活三 → 防守
        9. 评估函数
        """
        center = BOARD_SIZE // 2
        stone_count = sum(1 for r in range(BOARD_SIZE) for c in range(BOARD_SIZE) if self.board[r][c] != EMPTY)
        
        # 开局第一步
        if stone_count == 0:
            return center, center
        
        # 第二步下附近
        if stone_count == 1:
            for r in range(BOARD_SIZE):
                for c in range(BOARD_SIZE):
                    if self.board[r][c] != EMPTY:
                        best, best_score = None, -1
                        for dr in range(-2, 3):
                            for dc in range(-2, 3):
                                nr, nc = r + dr, c + dc
                                if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE and self.board[nr][nc] == EMPTY:
                                    dist = abs(nr - center) + abs(nc - center)
                                    score = 100 - dist * 5
                                    if score > best_score:
                                        best_score = score
                                        best = nr, nc
                        if best:
                            return best
        
        opponent = WHITE if player == BLACK else BLACK
        
        # ===== 进攻优先决策 =====
        
        # 1. 我能赢（五连）→ 直接下
        my_threats = self.find_all_threats(player)
        for r, c, level in my_threats:
            if level >= THREAT_FIVE:
                return r, c
        
        # 2. 对手要赢（五连）→ 必须堵
        defense = self.find_defense_point(opponent)
        if defense:
            dr_pos, dc_pos, opp_level = defense
            if opp_level >= THREAT_FIVE:
                return dr_pos, dc_pos
        
        # 3. VCF 搜索
        vcf_move = self.find_vcf(player)
        if vcf_move:
            return vcf_move
        
        # 4. 我冲四 → 直接下（修复"有四不下四"bug）
        for r, c, level in my_threats:
            if level >= THREAT_RUSH_FOUR:
                return r, c
        
        # 5. 对手冲四/活四 → 必须堵
        if defense:
            dr_pos, dc_pos, opp_level = defense
            if opp_level >= THREAT_RUSH_FOUR:
                return dr_pos, dc_pos
        
        # 6. 双威胁检测
        double_threat = self.find_double_threat(player)
        if double_threat:
            return double_threat
        
        # 7. 我活三 → 进攻
        for r, c, level in my_threats:
            if level >= THREAT_LIVE_THREE:
                # 尝试扩展成冲四
                for dr, dc in [(0,1), (1,0), (1,1), (1,-1)]:
                    fr, fc = r + dr, c + dc
                    if 0 <= fr < BOARD_SIZE and 0 <= fc < BOARD_SIZE and self.board[fr][fc] == EMPTY:
                        if self.get_threat_level(fr, fc, player) >= THREAT_RUSH_FOUR:
                            return fr, fc
                    br, bc = r - dr, c - dc
                    if 0 <= br < BOARD_SIZE and 0 <= bc < BOARD_SIZE and self.board[br][bc] == EMPTY:
                        if self.get_threat_level(br, bc, player) >= THREAT_RUSH_FOUR:
                            return br, bc
                return r, c
        
        # 8. 对手活三 → 防守
        if defense:
            dr_pos, dc_pos, opp_level = defense
            if opp_level >= THREAT_LIVE_THREE:
                return dr_pos, dc_pos
        
        # 9. 评估函数
        return self.evaluate(player)
    
    def evaluate(self, player=BLACK):
        """评估函数 - 找最佳位置"""
        opponent = WHITE if player == BLACK else BLACK
        center = BOARD_SIZE // 2
        
        candidates = set()
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self.board[r][c] != EMPTY:
                    for dr in range(-3, 4):
                        for dc in range(-3, 4):
                            nr, nc = r + dr, c + dc
                            if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE and self.board[nr][nc] == EMPTY:
                                candidates.add((nr, nc))
        
        if not candidates:
            return center, center
        
        best_score = -float('inf')
        best_moves = []
        
        for r, c in candidates:
            my_level = self.get_threat_level(r, c, player)
            opp_level = self.get_threat_level(r, c, opponent)
            
            self.board[r][c] = player
            opp_next = self.find_all_threats(opponent)
            opp_next_max = opp_next[0][2] if opp_next else 0
            self.board[r][c] = EMPTY
            
            score = 0
            score += my_level
            score -= opp_next_max
            score -= opp_level
            score += self.count_nearby(r, c, player) * 3000
            score += self.count_nearby(r, c, opponent) * 2000
            dist = abs(r - center) + abs(c - center)
            score += max(0, 30000 - dist * 2000)
            
            if score > best_score:
                best_score = score
                best_moves = [(r, c)]
            elif score == best_score:
                best_moves.append((r, c))
        
        if best_moves:
            best_moves.sort(key=lambda x: abs(x[0]-center) + abs(x[1]-center))
            choice_count = min(3, len(best_moves))
            return random.choice(best_moves[:choice_count])
        return center, center
    
    def get_move_notation(self, row, col):
        """将0索引的(row, col)转换为棋谱记号"""
        if 0 <= col <= 14:
            cols = 'ABCDEFGHJKLMNOP'
            return f"{cols[col]}{row+1}"
        else:
            return f"?{row+1}"

def main():
    board_str = sys.stdin.read()
    if not board_str.strip():
        print("H8")
        return
    ai = GomokuAI(board_str)
    
    black_count = sum(1 for r in range(BOARD_SIZE) for c in range(BOARD_SIZE) if ai.board[r][c] == BLACK)
    white_count = sum(1 for r in range(BOARD_SIZE) for c in range(BOARD_SIZE) if ai.board[r][c] == WHITE)
    
    if black_count > white_count:
        player = WHITE
    else:
        player = BLACK
    
    row, col = ai.find_best_move(player)
    if row is None:
        print("PASS")
        return
    print(ai.get_move_notation(row, col))

if __name__ == "__main__":
    main()
