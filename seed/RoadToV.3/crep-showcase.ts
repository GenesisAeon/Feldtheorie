/**
 * CREP Metrics Showcase - V3.0 All Systems
 *
 * Demonstrates Coherence, Resonance, Emergence, Poetics
 * across all 6 UTAC real-world systems.
 *
 * Phase: 3 (TypeScript Bridge)
 * Feature: v3-feat-p3-002
 *
 * @author Claude Sonnet 4.5
 * @date 2025-11-14
 */

// ==================== System Imports ====================

import { WAISSystem } from './antarctic-ice-sheet.js';
import { AMOCSystem } from './amoc-collapse.js';
import {
  CoralReefSystem,
  MeaslesSystem,
  FinancialSystem,
  CancerImmuneSystem
} from './additional-systems.js';

// ==================== CREP Interface ====================

interface CREPMetrics {
  coherence: number;   // System integrity (0-1)
  resonance: number;   // Response to forcing (0-1)
  emergence: number;   // β-normalized emergence potential (0-1)
  poetics: string;     // Human-readable system state
}

interface SystemCREP {
  name: string;
  utacType: string;
  beta: number;
  status: string;
  urgency: string;
  crep: CREPMetrics;
}

// ==================== CREP Showcase ====================

export class CREPShowcase {

  /**
   * Generate CREP metrics for all 6 systems
   */
  static generateAllCREP(): SystemCREP[] {
    const systems: SystemCREP[] = [];

    // 1. WAIS (β=13.5) - Highest β
    const wais = new WAISSystem.model();
    systems.push({
      name: WAISSystem.metadata.name,
      utacType: WAISSystem.metadata.utacType,
      beta: WAISSystem.metadata.beta,
      status: WAISSystem.metadata.status,
      urgency: WAISSystem.metadata.urgency,
      crep: wais.generateCREPMetrics()
    });

    // 2. AMOC (β=10.2) - Bistable
    const amoc = new AMOCSystem.model();
    systems.push({
      name: AMOCSystem.metadata.name,
      utacType: AMOCSystem.metadata.utacType,
      beta: AMOCSystem.metadata.beta,
      status: AMOCSystem.metadata.status,
      urgency: AMOCSystem.metadata.urgency,
      crep: amoc.generateCREPMetrics()
    });

    // 3. Coral Reefs (β=7.5) - Already tipped!
    const coral = new CoralReefSystem.model();
    systems.push({
      name: CoralReefSystem.metadata.name,
      utacType: CoralReefSystem.metadata.utacType,
      beta: CoralReefSystem.metadata.beta,
      status: CoralReefSystem.metadata.status,
      urgency: CoralReefSystem.metadata.urgency,
      crep: coral.generateCREPMetrics()
    });

    // 4. Measles (β=5.8) - Informational
    const measles = new MeaslesSystem.model();
    systems.push({
      name: MeaslesSystem.metadata.name,
      utacType: MeaslesSystem.metadata.utacType,
      beta: MeaslesSystem.metadata.beta,
      status: MeaslesSystem.metadata.status,
      urgency: MeaslesSystem.metadata.urgency,
      crep: measles.generateCREPMetrics()
    });

    // 5. Finance 2008 (β=4.9) - Network
    const finance = new FinancialSystem.model();
    systems.push({
      name: FinancialSystem.metadata.name,
      utacType: FinancialSystem.metadata.utacType,
      beta: FinancialSystem.metadata.beta,
      status: FinancialSystem.metadata.status,
      urgency: FinancialSystem.metadata.urgency,
      crep: finance.generateCREPMetrics()
    });

    // 6. Cancer-Immune (β=3.5) - Lowest β, Therapeutic
    const cancer = new CancerImmuneSystem.model();
    systems.push({
      name: CancerImmuneSystem.metadata.name,
      utacType: CancerImmuneSystem.metadata.utacType,
      beta: CancerImmuneSystem.metadata.beta,
      status: CancerImmuneSystem.metadata.status,
      urgency: CancerImmuneSystem.metadata.urgency,
      crep: cancer.generateCREPMetrics()
    });

    return systems;
  }

