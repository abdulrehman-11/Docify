import { ToolRouter } from "./router";
import {
  AvailabilitySlot,
  BookAppointmentInput,
  BookAppointmentOutput,
  CancelAppointmentInput,
  CancelAppointmentOutput,
  CheckAvailabilityInput,
  CheckAvailabilityOutput,
  EscalateToHumanInput,
  EscalateToHumanOutput,
  GetHoursInput,
  GetHoursOutput,
  GetInsuranceSupportedInput,
  GetInsuranceSupportedOutput,
  GetLocationInput,
  GetLocationOutput,
  RescheduleAppointmentInput,
  RescheduleAppointmentOutput,
  SendConfirmationInput,
  SendConfirmationOutput,
} from "./schemas";

// Side-effect free stubs; integrate real backends later
export function registerHandlers(router: ToolRouter) {
  router.register("check_availability", async (input: CheckAvailabilityInput): Promise<CheckAvailabilityOutput> => {
    const from = new Date(input.preferred_time_window.from);
    const slot: AvailabilitySlot = {
      start: from.toISOString(),
      end: new Date(from.getTime() + 30 * 60 * 1000).toISOString(),
    };
    return { slots: [slot] };
  });

  router.register("book_appointment", async (_: BookAppointmentInput): Promise<BookAppointmentOutput> => {
    // Return fake confirmation id; real system should persist after explicit confirmation
    return { confirmation_id: `cnf_${Date.now()}` };
  });

  router.register("cancel_appointment", async (_: CancelAppointmentInput): Promise<CancelAppointmentOutput> => {
    return { status: "cancelled" };
  });

  router.register("reschedule_appointment", async (_: RescheduleAppointmentInput): Promise<RescheduleAppointmentOutput> => {
    return { status: "rescheduled", new_confirmation_id: `cnf_${Date.now()}` };
  });

  router.register("get_hours", async (_: GetHoursInput): Promise<GetHoursOutput> => {
    return { hours_text: "Mon–Fri 8am–6pm; Sat 9am–1pm; Sun closed" };
  });

  router.register("get_location", async (_: GetLocationInput): Promise<GetLocationOutput> => {
    return { address_text: "123 Clinic Way, Suite 200, Springfield, ST" };
  });

  router.register("get_insurance_supported", async (input: GetInsuranceSupportedInput): Promise<GetInsuranceSupportedOutput> => {
    const accepted = ["Aetna", "Blue Cross", "Cigna", "United"].some(
      (p) => p.toLowerCase() === input.provider.toLowerCase()
    );
    return { accepted };
  });

  router.register("escalate_to_human", async (_: EscalateToHumanInput): Promise<EscalateToHumanOutput> => {
    return { status: "queued" };
  });

  router.register("send_confirmation", async (_: SendConfirmationInput): Promise<SendConfirmationOutput> => {
    return { status: "sent" };
  });
}


