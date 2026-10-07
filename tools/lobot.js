#!/usr/bin/env node
'use strict';
/*
 * Lobot: install, check, and update Lobot in a Project Brain.
 * No dependencies. See usage() below.
 */
const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const ENGINE = path.join(ROOT, 'engine');
const SCAFFOLD = path.join(ROOT, 'scaffold');
const VERSION = require(path.join(ROOT, 'package.json')).version;
// How people run this tool. Change it here and in the docs if Lobot moves.
const RUN = 'npx github:KeyboardCowboy/lobot';
const STAMP = '.lobot-version';
const TEXT_EXT = new Set(['.md', '.yaml', '.yml']);
// npm drops files named .gitignore from packages, so the scaffold stores it without the dot.
const RENAME = { gitignore: '.gitignore' };
// Where each kind of assistant looks for skills inside a project.
const SKILL_DIRS = { claude: '.claude/skills', agents: '.agents/skills' };
const SKILL_SOURCES = ['.ai/general/skills', '.ai/project/skills'];

function usage() {
  return [
    'Lobot ' + VERSION,
    '',
    'Run in a Project Brain (or pass its directory):',
    '  ' + RUN + ' init [dir] --name "Client Name" --key KEY [--harnesses claude,agents]',
    '  ' + RUN + ' status [dir]',
    '  ' + RUN + ' update [dir] [--dry-run] [--force] [--harnesses claude,agents]',
    '  ' + RUN + ' link [dir] [--harnesses claude,agents]',
    '',
    'init    New Project Brain: copies Lobot to .ai/general/, adds starting files',
    '        (existing files are kept), and makes the skills discoverable.',
    'status  Shows the installed version, local changes to .ai/general/, and what an',
    '        update would change. Changes nothing.',
    'update  Replaces .ai/general/ with this version. Refuses to run when .ai/general/',
    '        has local changes, so they can go back to Lobot first.',
    'link    Makes skills in .ai/general/skills/ and .ai/project/skills/ discoverable.',
    '        Run it after adding a project skill.',
    '',
    '--harnesses  Which assistants to set up: claude (.claude/skills, .claude/agents)',
    '             and/or agents (.agents/skills: Codex, Cursor, Gemini CLI, OpenCode).',
    '             Default: claude. Remembered after the first run.',
  ].join('\n');
}

function fail(message) {
  console.error('error: ' + message);
  process.exit(1);
}

function isJunk(rel) {
  const parts = rel.split('/');
  const name = parts[parts.length - 1];
  return name === '.DS_Store' || name === STAMP || name.endsWith('.pyc') || parts.includes('__pycache__');
}

function walk(base) {
  const out = [];
  (function visit(dir, prefix) {
    let entries;
    try {
      entries = fs.readdirSync(dir, { withFileTypes: true });
    } catch (e) {
      return;
    }
    for (const entry of entries.sort((a, b) => (a.name < b.name ? -1 : 1))) {
      const rel = prefix ? prefix + '/' + entry.name : entry.name;
      if (entry.isDirectory()) visit(path.join(dir, entry.name), rel);
      else if (entry.isFile() && !isJunk(rel)) out.push(rel);
    }
  })(base, '');
  return out;
}

function sha(file) {
  return crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
}

/** Relative path -> sha256 for every real file under base. */
function manifest(base) {
  const out = {};
  for (const rel of walk(base)) out[rel] = sha(path.join(base, rel));
  return out;
}

function generalDir(project) {
  return path.join(project, '.ai', 'general');
}

function readStamp(project) {
  const file = path.join(generalDir(project), STAMP);
  if (!fs.existsSync(file)) return null;
  try {
    return JSON.parse(fs.readFileSync(file, 'utf8'));
  } catch (e) {
    fail(file + ' is not valid JSON. Fix or remove it, then run again.');
  }
}

function writeStamp(project, harnesses) {
  // Record what Lobot installed, not whatever is in the directory, so files a
  // project added locally keep showing up as local changes.
  const data = {
    files: manifest(ENGINE),
    harnesses: harnesses,
    lobot_version: VERSION,
    updated: new Date().toISOString().slice(0, 10),
  };
  fs.writeFileSync(path.join(generalDir(project), STAMP), JSON.stringify(data, null, 2) + '\n');
}

