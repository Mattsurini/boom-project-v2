const { execFileSync } = require('child_process');
const fs = require('fs');
const os = require('os');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const CLI = path.join(ROOT, '.venv', 'Scripts', 'notebooklm.exe');
const OUTPUT_DIR = path.join(ROOT, 'Output', 'NotebookLM');
const RUN_LOG = path.join(OUTPUT_DIR, 'notebooklm-run-log.json');

function readRunLog() {
  try {
    return JSON.parse(fs.readFileSync(RUN_LOG, 'utf8'));
  } catch {
    return {};
  }
}

function writeRunLog(log) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  fs.writeFileSync(RUN_LOG, JSON.stringify(log, null, 2) + '\n', 'utf8');
}

function fail(msg) {
  console.error(`[notebooklm-run] ERROR: ${msg}`);
  process.exit(1);
}

function run(args, opts = {}) {
  try {
    const out = execFileSync(CLI, args, {
      encoding: 'utf8',
      input: opts.input,
      maxBuffer: 1024 * 1024 * 64,
      windowsHide: true,
    });
    return out.trim();
  } catch (e) {
    const err = (e.stderr || e.stdout || e.message || '').trim();
    fail(`${err || 'command failed'}\n  -> notebooklm ${args.join(' ')}`);
  }
}

function parseArgs(argv) {
  const out = { notebook: undefined, questionsJson: undefined };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--notebook' || a === '-n') {
      out.notebook = argv[++i];
    } else if (out.questionsJson === undefined) {
      out.questionsJson = a;
    }
  }
  return out;
}

function dateStamp() {
  const d = new Date();
  const p = (n) => String(n).padStart(2, '0');
  return `${d.getFullYear()}${p(d.getMonth() + 1)}${p(d.getDate())}`;
}

function slugify(s) {
  return String(s || 'research')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, 60);
}

function writeTempPrompt(content) {
  const dir = path.join(os.tmpdir(), 'nb-prompts');
  fs.mkdirSync(dir, { recursive: true });
  const file = path.join(dir, `prompt-${Date.now()}-${Math.random().toString(36).slice(2)}.txt`);
  fs.writeFileSync(file, content, 'utf8');
  return file;
}

function formatReferences(refs) {
  if (!Array.isArray(refs) || refs.length === 0) return '';
  const lines = refs.map((r, i) => {
    const n = r.citation_number != null ? r.citation_number : i + 1;
    const src = r.source_id ? ` (source: ${r.source_id})` : '';
    const text = r.cited_text ? ` — "${String(r.cited_text).slice(0, 220)}${String(r.cited_text).length > 220 ? '…' : ''}"` : '';
    return `[${n}]${src}${text}`;
  });
  return `\n**References:**\n${lines.map((l) => `- ${l}`).join('\n')}`;
}

