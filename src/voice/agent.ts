import { BargeInController } from "./bargeIn";
import { MetricsTracker } from "./metrics";
import { ClinicFSM, Intent } from "./fsm";
import { createToolRouter } from "../tools/router";
import { registerHandlers } from "../tools/handlers";

export interface Asr {
  onPartial: (cb: (text: string) => void) => void;
  onFinal: (cb: (text: string) => void) => void;
  onVadStart: (cb: () => void) => void;
}

export interface Tts {
  speak: (text: string) => void;
  stop: () => void;
  onStart: (cb: () => void) => void;
}

export class VoiceAgent {
  private fsm = new ClinicFSM();
  private barge = new BargeInController();
  private metrics = new MetricsTracker();
  private router = createToolRouter();
  private tts: Tts;

  constructor(asr: Asr, tts: Tts) {
    this.tts = tts;

    // wire handlers
    registerHandlers(this.router);

    // barge-in
    this.barge.attachTTS(tts);
    asr.onVadStart(() => this.barge.onVadStart());
    asr.onPartial((text) => {
      this.barge.onAsrPartial(text);
      this.metrics.handle({ type: "asr_partial", atMs: Date.now() });
    });

    // metrics
    tts.onStart(() => this.metrics.handle({ type: "tts_start", atMs: Date.now() }));

    // basic NL router (placeholder): detect intent keywords
    asr.onFinal((text) => this.onUserUtterance(text));
  }

  private say(text: string): void {
    this.tts.speak(text);
  }

  private detectIntent(text: string): Intent | null {
    const t = text.toLowerCase();
    if (/(book|schedule)/.test(t)) return "APPOINTMENT_BOOKING";
    if (/(cancel)/.test(t)) return "APPOINTMENT_CANCELLATION";
    if (/(resched|move)/.test(t)) return "APPOINTMENT_RESCHEDULING";
    if (/(hours|location|address|insurance)/.test(t)) return "GENERAL_INFO";
    if (/(human|staff|nurse|doctor|representative)/.test(t)) return "ESCALATE_TO_HUMAN";
    return null;
  }

  private async onUserUtterance(text: string): Promise<void> {
    // Minimal emergency detection
    if (/chest pain|trouble breathing|stroke|unconscious/i.test(text)) {
      this.say("This sounds urgent. Please hang up and dial emergency services now. I can also connect you to a staff member.");
      await this.router.dispatch("escalate_to_human", { reason: "urgent_symptoms", callback_number: null });
      this.metrics.handle({ type: "escalation" });
      return;
    }

    // Intent
    const guessed = this.detectIntent(text);
    if (guessed) this.fsm.setIntent(guessed);

    const prompt = this.fsm.nextPrompt();
    this.say(prompt.say);
  }
}


