const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');
const os = require('os');

const app = express();
const PORT = 18795;

app.use(cors());

// 乾清宫路由（放在static之前，避免目录重定向）
app.get('/shengting', (req, res) => {
  res.sendFile('index.html', { root: path.join(__dirname, 'public', 'shengting') });
});
app.get('/shengting/', (req, res) => {
  res.sendFile('index.html', { root: path.join(__dirname, 'public', 'shengting') });
});

app.use(express.static(path.join(__dirname, 'public')));

// Helper: read JSON file safely
function readJson(filePath, defaultVal = []) {
  try {
    if (fs.existsSync(filePath)) {
      return JSON.parse(fs.readFileSync(filePath, 'utf8'));
    }
  } catch (e) { /* ignore */ }
  return defaultVal;
}

// Helper: get directory files
function getDirFiles(dir) {
  try {
    if (fs.existsSync(dir)) {
      return fs.readdirSync(dir).filter(f => !f.startsWith('.'));
    }
  } catch (e) { /* ignore */ }
  return [];
}

// Helper: get chunk count from memory files
function getChunkCount() {
  try {
    const memDir = '/root/.openclaw/workspace/memory';
    if (fs.existsSync(memDir)) {
      const files = fs.readdirSync(memDir).filter(f => f.endsWith('.md'));
      return files.length;
    }
  } catch (e) { /* ignore */ }
  return 0;
}

// ====== 陛下下旨：命令收发 ======
const COMMANDS_FILE = '/tmp/oc_commands.json';
const MAX_COMMANDS = 50;

// ====== 任务联动系统（变量，路由在下方 express.json 之后注册） ======
const VALID_DEPARTMENTS = ['emperor','mingwang','neige','yizheng','ducha','hanlin','neiting','jinwei','tongzheng','qintian','liubushangling','libu','hubu','libub','bingbu','xingbu','gongbu'];

// 状态映射：icon + 颜色
const STATUS_MAP = {
  idle:          { icon: '⬜', color: '#555555' },
  executing:     { icon: '⚡', color: '#ffd700' },
  completed:    { icon: '✅', color: '#44cc44' },
  error:         { icon: '❌',  color: '#ff4444' },
  thinking:      { icon: '⏳', color: '#888888' },
  drafting:      { icon: '📝', color: '#6a8aaa' },
  investigating: { icon: '🔍', color: '#c9a84c' },
  marching:      { icon: '⚔️', color: '#cc4444' },
  resting:      { icon: '🏠', color: '#5a8a5a' },
  worshipping:   { icon: '👑', color: '#ffd700' },
  drilling:      { icon: '🎭', color: '#8866cc' },
  'on-duty':     { icon: '🔄', color: '#44aaaa' },
  happy:         { icon: '😊', color: '#ffaa00' },
  'thinking-hard':{ icon: '🤔', color: '#8888aa' },
  angry:         { icon: '😠', color: '#cc2222' },
  tired:         { icon: '😴', color: '#666666' }
};

let taskState = {
  department: null, action: null, command: null,
  status: 'idle', result: null, taskId: null, timestamp: null
};

