from dotenv import load_dotenv
import time
import logging

from livekit import agents, rtc
from livekit.agents import AgentSession, Agent, RoomInputOptions, llm
from livekit.plugins import openai
try:
    from livekit.plugins import noise_cancellation
except Exception:
    noise_cancellation = None
from tools.router import ToolRouter
from tools.handlers import register_handlers

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv(".env.local")
load_dotenv("../agent-starter-node/.env.local")

SYSTEM_PROMPT = (
    "You are a real-time voice assistant for a medical clinic that answers calls via LiveKit.\n"
    "Primary goals: schedule, reschedule, cancel appointments; provide concise clinic info; escalate to a human when requested or when safety triggers fire. The user may interrupt (barge-in) at any time—be responsive and natural.\n\n"
    "Conversation Contract\n"
    "1) Tone & pacing: Warm, concise, professional. Prefer short sentences. Insert brief natural pauses when confirming critical details.\n"
    "2) Turn-taking: When the caller stops speaking, start responding quickly, in short fragments. If the caller speaks while you talk, stop and listen.\n"
    "3) Transparency: If unsure, ask a direct clarifying question instead of guessing.\n"
    "4) No medical advice: Do not diagnose, prescribe, or provide treatment advice.\n"
    "5) PII/PHI: Only ask for needed fields (name, reason, preferred time, insurance, phone, email). Confirm before storing or sending confirmations.\n\n"
    "Supported Intents\n"
    "- APPOINTMENT_BOOKING — Collect name, reason, preferred time, insurance, phone, email → check availability → propose slot → confirm → book → send confirmation.\n"
    "- APPOINTMENT_CANCELLATION — Collect name + date/time (optional reason) → confirm → cancel → confirm done → offer to reschedule later.\n"
    "- APPOINTMENT_RESCHEDULING — Collect name + current slot + new preference → propose alternatives → confirm → reschedule → send updated confirmation.\n"
    "- GENERAL_INFO — Answer brief factual questions (hours, location, insurance) and offer to help book.\n"
    "- ESCALATE_TO_HUMAN — On request or urgent symptoms, connect to staff. If urgent symptoms are mentioned, advise calling emergency services first.\n\n"
    "Opening & Guidance\n"
    "- Start with a friendly greeting and scope (appointments & quick info). Identify intent quickly; keep on track; handle objections politely (e.g., offer secure follow-up if they won’t share insurance now).\n\n"
    "Safety & Escalation\n"
    "- If emergency symptoms are mentioned (e.g., chest pain, trouble breathing, stroke signs): Say: ‘This sounds urgent. Please hang up and dial emergency services immediately, or I can connect you to a staff member now.’ Immediately escalate_to_human. Do not continue routine booking.\n"
    "- On explicit requests to speak with staff, escalate and promise a callback if disconnected.\n\n"
    "Data Collection & Confirmation\n"
    "- Always confirm critical details (name spelling if low confidence, date/time, contact). Repeat date/time in a friendly way. Offer nearest alternatives if unavailable. Summarize actions and ask yes/no before booking/cancel/reschedule. After success, confirm and state a confirmation will be sent.\n\n"
    "Responses: Style for Real-Time TTS\n"
    "- Prefer one sentence at a time when streaming. Use brief acknowledgments (‘Got it’, ‘Thanks, Sarah’). Avoid long monologues; quickly prompt for the next field.\n\n"
    "Tool Calling (contract)\n"
    "- When needed, call tools with strict JSON. Never fabricate outputs. Validate required slots before booking/cancel/reschedule. Offer top 1–2 slots first. If a tool fails, apologize and retry once; otherwise offer escalation.\n"
)