function pickHarnesses(option, stamp) {
  const list = option ? option.split(',').map((s) => s.trim()).filter(Boolean)
    : (stamp && stamp.harnesses) || ['claude'];
  for (const h of list) {
    if (!SKILL_DIRS[h]) fail('unknown harness "' + h + '". Use: ' + Object.keys(SKILL_DIRS).join(', '));
  }
  return list;
}

/**
 * Changes in the project's Lobot copy that Lobot doesn't have.
 *
 * With a version stamp, the baseline is what was installed. Without one (a Project
 * Brain that predates Lobot), the baseline is this version's engine, and files the
 * engine has but the project lacks are simply new, not local removals.
 */
function localChanges(project) {
  const current = manifest(generalDir(project));
  const engine = manifest(ENGINE);
  const stamp = readStamp(project);
  const baseline = stamp ? stamp.files : engine;
  const changes = [];
  const all = Array.from(new Set(Object.keys(current).concat(Object.keys(baseline)))).sort();
  for (const rel of all) {
    const where = '.ai/general/' + rel;
    if (rel in current && rel in baseline) {
      // Identical to the new engine means the change is already in Lobot.
      if (current[rel] !== baseline[rel] && current[rel] !== engine[rel]) changes.push(['modified', where]);
    } else if (rel in current) {
      if (current[rel] !== engine[rel]) changes.push(['added', where]);
    } else if (stamp) {
      changes.push(['removed', where]);
    }
  }
  // Agent copies in .claude/agents/ are derived; an edit there would be lost.
  for (const rel of Object.keys(engine)) {
    if (!rel.startsWith('agents/')) continue;
    const name = rel.slice('agents/'.length);
    const copy = path.join(project, '.claude', 'agents', name);
    if (!fs.existsSync(copy)) continue;
    const have = sha(copy);
    if (have !== engine[rel] && have !== baseline[rel] && have !== current[rel]) {
      changes.push(['modified', '.claude/agents/' + name]);
    }
  }
  return { stamp, changes };
}

function planUpdate(project) {
  const current = manifest(generalDir(project));
  const engine = manifest(ENGINE);
  const stamp = readStamp(project);
  const write = Object.keys(engine).sort().filter((rel) => current[rel] !== engine[rel]);
  // Only delete files Lobot itself installed earlier and has since dropped.
  const remove = stamp ? Object.keys(stamp.files).sort().filter((rel) => !(rel in engine) && rel in current) : [];
  return { write, remove };
}

function copyFile(from, to) {
  fs.mkdirSync(path.dirname(to), { recursive: true });
  fs.copyFileSync(from, to);
}

function copyEngine(project, rels) {
  for (const rel of rels) copyFile(path.join(ENGINE, rel), path.join(generalDir(project), rel));
}

function copyAgents(project) {
  const src = path.join(ENGINE, 'agents');
  const copied = [];
  for (const rel of walk(src)) {
    if (!rel.endsWith('.md')) continue;
    const from = path.join(src, rel);
    const to = path.join(project, '.claude', 'agents', rel);
    if (fs.existsSync(to) && sha(to) === sha(from)) continue;
    copyFile(from, to);
    copied.push('.claude/agents/' + rel);
  }
  return copied;
}

function lstat(p) {
  try {
    return fs.lstatSync(p);
  } catch (e) {
    return null;
  }
}

function sameTree(a, b) {
  const ma = manifest(a);
  const mb = manifest(b);
  const keys = Object.keys(ma);
  return keys.length === Object.keys(mb).length && keys.every((k) => ma[k] === mb[k]);
}

/** Every skill in the project: name -> source directory relative to the project. A project skill overrides a general one. */
function findSkills(project) {
  const skills = {};
  for (const source of SKILL_SOURCES) {
    const dir = path.join(project, source);
    let names = [];
    try {
      names = fs.readdirSync(dir).sort();
    } catch (e) {
      continue;
    }
    for (const name of names) {
      if (fs.existsSync(path.join(dir, name, 'SKILL.md'))) skills[name] = source + '/' + name;
    }
  }
  return skills;
}

