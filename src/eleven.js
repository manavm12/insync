// ElevenLabs helpers for TTS and STT
const fs = require('fs');
const path = require('path');
// axios is optional. Prefer an installed axios if present, otherwise
// fall back to a tiny shim using the global fetch (Node 18+).
let axios;
try {
  // prefer installed axios when available
  axios = require('axios');
} catch (e) {
  // provide a minimal axios-like shim for the methods used in this file
  // supports: axios.post(url, body, { headers, responseType })
  //          axios.get(url, { headers })
  axios = {
    async post(url, body, opts = {}) {
      const headers = (opts && opts.headers) || {};
      const responseType = opts && opts.responseType;

      // If body looks like form-data (has getHeaders and is a streamable body), pass it through
      const isForm = body && typeof body.getHeaders === 'function';
      let res;
      if (isForm) {
        // form-data (from form-data package)
        const fetchOpts = { method: 'POST', headers: Object.assign({}, headers, body.getHeaders()), body };
        res = await fetch(url, fetchOpts);
      } else {
        // JSON body
        const fetchOpts = { method: 'POST', headers: Object.assign({ 'Content-Type': 'application/json' }, headers), body: JSON.stringify(body) };
        res = await fetch(url, fetchOpts);
      }

      if (responseType === 'arraybuffer') {
        const buf = await res.arrayBuffer();
        return { data: Buffer.from(buf) };
      }

      // try parse json, otherwise return text
      try {
        const json = await res.json();
        return { data: json };
      } catch (err) {
        const text = await res.text();
        return { data: text };
      }
    },

    async get(url, opts = {}) {
      const headers = (opts && opts.headers) || {};
      const res = await fetch(url, { method: 'GET', headers });
      try {
        const json = await res.json();
        return { data: json };
      } catch (err) {
        const text = await res.text();
        return { data: text };
      }
    }
  };
}
const FormData = require('form-data');
require('dotenv').config();

const XI_API_KEY = process.env.XI_API_KEY;
if (!XI_API_KEY) {
  // do not throw here; CLI will detect and exit gracefully
}

const BASE_URL = 'https://api.elevenlabs.io/v1';

async function createSpeech(voiceId, text, outputPath = './output.mp3', options = {}) {
  if (!XI_API_KEY) throw new Error('XI_API_KEY not set in env');
  if (!voiceId) throw new Error('voiceId is required');
  if (!text) throw new Error('text is required');

  const url = `${BASE_URL}/text-to-speech/${encodeURIComponent(voiceId)}`;

  const body = {
    text,
    model_id: options.model_id || 'eleven_multilingual_v2',
    voice_settings: options.voice_settings || null
  };

  const headers = {
    'xi-api-key': XI_API_KEY,
    'Content-Type': 'application/json'
  };

  const resp = await axios.post(url, body, { headers, responseType: 'arraybuffer' });
  fs.writeFileSync(outputPath, Buffer.from(resp.data));
  return path.resolve(outputPath);
}

async function transcribeAudio(audioPath, options = {}) {
  if (!XI_API_KEY) throw new Error('XI_API_KEY not set in env');
  if (!audioPath) throw new Error('audioPath is required');
  if (!fs.existsSync(audioPath)) throw new Error(`file not found: ${audioPath}`);

  const url = `${BASE_URL}/speech-to-text/transcripts`;
  const form = new FormData();
  form.append('file', fs.createReadStream(audioPath));
  // model param - using scribe_v1 per docs
  form.append('model', options.model || 'scribe_v1');

  const headers = Object.assign({ 'xi-api-key': XI_API_KEY }, form.getHeaders());

  // POST multipart form
  const resp = await axios.post(url, form, { headers });

  // The API may return transcription result immediately or an id to poll.
  const data = resp.data || {};

  // If the response already contains text, return it.
  if (data.text || data.transcript) return data;

  // Try to find a transcription id in common locations.
  const transcriptionId = data.transcription_id || data.transcriptionId || data.id || data.transcript_id || data.transcriptId;

  // helper to fetch transcript by id
  async function getTranscript(id) {
    const url = `${BASE_URL}/speech-to-text/transcripts/${encodeURIComponent(id)}`;
    const headers = { 'xi-api-key': XI_API_KEY };
    const r = await axios.get(url, { headers });
    return r.data;
  }

  const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

  if (transcriptionId) {
    const timeoutMs = options.timeoutMs || 120_000; // default 2 minutes
    const pollInterval = options.pollIntervalMs || 1500;
    const start = Date.now();

    while (Date.now() - start < timeoutMs) {
      await sleep(pollInterval);
      try {
        const status = await getTranscript(transcriptionId);
        // If text is present or words array present, consider it done.
        if (status && (status.text || (Array.isArray(status.words) && status.words.length > 0))) {
          return status;
        }
        // Some APIs include a status field; treat 'completed' as done
        if (status && (status.status === 'completed' || status.status === 'done')) {
          return status;
        }
        // otherwise continue polling
      } catch (err) {
        // transient errors - continue polling until timeout
      }
    }

    throw new Error('Timeout waiting for transcription result');
  }

  // No transcription id and no text — return raw data so caller can inspect error
  return data;
}

module.exports = {
  createSpeech,
  transcribeAudio,
};