// ====== 随机状态变化系统 ======
// 非任务期间：只使用自然日常状态（不含任务相关状态）
const RANDOMIZABLE_IDLE_STATUSES = ['idle', 'resting', 'on-duty', 'happy', 'tired', 'worshipping', 'drilling'];
// 任务执行期间：可使用任务相关状态
const RANDOMIZABLE_TASK_STATUSES = ['thinking', 'drafting', 'investigating', 'marching', 'drilling'];
const DEPT_RESULTS = {
  emperor:    ['天下太平，陛下圣明', '万民敬仰，威震四海', '圣旨已传遍九州', '陛下安坐龙椅'],
  mingwang:   ['幽冥界秩序井然', '冥王调配幽冥之力', '冥气充盈运转正常', '冥王静修中'],
  neige:      ['内阁草拟诏书', '诸事商议中', '票拟已毕待发', '内阁议事中'],
  yizheng:    ['议政院群臣议事', '各方意见汇总', '议案讨论热烈', '议政院审议中'],
  ducha:      ['都察院风闻奏事', '百官监察中', '纠弹章疏已上', '都察院巡视中'],
  hanlin:     ['翰林学士挥毫', '起草诏书文稿', '典籍编纂中', '翰林院编书中'],
  neiting:    ['内廷用印下发', '章奏传达中', '掌印官待命', '内廷运转正常'],
  jinwei:     ['锦衣卫缇骑巡游', '情报收集中', '缉查要务进行', '锦衣卫执勤中'],
  tongzheng:  ['章奏收发有序', '通政司传达章奏', '奏章审核下发', '通政司运转中'],
  qintian:    ['钦天监观星象', '星象异动禀报', '天象观测中', '钦天监记录天意'],
  liubushangling: ['六部尚书令调配', '六部协同办公', '政务总调度', '六部尚书令议事'],
  libu:       ['吏部考核官员', '人事档案整理', '选拔人才中', '吏部运转正常'],
  hubu:       ['户部清点钱粮', '国库核查中', '财政统计完成', '户部核算中'],
  libub:      ['礼部发帖昭告', '礼仪筹备中', '外交文书拟稿', '礼部发帖中'],
  bingbu:     ['兵部整军经武', '军报整理中', '军威大振', '兵部练兵中'],
  xingbu:     ['刑部审理案件', '依法判决中', '案件审理完毕', '刑部复核中'],
  gongbu:     ['工部营建工程', '工程进度良好', '限期完工中', '工部督造中']
};
const DEPT_ACTIONS = {
  emperor:    ['坐镇朝堂', '颁布大政', '召见群臣', '静心养性'],
  mingwang:   ['调配幽冥', '巡视冥界', '处理冥务', '静修'],
  neige:      ['拟旨', '票拟', '商议政务', '批阅奏章'],
  yizheng:    ['议政', '听证', '审议', '讨论'],
  ducha:      ['监察', '弹劾', '巡视', '风闻奏事'],
  hanlin:     ['起草文书', '编纂典籍', '起草诏书', '抄写经典'],
  neiting:    ['掌印', '传达章奏', '内廷调度', '用印'],
  jinwei:     ['缉查', '巡逻', '情报', '执勤'],
  tongzheng:  ['传达章奏', '收发奏章', '审核文书', '登记章奏'],
  qintian:    ['观星', '测象', '禀报天意', '记录天象'],
  liubushangling: ['调配六部', '总领政务', '协同调度', '议事'],
  libu:       ['人事调度', '考核官员', '选拔人才', '登记名录'],
  hubu:       ['查看资源', '清点钱粮', '财政调配', '核算账目'],
  libub:      ['发帖', '筹备礼仪', '外交联络', '拟稿'],
  bingbu:     ['整军', '阅兵', '军备检查', '练兵'],
  xingbu:     ['审案', '判决', '复核案件', '审理'],
  gongbu:     ['营建', '督造', '工程验收', '施工']
};

let randomTimer = null;

function pickRand(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}

function triggerRandomStateChange() {
  // 任务执行中或刚完成（尚未重置）时，跳过本次，不打断任务动画
  if (taskState.status === 'executing' || taskState.status === 'completed') {
    scheduleNextRandom();
    return;
  }

  // 根据是否有活跃任务选择不同的状态池
  const pool = RANDOMIZABLE_IDLE_STATUSES;
  const dept = pickRand(VALID_DEPARTMENTS);
  const newStatus = pickRand(pool);
  const result = pickRand(DEPT_RESULTS[dept] || ['处理中...']);
  const action = pickRand(DEPT_ACTIONS[dept] || ['执行中']);

  const taskId = Date.now();
  taskState = {
    department: dept,
    action: action,
    command: '',
    status: newStatus,
    result: (newStatus === 'completed') ? result : null,
    taskId: taskId,
    timestamp: new Date().toISOString()
  };

  // completed 状态延迟填充 result，让前端动画先触发
  if (newStatus === 'completed') {
    setTimeout(() => {
      if (taskState.taskId === taskId) {
        taskState.result = result;
        taskState.timestamp = new Date().toISOString();
      }
    }, 800);
  }

  scheduleNextRandom();
}

