import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';

async function text(file) {
  return readFile(new URL(`../${file}`, import.meta.url), 'utf8');
}

test('public package version starts at 0.0.1', async () => {
  const packageJson = JSON.parse(await text('package.json'));
  assert.equal(packageJson.version, '0.0.1');
  assert.equal(packageJson.private, true);
});

test('source and templates have explicit licenses', async () => {
  assert.match(await text('LICENSE'), /Apache License/);
  assert.match(await text('templates/LICENSE'), /MIT No Attribution/);
});

test('engineering loop template uses the public WetoLoop version', async () => {
  assert.match(await text('templates/engineering-loop/PLAN.template.yaml'), /loop_version: "0\.0\.1"/);
});
