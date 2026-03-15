#!/usr/bin/env node
/**
 * Capability Evolver - 自我进化引擎
 * 
 * 用法:
 *   node index.js           # 标准运行
 *   node index.js --review  # 审查模式(输出建议不执行)
 *   node index.js --loop    # 持续循环模式
 * 
 * 环境变量:
 *   EVOLVE_ALLOW_SELF_MODIFY - 是否允许自动修改文件 (default: false)
 *   EVOLVE_LOAD_MAX          - 最大负载阈值 (default: 2.0)
 *   EVOLVE_STRATEGY          - 进化策略 (default: balanced)
 */

const fs = require('fs');
const path = require('path');
const os = require('os');

const WORKSPACE = path.join(os.homedir(), '.openclaw', 'workspace');
const MEMORY_DIR = path.join(WORKSPACE, 'memory');
const EVOLVER_LOG = path.join(MEMORY_DIR, 'evolver-log.md');

const config = {
  allowSelfModify: process.env.EVOLVE_ALLOW_SELF_MODIFY === 'true',
  loadMax: parseFloat(process.env.EVOLVE_LOAD_MAX || '2.0'),
  strategy: process.env.EVOLVE_STRATEGY || 'balanced',
  review: process.argv.includes('--review'),
  loop: process.argv.includes('--loop'),
  loopIntervalMs: 3600000, // 1 hour
};

function log(msg) {
  const ts = new Date().toISOString();
  console.log(`[${ts}] ${msg}`);
}

function checkLoad() {
  const load = os.loadavg()[0];
  if (load > config.loadMax) {
    log(`⏸ 系统负载 ${load.toFixed(2)} > ${config.loadMax}, 退避等待`);
    return false;
  }
  return true;
}

function getRecentMemoryFiles(days = 7) {
  if (!fs.existsSync(MEMORY_DIR)) return [];
  
  const now = new Date();
  const files = [];
  
  for (let i = 0; i < days; i++) {
    const d = new Date(now);
    d.setDate(d.getDate() - i);
    const fname = `${d.toISOString().split('T')[0]}.md`;
    const fpath = path.join(MEMORY_DIR, fname);
    if (fs.existsSync(fpath)) {
      files.push({ path: fpath, name: fname, date: d });
    }
  }
  return files;
}

function isNegatedLine(line) {
  return /(?:不是|并非|非|无需|未|没有|无|不属于|不等于|暂不|暂无|不足以|更像|而不是)/i.test(line);
}

function analyzeErrors(content) {
  const patterns = {
    toolFailure: /(?:\b(?:error|failed|failure|exception)\b|失败|错误|异常)/gi,
    permission: /(?:\b(?:permission|denied|unauthorized|forbidden)\b|权限)/gi,
    timeout: /(?:\btimeout\b|超时|timed?\s*out|SIGTERM)/gi,
    crash: /(?:\bcrash\b|崩溃|\bpanic\b|segfault|\bOOM\b)/gi,
  };

  const findings = [];
  const lines = content.split(/\r?\n/);

  for (const [category, regex] of Object.entries(patterns)) {
    const matchedLines = [];

    for (const rawLine of lines) {
      const line = rawLine.trim();
      if (!line) continue;
      if (isNegatedLine(line)) continue;

      const matches = line.match(regex);
      if (matches && matches.length > 0) {
        matchedLines.push({ line, matches });
      }
    }

    if (matchedLines.length > 0) {
      const normalizedLines = [...new Set(matchedLines.map(item => item.line.toLowerCase()))];
      const samples = [...new Set(matchedLines.flatMap(item => item.matches.map(m => m.toLowerCase())))].slice(0, 3);
      findings.push({
        category,
        count: normalizedLines.length,
        samples,
      });
    }
  }
  return findings;
}

function identifyPatterns(files) {
  const allFindings = [];
  
  for (const file of files) {
    const content = fs.readFileSync(file.path, 'utf-8');
    const errors = analyzeErrors(content);
    if (errors.length > 0) {
      allFindings.push({ file: file.name, errors });
    }
  }
  return allFindings;
}

