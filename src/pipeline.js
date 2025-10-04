#!/usr/bin/env node
const { createSpeech, transcribeAudio } = require('./eleven');
const path = require('path');
const fs = require('fs');

/**
 * Simple pipeline:
 * 1) Generate TTS audio from text and voice id
 * 2) Optionally transcribe the generated file
 *
 * Usage:
 * node src/pipeline.js <VOICE_ID> "<TEXT>" [output.mp3] [--stt] [--stt-timeout <seconds>]
 */

async function main() {
  const argv = process.argv.slice(2);
  const voiceId = argv[0];
  const text = argv[1];
  const out = argv[2] || 'pipeline_output.mp3';

  // No convert option; pipeline focuses on generating TTS and optional STT

  // Look for --stt flag (automatically transcribe generated or converted file)
  const sttFlag = argv.includes('--stt');
  const sttTimeoutIndex = argv.indexOf('--stt-timeout');
  let sttTimeoutSec = 120;
  if (sttTimeoutIndex !== -1 && argv.length > sttTimeoutIndex + 1) {
    const v = Number(argv[sttTimeoutIndex + 1]);
    if (!Number.isNaN(v) && v > 0) sttTimeoutSec = v;
  }

  if (!voiceId || !text) {
    console.error('Usage: node src/pipeline.js <VOICE_ID> "<TEXT>" [output.mp3] [--stt] [--stt-timeout <seconds>]');
    process.exit(1);
  }

  try {
    console.log('Generating TTS...');
    const generated = await createSpeech(voiceId, text, out);
    console.log('Generated:', generated);

    if (sttFlag) {
      console.log('Running STT on', generated, `with timeout ${sttTimeoutSec}s`);
      const res = await transcribeAudio(generated, { timeoutMs: sttTimeoutSec * 1000 });
      if (res && res.text) {
        console.log('\n=== Transcript ===\n');
        console.log(res.text);
      } else if (res && res.words) {
        console.log('\n=== Transcript (reconstructed) ===\n');
        console.log(res.words.map(w => w.text).join(''));
      } else {
        console.log('STT result:');
        console.log(JSON.stringify(res, null, 2));
      }
    }
  } catch (err) {
    console.error('Pipeline error:', err.message || err);
    process.exit(1);
  }
}

main();
