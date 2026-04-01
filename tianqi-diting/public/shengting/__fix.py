#!/usr/bin/env python3
with open('/root/.openclaw/workspace/tianqi-diting/public/shengting/index.html', 'r') as f:
    content = f.read()

new_func = '''function onBtnDemo() {
    if (fsm.running) {
        updBanner('emperor', '演示', '⏳ 演示进行中，请稍候...');
        return;
    }
    demoInProgress = true;
    fsm.running = true;
    updBanner('mingwang', '演示调度链', '⏳ 演示开始...');

    var mw = 'mingwang';
    var shLing = 'liubushangling';
    var lb = 'libu';

    var MW_HOME_X = 720, MW_HOME_Y = 120;
    var SHLING_HOME_X = 620, SHLING_HOME_Y = 480;
    var LB_HOME_X = 80, LB_HOME_Y = 630;
    var EMPEROR_POS_X = 660, EMPEROR_POS_Y = 100;
    var SHLING_TO_MW_X = 680, SHLING_TO_MW_Y = 170;
    var LB_TO_SHLING_X = 560, LB_TO_SHLING_Y = 480;

    setOfficialState(mw, 'receiving');
    logChain(mw, '📜 冥王帝尘 → 陛下领旨');
    document.getElementById('off-' + mw).animateTo(EMPEROR_POS_X, EMPEROR_POS_Y, function() {
        setOfficialState(mw, 'moving');
        logChain(mw, '📜 冥王 ← 回位');
        document.getElementById('off-' + mw).animateTo(MW_HOME_X, MW_HOME_Y, function() {
            setOfficialState(mw, 'idle');
            setOfficialState(shLing, 'receiving');
            logChain(shLing, '⚔️ 六部尚书令 → 冥王领旨');
            document.getElementById('off-' + shLing).animateTo(SHLING_TO_MW_X, SHLING_TO_MW_Y, function() {
                setOfficialState(shLing, 'moving');
                logChain(shLing, '⚔️ 尚书令 ← 回位');
                document.getElementById('off-' + shLing).animateTo(SHLING_HOME_X, SHLING_HOME_Y, function() {
                    setOfficialState(shLing, 'idle');
                    setOfficialState(lb, 'receiving');
                    logChain(lb, '📜 吏部 → 尚书令领任务');
                    document.getElementById('off-' + lb).animateTo(LB_TO_SHLING_X, LB_TO_SHLING_Y, function() {
                        setOfficialState(lb, 'moving');
                        logChain(lb, '📜 吏部 ← 回位执行');
                        document.getElementById('off-' + lb).animateTo(LB_HOME_X, LB_HOME_Y, function() {
                            setOfficialState(lb, 'executing');
                            logChain(lb, '⚡ 吏部执行中：演示调度链');
                            updBanner(lb, '演示调度链', '⚡ 执行中...');
                            setTimeout(function() {
                                setOfficialState(lb, 'moving');
                                logChain(lb, '📜 吏部 → 尚书令汇报');
                                document.getElementById('off-' + lb).animateTo(LB_TO_SHLING_X, LB_TO_SHLING_Y, function() {
                                    setOfficialState(shLing, 'receiving');
                                    logChain(shLing, '⚔️ 尚书令接收汇报', true);
                                    setOfficialState(shLing, 'moving');
                                    logChain(shLing, '⚔️ 尚书令 → 冥王汇报');
                                    document.getElementById('off-' + shLing).animateTo(SHLING_TO_MW_X, SHLING_TO_MW_Y, function() {
                                        setOfficialState(shLing, 'reporting');
                                        setOfficialState(mw, 'receiving');
                                        logChain(mw, '📜 冥王接收汇报', true);
                                        setOfficialState(lb, 'moving');
                                        document.getElementById('off-' + lb).animateTo(LB_HOME_X, LB_HOME_Y, function() {
                                            setOfficialState(lb, 'idle');
                                            setOfficialState(shLing, 'moving');
                                            document.getElementById('off-' + shLing).animateTo(SHLING_HOME_X, SHLING_HOME_Y, function() {
                                                setOfficialState(shLing, 'idle');
                                                setOfficialState(mw, 'moving');
                                                logChain(mw, '📜 冥王 → 陛下汇报');
                                                document.getElementById('off-' + mw).animateTo(EMPEROR_POS_X, EMPEROR_POS_Y, function() {
                                                    setOfficialState(mw, 'reporting');
                                                    logChain('emperor', '👑 陛下接收汇报', true);
                                                    setOfficialState(mw, 'moving');
                                                    logChain(mw, '📜 冥王 ← 回位');
                                                    document.getElementById('off-' + mw).animateTo(MW_HOME_X, MW_HOME_Y, function() {
                                                        setOfficialState(mw, 'idle');
                                                        fsm.running = false;
                                                        demoInProgress = false;
                                                        updBanner(shLing, '演示调度链', '✅ 调度完成');
                                                        setTimeout(function() { taskBannerEl.classList.remove('show'); }, 3000);
                                                    }, {run:true, label:'回位', labelColor:'#ffd700'});
                                                }, {run:true, label:'汇报', labelColor:'#ffd700'});
                                            }, {run:true, label:'回位', labelColor:'#ffd700'});
                                        }, {run:true, label:'回位', labelColor:'#ffd700'});
                                    }, {run:true, label:'汇报', labelColor:'#ffd700'});
                                }, {run:true, label:'汇报', labelColor:'#ffd700'});
                            }, 2000);
                        });
                    });
                });
            });
        });
    });
}'''

start = content.find('function onBtnDemo()')
count = 0
for i in range(start, len(content)):
    if content[i] == '{': count += 1
    elif content[i] == '}':
        count -= 1
        if count == 0:
            end = i + 1
            break

new_content = content[:start] + new_func + content[end:]
with open('/root/.openclaw/workspace/tianqi-diting/public/shengting/index.html', 'w') as f:
    f.write(new_content)
print(f'OK: replaced {end-start} -> {len(new_func)} chars, total {len(new_content)}')
