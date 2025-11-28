import { VoiceAgent } from "../voice/agent";

class MockASR {
  private partialCbs: Array<(t: string) => void> = [];
  private finalCbs: Array<(t: string) => void> = [];
  private vadCbs: Array<() => void> = [];
  onPartial(cb: (t: string) => void) { this.partialCbs.push(cb); }
  onFinal(cb: (t: string) => void) { this.finalCbs.push(cb); }
  onVadStart(cb: () => void) { this.vadCbs.push(cb); }
  // test helpers
  emitPartial(t: string) { this.partialCbs.forEach((cb) => cb(t)); }
  emitFinal(t: string) { this.finalCbs.forEach((cb) => cb(t)); }
  emitVad() { this.vadCbs.forEach((cb) => cb()); }
}

class MockTTS {
  private startCbs: Array<() => void> = [];
  speak(text: string) { this.startCbs.forEach((cb) => cb()); console.log("TTS:", text); }
  stop() { console.log("TTS stop"); }
  onStart(cb: () => void) { this.startCbs.push(cb); }
}

async function main() {
  const asr = new MockASR();
  const tts = new MockTTS();
  const agent = new VoiceAgent(asr as any, tts as any);

  // simple scripted run
  tts.speak("Hello. I can help with appointments and quick info.");
  asr.emitVad();
  asr.emitPartial("I want to schedule");
  asr.emitFinal("I want to schedule an appointment");
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});


