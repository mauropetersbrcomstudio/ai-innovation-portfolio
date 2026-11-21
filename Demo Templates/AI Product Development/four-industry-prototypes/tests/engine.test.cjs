const test = require('node:test');
const assert = require('node:assert/strict');
const { SCENARIOS, triage } = require('../engine.js');

for (const [sector, cfg] of Object.entries(SCENARIOS)) {
  test(`${sector}: standard and exception routes`, () => {
    const standard = triage(sector, cfg.examples[0]);
    const exception = triage(sector, cfg.examples[1]);
    assert.equal(standard.priority, 'Normal');
    assert.equal(standard.reasons.length, 0);
    assert.notEqual(exception.priority, 'Normal');
    assert.ok(exception.reasons.length > 0);
    assert.notEqual(standard.queue, exception.queue);
  });
  test(`${sector}: rejects invalid and missing fields`, () => {
    assert.throws(() => triage(sector, {}), /obrigatório/);
    const invalid = { ...cfg.examples[0] };
    const select = cfg.fields.find(f => f.options);
    invalid[select.key] = 'value-outside-config';
    assert.throws(() => triage(sector, invalid), /opção inválida/);
  });
}

test('retail: monetary threshold routes to review', () => {
  const record = triage('retail', { ...SCENARIOS.retail.examples[0], amount: '501' });
  assert.equal(record.queue, 'Revisão de devolução');
});
test('manufacturing: released batch is urgent', () => {
  const record = triage('manufacturing', { ...SCENARIOS.manufacturing.examples[0], released: 'Sim' });
  assert.equal(record.priority, 'Urgente');
});
test('unknown scenario is rejected', () => assert.throws(() => triage('unknown', {}), /inválido/));
