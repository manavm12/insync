"""eleven_tts.py

Lightweight ElevenLabs Text-to-Speech helper.

Usage:
  - Install elevenlabs: pip install elevenlabs
  - Set XI_API_KEY in your environment or pass api_key param
  - Call synthesize_to_file(...) from Python or run from CLI

Examples:
  python -m src.eleven_tts --voice XW70ikSsadUbinwLMZ5w --text "Hello world" --out out.mp3

This module intentionally keeps dependencies small and uses the public ElevenLabs
REST endpoint: POST /v1/text-to-speech/{voice_id}
"""

from __future__ import annotations

import os
import sys
import argparse
from typing import Optional
import types

# Module-level persistent ElevenLabs client. Use init_eleven_client() to set.
_ELEVEN_CLIENT = None


def init_eleven_client(api_key: Optional[str] = None, base_url: str = "https://api.elevenlabs.io"):
    """Initialize and store a persistent ElevenLabs client.

    Args:
        api_key: Optional API key to set in the environment for the SDK.
        base_url: Base URL for the ElevenLabs API.

    Returns:
        The initialized client instance.

    Raises:
        RuntimeError if the SDK is not installed or client creation fails.
    """
    global _ELEVEN_CLIENT
    if api_key:
        os.environ["XI_API_KEY"] = api_key

    try:
        from elevenlabs import ElevenLabs
    except Exception as exc:
        raise RuntimeError(f"Failed to import ElevenLabs SDK: {exc}")

    try:
        key = api_key or os.getenv("XI_API_KEY")
        # Prefer passing the API key explicitly to the constructor if supported
        try:
            _ELEVEN_CLIENT = ElevenLabs(base_url=base_url, api_key=key) if key else ElevenLabs(base_url=base_url)
        except TypeError:
            # Older/newer SDK may not accept api_key kwarg; fall back to base constructor
            _ELEVEN_CLIENT = ElevenLabs(base_url=base_url)

        # Best-effort: if the SDK uses an underlying HTTP client/session, try
        # to inject the xi-api-key header so the server receives it.
        try:
            real_key = key or os.getenv("XI_API_KEY")
            if real_key:
                # Common SDK internals: client.text_to_speech._raw_client._client or _session
                raw = getattr(_ELEVEN_CLIENT, 'text_to_speech', None)
                if raw is not None:
                    raw_client = getattr(raw, '_raw_client', None)
                    if raw_client is not None:
                        # httpx or requests style
                        sess = getattr(raw_client, '_client', None) or getattr(raw_client, '_session', None) or getattr(raw_client, 'session', None)
                        if sess is not None:
                            headers = getattr(sess, 'headers', None)
                            if isinstance(headers, dict):
                                headers['xi-api-key'] = real_key
                            else:
                                try:
                                    sess.headers.update({'xi-api-key': real_key})
                                except Exception:
                                    pass
        except Exception:
            # non-fatal
            pass

        return _ELEVEN_CLIENT
    except Exception as exc:
        raise RuntimeError(f"Failed to initialize ElevenLabs client: {exc}")


def get_eleven_client():
    """Return the module-level ElevenLabs client if available, else None.

    If a client hasn't been initialized but XI_API_KEY is present, this will
    attempt to initialize one on-demand.
    """
    global _ELEVEN_CLIENT
    if _ELEVEN_CLIENT is not None:
        return _ELEVEN_CLIENT
    # Try to initialize lazily if an API key exists in env
    if os.getenv("XI_API_KEY"):
        try:
            return init_eleven_client()
        except Exception:
            return None
    return None