function generateRecommendations(findings, strategy) {
  const recommendations = [];

  const errorCounts = {};
  for (const f of findings) {
    for (const e of f.errors) {
      errorCounts[e.category] = (errorCounts[e.category] || 0) + e.count;
    }
  }

  // Strategy-based recommendations
  if (strategy === 'repair-only' || strategy === 'balanced') {
    if (errorCounts.toolFailure >= 3) {
      recommendations.push({
        priority: 'high',
        type: 'repair',
        desc: `工具调用失败出现${errorCounts.toolFailure}次,需检查工具配置、输入格式和权限`,
      });
    }
    if (errorCounts.permission >= 1) {
      recommendations.push({
        priority: 'high',
        type: 'repair',
        desc: `权限问题出现${errorCounts.permission}次,需更新权限或记录到TOOLS.md`,
      });
    }
    if (errorCounts.timeout >= 2) {
      recommendations.push({
        priority: 'medium',
        type: 'repair',
        desc: `超时/中断问题出现${errorCounts.timeout}次,需优化超时配置或执行通道`,
      });
    }
  }

  if (strategy === 'harden' || strategy === 'balanced') {
    if (errorCounts.crash >= 2) {
      recommendations.push({
        priority: 'critical',
        type: 'harden',
        desc: `崩溃事件出现${errorCounts.crash}次,需立即排查`,
      });
    }
  }

  if (strategy === 'innovate' || strategy === 'balanced') {
    if (findings.length === 0) {
      recommendations.push({
        priority: 'low',
        type: 'innovate',
        desc: '近期无错误,可尝试优化现有流程或探索新工具',
      });
    }
  }

  return recommendations;
}

function writeLog(findings, recommendations) {
  const date = new Date().toISOString().split('T')[0];
  const time = new Date().toISOString();
  
  let entry = `\n## ${date} 进化记录 (${time})\n\n`;
  entry += `**策略**: ${config.strategy}\n\n`;
  
  entry += `### 发现\n`;
  if (findings.length === 0) {
    entry += `- 近7天无异常模式\n`;
  } else {
    for (const f of findings) {
      for (const e of f.errors) {
        entry += `- [${f.file}] ${e.category}: ${e.count}次 (${e.samples.join(', ')})\n`;
      }
    }
  }
  
  entry += `\n### 建议\n`;
  if (recommendations.length === 0) {
    entry += `- 系统运行正常,无需改进\n`;
  } else {
    for (const r of recommendations) {
      entry += `- [${r.priority}/${r.type}] ${r.desc}\n`;
    }
  }
  
  entry += `\n---\n`;

  if (!config.review) {
    if (!fs.existsSync(MEMORY_DIR)) {
      fs.mkdirSync(MEMORY_DIR, { recursive: true });
    }
    
    let existing = '';
    if (fs.existsSync(EVOLVER_LOG)) {
      existing = fs.readFileSync(EVOLVER_LOG, 'utf-8');
    } else {
      existing = '# Evolver Log - 自我进化记录\n';
    }
    
    fs.writeFileSync(EVOLVER_LOG, existing + entry);
    log(`📝 进化日志已写入 ${EVOLVER_LOG}`);
  }
  
  return entry;
}

async function evolve() {
  log(`🧬 开始进化分析 (策略: ${config.strategy}, 模式: ${config.review ? '审查' : '执行'})`);
  
  if (!checkLoad()) return;

  // 1. Scan recent memory files
  const files = getRecentMemoryFiles(7);
  log(`📂 发现 ${files.length} 个近期memory文件`);

  // 2. Analyze patterns
  const findings = identifyPatterns(files);
  log(`🔍 发现 ${findings.length} 个文件包含异常模式`);

  // 3. Generate recommendations
  const recommendations = generateRecommendations(findings, config.strategy);
  log(`💡 生成 ${recommendations.length} 条建议`);

  // 4. Write log
  const entry = writeLog(findings, recommendations);
  
  if (config.review) {
    console.log('\n--- 审查输出 ---');
    console.log(entry);
    console.log('--- 审查模式: 未写入文件 ---');
  }

  // 5. Summary
  const critical = recommendations.filter(r => r.priority === 'critical').length;
  const high = recommendations.filter(r => r.priority === 'high').length;
  
  if (critical > 0) {
    log(`🚨 ${critical} 个严重问题需要立即处理`);
  } else if (high > 0) {
    log(`⚠️ ${high} 个高优问题需要关注`);
  } else {
    log(`✅ 系统状态良好`);
  }
}

async function main() {
  log('🚀 Capability Evolver 启动');
  log(`   策略: ${config.strategy}`);
  log(`   自修改: ${config.allowSelfModify}`);
  log(`   负载上限: ${config.loadMax}`);
  
  if (config.loop) {
    log(`🔄 循环模式, 间隔 ${config.loopIntervalMs / 1000}s`);
    while (true) {
      await evolve();
      await new Promise(r => setTimeout(r, config.loopIntervalMs));
    }
  } else {
    await evolve();
  }
}

main().catch(err => {
  console.error('❌ 进化失败:', err.message);
  process.exit(1);
});
