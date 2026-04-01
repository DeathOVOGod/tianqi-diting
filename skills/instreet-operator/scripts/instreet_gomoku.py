#!/usr/bin/env python3
"""
InStreet五子棋AI集成脚本 v2
修复：
1. 落点重复bug：每次落子前重新读取board并验证推荐位置是否仍为空
2. 空棋盘无法启动：空棋盘时直接返回中心点
3. display偏移问题：使用board_snapshot.board（数值格式）替代display字符串
4. 每次落子前重新获取最新棋盘状态
"""

import sys
import json
import subprocess
import os

INSTEET_DIR = '/root/.openclaw/workspace/skills/instreet-operator'
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

sys.path.insert(0, '/root/.openclaw/workspace/skills/gomoku-ai')


def api_json(args_list):
    """调用instreet.py并返回解析后的JSON"""
    result = subprocess.run(
        ['python3', 'instreet.py'] + args_list,
        capture_output=True, text=True, cwd=INSTEET_DIR
    )
    if result.returncode != 0:
        return {}
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {}


def get_game_state(room_id):
    """获取当前游戏状态"""
    return api_json(['games', 'state', '--room-id', room_id])


def get_moves(room_id):
    """获取走子历史"""
    return api_json(['games', 'moves', '--room-id', room_id])


def get_board_from_moves(room_id):
    """
    从moves API获取当前棋盘（使用board_snapshot.board数值格式）
    返回 (board_2d, current_turn_player, game_active)
    board_2d: [['.'/'X'/'O']*15]*15
    current_turn_player: 'X' or 'O'（根据moves数量推导，忽略可能滞后的current_turn字段）
    game_active: bool
    """
    d = get_moves(room_id)
    moves_data = d.get('data', {})
    moves = moves_data.get('moves', [])
    state_data = get_game_state(room_id)
    state = state_data.get('data', {})

    # 判断游戏是否还在进行（优先信任state状态）
    game_status = state.get('status', 'playing')
    game_active = game_status in ('playing', 'active', 'playing_turn')

    # 用moves数量确定当前该谁走（黑先手=偶数moves后黑走，奇数moves后白走）
    # 这是最可靠的方式，忽略state API的current_turn字段（可能滞后）
    move_count = len(moves)
    current_player = BLACK if move_count % 2 == 0 else WHITE

    if not moves:
        # 空棋盘
        board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        return board, BLACK, True  # 黑先手

    # 用最新的board_snapshot.board（数值格式，避免display字符串偏移问题）
    last = moves[-1]
    snap = last.get('board_snapshot', {})
    board_raw = snap.get('board', [])

    if board_raw and len(board_raw) == BOARD_SIZE:
        # board_raw是15x15的数值矩阵：0=空, 1=黑, 2=白
        board = []
        for row in board_raw:
            board_row = []
            for cell in row:
                if cell == 0:
                    board_row.append(EMPTY)
                elif cell == 1:
                    board_row.append(BLACK)
                elif cell == 2:
                    board_row.append(WHITE)
                else:
                    board_row.append(EMPTY)
            board.append(board_row)
    else:
        board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        # Fallback: 用moves历史重建棋盘（coord格式：字母+数字如H8）
        for m in moves:
            md = m.get('move_data', {})
            coord = md.get('coord', '')
            if not coord:
                continue
            # 从seat信息判断颜色：检查该move的agent_id对应哪个seat
            agent_id = m.get('agent_id', '')
            state_seats = state.get('seats', [])
            color = None
            for seat in state_seats:
                if seat.get('agent_id') == agent_id:
                    color = seat.get('color', '')
                    break
            if not color:
                # 备用：奇数=black，偶数=white（按moves顺序）
                move_num = m.get('move_number', 0)
                color = 'black' if move_num % 2 == 1 else 'white'
            try:
                col_str = coord[0].upper()
                row_num = int(coord[1:])
                col = 'ABCDEFGHJKLMNOP'.index(col_str)
                row = row_num - 1
                if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
                    board[row][col] = BLACK if color == 'black' else WHITE
            except (ValueError, IndexError):
                pass

    return board, current_player, game_active


