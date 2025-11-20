// Lightweight validation utilities (no external deps)
const isIsoDateTime = (value: unknown): value is string => {
  return typeof value === "string" && !Number.isNaN(Date.parse(value));
};

const isE164 = (value: unknown): value is string => {
  return typeof value === "string" && /^\+?[1-9]\d{1,14}$/u.test(value);
};

const isEmail = (value: unknown): value is string => {
  return (
    typeof value === "string" &&
    /^[^\s@]+@[^\s@]+\.[^\s@]+$/u.test(value)
  );
};

const ensure = (cond: unknown, msg: string): void => {
  if (!cond) throw new Error(msg);
};

// Types
export type AvailabilitySlot = {
  start: string; // ISO-8601
  end: string; // ISO-8601
};

export type CheckAvailabilityInput = {
  reason: string;
  preferred_time_window: { from: string; to: string };
};
export type CheckAvailabilityOutput = { slots: AvailabilitySlot[] };

export type BookAppointmentInput = {
  name: string;
  reason: string;
  slot_start: string;
  slot_end: string;
  insurance: string | null;
  phone: string; // E.164
  email: string;
};
export type BookAppointmentOutput = { confirmation_id: string };

export type CancelAppointmentInput = {
  name: string;
  slot_start: string;
  reason: string | null;
};
export type CancelAppointmentOutput = { status: "cancelled" };

export type RescheduleAppointmentInput = {
  name: string;
  current_slot_start: string;
  new_slot_start: string;
  new_slot_end: string;
};
export type RescheduleAppointmentOutput = {
  status: "rescheduled";
  new_confirmation_id: string;
};

export type GetHoursInput = {};
export type GetHoursOutput = { hours_text: string };

export type GetLocationInput = {};
export type GetLocationOutput = { address_text: string };

export type GetInsuranceSupportedInput = { provider: string };
export type GetInsuranceSupportedOutput = { accepted: boolean };

export type EscalateToHumanInput = {
  reason: string;
  callback_number: string | null; // E.164 or null
};
export type EscalateToHumanOutput = { status: "connected" | "queued" };

export type SendConfirmationInput = {
  channel: "sms" | "email";
  address: string;
  message: string;
};
export type SendConfirmationOutput = { status: "sent" };

export type ToolName =
  | "check_availability"
  | "book_appointment"
  | "cancel_appointment"
  | "reschedule_appointment"
  | "get_hours"
  | "get_location"
  | "get_insurance_supported"
  | "escalate_to_human"
  | "send_confirmation";

export type ToolInputByName = {
  check_availability: CheckAvailabilityInput;
  book_appointment: BookAppointmentInput;
  cancel_appointment: CancelAppointmentInput;
  reschedule_appointment: RescheduleAppointmentInput;
  get_hours: GetHoursInput;
  get_location: GetLocationInput;
  get_insurance_supported: GetInsuranceSupportedInput;
  escalate_to_human: EscalateToHumanInput;
  send_confirmation: SendConfirmationInput;
};

export type ToolOutputByName = {
  check_availability: CheckAvailabilityOutput;
  book_appointment: BookAppointmentOutput;
  cancel_appointment: CancelAppointmentOutput;
  reschedule_appointment: RescheduleAppointmentOutput;
  get_hours: GetHoursOutput;
  get_location: GetLocationOutput;
  get_insurance_supported: GetInsuranceSupportedOutput;
  escalate_to_human: EscalateToHumanOutput;
  send_confirmation: SendConfirmationOutput;
};

