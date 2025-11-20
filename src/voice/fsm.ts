export type Intent =
  | "APPOINTMENT_BOOKING"
  | "APPOINTMENT_CANCELLATION"
  | "APPOINTMENT_RESCHEDULING"
  | "GENERAL_INFO"
  | "ESCALATE_TO_HUMAN";

export interface CallerContext {
  name?: string;
  reason?: string;
  preferredFrom?: string;
  preferredTo?: string;
  insurance?: string | null;
  phone?: string;
  email?: string;
  currentSlotStart?: string;
  cancelSlotStart?: string;
}

export type Prompt = {
  say: string; // keep short for streaming TTS
  expect?: "freeform" | "yesno";
};

export class ClinicFSM {
  private intent: Intent | null = null;
  private ctx: CallerContext = {};

  getContext(): CallerContext { return this.ctx; }
  setIntent(intent: Intent): void { this.intent = intent; }

  // Very light prompt generator based on required fields per intent
  nextPrompt(): Prompt {
    switch (this.intent) {
      case "APPOINTMENT_BOOKING":
        if (!this.ctx.name) return { say: "Got it. What's your full name?" };
        if (!this.ctx.reason) return { say: "Thanks. What's the reason for the visit?" };
        if (!this.ctx.preferredFrom || !this.ctx.preferredTo) return { say: "What day and time works?" };
        if (this.ctx.insurance === undefined) return { say: "Do you have insurance to add? You can say skip.", expect: "freeform" };
        if (!this.ctx.phone) return { say: "What's the best phone number?" };
        if (!this.ctx.email) return { say: "And your email?" };
        return { say: "I can check availability now. Ready?", expect: "yesno" };

      case "APPOINTMENT_CANCELLATION":
        if (!this.ctx.name) return { say: "Sure. Your full name?" };
        if (!this.ctx.cancelSlotStart) return { say: "What is the appointment date and time?" };
        return { say: "Confirm cancel this appointment?", expect: "yesno" };

      case "APPOINTMENT_RESCHEDULING":
        if (!this.ctx.name) return { say: "Okay. What's your full name?" };
        if (!this.ctx.currentSlotStart) return { say: "What date and time is your current appointment?" };
        if (!this.ctx.preferredFrom || !this.ctx.preferredTo) return { say: "What new day and time works?" };
        return { say: "I'll search for the nearest options. Continue?", expect: "yesno" };

      case "GENERAL_INFO":
        return { say: "What would you like to know? Hours, location, or insurance?" };

      case "ESCALATE_TO_HUMAN":
        return { say: "I can connect you now. Should I proceed?", expect: "yesno" };
    }
    return { say: "Hi. I can help with appointments and quick info. How can I help?" };
  }

  // Minimal slot filling updates
  update(key: keyof CallerContext, value: string | null): void {
    (this.ctx as any)[key] = value as any;
  }
}