function pointsAtSkillSource(project, linkPath) {
  const target = path.resolve(path.dirname(linkPath), fs.readlinkSync(linkPath));
  return SKILL_SOURCES.some((s) => target.startsWith(path.join(project, s) + path.sep));
}

/**
 * Make skills discoverable: one link per skill in each harness's skills directory,
 * pointing at the copy in .ai/. With dryRun, reports what it would do.
 */
function linkSkills(project, harnesses, dryRun) {
  const skills = findSkills(project);
  const result = { linked: [], copied: [], removed: [], conflicts: [] };
  for (const harness of harnesses) {
    const relDir = SKILL_DIRS[harness];
    const dir = path.join(project, relDir);
    for (const name of Object.keys(skills).sort()) {
      const dest = path.join(dir, name);
      const source = path.join(project, skills[name]);
      const target = path.relative(dir, source).split(path.sep).join('/');
      const label = relDir + '/' + name;
      const st = lstat(dest);
      if (st && st.isSymbolicLink()) {
        if (fs.readlinkSync(dest) === target) continue;
        if (!pointsAtSkillSource(project, dest)) {
          result.conflicts.push(label + ' (a link to somewhere else)');
          continue;
        }
        if (!dryRun) {
          try {
            fs.unlinkSync(dest);
          } catch (e) {
            result.conflicts.push(label + ' (points at the wrong skill; could not replace it)');
            continue;
          }
        }
      } else if (st) {
        if (!(st.isDirectory() && sameTree(dest, source))) result.conflicts.push(label + ' (already exists and differs from ' + skills[name] + ')');
        continue;
      }
      if (dryRun) {
        result.linked.push(label);
        continue;
      }
      fs.mkdirSync(dir, { recursive: true });
      try {
        fs.symlinkSync(target, dest, 'dir');
        result.linked.push(label);
      } catch (e) {
        // No symlink support (some Windows setups): fall back to a copy.
        for (const rel of walk(source)) copyFile(path.join(source, rel), path.join(dest, rel));
        result.copied.push(label);
      }
    }
    // Remove links Lobot made to skills that no longer exist.
    let entries = [];
    try {
      entries = fs.readdirSync(dir);
    } catch (e) {
      continue;
    }
    for (const name of entries) {
      const dest = path.join(dir, name);
      const st = lstat(dest);
      if (!st || !st.isSymbolicLink() || !pointsAtSkillSource(project, dest)) continue;
      if (fs.existsSync(path.join(dest, 'SKILL.md'))) continue;
      if (!dryRun) {
        try {
          fs.unlinkSync(dest);
        } catch (e) {
          result.conflicts.push(relDir + '/' + name + ' (stale link; could not delete it)');
          continue;
        }
      }
      result.removed.push(relDir + '/' + name);
    }
  }
  return result;
}

function printLinks(result, dryRun) {
  const verb = dryRun ? 'would link ' : 'linked   ';
  for (const l of result.linked) console.log('  ' + verb + l);
  for (const l of result.copied) console.log('  copied   ' + l + ' (links are not available here; run link again after changing the skill)');
  for (const l of result.removed) console.log('  ' + (dryRun ? 'would remove ' : 'removed  ') + l);
  for (const l of result.conflicts) console.log('  skipped  ' + l);
}

function printChanges(changes) {
  for (const [kind, where] of changes) console.log('  ' + (kind + '        ').slice(0, 9) + where);
}

function requireBrain(project) {
  if (!fs.existsSync(generalDir(project))) {
    fail(project + ' has no .ai/general/. Use "init" for a new Project Brain.');
  }
}

