/**
 * Web Audio API Sonification for UTAC Field Dynamics
 *
 * Provides audio feedback for:
 * - Instability vibrato (oscillation when zeta < 0 or CREP > 0.7)
 * - Frequency ∝ rate_of_change (faster change = higher pitch)
 * - Volume ∝ gate magnitude (louder when active)
 *
 * References:
 * - FinalyzeVorschlägeGemini.txt:79-161 (UX Sonification)
 * - V6ToDorefresh.md Priority 10 (Simulator-UX)
 */

import { useEffect, useRef, useState } from 'react';

interface SonificationParams {
  baseFrequency: number;
  rateOfChange: number;
  gate: number;
  crep: number;
  enabled: boolean;
}

const BASE_FREQUENCY = 220; // A3 note
const MAX_FREQUENCY = 880; // A5 note
const MIN_FREQUENCY = 110; // A2 note
const VIBRATO_RATE = 5; // Hz
const VIBRATO_DEPTH = 15; // Hz

/**
 * Custom hook for audio sonification of field dynamics
 */
export function useAudioSonification() {
  const [enabled, setEnabled] = useState(false);
  const audioContextRef = useRef<AudioContext | null>(null);
  const oscillatorRef = useRef<OscillatorNode | null>(null);
  const gainNodeRef = useRef<GainNode | null>(null);
  const vibratoOscillatorRef = useRef<OscillatorNode | null>(null);
  const vibratoGainRef = useRef<GainNode | null>(null);

  useEffect(() => {
    if (!enabled) {
      // Clean up audio context when disabled
      if (oscillatorRef.current) {
        oscillatorRef.current.stop();
        oscillatorRef.current = null;
      }
      if (vibratoOscillatorRef.current) {
        vibratoOscillatorRef.current.stop();
        vibratoOscillatorRef.current = null;
      }
      if (audioContextRef.current) {
        audioContextRef.current.close();
        audioContextRef.current = null;
      }
      gainNodeRef.current = null;
      vibratoGainRef.current = null;
      return;
    }

    // Initialize Web Audio API
    const AudioContextClass = window.AudioContext || (window as any).webkitAudioContext;
    const audioContext = new AudioContextClass();
    audioContextRef.current = audioContext;

    // Main oscillator (carrier)
    const oscillator = audioContext.createOscillator();
    oscillator.type = 'sine';
    oscillator.frequency.value = BASE_FREQUENCY;
    oscillatorRef.current = oscillator;

    // Gain node for volume control
    const gainNode = audioContext.createGain();
    gainNode.gain.value = 0; // Start silent
    gainNodeRef.current = gainNode;

    // Vibrato oscillator (LFO - Low Frequency Oscillator)
    const vibratoOscillator = audioContext.createOscillator();
    vibratoOscillator.type = 'sine';
    vibratoOscillator.frequency.value = VIBRATO_RATE;
    vibratoOscillatorRef.current = vibratoOscillator;

    // Vibrato gain (controls depth of frequency modulation)
    const vibratoGain = audioContext.createGain();
    vibratoGain.gain.value = 0; // Start with no vibrato
    vibratoGainRef.current = vibratoGain;

    // Connect the audio graph:
    // vibratoOscillator -> vibratoGain -> oscillator.frequency (FM)
    // oscillator -> gainNode -> destination
    vibratoOscillator.connect(vibratoGain);
    vibratoGain.connect(oscillator.frequency);
    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);

    // Start oscillators
    oscillator.start();
    vibratoOscillator.start();

    return () => {
      if (oscillator) oscillator.stop();
      if (vibratoOscillator) vibratoOscillator.stop();
      if (audioContext) audioContext.close();
    };
  }, [enabled]);

  const updateSonification = (params: Omit<SonificationParams, 'enabled'>) => {
    if (!enabled || !audioContextRef.current || !oscillatorRef.current) return;

    const { baseFrequency, rateOfChange, gate, crep } = params;

    // Map rate_of_change to frequency (faster = higher pitch)
    // Clamp between MIN and MAX frequency
    const frequencyScale = Math.abs(rateOfChange) * 100;
    const targetFrequency = Math.max(
      MIN_FREQUENCY,
      Math.min(MAX_FREQUENCY, baseFrequency + frequencyScale)
    );

    // Smooth frequency transition
    if (oscillatorRef.current.frequency) {
      oscillatorRef.current.frequency.setTargetAtTime(
        targetFrequency,
        audioContextRef.current.currentTime,
        0.05
      );
    }

    // Volume based on gate magnitude
    // Active gates (gate > 0.5) are louder
    const targetVolume = gate > 0.5 ? 0.15 : 0.05;
    if (gainNodeRef.current) {
      gainNodeRef.current.gain.setTargetAtTime(
        targetVolume,
        audioContextRef.current.currentTime,
        0.1
      );
    }

    // Vibrato depth based on instability (CREP > 0.7 or negative zeta)
    // Higher CREP = more vibrato = more "nervous" sound
    let vibratoDepth = 0;
    if (crep > 0.7) {
      // Map CREP [0.7, 1.0] to vibrato depth [0, VIBRATO_DEPTH]
      vibratoDepth = ((crep - 0.7) / 0.3) * VIBRATO_DEPTH;
    }

    if (vibratoGainRef.current) {
      vibratoGainRef.current.gain.setTargetAtTime(
        vibratoDepth,
        audioContextRef.current.currentTime,
        0.05
      );
    }
  };

  const toggle = () => {
    setEnabled((prev) => !prev);
  };

  return {
    enabled,
    toggle,
    updateSonification
  };
}
