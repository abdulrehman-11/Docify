import logging
from livekit.agents import function_tool

logger = logging.getLogger(__name__)


def create_livekit_tools(router):
    """Create LiveKit-compatible tool wrappers for all registered tools"""

    @function_tool(
        raw_schema={
            "name": "check_availability",
            "description": "Check available appointment slots within a time window. Returns list of slots with 'start' and 'end' times in ISO8601 format. To determine if user's requested time is available: compare their time to each slot's start time (within 15 minutes tolerance). Example: User wants '2:30 PM' (14:30), slot with start='2025-11-14T14:30:00+00:00' is a perfect match.",
            "parameters": {
                "type": "object",
                "properties": {
                    "reason": {
                        "type": "string",
                        "description": "Reason for the appointment"
                    },
                    "preferred_time_window": {
                        "type": "object",
                        "description": "Time window with 'from_' and 'to' times in ISO8601 format",
                        "properties": {
                            "from_": {
                                "type": "string",
                                "description": "Start time in ISO8601 format"
                            },
                            "to": {
                                "type": "string",
                                "description": "End time in ISO8601 format"
                            }
                        },
                        "required": ["from_", "to"],
                        "additionalProperties": False
                    }
                },
                "required": ["reason", "preferred_time_window"],
                "additionalProperties": False
            }
        }
    )
    async def check_availability(raw_arguments: dict):
        """Check available appointment slots within a time window."""
        logger.info("LiveKit calling check_availability")
        reason = raw_arguments["reason"]
        preferred_time_window = raw_arguments["preferred_time_window"]
        return await router.dispatch("check_availability", {
            "reason": reason,
            "preferred_time_window": preferred_time_window
        })

    @function_tool(
        raw_schema={
            "name": "book_appointment",
            "description": "Book a new appointment with patient details. CRITICAL: (1) Always call check_availability first and use EXACT 'start'/'end' from returned slots. (2) ALWAYS spell email back letter-by-letter to patient and get confirmation before booking - emails must be perfect to find returning patients.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Full name of the patient"
                    },
                    "reason": {
                        "type": "string",
                        "description": "Reason for the appointment"
                    },
                    "slot_start": {
                        "type": "string",
                        "description": "Appointment start time in ISO8601 format (e.g., 2025-11-14T14:00:00+00:00). MUST be copied exactly from check_availability result. Must be in the future."
                    },
                    "slot_end": {
                        "type": "string",
                        "description": "Appointment end time in ISO8601 format (e.g., 2025-11-14T14:30:00+00:00). MUST be exactly 30 minutes after slot_start. Copy exactly from check_availability result."
                    },
                    "phone": {
                        "type": "string",
                        "description": "Patient's phone number"
                    },
                    "email": {
                        "type": "string",
                        "description": "Patient's email address"
                    },
                    "insurance": {
                        "type": "string",
                        "description": "Insurance provider name (optional)"
                    }
                },
                "required": ["name", "reason", "slot_start", "slot_end", "phone", "email"],
                "additionalProperties": False
            }
        }
    )
    async def book_appointment(raw_arguments: dict):
        """Book a new appointment with patient details."""
        logger.info("LiveKit calling book_appointment")
        return await router.dispatch("book_appointment", {
            "name": raw_arguments["name"],
            "reason": raw_arguments["reason"],
            "slot_start": raw_arguments["slot_start"],
            "slot_end": raw_arguments["slot_end"],
            "phone": raw_arguments["phone"],
            "email": raw_arguments["email"],
            "insurance": raw_arguments.get("insurance"),
        })

    @function_tool(
        raw_schema={
            "name": "cancel_appointment",
            "description": "Cancel an existing appointment",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Full name of the patient"
                    },
                    "slot_start": {
                        "type": "string",
                        "description": "Appointment start time in ISO8601 format"
                    },
                    "reason": {
                        "type": "string",
                        "description": "Reason for cancellation (optional)"
                    }
                },
                "required": ["name", "slot_start"],
                "additionalProperties": False
            }
        }
    )
    async def cancel_appointment(raw_arguments: dict):
        """Cancel an existing appointment."""
        logger.info("LiveKit calling cancel_appointment")
        return await router.dispatch("cancel_appointment", {
            "name": raw_arguments["name"],
            "slot_start": raw_arguments["slot_start"],
            "reason": raw_arguments.get("reason"),
        })

    @function_tool(
        raw_schema={
            "name": "reschedule_appointment",
            "description": "Reschedule an existing appointment to a new time",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Full name of the patient"
                    },
                    "current_slot_start": {
                        "type": "string",
                        "description": "Current appointment start time in ISO8601 format"
                    },
                    "new_slot_start": {
                        "type": "string",
                        "description": "New appointment start time in ISO8601 format"
                    },
                    "new_slot_end": {
                        "type": "string",
                        "description": "New appointment end time in ISO8601 format"
                    }
                },
                "required": ["name", "current_slot_start", "new_slot_start", "new_slot_end"],
                "additionalProperties": False
            }
        }
    )
    async def reschedule_appointment(raw_arguments: dict):
        """Reschedule an existing appointment to a new time."""
        logger.info("LiveKit calling reschedule_appointment")
        return await router.dispatch("reschedule_appointment", {
            "name": raw_arguments["name"],
            "current_slot_start": raw_arguments["current_slot_start"],
            "new_slot_start": raw_arguments["new_slot_start"],
            "new_slot_end": raw_arguments["new_slot_end"],
        })

    @function_tool(
        raw_schema={
            "name": "get_upcoming_appointments",
            "description": "Get all upcoming confirmed appointments for a patient starting from now. Use this when the caller asks about their upcoming or future appointments.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Full name of the patient"
                    }
                },
                "required": ["name"],
                "additionalProperties": False
            }
        }
    )
    async def get_upcoming_appointments(raw_arguments: dict):
        """Get upcoming confirmed appointments for a patient."""
        logger.info("LiveKit calling get_upcoming_appointments")
        return await router.dispatch("get_upcoming_appointments", {
            "name": raw_arguments["name"],
        })

    @function_tool(
        raw_schema={
            "name": "get_hours",
            "description": "Get clinic operating hours",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False
            }
        }
    )
    async def get_hours(raw_arguments: dict):
        """Get clinic operating hours."""
        logger.info("LiveKit calling get_hours")
        return await router.dispatch("get_hours", {})

    @function_tool(
        raw_schema={
            "name": "get_location",
            "description": "Get clinic location and address",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False
            }
        }
    )
    async def get_location(raw_arguments: dict):
        """Get clinic location and address."""
        logger.info("LiveKit calling get_location")
        return await router.dispatch("get_location", {})

    @function_tool(
        raw_schema={
            "name": "get_insurance_supported",
            "description": "Check if an insurance provider is supported",
            "parameters": {
                "type": "object",
                "properties": {
                    "provider": {
                        "type": "string",
                        "description": "Insurance provider name"
                    }
                },
                "required": ["provider"],
                "additionalProperties": False
            }
        }
    )
    async def get_insurance_supported(raw_arguments: dict):
        """Check if an insurance provider is supported."""
        logger.info("LiveKit calling get_insurance_supported")
        return await router.dispatch("get_insurance_supported", {
            "provider": raw_arguments["provider"]
        })

    @function_tool(
        raw_schema={
            "name": "escalate_to_human",
            "description": "Escalate the conversation to a human agent",
            "parameters": {
                "type": "object",
                "properties": {
                    "reason": {
                        "type": "string",
                        "description": "Reason for escalation"
                    },
                    "callback_number": {
                        "type": "string",
                        "description": "Callback phone number (optional)"
                    }
                },
                "required": ["reason"],
                "additionalProperties": False
            }
        }
    )
    async def escalate_to_human(raw_arguments: dict):
        """Escalate the conversation to a human agent."""
        logger.info("LiveKit calling escalate_to_human")
        return await router.dispatch("escalate_to_human", {
            "reason": raw_arguments["reason"],
            "callback_number": raw_arguments.get("callback_number"),
        })

    @function_tool(
        raw_schema={
            "name": "send_confirmation",
            "description": "Send appointment confirmation via SMS or email",
            "parameters": {
                "type": "object",
                "properties": {
                    "channel": {
                        "type": "string",
                        "description": "Confirmation method: 'sms' or 'email'"
                    },
                    "address": {
                        "type": "string",
                        "description": "Phone number (for SMS) or email address (for email)"
                    },
                    "message": {
                        "type": "string",
                        "description": "Confirmation message to send"
                    }
                },
                "required": ["channel", "address", "message"],
                "additionalProperties": False
            }
        }
    )
    async def send_confirmation(raw_arguments: dict):
        """Send appointment confirmation via SMS or email."""
        logger.info("LiveKit calling send_confirmation")
        return await router.dispatch("send_confirmation", {
            "channel": raw_arguments["channel"],
            "address": raw_arguments["address"],
            "message": raw_arguments["message"],
        })

    return [
        check_availability,
        book_appointment,
        cancel_appointment,
        reschedule_appointment,
        get_upcoming_appointments,
        get_hours,
        get_location,
        get_insurance_supported,
        escalate_to_human,
        send_confirmation,
    ]