def synthesize_to_file(
    text: str,
    voice_id: Optional[str] = None,
    output_path: str = "out.mp3",
    api_key: Optional[str] = None,
    output_format: str = "mp3_44100_128",
) -> str:
    """Synthesize `text` using ElevenLabs SDK and save to `output_path`.

    Args:
        text: The text to synthesize.
        voice_id: ElevenLabs voice id. If not provided, reads XI_VOICE_ID env var.
        output_path: Path to write synthesized audio.
        api_key: Optional ElevenLabs API key. If provided, this will be set on
                 the environment for the SDK to pick up.
        output_format: Output format string for the SDK (e.g. "mp3_44100_128").

    Returns:
        The path to the written audio file.

    Raises:
        ValueError if required parameters are missing.
        RuntimeError for unexpected SDK responses or missing SDK.
    """
    if not text:
        raise ValueError("text must be provided for synthesis")

    voice_id = voice_id or os.getenv("XI_VOICE_ID")
    if not voice_id:
        raise ValueError("voice_id must be provided either as an argument or via XI_VOICE_ID environment variable")

    # Prefer explicit api_key, otherwise expect XI_API_KEY in env
    if api_key:
        os.environ["XI_API_KEY"] = api_key
    if "XI_API_KEY" not in os.environ or not os.environ.get("XI_API_KEY"):
        raise ValueError("XI_API_KEY must be set in the environment or passed via the api_key argument")

    # Prefer a module-level client if initialized
    try:
        from src.eleven_tts import get_eleven_client
        client = get_eleven_client()
    except Exception:
        client = None

    if client is None:
        # Lazy import and instantiate a short-lived client for this call
        try:
            from elevenlabs import ElevenLabs
            client = ElevenLabs(base_url="https://api.elevenlabs.io")
        except Exception as exc:
            raise RuntimeError(f"Failed to import/initialize ElevenLabs SDK: {exc}")

    # Call the SDK's text-to-speech convert method. Different SDK versions
    # may return different types (bytes, file-like object, path string, or
    # structured dict). We handle common cases below.
    try:
        result = client.text_to_speech.convert(
            voice_id=voice_id,
            text=text,
            output_format=output_format,
        )
    except Exception as exc:
        raise RuntimeError(f"ElevenLabs SDK synthesis failed: {exc}")

    # Process common return shapes
    # 1) bytes/bytearray -> write directly
    if isinstance(result, (bytes, bytearray)):
        with open(output_path, "wb") as fh:
            fh.write(result)
        return output_path

    # 2) file-like object with read()
    if hasattr(result, "read"):
        try:
            data = result.read()
        except Exception as exc:
            raise RuntimeError(f"Failed to read audio stream from SDK result: {exc}")
        with open(output_path, "wb") as fh:
            fh.write(data)
        return output_path

    # 3) SDK might return a path string where it saved the file
    if isinstance(result, str):
        # If the SDK already returned a path, just return it. If the caller
        # requested a different path, try to copy it into output_path.
        if os.path.exists(result) and result != output_path:
            try:
                with open(result, "rb") as src, open(output_path, "wb") as dst:
                    dst.write(src.read())
                return output_path
            except Exception:
                # Fall back to returning the SDK-provided path
                return result
        return result

    # 4) Some SDKs return a structured dict that contains audio bytes
    if isinstance(result, dict):
        for key in ("audio", "audio_content", "content"):
            if key in result and isinstance(result[key], (bytes, bytearray)):
                with open(output_path, "wb") as fh:
                    fh.write(result[key])
                return output_path

    # 4b) SDK may return a generator/iterable that yields audio chunks
    if isinstance(result, types.GeneratorType) or (hasattr(result, '__iter__') and not isinstance(result, (str, bytes, bytearray, dict))):
        try:
            with open(output_path, 'wb') as fh:
                for chunk in result:
                    if chunk is None:
                        continue
                    if isinstance(chunk, (bytes, bytearray)):
                        fh.write(chunk)
                    elif hasattr(chunk, 'read'):
                        fh.write(chunk.read())
                    else:
                        try:
                            fh.write(bytes(chunk))
                        except Exception:
                            # ignore non-bytes chunk
                            pass
            return output_path
        except Exception as exc:
            raise RuntimeError(f"Failed to stream-write generator result: {exc}")

    # 5) Try to coerce to bytes as a last resort
    try:
        blob = bytes(result)
        with open(output_path, "wb") as fh:
            fh.write(blob)
        return output_path
    except Exception:
        raise RuntimeError(f"Unsupported return type from ElevenLabs SDK: {type(result)}")


def _cli(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="ElevenLabs TTS CLI")
    parser.add_argument("--voice", required=True, help="Voice ID to use (e.g. XW70...)")
    parser.add_argument("--text", required=False, help="Text to synthesize. If omitted, reads from stdin.")
    parser.add_argument("--infile", required=False, help="Path to a text file to read as input")
    parser.add_argument("--out", default="out.mp3", help="Output audio file path")
    parser.add_argument("--api-key", required=False, help="XI API key (optional, otherwise read from XI_API_KEY env)")
    parser.add_argument("--model", required=False, help="Optional model id to use")
    args = parser.parse_args(argv)

    if args.text:
        text = args.text
    elif args.infile:
        if not os.path.exists(args.infile):
            print(f"Input file not found: {args.infile}", file=sys.stderr)
            return 2
        with open(args.infile, "r", encoding="utf-8") as f:
            text = f.read()
    else:
        # read stdin
        text = sys.stdin.read().strip()

    try:
        out = synthesize_to_file(text=text, voice_id=args.voice, output_path=args.out, api_key=args.api_key)
        print(f"Wrote audio to: {out}")
        return 0
    except Exception as e:
        print(f"Pipeline error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(_cli())