function main() {
  const { notebook, questionsJson } = parseArgs(process.argv.slice(2));
  if (!questionsJson) fail('usage: node notebooklm-run.js <questions.json> [--notebook <id>]');
  if (!fs.existsSync(CLI)) fail(`CLI not found at ${CLI} (run .venv\\Scripts\\pip install -r requirements.txt)`);

  const raw = fs.readFileSync(questionsJson, 'utf8').replace(/^\uFEFF/, '');
  const spec = JSON.parse(raw);
  // Accept both the documented object form and the plain-string form
  // ("questions": ["text", ...]) that earlier packets in Output/Plawan use.
  const normalizeQ = (q, i) => {
    if (typeof q === 'string') return { id: `Q${i + 1}`, phase: null, prompt: q };
    if (q && typeof q === 'object' && typeof q.prompt === 'string') {
      return { id: q.id || `Q${i + 1}`, phase: q.phase || null, prompt: q.prompt };
    }
    throw new Error(
      `question #${i + 1} in ${path.basename(questionsJson)} is neither a string nor {prompt: ...}: ${JSON.stringify(q)}`
    );
  };
  const rawQuestions = Array.isArray(spec.questions) ? spec.questions : [];
  if (rawQuestions.length === 0) fail(`no questions found in ${questionsJson}`);
  const questions = rawQuestions.map(normalizeQ);
  const title = spec.title || spec.topic || 'Research';
  const slug = spec.slug || slugify(title);
  const blindSpot = spec.blindSpot;
  const notebookArgs = notebook ? ['--notebook', notebook] : [];

  const log = readRunLog();
  const prev = log[slug];
  if (prev) {
    console.log(`[notebooklm-run] ALREADY RUN for "${slug}" on ${prev.runAt}.`);
    console.log(`[notebooklm-run] SKIPPING re-run. Results: ${prev.resultsFile}`);
    console.log(`[notebooklm-run] conversation: ${prev.conversationId || 'n/a'}`);
    console.log(`[notebooklm-run] questions source: ${prev.questionsJson}`);
    return;
  }

  console.log(`[notebooklm-run] title: ${title}`);
  console.log(`[notebooklm-run] questions: ${questions.length}` + (blindSpot ? ' + blind-spot sweep' : '') + (notebook ? ` | notebook: ${notebook}` : ' (current notebook)'));

  const sections = [`# NotebookLM Research Results — ${title}`, `\nGenerated: ${new Date().toISOString()}`];

  if (spec.contextNote) {
    console.log('[notebooklm-run] creating Context Note...');
    const titleArg = spec.contextNoteTitle ? ['-t', spec.contextNoteTitle] : [];
    const res = run(['note', 'create', '--content', '-', ...titleArg, ...notebookArgs, '--json'], {
      input: spec.contextNote,
    });
    const created = JSON.parse(res);
    sections.push(`\n## Context Note\nCreated as NotebookLM note (id: ${created.id || created.note_id || '?'}) and referenced during the session.`);
  }

  let first = true;
  let lastConversation = null;
  questions.forEach((q, i) => {
    const id = q.id || `Q${i + 1}`;
    const phase = q.phase ? `\n### ${q.phase}` : '';
    console.log(`[notebooklm-run] asking ${id}${first ? ' (new conversation)' : ''}...`);
    const promptFile = writeTempPrompt(q.prompt);
    const args = ['ask', '--prompt-file', promptFile, '--json', ...(first ? ['--new'] : []), ...notebookArgs];
    const res = run(args);
    fs.unlinkSync(promptFile);
    let data;
    try {
      data = JSON.parse(res);
    } catch {
      fail(`unparseable output for ${id}:\n${res.slice(0, 500)}`);
    }
    first = false;
    lastConversation = data.conversation_id || lastConversation;
    const refs = formatReferences(data.references);
    sections.push(`\n## ${id}. ${q.prompt}${phase}\n\n**Answer:**\n\n${data.answer || '(no answer returned)'}${refs}`);
  });

  if (blindSpot) {
    console.log('[notebooklm-run] running Blind-Spot Sweep...');
    const promptFile = writeTempPrompt(blindSpot);
    const res = run(['ask', '--prompt-file', promptFile, '--json', ...notebookArgs]);
    fs.unlinkSync(promptFile);
    const data = JSON.parse(res);
    const refs = formatReferences(data.references);
    sections.push(`\n## Blind-Spot Sweep\n\n**Answer:**\n\n${data.answer || '(no answer returned)'}${refs}`);
  }

  const filename = `${dateStamp()}-${slug}-notebooklm-results.md`;
  const outPath = path.join(OUTPUT_DIR, filename);
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  fs.writeFileSync(outPath, sections.join('\n'), 'utf8');

  console.log(`\n[notebooklm-run] DONE. Results saved to:\n  ${outPath}`);
  if (lastConversation) console.log(`  conversation: ${lastConversation}`);

  log[slug] = {
    title,
    questionsJson: path.basename(questionsJson),
    resultsFile: path.basename(outPath),
    conversationId: lastConversation || null,
    runAt: new Date().toISOString(),
  };
  writeRunLog(log);
  console.log(`[notebooklm-run] Logged to ${RUN_LOG}`);
}

main();
