export type MetricsEvent =
  | { type: "asr_partial"; atMs: number }
  | { type: "tts_start"; atMs: number }
  | { type: "booking_success" }
  | { type: "escalation" }
  | { type: "low_confidence_reask" };

export interface MetricsSink {
  emit: (name: string, value: number | string | boolean) => void;
}

export class MetricsTracker {
  private startMs: number;
  private firstPartialMs: number | null = null;
  private firstAudioMs: number | null = null;
  private sink: MetricsSink | null = null;

  constructor(startMs: number = Date.now()) {
    this.startMs = startMs;
  }

  attachSink(sink: MetricsSink): void {
    this.sink = sink;
  }

  handle(event: MetricsEvent): void {
    if (event.type === "asr_partial" && this.firstPartialMs === null) {
      this.firstPartialMs = event.atMs;
      this.emit("time_to_first_partial_ms", this.firstPartialMs - this.startMs);
    }
    if (event.type === "tts_start" && this.firstAudioMs === null) {
      this.firstAudioMs = event.atMs;
      this.emit("time_to_first_audio_ms", this.firstAudioMs - this.startMs);
    }
    if (event.type === "booking_success") {
      this.emit("booking_success", true);
    }
    if (event.type === "escalation") {
      this.emit("escalation", true);
    }
    if (event.type === "low_confidence_reask") {
      this.emit("low_confidence_reask", true);
    }
  }

  private emit(name: string, value: number | string | boolean): void {
    if (this.sink) this.sink.emit(name, value);
  }
}


