import re

path = '/root/.openclaw/workspace/tianqi-diting/public/shengting/index.html'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# New tooltip data: role_id -> (t-name, t-title, t-dept)
updates = {
    'off-emperor':     ('神帝陛下',       '统御万界·帝庭之主',     '🐉 帝庭之主'),
    'off-mingwang':    ('冥王帝尘',       '调度总管·统领全廷',     '⚫ 司礼监'),
    'off-neige':       ('内阁首辅',       '内阁总负责人·文官领袖',  '🏛 内阁'),
    'off-yizheng':     ('议政院大学士',   '内阁首席·决策之首',     '🏛 议政院'),
    'off-ducha':       ('都察院掌院',     '监察之首·廉政督查',     '🛡 都察院'),
    'off-hanlin':      ('翰林院大学士',   '学术之首·文化传承',     '📚 翰林院'),
    'off-neiting':     ('内廷掌印',       '内廷总负责人·机要领袖', '⚫ 内廷'),
    'off-jinwei':      ('锦衣卫指挥',     '安全之首·拱卫中枢',     '🛠 锦衣卫'),
    'off-tongzheng':   ('通政司通政使',   '外联之首·渠道开拓',     '📋 通政司'),
    'off-qintian':     ('钦天监监正',     '预研之首·战略洞察',     '🔥 钦天监'),
    'off-liubushangling': ('六部尚书令', '六部总负责人·执行领袖', '⚔ 六部'),
    'off-libu':        ('吏部尚书',       '管理之首·协调统筹',     '📜 吏部'),
    'off-hubu':        ('户部尚书',       '财务之首·资源管理',     '💰 户部'),
    'off-libub':       ('礼部尚书',       '营销之首·形象塑造',     '🎴 礼部'),
    'off-bingbu':      ('兵部尚书',       '开发之首·技术攻坚',     '⚔ 兵部'),
    'off-xingbu':      ('刑部尚书',       '法务之首·合规保障',     '⚖ 刑部'),
    'off-gongbu':      ('工部尚书',       '运维之首·稳定保障',     '🏗 工部'),
}

count = 0
for role_id, (t_name, t_title, t_dept) in updates.items():
    # Match the official div for this role_id
    # The tooltip-card div follows the canvas, pattern:
    # id="role_id"...<canvas...></canvas><div class="tooltip-card">...</div>
    # We need to replace just the tooltip-card content within this official div
    
    # Build the new tooltip-card HTML
    new_tooltip = f'<div class="tooltip-card"><div class="t-name">{t_name}</div><div class="t-title">{t_title}</div><div class="t-dept">{t_dept}</div></div>'
    
    # Use a regex to match the specific official div and its tooltip-card
    pattern = rf'(<div class="official" id="{re.escape(role_id)}"[^>]*>.*?<div class="tooltip-card">)[^<]*(?:<div class="t-name">[^<]*</div><div class="t-title">[^<]*</div><div class="t-dept">[^<]*</div>)(</div>)'
    
    # More targeted: replace the tooltip-card content inside the specific official div
    # Find the official div for this role, then replace its tooltip-card inner content
    official_pat = rf'(<div class="official" id="{re.escape(role_id)}".*?<div class="tooltip-card">)(.*?)(</div>\s*</div>)'
    
    def replacer(m):
        return m.group(1) + new_tooltip + m.group(3)
    
    new_content, n = re.subn(official_pat, replacer, content, flags=re.DOTALL)
    if n > 0:
        count += n
        content = new_content
    else:
        print(f"WARNING: no match for {role_id}")

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Updated {count} tooltip-cards")