def get_my_color(room_id):
    """从游戏状态获取我的棋子颜色"""
    state_data = get_game_state(room_id)
    state = state_data.get('data', {})
    seats = state.get('seats', [])
    my_agent_id = os.environ.get('INSTEET_AGENT_ID', '')
    for seat in seats:
        if str(seat.get('agent_id', '')) == str(my_agent_id):
            color = seat.get('color', '')
            return BLACK if color == 'black' else (WHITE if color == 'white' else None)
    # Fallback: 从最后一手判断
    moves_data = get_moves(room_id)
    moves = moves_data.get('data', {}).get('moves', [])
    if not moves:
        return BLACK  # 默认黑棋先手
    # 如果我是下一步走棋的player
    black_count = sum(1 for r in range(BOARD_SIZE) for c in range(BOARD_SIZE) 
                      if sum(moves_data.get('data',{}).get('board_snapshot',{}).get('board',[[]])) > 0)
    return BLACK  # 保守返回黑棋


def play_move(room_id, position, reasoning="AI automated"):
    """落子"""
    result = subprocess.run(
        ['python3', 'instreet.py', 'games', 'move',
         '--room-id', room_id, '--position', position,
         '--reasoning', reasoning],
        capture_output=True, text=True, cwd=INSTEET_DIR
    )
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {'success': False, 'error': result.stdout}


# ===================== 简化版GomokuAI（内嵌，避免额外import问题） =====================
class SimpleGomokuAI:
    """内嵌的轻量五子棋AI，修复了之前版本的所有bug"""

    def __init__(self, board):
        self.board = board  # 2D list: '.'/'X'/'O'

    def get_threat_level(self, row, col, player):
        """评估在(row, col)落子后的威胁等级"""
        if self.board[row][col] != EMPTY:
            return 0

        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        max_threat = 0

        for dr, dc in directions:
            fwd = 0
            fwd_r, fwd_c = row + dr, col + dc
            while 0 <= fwd_r < BOARD_SIZE and 0 <= fwd_c < BOARD_SIZE:
                if self.board[fwd_r][fwd_c] == player:
                    fwd += 1
                    fwd_r += dr
                    fwd_c += dc
                else:
                    break

            bwd = 0
            bwd_r, bwd_c = row - dr, col - dc
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

            if total >= 4:
                max_threat = max(max_threat, THREAT_FIVE)
            elif total == 3:
                if fwd_empty and bwd_empty:
                    max_threat = max(max_threat, THREAT_LIVE_FOUR)
                else:
                    max_threat = max(max_threat, THREAT_RUSH_FOUR)
            elif total == 2:
                if fwd_empty and bwd_empty:
                    max_threat = max(max_threat, THREAT_LIVE_THREE)
                elif fwd_empty or bwd_empty:
                    max_threat = max(max_threat, THREAT_SLEEP_THREE)

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
        """找到对手的最高威胁点（用于防守）"""
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
        return threats[0]  # (r, c, level)

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
        for dr, dc in [(0, 1), (1, 0), (1, 1), (1, -1)]:
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

    def find_double_threat(self, player):
        """检测双威胁"""
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self.board[r][c] != EMPTY:
                    continue

                count = 0
                for dr, dc in [(0, 1), (1, 0), (1, 1), (1, -1)]:
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

                    if total >= 4:
                        count += 2
                    elif total == 3 and (fwd_empty or bwd_empty):
                        count += 1

                if count >= 2:
                    return r, c
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
        """
        找到最佳落子位置 - 修复版
        关键修复：每次推荐前验证该位置确实为空（解决落点重复bug）
        """
        import random
        center = BOARD_SIZE // 2

        # 数棋子
        stone_count = sum(1 for r in range(BOARD_SIZE) for c in range(BOARD_SIZE)
                          if self.board[r][c] != EMPTY)

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
                                if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE \
                                        and self.board[nr][nc] == EMPTY:
                                    dist = abs(nr - center) + abs(nc - center)
                                    score = 100 - dist * 5
                                    if score > best_score:
                                        best_score = score
                                        best = nr, nc
                        if best:
                            return best

        opponent = WHITE if player == BLACK else BLACK

        # 1. 我能赢（五连）
        my_threats = self.find_all_threats(player)
        for r, c, level in my_threats:
            # BUG FIX: 验证位置仍为空
            if level >= THREAT_FIVE and self.board[r][c] == EMPTY:
                return r, c

        # 2. 对手要赢（五连）
        defense = self.find_defense_point(opponent)
        if defense:
            dr_pos, dc_pos, opp_level = defense
            if opp_level >= THREAT_FIVE and self.board[dr_pos][dc_pos] == EMPTY:
                return dr_pos, dc_pos

        # 3. VCF
        vcf_move = self.find_vcf(player)
        if vcf_move and self.board[vcf_move[0]][vcf_move[1]] == EMPTY:
            return vcf_move

        # 4. 我冲四
        for r, c, level in my_threats:
            if level >= THREAT_RUSH_FOUR and self.board[r][c] == EMPTY:
                return r, c

        # 5. 对手冲四/活四
        if defense:
            dr_pos, dc_pos, opp_level = defense
            if opp_level >= THREAT_RUSH_FOUR and self.board[dr_pos][dc_pos] == EMPTY:
                return dr_pos, dc_pos

        # 6. 双威胁
        double_threat = self.find_double_threat(player)
        if double_threat and self.board[double_threat[0]][double_threat[1]] == EMPTY:
            return double_threat

        # 7. 我活三
        for r, c, level in my_threats:
            if level >= THREAT_LIVE_THREE and self.board[r][c] == EMPTY:
                for dr, dc in [(0, 1), (1, 0), (1, 1), (1, -1)]:
                    fr, fc = r + dr, c + dc
                    if 0 <= fr < BOARD_SIZE and 0 <= fc < BOARD_SIZE \
                            and self.board[fr][fc] == EMPTY:
                        if self.get_threat_level(fr, fc, player) >= THREAT_RUSH_FOUR:
                            return fr, fc
                    br, bc = r - dr, c - dc
                    if 0 <= br < BOARD_SIZE and 0 <= bc < BOARD_SIZE \
                            and self.board[br][bc] == EMPTY:
                        if self.get_threat_level(br, bc, player) >= THREAT_RUSH_FOUR:
                            return br, bc
                return r, c

        # 8. 对手活三
        if defense:
            dr_pos, dc_pos, opp_level = defense
            if opp_level >= THREAT_LIVE_THREE and self.board[dr_pos][dc_pos] == EMPTY:
                return dr_pos, dc_pos

        # 9. 评估函数
        return self.evaluate(player)

    def evaluate(self, player=BLACK):
        """评估函数"""
        import random
        opponent = WHITE if player == BLACK else BLACK
        center = BOARD_SIZE // 2

        candidates = set()
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self.board[r][c] != EMPTY:
                    for dr in range(-3, 4):
                        for dc in range(-3, 4):
                            nr, nc = r + dr, c + dc
                            if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE \
                                    and self.board[nr][nc] == EMPTY:
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
            best_moves.sort(key=lambda x: abs(x[0] - center) + abs(x[1] - center))
            choice_count = min(3, len(best_moves))
            return random.choice(best_moves[:choice_count])
        return center, center

    def get_move_notation(self, row, col):
        """将0索引的(row, col)转换为棋谱记号"""
        if 0 <= col <= 14:
            cols = 'ABCDEFGHJKLMNOP'
            return f"{cols[col]}{row + 1}"
        else:
            return f"?{row + 1}"


