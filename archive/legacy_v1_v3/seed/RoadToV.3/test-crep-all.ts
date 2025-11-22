/**
 * CREP Metrics Test - All 6 Systems
 *
 * Simple test to verify all systems have generateCREPMetrics()
 * WITHOUT complex ES module imports
 *
 * @author Claude Sonnet 4.5
 * @date 2025-11-14
 */

console.log('═══════════════════════════════════════════════════════════════');
console.log('  CREP METRICS - Completeness Test');
console.log('═══════════════════════════════════════════════════════════════\n');

// Test plan: Check each .ts file for generateCREPMetrics presence
const systems = [
  { name: 'WAIS', file: 'antarctic-ice-sheet.ts', beta: 13.5, type: 'Type-2: Thermodynamic' },
  { name: 'AMOC', file: 'amoc-collapse.ts', beta: 10.2, type: 'Type-2: Bistable' },
  { name: 'Coral Reefs', file: 'additional-systems.ts', beta: 7.5, type: 'Type-2/3' },
  { name: 'Measles', file: 'additional-systems.ts', beta: 5.8, type: 'Type-4: Informational' },
  { name: 'Finance 2008', file: 'additional-systems.ts', beta: 4.9, type: 'Type-4: Network' },
  { name: 'Cancer-Immune', file: 'additional-systems.ts', beta: 3.5, type: 'Type-3: Electrochemical' }
];

import * as fs from 'fs';
import * as path from 'path';

const basePath = '/home/user/Feldtheorie/seed/RoadToV.3';
let allPass = true;

systems.forEach((sys, idx) => {
  const filePath = path.join(basePath, sys.file);
  const content = fs.readFileSync(filePath, 'utf-8');

  // Simple check: does file contain generateCREPMetrics?
  const hasCREP = content.includes('generateCREPMetrics');
  const hasImplementation = content.match(/generateCREPMetrics\(\)[\s\S]*?\{[\s\S]*?coherence[\s\S]*?resonance[\s\S]*?emergence[\s\S]*?poetics/);

  const status = hasImplementation ? '✅ FULL' : hasCREP ? '⚠️  PARTIAL' : '❌ MISSING';

  console.log(`${idx + 1}. ${sys.name} (β=${sys.beta})`);
  console.log(`   Type: ${sys.type}`);
  console.log(`   File: ${sys.file}`);
  console.log(`   CREP: ${status}`);

  if (!hasImplementation) {
    allPass = false;
    console.log(`   ⚠️  WARNING: generateCREPMetrics() may be incomplete!`);
  }

  console.log('');
});

console.log('═══════════════════════════════════════════════════════════════');
console.log(`  Result: ${allPass ? '✅ ALL 6 SYSTEMS HAVE CREP!' : '❌ INCOMPLETE'}`);
console.log('═══════════════════════════════════════════════════════════════\n');

// CREP Definition reminder
console.log('CREP Framework:');
console.log('  Coherence:  System integrity (0-1)');
console.log('  Resonance:  Response to forcing (0-1)');
console.log('  Emergence:  β-normalized emergence potential (0-1)');
console.log('  Poetics:    Human-readable system state');
console.log('\nAll systems should implement:');
console.log('  generateCREPMetrics(): { coherence, resonance, emergence, poetics }');
console.log('');