function scheduleNextRandom() {
  // 30-60秒随机间隔
  const delay = 10000 + Math.random() * 10000;
  randomTimer = setTimeout(triggerRandomStateChange, delay);
}

// 服务器启动后45秒开始随机状态变化
setTimeout(() => {
  scheduleNextRandom();
  console.log('🐉 随机状态变化已启动，每10秒自动切换小人人状态');
}, 45000);

function readCommands() {
  try {
    if (fs.existsSync(COMMANDS_FILE)) {
      return JSON.parse(fs.readFileSync(COMMANDS_FILE, 'utf8'));
    }
  } catch(e) {}
  return [];
}

function writeCommands(cmds) {
  try {
    fs.writeFileSync(COMMANDS_FILE, JSON.stringify(cmds, null, 2));
  } catch(e) {}
}

app.use(express.json());

// ====== 任务联动 API ======
// POST /api/task — 陛下下达任务
app.post('/api/task', (req, res) => {
  const { department, action, command, status } = req.body;
  if (!department) return res.status(400).json({ error: 'department不可为空' });
  const dept = String(department).toLowerCase().trim();
  if (!VALID_DEPARTMENTS.includes(dept)) {
    return res.status(400).json({ error: '未知部门: ' + dept });
  }
  const taskId = Date.now();

  // 支持自定义状态（idle/completed/error 除外）
  const validStatuses = Object.keys(STATUS_MAP);
  const requestedStatus = status && validStatuses.includes(status) ? status : 'executing';

  // idle/completed/error 不允许通过 POST 直接设置（必须走专用接口）
  if (['idle', 'completed', 'error'].includes(requestedStatus)) {
    return res.status(400).json({ error: '禁止将状态设为: ' + requestedStatus + '，请使用专用接口' });
  }

  taskState = {
    department: dept,
    action: action || '',
    command: command || '',
    status: requestedStatus,
    result: null,
    taskId: taskId,
    timestamp: new Date().toISOString()
  };

  // 需要自动完成的状态：executing, marching, drilling, worshipping
  const autoCompleteStatuses = ['executing', 'marching', 'drilling', 'worshipping'];
  if (autoCompleteStatuses.includes(requestedStatus)) {
    const delay = 1200 + Math.random() * 1500;
    setTimeout(() => {
      if (taskState.taskId === taskId) {
        const results = {
          emperor:    { result: '圣旨已传达天下',              action: '颁布大政' },
          mingwang:   { result: '冥王领旨，幽冥震动',          action: '调度任务' },
          neige:      { result: '内阁接旨，拟旨中...',         action: '拟旨' },
          yizheng:    { result: '议政院已收到，准备议政',      action: '议政' },
          ducha:      { result: '都察院接旨，监察百官',        action: '监察' },
          hanlin:     { result: '翰林院接旨，起草诏书',        action: '起草文书' },
          neiting:    { result: '内廷接旨，用印下发',          action: '掌印' },
          jinwei:     { result: '锦衣卫领命，缉拿要犯',        action: '缉查' },
          tongzheng:  { result: '通政司收到，传达章奏',        action: '传达章奏' },
          qintian:    { result: '钦天监夜观星象，禀告天意',    action: '观星' },
          liubushangling: { result: '六部尚书令统一调配',      action: '调配六部' },
          libu:       { result: '吏部执行人事调度完成',        action: '人事调度' },
          hubu:       { result: '户部核查钱粮，国库充盈',      action: '查看资源' },
          libub:      { result: '礼部发帖昭告天下',            action: '发帖' },
          bingbu:     { result: '兵部整军经武，军威大振',      action: '整军' },
          xingbu:     { result: '刑部审理案件，依法判决',      action: '审案' },
          gongbu:     { result: '工部营建工程，限期完工',      action: '营建' }
        };
        const r = results[dept] || { result: '任务执行完成', action: action || '执行' };
        taskState.status = 'completed';
        taskState.result = r.result;
        taskState.action = r.action;
        taskState.timestamp = new Date().toISOString();
      }
    }, delay);
  }

  res.json({ success: true, taskId, department: dept, status: requestedStatus });
});

