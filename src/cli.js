#!/usr/bin/env node
const path = require('path');
const fs = require('fs');
const { createSpeech, transcribeAudio } = require('./eleven');
require('dotenv').config();

async function main() {
  const argv = process.argv.slice(2);
  const cmd = argv[0];

  if (!process.env.XI_API_KEY) {
    console.error('Missing XI_API_KEY in environment. Copy .env.example -> .env and set XI_API_KEY');
    process.exit(1);
  }

  try {
    if (cmd === 'tts') {
      const voiceId = argv[1];
      const text = argv[2];
      const out = argv[3] || 'output.mp3';
      if (!voiceId || !text) {
        console.error('Usage: node src/cli.js tts <VOICE_ID> "<TEXT>" [output.mp3]');
        process.exit(1);
      }
      console.log(`Requesting TTS for voice=${voiceId} -> ${out}`);
      const outPath = await createSpeech(voiceId, text, out);
      console.log('Saved audio to', outPath);
    } else if (cmd === 'stt') {
      const audioPath = argv[1];
      const timeoutSec = Number(argv[2]) || 120;
      if (!audioPath) {
        console.error('Usage: node src/cli.js stt <AUDIO_FILE_PATH> [timeout_seconds]');
        process.exit(1);
      }
      console.log('Uploading', audioPath, 'for transcription...');
      const res = await transcribeAudio(audioPath, { timeoutMs: timeoutSec * 1000 });

      // Print a friendly summary if possible
      if (res && res.text) {
        console.log('\n=== Transcript (text) ===\n');
        console.log(res.text);
      } else if (res && res.words) {
        // Join words to reconstruct text when available
        const text = res.words.map(w => w.text).join('');
        console.log('\n=== Transcript (reconstructed from words) ===\n');
        console.log(text);
      } else if (res && res.transcription_id && res.text) {
        console.log('\n=== Transcript ===\n');
        console.log(res.text);
      } else {
        console.log('Transcription response:');
        console.log(JSON.stringify(res, null, 2));
      }
    } else {
      console.log('Usage:');
      console.log('  node src/cli.js tts <VOICE_ID> "<TEXT>" [output.mp3]');
      console.log('  node src/cli.js stt <AUDIO_FILE_PATH>');
    }
  } catch (err) {
    console.error('Error:', err.message || err);
    process.exit(1);
  }
}

main();