class LatencyTracker:

    def __init__(self):
        self.last_user_speech_end = None
        self.latencies = []
        self.turn_count = 0

    def record_user_speech_end(self):
        self.last_user_speech_end = time.time()

    def record_agent_response_start(self):
        if self.last_user_speech_end:
            latency = time.time() - self.last_user_speech_end
            self.latencies.append(latency)
            self.turn_count += 1

            status = " EXCELLENT" if latency < 1.0 else "  WARNING" if latency < 2.0 else " POOR"
            logger.info(f"\n{'='*60}")
            logger.info(f" LATENCY MEASUREMENT #{self.turn_count}")
            logger.info(f"   Response Time: {latency:.3f}s - {status}")
            logger.info(f"   Target: < 1.000s")

            if latency < 1.0:
                logger.info(
                    f"   Status: Under target by {(1.0 - latency):.3f}s ✓")
            else:
                logger.info(
                    f"   Status: Over target by {(latency - 1.0):.3f}s ✗")

            if len(self.latencies) > 1:
                avg = sum(self.latencies) / len(self.latencies)
                min_lat = min(self.latencies)
                max_lat = max(self.latencies)
                logger.info(f"\n STATISTICS:")
                logger.info(f"   Average: {avg:.3f}s")
                logger.info(f"   Best:    {min_lat:.3f}s")
                logger.info(f"   Worst:   {max_lat:.3f}s")
                logger.info(f"   Turns:   {len(self.latencies)}")

                under_1s = sum(1 for l in self.latencies if l < 1.0)
                success_rate = (under_1s / len(self.latencies)) * 100
                logger.info(f"   Success Rate: {success_rate:.1f}% (under 1s)")

            logger.info(f"{'='*60}\n")

            self.last_user_speech_end = None
            return latency
        return None


class Assistant(Agent):
    def __init__(self, latency_tracker: LatencyTracker) -> None:
        super().__init__(instructions=SYSTEM_PROMPT)
        self.latency_tracker = latency_tracker


async def entrypoint(ctx: agents.JobContext):
    latency_tracker = LatencyTracker()
    logger.info(
        " Initializing Medical Clinic Voice Agent with Latency Monitoring...")

    tts_instance = openai.TTS(voice="nova")
    session = AgentSession(
        stt="deepgram/nova-2",
        llm="openai/gpt-4o-mini",
        tts=tts_instance,
    )
    original_agent = Assistant(latency_tracker)
    original_generate = session.generate_reply
    last_input_time = [None]

    async def tracked_generate(*args, **kwargs):
        """Wrapper to track when agent starts responding"""
        if last_input_time[0] is None:
            last_input_time[0] = time.time()
            logger.info(" USER INPUT RECEIVED - Starting to process...")

        logger.info(" AGENT GENERATING RESPONSE...")
        result = await original_generate(*args, **kwargs)
        if last_input_time[0]:
            latency = time.time() - last_input_time[0]
            latency_tracker.latencies.append(latency)
            latency_tracker.turn_count += 1

            status = " EXCELLENT" if latency < 1.0 else "  WARNING" if latency < 2.0 else " POOR"
            logger.info(f"\n{'='*60}")
            logger.info(f" LATENCY MEASUREMENT #{latency_tracker.turn_count}")
            logger.info(f"   Response Time: {latency:.3f}s - {status}")
            logger.info(f"   Target: < 1.000s")

            if latency < 1.0:
                logger.info(
                    f"   Status: Under target by {(1.0 - latency):.3f}s ✓")
            else:
                logger.info(
                    f"   Status: Over target by {(latency - 1.0):.3f}s ✗")
            if len(latency_tracker.latencies) > 1:
                avg = sum(latency_tracker.latencies) / \
                    len(latency_tracker.latencies)
                min_lat = min(latency_tracker.latencies)
                max_lat = max(latency_tracker.latencies)
                logger.info(f"\n STATISTICS:")
                logger.info(f"   Average: {avg:.3f}s")
                logger.info(f"   Best:    {min_lat:.3f}s")
                logger.info(f"   Worst:   {max_lat:.3f}s")
                logger.info(f"   Turns:   {len(latency_tracker.latencies)}")

                under_1s = sum(1 for l in latency_tracker.latencies if l < 1.0)
                success_rate = (
                    under_1s / len(latency_tracker.latencies)) * 100
                logger.info(f"   Success Rate: {success_rate:.1f}% (under 1s)")

            logger.info(f"{'='*60}\n")

            last_input_time[0] = None

        return result
    session.generate_reply = tracked_generate
    await session.start(
        room=ctx.room,
        agent=original_agent,
        room_input_options=RoomInputOptions(
            noise_cancellation=(noise_cancellation.BVC()
                                if noise_cancellation is not None
                                else None),
        ),
    )

    logger.info("Agent ready! Monitoring latency for all interactions.\n")
    await session.generate_reply(
        instructions="Greet briefly and ask how you can help."
    )
    router = ToolRouter()
    register_handlers(router)

if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