// Runtime input validators
export const validateInput = (
  name: ToolName,
  raw: unknown
): ToolInputByName[typeof name] => {
  ensure(raw && typeof raw === "object", "Input must be an object");
  const obj = raw as Record<string, unknown>;
  switch (name) {
    case "check_availability": {
      ensure(typeof obj.reason === "string" && obj.reason.length > 0, "reason");
      const tw = obj.preferred_time_window as any;
      ensure(tw && typeof tw === "object", "preferred_time_window");
      ensure(isIsoDateTime(tw.from), "preferred_time_window.from");
      ensure(isIsoDateTime(tw.to), "preferred_time_window.to");
      return obj as ToolInputByName[typeof name];
    }
    case "book_appointment": {
      ensure(typeof obj.name === "string" && obj.name.length > 0, "name");
      ensure(typeof obj.reason === "string" && obj.reason.length > 0, "reason");
      ensure(isIsoDateTime(obj.slot_start), "slot_start");
      ensure(isIsoDateTime(obj.slot_end), "slot_end");
      ensure(
        obj.insurance === null || typeof obj.insurance === "string",
        "insurance"
      );
      ensure(isE164(obj.phone), "phone");
      ensure(isEmail(obj.email), "email");
      return obj as ToolInputByName[typeof name];
    }
    case "cancel_appointment": {
      ensure(typeof obj.name === "string" && obj.name.length > 0, "name");
      ensure(isIsoDateTime(obj.slot_start), "slot_start");
      ensure(
        obj.reason === null || typeof obj.reason === "string",
        "reason"
      );
      return obj as ToolInputByName[typeof name];
    }
    case "reschedule_appointment": {
      ensure(typeof obj.name === "string" && obj.name.length > 0, "name");
      ensure(isIsoDateTime(obj.current_slot_start), "current_slot_start");
      ensure(isIsoDateTime(obj.new_slot_start), "new_slot_start");
      ensure(isIsoDateTime(obj.new_slot_end), "new_slot_end");
      return obj as ToolInputByName[typeof name];
    }
    case "get_hours": {
      return {} as ToolInputByName[typeof name];
    }
    case "get_location": {
      return {} as ToolInputByName[typeof name];
    }
    case "get_insurance_supported": {
      ensure(
        typeof obj.provider === "string" && obj.provider.length > 0,
        "provider"
      );
      return obj as ToolInputByName[typeof name];
    }
    case "escalate_to_human": {
      ensure(
        typeof obj.reason === "string" && obj.reason.length > 0,
        "reason"
      );
      ensure(
        obj.callback_number === null || isE164(obj.callback_number),
        "callback_number"
      );
      return obj as ToolInputByName[typeof name];
    }
    case "send_confirmation": {
      ensure(
        obj.channel === "sms" || obj.channel === "email",
        "channel"
      );
      ensure(
        typeof obj.address === "string" && obj.address.length > 0,
        "address"
      );
      ensure(
        typeof obj.message === "string" && obj.message.length > 0,
        "message"
      );
      return obj as ToolInputByName[typeof name];
    }
  }
};

// Runtime output validators
export const validateOutput = (
  name: ToolName,
  raw: unknown
): ToolOutputByName[typeof name] => {
  ensure(raw && typeof raw === "object", "Output must be an object");
  const obj = raw as Record<string, unknown>;
  switch (name) {
    case "check_availability": {
      ensure(Array.isArray(obj.slots), "slots");
      for (const slot of obj.slots as any[]) {
        ensure(isIsoDateTime(slot.start), "slots[].start");
        ensure(isIsoDateTime(slot.end), "slots[].end");
      }
      return obj as ToolOutputByName[typeof name];
    }
    case "book_appointment": {
      ensure(
        typeof obj.confirmation_id === "string" && obj.confirmation_id.length > 0,
        "confirmation_id"
      );
      return obj as ToolOutputByName[typeof name];
    }
    case "cancel_appointment": {
      ensure(obj.status === "cancelled", "status");
      return obj as ToolOutputByName[typeof name];
    }
    case "reschedule_appointment": {
      ensure(obj.status === "rescheduled", "status");
      ensure(
        typeof obj.new_confirmation_id === "string" &&
          obj.new_confirmation_id.length > 0,
        "new_confirmation_id"
      );
      return obj as ToolOutputByName[typeof name];
    }
    case "get_hours": {
      ensure(typeof obj.hours_text === "string" && obj.hours_text.length > 0, "hours_text");
      return obj as ToolOutputByName[typeof name];
    }
    case "get_location": {
      ensure(
        typeof obj.address_text === "string" && obj.address_text.length > 0,
        "address_text"
      );
      return obj as ToolOutputByName[typeof name];
    }
    case "get_insurance_supported": {
      ensure(typeof obj.accepted === "boolean", "accepted");
      return obj as ToolOutputByName[typeof name];
    }
    case "escalate_to_human": {
      ensure(
        obj.status === "connected" || obj.status === "queued",
        "status"
      );
      return obj as ToolOutputByName[typeof name];
    }
    case "send_confirmation": {
      ensure(obj.status === "sent", "status");
      return obj as ToolOutputByName[typeof name];
    }
  }
};


