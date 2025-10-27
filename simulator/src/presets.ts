import honeybeeData from '../presets/honeybee_membrane.json';
import qpoData from '../presets/qpo_eruption.json';
import llmData from '../presets/llm_resonance.json';
import cognitiveData from '../presets/cognitive_gate.json';
import amazonData from '../presets/amazon_canopy.json';
import { DomainPreset } from './types';

export const PRESETS: DomainPreset[] = [
  honeybeeData as DomainPreset,
  qpoData as DomainPreset,
  llmData as DomainPreset,
  cognitiveData as DomainPreset,
  amazonData as DomainPreset
];

export const FEATURED_PRESETS = PRESETS.filter((preset) => preset.featured);
