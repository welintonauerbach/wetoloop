import { readFile, readdir } from 'node:fs/promises';
import path from 'node:path';
import process from 'node:process';

const root = process.cwd();
const required = [
  'README.md',
  'LICENSE',
  'CONTRIBUTING.md',
  'SECURITY.md',
  'package.json',
  'templates/LICENSE',
  'templates/engineering-loop/PLAN.template.yaml',
  'templates/engineering-loop/schemas/plan.schema.json',
];

async function exists(relative) {
  try {
    await readFile(path.join(root, relative));
    return true;
  } catch {
    return false;
  }
}

async function collectJson(directory) {
  const entries = await readdir(directory, { withFileTypes: true });
  const files = [];
  for (const entry of entries) {
    if (['node_modules', '.git'].includes(entry.name)) continue;
    const resolved = path.join(directory, entry.name);
    if (entry.isDirectory()) files.push(...await collectJson(resolved));
    else if (entry.isFile() && entry.name.endsWith('.json')) files.push(resolved);
  }
  return files;
}

const failures = [];
for (const file of required) {
  if (!await exists(file)) failures.push(`missing required file: ${file}`);
}

const packageJson = JSON.parse(await readFile(path.join(root, 'package.json'), 'utf8'));
if (packageJson.version !== '0.0.1') failures.push('package.json version must be 0.0.1');
if (packageJson.license !== 'Apache-2.0') failures.push('package.json license must be Apache-2.0');
if (packageJson.private !== true) failures.push('root package must remain private until public CLI packaging is ready');

for (const jsonFile of await collectJson(root)) {
  try {
    JSON.parse(await readFile(jsonFile, 'utf8'));
  } catch (error) {
    failures.push(`invalid JSON: ${path.relative(root, jsonFile)} (${error.message})`);
  }
}

const planTemplate = await readFile(path.join(root, 'templates/engineering-loop/PLAN.template.yaml'), 'utf8');
if (!planTemplate.includes('loop_version: "0.0.1"')) {
  failures.push('PLAN.template.yaml must declare loop_version 0.0.1');
}

if (failures.length) {
  console.error('Repository checks failed:');
  for (const failure of failures) console.error(`- ${failure}`);
  process.exit(1);
}

console.log('Repository checks passed.');