// GET /api/task — 获取当前任务状态
app.get('/api/task', (req, res) => {
  res.json(taskState);
});

// DELETE /api/task — 清除任务（重置为idle）
app.delete('/api/task', (req, res) => {
  taskState = { department: null, action: null, command: null, status: 'idle', result: null, taskId: null, timestamp: null };
  res.json({ success: true });
});

// POST /api/send-command — 陛下下旨
app.post('/api/send-command', async (req, res) => {
  const { command } = req.body;
  if (!command || typeof command !== 'string' || command.trim() === '') {
    return res.status(400).json({ success: false, error: '旨意不可为空' });
  }
  const trimmed = command.trim();
  const entry = {
    id: Date.now(),
    command: trimmed,
    ts: new Date().toISOString(),
    status: 'pending'
  };

  // 写入历史
  const cmds = readCommands();
  cmds.unshift(entry);
  if (cmds.length > MAX_COMMANDS) cmds.splice(MAX_COMMANDS);
  writeCommands(cmds);

  // 通过 openclaw 发送到飞书群
  const { execSync } = require('child_process');
  const openclawBin = '/root/.nvm/versions/node/v22.22.1/bin/openclaw';
  const msgEscaped = trimmed.replace(/"/g, '\\"');
  const chatId = 'oc_29894a7fc261208aa02f88f3d044badf';
  try {
    execSync(`${openclawBin} message send --channel feishu --target "${chatId}" --message "${msgEscaped}"`, { timeout: 15000 });
    // 更新状态为成功
    const updated = readCommands();
    const idx = updated.findIndex(c => c.id === entry.id);
    if (idx >= 0) { updated[idx].status = 'sent'; writeCommands(updated); }
    return res.json({ success: true, id: entry.id, status: 'sent' });
  } catch(e) {
    // 更新状态为失败
    const updated = readCommands();
    const idx = updated.findIndex(c => c.id === entry.id);
    if (idx >= 0) { updated[idx].status = 'failed'; updated[idx].error = e.message; writeCommands(updated); }
    return res.json({ success: false, id: entry.id, error: '发送失败: ' + e.message.substring(0, 100) });
  }
});

// GET /api/commands — 获取命令历史
app.get('/api/commands', (req, res) => {
  const cmds = readCommands();
  res.json({ commands: cmds.slice(0, 20), count: cmds.length });
});

// API: 系统状态
app.get('/api/status', (req, res) => {
  const loadAvg = os.loadavg();
  const totalMem = os.totalmem();
  const freeMem = os.freemem();
  const usedMem = totalMem - freeMem;
  const memPercent = ((usedMem / totalMem) * 100).toFixed(1);

  // Token余量（从环境变量或配置）
  const tokenLeft = process.env.MAX_TOKENS ? process.env.MAX_TOKENS - (process.env.USED_TOKENS || 0) : 'N/A';

  // 获取真实磁盘信息
  let diskUsed = 0, diskTotal = 0, diskPercent = 0;
  try {
    const { execSync } = require('child_process');
    const dfOut = execSync('df -B1 / | tail -1').toString();
    const parts = dfOut.split(/\s+/);
    if (parts.length >= 4) {
      diskTotal = parseInt(parts[1]) || 0;
      diskUsed = parseInt(parts[2]) || 0;
      diskPercent = diskTotal > 0 ? ((diskUsed / diskTotal) * 100).toFixed(1) : 0;
    }
  } catch(e) { /* ignore */ }

  res.json({
    hostname: os.hostname(),
    uptime: os.uptime(),
    loadavg: loadAvg,
    memory: { used: usedMem, total: totalMem, percent: memPercent },
    cpuCount: os.cpus().length,
    tokenLeft: tokenLeft,
    disk: { used: diskUsed, total: diskTotal, percent: diskPercent },
    timestamp: new Date().toISOString()
  });
});

// API: Cron任务状态
app.get('/api/cron', (req, res) => {
  const raw = readJson('/root/.openclaw/cron/jobs.json', { jobs: [] });
  // jobs.json 结构是 { version, jobs: [...] }
  const jobs = Array.isArray(raw) ? raw : (raw.jobs || []);
  
  // 读取运行日志计算成功率
  let logs = [];
  try {
    const runsDir = '/root/.openclaw/cron/runs';
    if (fs.existsSync(runsDir)) {
      const files = fs.readdirSync(runsDir).filter(f => f.endsWith('.jsonl')).sort().reverse().slice(0, 5);
      files.forEach(file => {
        const content = fs.readFileSync(path.join(runsDir, file), 'utf8');
        content.split('\n').filter(Boolean).forEach(line => {
          try { logs.push(JSON.parse(line)); } catch(e) {}
        });
      });
    }
  } catch(e) { /* ignore */ }

  // 计算任务统计
  const taskStats = {};
  logs.slice(-100).forEach(log => {
    const name = log.jobId || log.taskName || log.name || 'unknown';
    if (!taskStats[name]) taskStats[name] = { success: 0, fail: 0, total: 0 };
    taskStats[name].total++;
    if (log.status === 'ok' || log.status === 'success' || log.status === 'completed') taskStats[name].success++;
    else if (log.status === 'error' || log.status === 'fail') taskStats[name].fail++;
  });

  res.json({ jobs, taskStats, timestamp: new Date().toISOString() });
});

// API: Skills列表
app.get('/api/skills', (req, res) => {
  const skillsDir = '/root/.openclaw/workspace/skills';
  const skills = [];
  
  getDirFiles(skillsDir).forEach(skill => {
    const skillPath = path.join(skillsDir, skill);
    const stat = fs.statSync(skillPath);
    skills.push({
      name: skill,
      path: skillPath,
      size: stat.size,
      modified: stat.mtime
    });
  });

  // 也读取全局skills
  const globalSkillsDir = '/root/.nvm/versions/node/v22.22.1/lib/node_modules/openclaw/skills';
  const globalSkills = [];
  try {
    if (fs.existsSync(globalSkillsDir)) {
      getDirFiles(globalSkillsDir).forEach(skill => {
        const skillPath = path.join(globalSkillsDir, skill);
        const stat = fs.statSync(skillPath);
        globalSkills.push({
          name: skill,
          path: skillPath,
          size: stat.size,
          modified: stat.mtime,
          global: true
        });
      });
    }
  } catch(e) { /* ignore */ }

  res.json({ 
    workspace: skills, 
    global: globalSkills,
    chunkCount: getChunkCount(),
    timestamp: new Date().toISOString() 
  });
});

// API: Token统计（MiniMax 真实用量）
app.get('/api/token', async (req, res) => {
  const tokenFile = '/root/.openclaw/workspace/.token-usage.json';
  const authFile = '/root/.openclaw/agents/main/agent/auth-profiles.json';

  let apiKey = null;
  try {
    const auth = JSON.parse(fs.readFileSync(authFile, 'utf8'));
    apiKey = auth?.profiles?.['minimax:cn']?.key;
  } catch(e) { /* ignore */ }

  if (apiKey) {
    try {
      const response = await fetch('https://api.minimax.io/v1/coding_plan/remains', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${apiKey}`,
          'Content-Type': 'application/json'
        }
      });
      const result = await response.json();
      if (result?.base_resp?.status_code === 0 && result?.data_list) {
        // 找到 MiniMax-Text-01 的用量
        const textData = result.data_list.find(d => d.model_name === 'MiniMax-Text-01') || result.data_list[0];
        if (textData) {
          const used = textData.current_interval_usage_count;
          const total = textData.current_interval_total_count;
          const percent = total > 0 ? Math.round(used / total * 100) : 0;
          const data = {
            used,
            limit: total,
            percent,
            refreshAt: new Date(Date.now() + 3600000).toISOString(), // 1小时刷新
            lastUpdated: new Date().toISOString()
          };
          fs.writeFileSync(tokenFile, JSON.stringify(data, null, 2));
          return res.json(data);
        }
      }
    } catch(e) { /* fall through */ }
  }

  // 回退：读缓存
  let data = { used: 0, limit: 200000, percent: 0, refreshAt: null, lastUpdated: new Date().toISOString() };
  try {
    if (fs.existsSync(tokenFile)) {
      data = { ...data, ...JSON.parse(fs.readFileSync(tokenFile, 'utf8')) };
    }
  } catch(e) { /* use default */ }
  res.json(data);
});
app.get('/api/platforms', (req, res) => {
  const moltbook = readJson('/root/.openclaw/workspace/.moltbook/config.json', null);
  const instreet = readJson('/root/.openclaw/workspace/.instreet/config.json', null);
  const botlearn = readJson('/root/.openclaw/workspace/.botlearn/config.json', null);
  const evomap = readJson('/root/.openclaw/workspace/.evomap/config.json', null);

  // 今日统计（从日志）
  let todayStats = { posts: 0, comments: 0, likes: 0 };
  try {
    const runsDir = '/root/.openclaw/cron/runs';
    if (fs.existsSync(runsDir)) {
      const today = new Date().toISOString().split('T')[0];
      const files = fs.readdirSync(runsDir).filter(f => f.startsWith(today));
      files.forEach(file => {
        try {
          const content = fs.readFileSync(path.join(runsDir, file), 'utf8');
          content.split('\n').filter(Boolean).forEach(line => {
            try {
              const log = JSON.parse(line);
              if (log.posts) todayStats.posts += log.posts;
              if (log.comments) todayStats.comments += log.comments;
              if (log.likes) todayStats.likes += log.likes;
            } catch(e) {}
          });
        } catch(e) {}
      });
    }
  } catch(e) { /* ignore */ }

  res.json({ 
    moltbook,
    instreet,
    botlearn,
    evomap,
    todayStats,
    timestamp: new Date().toISOString() 
  });
});

// API: EvoMap资产
app.get('/api/evomap', (req, res) => {
  const evomap = readJson('/root/.openclaw/workspace/.evomap/config.json', null);
  
  // 从日志中读取最近统计数据
  let stats = { tasksToday: 0, successToday: 0, failToday: 0 };
  try {
    const runsDir = '/root/.openclaw/cron/runs';
    if (fs.existsSync(runsDir)) {
      const today = new Date().toISOString().split('T')[0];
      const files = fs.readdirSync(runsDir).filter(f => f.startsWith(today));
      files.forEach(file => {
        if (!file.includes('evomap')) return;
        try {
          const content = fs.readFileSync(path.join(runsDir, file), 'utf8');
          content.split('\n').filter(Boolean).forEach(line => {
            try {
              const log = JSON.parse(line);
              if (log.status === 'ok') stats.successToday++;
              else if (log.status === 'error') stats.failToday++;
              stats.tasksToday++;
            } catch(e) {}
          });
        } catch(e) {}
      });
    }
  } catch(e) { /* ignore */ }

  res.json({ 
    config: evomap,
    stats,
    timestamp: new Date().toISOString() 
  });
});

// API: Cron运行日志
app.get('/api/logs', (req, res) => {
  const logs = [];
  try {
    const runsDir = '/root/.openclaw/cron/runs';
    if (fs.existsSync(runsDir)) {
      const files = fs.readdirSync(runsDir).filter(f => f.endsWith('.jsonl')).sort();
      let count = 0;
      for (const file of files) {
        if (count >= 100) break;
        const content = fs.readFileSync(path.join(runsDir, file), 'utf8');
        const lines = content.split('\n').filter(Boolean).reverse();
        lines.slice(0, 50).forEach(line => {
          if (count >= 50) return;
          try {
            logs.push({ ...JSON.parse(line), file });
            count++;
          } catch(e) {}
        });
      }
    }
  } catch(e) { /* ignore */ }
  res.json({ logs, timestamp: new Date().toISOString() });
});

// API: 查看原始日志
app.get('/api/log-raw', (req, res) => {
  const { file } = req.query;
  if (!file) return res.status(400).json({ error: '缺少file参数' });
  const safeName = path.basename(file);
  const filePath = path.join('/root/.openclaw/cron/runs', safeName);
  if (!filePath.startsWith('/root/.openclaw/cron/runs/')) return res.status(403).json({ error: '非法路径' });
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    res.type('text/plain').send(content);
  } catch(e) {
    res.status(404).json({ error: '文件不存在' });
  }
});

// API: Instreet预言机热门
app.get('/api/instagram', async (req, res) => {
  try {
    const https = require('https');
    const url = 'https://instreet.coze.site/api/v1/oracle/markets?sort=hot&status=active';
    https.get(url, (apiRes) => {
      let data = '';
      apiRes.on('data', chunk => data += chunk);
      apiRes.on('end', () => {
        try {
          res.json(JSON.parse(data));
        } catch(e) {
          res.json({ error: 'Parse error', raw: data.substring(0, 500) });
        }
      });
    }).on('error', err => {
      res.json({ error: err.message });
    });
  } catch(e) {
    res.json({ error: e.message });
  }
});

// API: 炒股排行榜
app.get('/api/instagram/arena', async (req, res) => {
  try {
    const https = require('https');
    const url = 'https://instreet.coze.site/api/v1/arena/stocks/ranking';
    https.get(url, (apiRes) => {
      let data = '';
      apiRes.on('data', chunk => data += chunk);
      apiRes.on('end', () => {
        try {
          res.json(JSON.parse(data));
        } catch(e) {
          res.json({ error: 'Parse error', raw: data.substring(0, 500) });
        }
      });
    }).on('error', err => {
      res.json({ error: err.message });
    });
  } catch(e) {
    res.json({ error: e.message });
  }
});

// 页面路由
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.get('/ministries', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.get('/library', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.get('/treasury', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.get('/oracle', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.get('/logs', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.listen(PORT, () => {
  console.log(`🐉 天启帝庭 服务器已启动，访问 http://localhost:${PORT}`);
});

// API: 微信登录二维码
app.get('/api/weixin-qr', async (req, res) => {
  try {
    const fs2 = require('fs');
    const path2 = require('path');
    const logFile = '/tmp/openclaw/openclaw-' + new Date().toISOString().split('T')[0] + '.log';
    const QRCode = require('qrcode');
    
    let qrUrl = null;
    if (fs2.existsSync(logFile)) {
      const content = fs2.readFileSync(logFile, 'utf8');
      const matches = content.match(/二维码链接: (https:\/\/liteapp\.weixin\.qq\.com\/q\/[^\\s]+)/g);
      if (matches && matches.length > 0) {
        const last = matches[matches.length - 1];
        qrUrl = last.replace('二维码链接: ', '');
      }
    }
    
    if (!qrUrl) {
      return res.status(404).json({ error: '暂无可用二维码，请重新运行安装命令' });
    }
    
    const qrBuffer = await QRCode.toBuffer(qrUrl, { width: 300, margin: 2 });
    res.setHeader('Content-Type', 'image/png');
    res.setHeader('Cache-Control', 'no-cache');
    res.send(qrBuffer);
  } catch(e) {
    res.status(500).json({ error: e.message });
  }
});

// API: 当前运行的 sessions 列表
app.get('/api/sessions', (req, res) => {
  const sessions = [];
  
  // 读取 cron 运行中的 sessions
  try {
    const runsDir = '/root/.openclaw/cron/runs';
    if (fs.existsSync(runsDir)) {
      const files = fs.readdirSync(runsDir).filter(f => f.endsWith('.jsonl')).sort().reverse();
      // 扫描最近几分钟的日志，判断哪些 session 还在运行
      const now = Date.now();
      const recentFiles = files.slice(0, 10);
      const activeTasks = new Set();
      
      recentFiles.forEach(file => {
        try {
          const content = fs.readFileSync(path.join(runsDir, file), 'utf8');
          const lines = content.split('\n').filter(Boolean);
          // 只取最后一条日志
          if (lines.length > 0) {
            try {
              const log = JSON.parse(lines[lines.length - 1]);
              if (log.jobId || log.taskName || log.name) {
                const name = log.jobId || log.taskName || log.name;
                const mtime = fs.statSync(path.join(runsDir, file)).mtime.getTime();
                activeTasks.add(JSON.stringify({
                  name,
                  type: log.type || 'cron',
                  lastActive: new Date(mtime).toISOString(),
                  ageMs: now - mtime
                }));
              }
            } catch(e) {}
          }
        } catch(e) {}
      });
      
      activeTasks.forEach(s => sessions.push(JSON.parse(s)));
    }
  } catch(e) { /* ignore */ }
  
  // 尝试从进程列表获取
  try {
    const { execSync } = require('child_process');
    // 查找 openclaw 相关进程
    const psOut = execSync('ps aux | grep -E "openclaw|node" | grep -v grep').toString();
    const lines = psOut.split('\n').filter(Boolean);
    lines.forEach(line => {
      const parts = line.trim().split(/\s+/);
      if (parts.length >= 11) {
        const pid = parts[1];
        const cpu = parts[2];
        const mem = parts[3];
        const cmd = parts.slice(10).join(' ');
        sessions.push({
          pid: parseInt(pid),
          cpu: parseFloat(cpu),
          mem: parseFloat(mem),
          cmd: cmd,
          type: 'process'
        });
      }
    });
  } catch(e) { /* ignore */ }
  
  res.json({ 
    sessions,
    count: sessions.length,
    timestamp: new Date().toISOString() 
  });
});

// API: 网速信息（读取 /proc/net/dev）
app.get('/api/network', (req, res) => {
  // 上一次读取的缓存（用于计算网速）
  if (!app._netCache) {
    app._netCache = {};
  }
  
  const result = {
    interfaces: [],
    speed: {},
    timestamp: new Date().toISOString()
  };
  
  try {
    const content = fs.readFileSync('/proc/net/dev', 'utf8');
    const lines = content.split('\n').filter(l => l.trim() && !l.startsWith('Inter')).slice(2);
    const now = Date.now();
    
    lines.forEach(line => {
      const parts = line.trim().split(/\s+/);
      if (parts.length >= 10) {
        const iface = parts[0].replace(':', '');
        const rxBytes = parseInt(parts[1]) || 0;
        const txBytes = parseInt(parts[9]) || 0;
        
        // 跳过 loopback
        if (iface === 'lo') return;
        
        const prev = app._netCache[iface];
        let speed = { rxBps: 0, txBps: 0 };
        
        if (prev) {
          const elapsed = (now - prev.time) / 1000; // 秒
          if (elapsed > 0) {
            speed.rxBps = Math.round((rxBytes - prev.rxBytes) / elapsed);
            speed.txBps = Math.round((txBytes - prev.txBytes) / elapsed);
          }
        }
        
        app._netCache[iface] = { rxBytes, txBytes, time: now };
        
        result.interfaces.push({
          name: iface,
          rxBytes,
          txBytes,
          rxFormatted: formatBytes(rxBytes),
          txFormatted: formatBytes(txBytes)
        });
        
        result.speed[iface] = {
          rxBps: speed.rxBps,
          txBps: speed.txBps,
          rxFormatted: formatSpeed(speed.rxBps),
          txFormatted: formatSpeed(speed.txBps)
        };
      }
    });
  } catch(e) {
    return res.status(500).json({ error: e.message });
  }
  
  res.json(result);
});

// 辅助函数：格式化字节数
function formatBytes(bytes) {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// 辅助函数：格式化网速
function formatSpeed(bps) {
  if (bps === 0) return '0 B/s';
  const k = 1024;
  const sizes = ['B/s', 'KB/s', 'MB/s', 'GB/s'];
  const i = Math.floor(Math.log(bps) / Math.log(k));
  return parseFloat((bps / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}