  /**
   * Print CREP showcase to console
   */
  static printShowcase(): void {
    console.log('═══════════════════════════════════════════════════════════════');
    console.log('  CREP METRICS SHOWCASE - 6 Real-World UTAC Systems');
    console.log('  Coherence | Resonance | Emergence | Poetics');
    console.log('═══════════════════════════════════════════════════════════════\n');

    const systems = this.generateAllCREP();

    // Sort by β (descending)
    systems.sort((a, b) => b.beta - a.beta);

    systems.forEach((sys, idx) => {
      console.log(`${idx + 1}. ${sys.name} (β=${sys.beta})`);
      console.log(`   Type: ${sys.utacType}`);
      console.log(`   Status: ${sys.status} | Urgency: ${sys.urgency}`);
      console.log(`   ───────────────────────────────────────────────────────────`);
      console.log(`   Coherence:  ${sys.crep.coherence.toFixed(2)} ${this.getCohBar(sys.crep.coherence)}`);
      console.log(`   Resonance:  ${sys.crep.resonance.toFixed(2)} ${this.getResBar(sys.crep.resonance)}`);
      console.log(`   Emergence:  ${sys.crep.emergence.toFixed(2)} ${this.getEmerBar(sys.crep.emergence)}`);
      console.log(`   Poetics:`);
      console.log(`   "${sys.crep.poetics}"`);
      console.log('');
    });

    // Summary statistics
    console.log('═══════════════════════════════════════════════════════════════');
    console.log('  SUMMARY STATISTICS');
    console.log('═══════════════════════════════════════════════════════════════\n');

    const avgCoherence = systems.reduce((sum, s) => sum + s.crep.coherence, 0) / systems.length;
    const avgResonance = systems.reduce((sum, s) => sum + s.crep.resonance, 0) / systems.length;
    const avgEmergence = systems.reduce((sum, s) => sum + s.crep.emergence, 0) / systems.length;

    console.log(`   Average Coherence:  ${avgCoherence.toFixed(3)} (System integrity across 6 domains)`);
    console.log(`   Average Resonance:  ${avgResonance.toFixed(3)} (Response to forcing)`);
    console.log(`   Average Emergence:  ${avgEmergence.toFixed(3)} (β-normalized potential)`);
    console.log(`   β-Range Coverage:   ${systems[systems.length-1].beta} → ${systems[0].beta} (3.5x span)`);
    console.log(`   Critical Systems:   ${systems.filter(s => s.urgency === 'CRITICAL').length}/6`);
    console.log(`   Systems at tipping: ${systems.filter(s => s.status.includes('TIPPING') || s.status.includes('TIPPED')).length}/6`);
    console.log('\n═══════════════════════════════════════════════════════════════\n');
  }

  /**
   * Helper: Coherence bar chart
   */
  private static getCohBar(val: number): string {
    const bars = Math.round(val * 20);
    return '█'.repeat(bars) + '░'.repeat(20 - bars);
  }

  /**
   * Helper: Resonance bar chart
   */
  private static getResBar(val: number): string {
    const bars = Math.round(val * 20);
    return '▓'.repeat(bars) + '░'.repeat(20 - bars);
  }

  /**
   * Helper: Emergence bar chart
   */
  private static getEmerBar(val: number): string {
    const bars = Math.round(val * 20);
    return '▒'.repeat(bars) + '░'.repeat(20 - bars);
  }

  /**
   * Export as JSON
   */
  static exportJSON(): string {
    const systems = this.generateAllCREP();
    return JSON.stringify({
      metadata: {
        analysis: "CREP Metrics",
        systems_count: systems.length,
        generated: new Date().toISOString()
      },
      systems: systems.reduce((acc, sys) => {
        acc[sys.name] = {
          utac_type: sys.utacType,
          beta: sys.beta,
          status: sys.status,
          urgency: sys.urgency,
          crep: sys.crep
        };
        return acc;
      }, {} as any)
    }, null, 2);
  }
}

// ==================== CLI Entry Point ====================

// Auto-run when executed directly
const showcase = new CREPShowcase();
CREPShowcase.printShowcase();

// Optionally export JSON
// console.log(CREPShowcase.exportJSON());
