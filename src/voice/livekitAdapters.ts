// Thin interfaces to adapt a LiveKit Node starter's ASR/TTS into our agent
import { Asr, Tts } from "./agent";

export function createAsrAdapter(livekitAsr: {
  on: (event: string, cb: (...args: any[]) => void) => void;
}): Asr {
  return {
    onPartial(cb) {
      livekitAsr.on("partial", (text: string) => cb(text));
    },
    onFinal(cb) {
      livekitAsr.on("final", (text: string) => cb(text));
    },
    onVadStart(cb) {
      livekitAsr.on("vad_start", () => cb());
    },
  };
}

export function createTtsAdapter(livekitTts: {
  speak: (text: string) => void;
  stop: () => void;
  on: (event: string, cb: () => void) => void;
}): Tts {
  return {
    speak(text) {
      livekitTts.speak(text);
    },
    stop() {
      livekitTts.stop();
    },
    onStart(cb) {
      livekitTts.on("start", cb);
    },
  };
}


