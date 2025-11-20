export interface StoppableTTS {
  stop: () => void;
}

export class BargeInController {
  private tts: StoppableTTS | null = null;

  attachTTS(tts: StoppableTTS): void {
    this.tts = tts;
  }

  onVadStart(): void {
    if (this.tts) this.tts.stop();
  }

  onAsrPartial(_: string): void {
    if (this.tts) this.tts.stop();
  }
}