function cmdInit(project, opts) {
  const general = generalDir(project);
  if (fs.existsSync(general) && fs.readdirSync(general).length) {
    fail(project + ' already has .ai/general/. Use "update" instead.');
  }
  if (!opts.name || !opts.key) fail('init needs --name "Client Name" and --key KEY.');
  const harnesses = pickHarnesses(opts.harnesses, null);
  fs.mkdirSync(project, { recursive: true });
  copyEngine(project, Object.keys(manifest(ENGINE)).sort());
  const values = {
    '{{PROJECT_NAME}}': opts.name,
    '{{PROJECT_KEY}}': opts.key,
    '{{DATE}}': new Date().toISOString().slice(0, 10),
  };
  const kept = [];
  for (const rel of walk(SCAFFOLD)) {
    const parts = rel.split('/');
    const last = parts.length - 1;
    parts[last] = RENAME[parts[last]] || parts[last];
    const destRel = parts.join('/');
    const dest = path.join(project, destRel);
    if (lstat(dest)) {
      kept.push(destRel);
      continue;
    }
    fs.mkdirSync(path.dirname(dest), { recursive: true });
    const from = path.join(SCAFFOLD, rel);
    if (TEXT_EXT.has(path.extname(rel))) {
      let text = fs.readFileSync(from, 'utf8');
      for (const key of Object.keys(values)) text = text.split(key).join(values[key]);
      fs.writeFileSync(dest, text);
    } else {
      fs.copyFileSync(from, dest);
    }
  }
  if (harnesses.includes('claude')) copyAgents(project);
  const links = linkSkills(project, harnesses, false);
  writeStamp(project, harnesses);
  console.log('Installed Lobot ' + VERSION + ' into ' + project);
  if (kept.length) {
    console.log('Kept files that were already there:');
    for (const rel of kept) console.log('  ' + rel);
  }
  console.log('Skills:');
  printLinks(links, false);
  console.log([
    'Next steps:',
    '  1. git init, and push to a private repository (it will hold transcripts and a people directory).',
    '  2. Clone the project\'s code repository into repo/ and point the drive symlink at the shared Drive folder.',
    '  3. Copy .env.example to .env and add your token.',
    '  4. Fill in the TODOs in CLAUDE.md and .ai/project/adr.md.',
    '  5. Follow README.md to set up your assistant.',
  ].join('\n'));
}

function cmdStatus(project) {
  requireBrain(project);
  const { stamp, changes } = localChanges(project);
  const harnesses = pickHarnesses(null, stamp);
  console.log('Project Brain:   ' + project);
  console.log('Installed Lobot: ' + (stamp ? stamp.lobot_version : 'none recorded (no ' + STAMP + '; set up before Lobot or by hand)'));
  console.log('This Lobot:      ' + VERSION);
  if (!changes.length) {
    console.log('Local changes Lobot doesn\'t have: none');
  } else {
    console.log(stamp
      ? 'Local changes Lobot doesn\'t have (send them to Lobot before updating):'
      : 'Differences from this Lobot (local edits or an older version; without a stamp Lobot can\'t tell which):');
    printChanges(changes);
  }
  const { write, remove } = planUpdate(project);
  if (write.length || remove.length) {
    console.log('An update would:');
    for (const rel of write) console.log('  write    .ai/general/' + rel);
    for (const rel of remove) console.log('  delete   .ai/general/' + rel);
  } else {
    console.log('An update would change nothing in .ai/general/.');
  }
  const links = linkSkills(project, harnesses, true);
  if (links.linked.length || links.removed.length || links.conflicts.length) {
    console.log('Skill discovery (' + harnesses.join(', ') + '): out of date. "link" or "update" would fix:');
    printLinks(links, true);
  } else {
    console.log('Skill discovery (' + harnesses.join(', ') + '): up to date.');
  }
}

