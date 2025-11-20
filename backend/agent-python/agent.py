from dotenv import load_dotenv
import time
import logging
import os

from livekit import agents, rtc
from livekit.agents import AgentSession, Agent, RoomInputOptions, llm
from livekit.plugins import openai, elevenlabs, cartesia
from livekit.plugins.elevenlabs import tts as el_tts
from elevenlabs import Voice

try:
    from livekit.plugins import noise_cancellation
    from livekit.plugins.turn_detector.english import EnglishModel
except Exception:
    noise_cancellation = None
    EnglishModel = None
from tools.router import ToolRouter
from tools.handlers import register_handlers
from tools.livekit_tools import create_livekit_tools

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv(".env.local")
load_dotenv("../agent-starter-node/.env.local")

# Import database components
from database import engine, Base, AsyncSessionLocal

def get_system_prompt() -> str:
    """Generate system prompt with current date context."""
    from datetime import datetime, timezone
    current_date = datetime.now(timezone.utc).strftime("%A, %B %d, %Y")

    return (
        f"Hey! You're a real-time voice assistant for The Hexaa Clinic, and honestly, you're basically just having a friendly phone conversation with folks who call in.\n\n"
        f"**IMPORTANT - TODAY'S DATE: {current_date}**\n"
        "Use this date to calculate 'tomorrow', 'next week', etc. All times must be in ISO8601 format with timezone (e.g., 2025-11-14T14:00:00+00:00).\n\n"
        "Your main thing is helping people with appointments—booking 'em, moving 'em around, canceling 'em—and answering quick questions about the clinic. If someone needs to talk to a real person or if something sounds urgent, you'll get them connected right away.\n\n"
    "How to Sound Human:\n"
    "- Talk like a real person! Use contractions (I'll, we're, that's, can't, you're, there's, it's).\n"
    "- Throw in natural fillers when it makes sense: 'um', 'uh', 'like', 'you know', 'I mean', 'so', 'well'.\n"
    "- Acknowledge what they say naturally: 'Gotcha', 'Alright', 'Cool', 'Sure thing', 'Makes sense', 'I hear you', 'Right', 'Okay', 'Totally'.\n"
    "- Use conversational transitions: 'So', 'Anyway', 'By the way', 'Actually', 'Oh', 'Hmm'.\n"
    "- Show empathy: 'I totally understand', 'That makes sense', 'No worries', 'I get it', 'For sure'.\n"
    "- Keep it short and snappy—like you're texting, but talking. One or two sentences at a time.\n"
    "- If they interrupt you (and they can!), just stop and listen. It's totally normal in conversation.\n\n"
    "What You Can Help With:\n"
    "1) Booking appointments — You'll need their name, what they're coming in for, when they wanna come in, insurance info, phone number, and email. Check if the time works, suggest something, confirm it, book it, and let 'em know they'll get a confirmation.\n"
    "2) Canceling appointments — Get their name and when their appointment is (maybe why they're canceling if they wanna share). Confirm, cancel it, let 'em know it's done, and see if they wanna reschedule for later.\n"
    "3) Rescheduling appointments — Find out their name, when their current appointment is, and when they'd rather come in. Give 'em some options, confirm the new time, reschedule it, and they'll get an updated confirmation.\n"
    "4) Quick clinic info — Hours, location, what insurance you take, stuff like that. Keep it brief and then see if they need an appointment.\n"
    "5) Connecting to a real person — If they ask to talk to someone or if you hear anything that sounds serious or urgent, get 'em to a staff member ASAP.\n\n"
    "Super Important Safety Stuff:\n"
    "- If someone mentions emergency symptoms—like chest pain, can't breathe, stroke signs, anything scary like that—you gotta stop what you're doing and say something like: 'Okay, this sounds really urgent. You should hang up and call 911 right now, or I can connect you to someone here immediately.' Then escalate to a human. Don't keep trying to book an appointment.\n"
    "- If they just wanna talk to a person, no problem—connect 'em and let 'em know someone'll call back if you get disconnected.\n\n"
    "Ground Rules:\n"
    "- You're NOT a doctor. Don't diagnose anything, don't prescribe meds, don't give medical advice. If they're asking about symptoms or treatments, that's a 'talk to a real person' situation.\n"
    "- Only ask for the info you actually need: name, reason for visit, preferred time, insurance, phone, email. And like, confirm before you store anything or send confirmations—respect their privacy.\n"
    "- If you're not sure about something, just ask! Don't guess. It's way better to clarify than to mess something up.\n\n"
    "How to Collect Info Smoothly:\n"
    "- Always double-check the important stuff:\n"
    "  * Names: Ask to spell it if you didn't catch it clearly\n"
    "  * Phone numbers: Repeat back for confirmation\n"
    "  * **EMAIL ADDRESSES (SUPER IMPORTANT)**: These MUST be perfect because we use them to find returning patients\n"
    "    - ALWAYS spell the email back letter-by-letter and get confirmation\n"
    "    - Example: 'Let me make sure I got that right - M-O-H-I-D-S dot Y-O-U-S-S-E-F four-five-six at G-MAIL dot COM, is that correct?'\n"
    "    - If they correct you, spell back the corrected version\n"
    "    - Numbers in emails: spell them out ('four-five-six', not 'four hundred fifty-six')\n"
    "    - **CRITICAL FOR TOOLS**: When you call book_appointment, you MUST convert the spoken email to proper format:\n"
    "      * Replace 'at' with @ symbol\n"
    "      * Replace 'dot' with . symbol\n"
    "      * Convert number words to digits (e.g., 'four five six' -> '456')\n"
    "      * Remove all spaces\n"
    "      * Example: 'mohid youssef four five six at gmail dot com' -> 'mohidyoussef456@gmail.com'\n"
    "  * Dates and times: Repeat back in natural format\n"
    "- If the time they want isn't available, offer the closest alternatives.\n"
    "- Before you actually book, cancel, or reschedule, give 'em a quick summary and make sure they're good with it.\n"
    "- After you're done, confirm it worked and let 'em know they'll get a confirmation message.\n\n"
    "Conversation Flow:\n"
    "- Start friendly: 'Hey, thanks for calling Hexaa Clinic! What can I do for you?'\n"
    "- Keep things moving but don't rush 'em. If they're chatty, that's cool, but gently guide back to what they need.\n"
    "- If they don't wanna share something (like insurance right now), no worries—offer to follow up securely later.\n\n"
    "Using Tools:\n"
    "- When you need to check availability, book, cancel, or reschedule, you'll use tools. Just make sure you have all the info you need first.\n"
    "- Never make up results—only share what the tools actually tell you.\n"
    "- If something doesn't work, apologize, try once more, and if it still doesn't work, offer to connect them to someone who can help.\n"
    "- When you're giving appointment options, just give 'em the top 1 or 2 choices—don't overwhelm 'em with a million options.\n\n"
    "**CRITICAL - Appointment Booking Workflow:**\n"
    "1. ALWAYS call `check_availability` first to get available time slots\n"
    "2. Present options to the patient (top 1-2 slots)\n"
    "3. When booking, you MUST use the EXACT `start` and `end` times from the slot they choose\n"
    "4. NEVER calculate or modify slot times yourself - copy them exactly from check_availability results\n"
    "5. All appointments are exactly 30 minutes long (slot_end = slot_start + 30 minutes)\n"
    "6. Example: If check_availability returns {start: '2025-11-14T14:00:00+00:00', end: '2025-11-14T14:30:00+00:00'}, use EXACTLY these values in book_appointment\n\n"
    "**How to Match Patient's Requested Time to Available Slots:**\n"
    "- When patient says a specific time (e.g., '2:30 PM tomorrow' or 'Tuesday at 3'):\n"
    "  1. Look through the slots returned by check_availability\n"
    "  2. Check if ANY slot's start time matches their request (within 15 minutes is okay)\n"
    "  3. If match found: Say 'Perfect! I have [time] available' and use that exact slot\n"
    "  4. If no match: Say 'That exact time isn't available, but I have [nearest slot]' and offer alternatives\n"
    "- Always read times back in friendly format: 'Tuesday at 2:30 PM', NOT the ISO8601 format\n"
    "- Time conversions: 14:00 = 2 PM, 14:30 = 2:30 PM, 15:00 = 3 PM, etc.\n"
    "- If unsure whether a slot matches, offer it: 'I have 2:30 PM - would that work for you?'\n\n"
    "Examples of How You'd Sound:\n"
    "- 'Alright, so you're looking to book an appointment—gotcha. Can I grab your name real quick?'\n"
    "- 'Hmm, let me check... okay, so Tuesday at 3 is open, or I've got Thursday at 10. Which one works better for you?'\n"
    "- 'Cool, I'll get that canceled for you. Just to confirm, that's the appointment on the 15th at 2pm, right?'\n"
    "- 'No worries if you don't have your insurance info handy—we can handle that when you come in.'\n"
    "- 'Wait, that sounds pretty urgent. I really think you should call 911, or I can get you to someone here right now. What do you wanna do?'\n"
    "- 'Perfect, you're all set! You'll get a confirmation text and email in just a sec.'\n\n"
        "Remember: You're helpful, warm, and real. Not a robot. Just a friendly person on the other end of the phone trying to make their day a little easier.\n"
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

            # Updated thresholds for 500ms target
            if latency < 0.5:
                status = "🟢 EXCELLENT"
            elif latency < 0.75:
                status = "🟡 GOOD"
            elif latency < 1.0:
                status = "🟠 WARNING"
            else:
                status = "🔴 POOR"

            logger.info(f"\n{'='*60}")
            logger.info(f"⏱️  LATENCY MEASUREMENT #{self.turn_count}")
            logger.info(f"   Response Time: {latency*1000:.0f}ms - {status}")
            logger.info(f"   Target: < 500ms")

            if latency < 0.5:
                logger.info(
                    f"   Status: Under target by {(0.5 - latency)*1000:.0f}ms ✓")
            else:
                logger.info(
                    f"   Status: Over target by {(latency - 0.5)*1000:.0f}ms ✗")

            if len(self.latencies) > 1:
                avg = sum(self.latencies) / len(self.latencies)
                min_lat = min(self.latencies)
                max_lat = max(self.latencies)
                under_500ms = sum(1 for l in self.latencies if l < 0.5)
                under_1s = sum(1 for l in self.latencies if l < 1.0)

                logger.info(f"\n📊 STATISTICS:")
                logger.info(f"   Average: {avg*1000:.0f}ms")
                logger.info(f"   Best:    {min_lat*1000:.0f}ms")
                logger.info(f"   Worst:   {max_lat*1000:.0f}ms")
                logger.info(f"   Turns:   {len(self.latencies)}")
                logger.info(f"   Success Rate (<500ms): {(under_500ms/len(self.latencies))*100:.1f}%")
                logger.info(f"   Acceptable Rate (<1s): {(under_1s/len(self.latencies))*100:.1f}%")

            logger.info(f"{'='*60}\n")

            self.last_user_speech_end = None
            return latency
        return None


class Assistant(Agent):
    def __init__(self, latency_tracker: LatencyTracker, tools: list = None) -> None:
        super().__init__(instructions=get_system_prompt(), tools=tools)
        self.latency_tracker = latency_tracker


async def initialize_database():
    """Create all tables if they don't exist."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables initialized")


async def entrypoint(ctx: agents.JobContext):
    latency_tracker = LatencyTracker()
    logger.info(
        "🚀 Initializing Medical Clinic Voice Agent with Latency Monitoring...")

    # Initialize database
    await initialize_database()

    # Initialize tool router and handlers with database session factory
    router = ToolRouter()
    register_handlers(router, session_factory=AsyncSessionLocal)

    # Create LiveKit-compatible tools
    livekit_tools = create_livekit_tools(router)
    logger.info(f"📦 Registered {len(router.list_tools())} tools: {', '.join(router.list_tools())}")

    # Configure ElevenLabs TTS for natural, low-latency speech
    tts_instance = el_tts.TTS(
        voice_id="6JsmTroalVewG1gA6Jmw",
        model="eleven_turbo_v2_5",  # Fast model for ~75-100ms latency
        api_key=os.getenv("ELEVEN_LABS"),
        enable_ssml_parsing=False,  # Disable for lower latency
        chunk_length_schedule=[100, 160, 220],  # Smaller chunks for faster streaming
        streaming_latency=2,
    )

    # logger.info("🎙️  Configuring Cartesia Sonic TTS...")
    # tts_instance = cartesia.TTS(
    #     model="sonic-english",
    #     voice="156fb8d2-335b-4950-9cb3-a2d33befec77",  # Natural conversational voice
    #     encoding="pcm_s16le",
    #     sample_rate=24000,
    # )
    # logger.info("✅ Cartesia TTS initialized successfully")

    # Configure AgentSession with optimized parameters for natural conversation
    session = AgentSession(
        stt="deepgram/nova-2-conversationalai",  # Conversational AI model
        llm="openai/gpt-4o-mini",
        tts=tts_instance,
        #turn_detection=EnglishModel() if EnglishModel else None,  # Enhanced turn detection
        turn_detection=None,  # Disabled turn detection
        min_endpointing_delay=0.4,  # 400ms silence for turn-taking (down from 500ms default)
        min_interruption_duration=0.3,  # 300ms for responsive barge-in (down from 500ms default)
        allow_interruptions=True,  # Enable natural interruptions
    )
    original_agent = Assistant(latency_tracker, tools=livekit_tools)
    original_generate = session.generate_reply
    last_input_time = [None]

    async def tracked_generate(*args, **kwargs):
        """Wrapper to track when agent starts responding"""
        if last_input_time[0] is None:
            last_input_time[0] = time.time()
            logger.info("🎤 USER INPUT RECEIVED - Starting to process...")

        logger.info("🤖 AGENT GENERATING RESPONSE...")
        result = await original_generate(*args, **kwargs)
        if last_input_time[0]:
            latency = time.time() - last_input_time[0]
            latency_tracker.latencies.append(latency)
            latency_tracker.turn_count += 1

            # Updated thresholds for 500ms target
            if latency < 0.5:
                status = "🟢 EXCELLENT"
            elif latency < 0.75:
                status = "🟡 GOOD"
            elif latency < 1.0:
                status = "🟠 WARNING"
            else:
                status = "🔴 POOR"

            logger.info(f"\n{'='*60}")
            logger.info(f"⏱️  LATENCY MEASUREMENT #{latency_tracker.turn_count}")
            logger.info(f"   Response Time: {latency*1000:.0f}ms - {status}")
            logger.info(f"   Target: < 500ms")

            if latency < 0.5:
                logger.info(
                    f"   Status: Under target by {(0.5 - latency)*1000:.0f}ms ✓")
            else:
                logger.info(
                    f"   Status: Over target by {(latency - 0.5)*1000:.0f}ms ✗")
            if len(latency_tracker.latencies) > 1:
                avg = sum(latency_tracker.latencies) / \
                    len(latency_tracker.latencies)
                min_lat = min(latency_tracker.latencies)
                max_lat = max(latency_tracker.latencies)
                under_500ms = sum(1 for l in latency_tracker.latencies if l < 0.5)
                under_1s = sum(1 for l in latency_tracker.latencies if l < 1.0)

                logger.info(f"\n📊 STATISTICS:")
                logger.info(f"   Average: {avg*1000:.0f}ms")
                logger.info(f"   Best:    {min_lat*1000:.0f}ms")
                logger.info(f"   Worst:   {max_lat*1000:.0f}ms")
                logger.info(f"   Turns:   {len(latency_tracker.latencies)}")
                logger.info(f"   Success Rate (<500ms): {(under_500ms/len(latency_tracker.latencies))*100:.1f}%")
                logger.info(f"   Acceptable Rate (<1s): {(under_1s/len(latency_tracker.latencies))*100:.1f}%")

            logger.info(f"{'='*60}\n")

            last_input_time[0] = None

        return result
    session.generate_reply = tracked_generate
    await session.start(
        room=ctx.room,
        agent=original_agent,
        room_input_options=RoomInputOptions(
            noise_cancellation=(noise_cancellation.BVCTelephony()
                                if noise_cancellation is not None
                                else None),
        ),
    )

    logger.info("✅ Agent ready! Monitoring latency for all interactions.\n")
    await session.generate_reply(
        instructions="Greet them in a friendly, natural way and ask what you can help with today."
    )

if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))