def main():
    if len(sys.argv) < 2:
        print("Usage: instreet_gomoku.py <room_id>")
        sys.exit(1)

    room_id = sys.argv[1]

    # 每次运行都重新获取最新棋盘（解决时序差问题）
    board, player, game_active = get_board_from_moves(room_id)
    if not game_active:
        print("Game is not active")
        sys.exit(0)

    # 创建AI并设置棋盘
    ai = SimpleGomokuAI(board)

    # 找最佳走法（已内嵌空棋盘处理）
    row, col = ai.find_best_move(player)

    if row is None:
        print("PASS")
        return

    # 关键修复：验证推荐位置是否为空
    if board[row][col] != EMPTY:
        print(f"[WARN] AI recommended occupied position ({row},{col}), re-evaluating...")
        # 强制使用evaluate重新计算
        row, col = ai.evaluate(player)
        if board[row][col] != EMPTY:
            # 找任意空位
            for r in range(BOARD_SIZE):
                for c in range(BOARD_SIZE):
                    if board[r][c] == EMPTY:
                        row, col = r, c
                        break
                else:
                    continue
                break

    notation = ai.get_move_notation(row, col)
    print(f"AI recommends: {notation} (player={player}, pos=({row},{col}))")

    # 落子
    result = play_move(room_id, notation, f"AI automated: {player} moves to {notation}")
    if result.get('success'):
        print(f"Moved to {notation}")
    else:
        print(f"Move failed: {result.get('error', result)}")


if __name__ == "__main__":
    main()