function cmdUpdate(project, opts) {
  requireBrain(project);
  const { stamp, changes } = localChanges(project);
  const harnesses = pickHarnesses(opts.harnesses, stamp);
  if (changes.length && !opts.force) {
    console.log('Not updated. ' + project + ' has changes Lobot doesn\'t have:');
    printChanges(changes);
    if (!stamp) {
      console.log([
        'This Project Brain has no ' + STAMP + ', so Lobot can\'t tell a local edit from an older',
        'version of the same file. Compare each file above with Lobot\'s copy. If nothing would be',
        'lost, run update again with --force; it records the version from then on.',
      ].join('\n'));
    } else {
      console.log('Send them to the Lobot repository first (or discard them), then run update again.');
    }
    console.log('--force overwrites modified files. Added files are always left in place.');
    process.exit(1);
  }
  const { write, remove } = planUpdate(project);
  if (opts.dryRun) {
    console.log('Dry run. Updating to Lobot ' + VERSION + ' would:');
    for (const rel of write) console.log('  write    .ai/general/' + rel);
    for (const rel of remove) console.log('  delete   .ai/general/' + rel);
    if (!write.length && !remove.length) console.log('  change nothing in .ai/general/');
    console.log('  refresh agent definitions and skill links, and record the version');
    return;
  }
  copyEngine(project, write);
  const failed = [];
  for (const rel of remove) {
    try {
      fs.unlinkSync(path.join(generalDir(project), rel));
    } catch (e) {
      failed.push(rel);
      continue;
    }
    // Tidy up directories the deletion left empty.
    let dir = path.dirname(path.join(generalDir(project), rel));
    while (dir !== generalDir(project)) {
      try {
        fs.rmdirSync(dir);
      } catch (e) {
        break;
      }
      dir = path.dirname(dir);
    }
  }
  const agents = harnesses.includes('claude') ? copyAgents(project) : [];
  const links = linkSkills(project, harnesses, false);
  writeStamp(project, harnesses);
  console.log('Updated ' + project + ': Lobot ' + (stamp ? stamp.lobot_version : 'unversioned') + ' -> ' + VERSION);
  for (const rel of write) console.log('  wrote    .ai/general/' + rel);
  for (const rel of remove) if (!failed.includes(rel)) console.log('  deleted  .ai/general/' + rel);
  for (const rel of agents) console.log('  wrote    ' + rel);
  printLinks(links, false);
  if (!write.length && !remove.length && !agents.length && !links.linked.length) console.log('  nothing needed changing');
  if (failed.length) {
    console.log('Could not delete these files Lobot no longer ships; delete them by hand:');
    for (const rel of failed) console.log('  .ai/general/' + rel);
  }
  console.log('Review the changes, commit them in the Project Brain, and start a new assistant session.');
}

function cmdLink(project, opts) {
  requireBrain(project);
  const stamp = readStamp(project);
  const harnesses = pickHarnesses(opts.harnesses, stamp);
  const links = linkSkills(project, harnesses, false);
  if (stamp && opts.harnesses) {
    stamp.harnesses = harnesses;
    fs.writeFileSync(path.join(generalDir(project), STAMP), JSON.stringify(stamp, null, 2) + '\n');
  }
  if (links.linked.length || links.copied.length || links.removed.length || links.conflicts.length) printLinks(links, false);
  else console.log('Skill discovery (' + harnesses.join(', ') + '): already up to date.');
}

function main() {
  const argv = process.argv.slice(2);
  const opts = {};
  const positional = [];
  const valued = { '--name': 'name', '--key': 'key', '--harnesses': 'harnesses' };
  const flags = { '--dry-run': 'dryRun', '--force': 'force' };
  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];
    if (arg === '--help' || arg === '-h') return console.log(usage());
    if (arg === '--version' || arg === '-v') return console.log(VERSION);
    if (valued[arg]) {
      if (i + 1 >= argv.length) fail(arg + ' needs a value.');
      opts[valued[arg]] = argv[++i];
    } else if (flags[arg]) {
      opts[flags[arg]] = true;
    } else if (arg.startsWith('-')) {
      fail('unknown option ' + arg + '\n\n' + usage());
    } else {
      positional.push(arg);
    }
  }
  const command = positional[0];
  const project = path.resolve(positional[1] || '.');
  if (command === 'init') return cmdInit(project, opts);
  if (command === 'status') return cmdStatus(project);
  if (command === 'update') return cmdUpdate(project, opts);
  if (command === 'link') return cmdLink(project, opts);
  console.log(usage());
  process.exit(command ? 1 : 0);
}

main();
