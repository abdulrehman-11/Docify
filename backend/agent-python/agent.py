from dotenv import load_dotenv
import time
import logging
import os
import platform
import asyncio

# Load environment first
load_dotenv(".env.local")
load_dotenv("../agent-starter-node/.env.local")

# CRITICAL FIX: Disable inference executor on non-macOS platforms (Render uses Linux)
# This prevents timeout errors during deployment on platforms without GPU/ML support
if platform.system() != "Darwin":  # Disable on Linux (Render) and Windows
    os.environ["LIVEKIT_AGENT_INFERENCE_EXECUTOR_DISABLED"] = "1"
    print("🔧 Inference executor disabled for deployment environment")

from livekit import agents, rtc
from livekit.agents import AgentSession, Agent, RoomInputOptions, llm, WorkerOptions, WorkerType, JobContext
from livekit.plugins import openai
from livekit.plugins import elevenlabs
from livekit.plugins.elevenlabs import tts as el_tts

# Only load these plugins if inference executor is enabled (macOS only)
# Prevents dependency issues on Render deployment
if platform.system() == "Darwin":
    try:
        from livekit.plugins import noise_cancellation
        from livekit.plugins.turn_detector.english import EnglishModel
    except Exception:
        noise_cancellation = None
        EnglishModel = None
else:
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

from database import engine, Base, AsyncSessionLocal


LIVEKIT_SIP_NUMBER = "+15184006003"

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
        "**CRITICAL SPEAKING RULES FOR TIMES AND NUMBERS:**\n"
        "- When saying appointment times, SLOW DOWN and speak CLEARLY with pauses:\n"
        "  * WRONG: 'ninethirtyamtotenam' (too fast, runs together)\n"
        "  * RIGHT: 'nine... thirty... A M... to... ten... A M' (clear pauses between each part)\n"
        "- When saying phone numbers, add pauses between digit groups:\n"
        "  * WRONG: '5551234567' (too fast)\n"
        "  * RIGHT: '555... 123... 4567' (pause after area code and prefix)\n"
        "- When listing multiple time slots, pause between each option:\n"
        "  * Say: 'I have... nine thirty A M... [pause]... or... two P M... [pause]... which works better?'\n"
        "- Use words to create natural spacing: 'around', 'at about', 'sometime around'\n"
        "  * Instead of: '9:30 AM'\n"
        "  * Say: 'around nine thirty in the morning'\n\n"
        "What You Can Help With:\n"
        "1) Booking appointments — You'll need their name, what they're coming in for, when they wanna come in, insurance info, phone number, and email. Check if the time works, suggest something, confirm it, book it, and let 'em know they'll get a confirmation.\n"
        "2) Canceling appointments — Get their name and when their appointment is (maybe why they're canceling if they wanna share). Confirm, cancel it, let 'em know it's done, and see if they wanna reschedule for later.\n"
        "3) Rescheduling appointments — Find out their name, when their current appointment is, and when they'd rather come in. Give 'em some options, confirm the new time, reschedule it, and they'll get an updated confirmation.\n"
        "4) Quick clinic info — Hours, location, what insurance you take, stuff like that. Keep it brief and then see if they need an appointment.\n"
        "5) Connecting to a real person — If they ask to talk to someone or if you hear anything that sounds serious or urgent, get 'em to a staff member ASAP.\n\n"
        "**WHAT YOU SHOULD NOT HELP WITH:**\n"
        "- Questions about receptionist jobs, salaries, careers, or employment at the clinic\n"
        "- Human resources or hiring questions\n"
        "- Staff schedules or internal clinic operations\n"
        "- Medical advice, diagnosis, or treatment recommendations\n"
        "- Billing disputes or detailed insurance claims\n"
        "For ANY of these topics, politely say: 'That's not something I can help with over the phone, but I can connect you with someone from our office who can assist you. Would you like me to do that?'\n\n"
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
        "  * Phone numbers: Repeat back for confirmation with pauses (555... 123... 4567)\n"
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
        "  * Dates and times: Repeat back in natural format with clear pauses\n"
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
        "**CRITICAL - Appointment Verification and Management:**\n"
        "1. **NEVER assume an appointment exists** - ALWAYS use lookup tools to verify first\n"
        "2. **Before updating/canceling**: MUST call the appointment lookup tool with their name and date to confirm it exists\n"
        "3. **If lookup returns no results**: Say 'I'm not seeing an appointment under that name for that date. Let me double-check - can you confirm the name and date?'\n"
        "4. **NEVER say 'yes, I see your appointment' unless the tool confirms it exists**\n"
        "5. **When checking multiple appointments**: Use the lookup tool and report the EXACT number found - 'I see you have 2 appointments scheduled' or 'I don't see any appointments under that name'\n"
        "6. **Name verification for existing appointments**:\n"
        "   - When updating an appointment, use the EXACT name from the database lookup result\n"
        "   - NEVER change the patient's name in the database unless they explicitly request a name correction\n"
        "   - If you hear a slightly different pronunciation (like 'Alex' vs 'Alek'), use the name that's ALREADY in the system\n"
        "   - Only ask to confirm the spelling if it's a NEW patient or if they say 'my name is actually spelled...'\n\n"
        "**CRITICAL - Appointment Booking Workflow:**\n"
        "1. ALWAYS call `check_availability` first to get available time slots\n"
        "2. **Verify the results before responding**:\n"
        "   - If check_availability returns EMPTY slots or NO slots: Say 'Let me check another day' and try a different date\n"
        "   - If check_availability returns slots: Present them clearly\n"
        "   - NEVER say 'that time isn't available' without calling check_availability first\n"
        "3. Present options to the patient (top 1-2 slots) with CLEAR PAUSES\n"
        "4. When booking, you MUST use the EXACT `start` and `end` times from the slot they choose\n"
        "5. NEVER calculate or modify slot times yourself - copy them exactly from check_availability results\n"
        "6. All appointments are exactly 30 minutes long (slot_end = slot_start + 30 minutes)\n"
        "7. Example: If check_availability returns {start: '2025-11-14T14:00:00+00:00', end: '2025-11-14T14:30:00+00:00'}, use EXACTLY these values in book_appointment\n\n"
        "**How to Match Patient's Requested Time to Available Slots:**\n"
        "- When patient says a specific time (e.g., '2:30 PM tomorrow' or 'Tuesday at 3'):\n"
        "  1. FIRST call check_availability for that date\n"
        "  2. Look through the slots returned by check_availability\n"
        "  3. Check if ANY slot's start time matches their request (within 15 minutes is okay)\n"
        "  4. If match found: Say 'Perfect! I have... [pause]... two thirty P M... available' and use that exact slot\n"
        "  5. If no match: Say 'That exact time isn't available, but I have... [pause]... [nearest slot]' and offer alternatives\n"
        "  6. If check_availability returns NO slots: Say 'I'm not seeing availability that day. Let me try another day for you.'\n"
        "- Always read times back in friendly format with pauses: 'Tuesday... at... two thirty P M', NOT the ISO8601 format\n"
        "- Time conversions: 14:00 = 2 PM, 14:30 = 2:30 PM, 15:00 = 3 PM, etc.\n"
        "- If unsure whether a slot matches, offer it: 'I have two thirty P M - would that work for you?'\n\n"
        "Examples of How You'd Sound:\n"
        "- 'Alright, so you're looking to book an appointment—gotcha. Can I grab your name real quick?'\n"
        "- 'Let me check what's available... [pause while checking]... okay, so I have... nine thirty A M on Tuesday... [pause]... or two P M on Thursday. Which one works better for you?'\n"
        "- 'Let me look up your appointment first... [pause]... okay, I see you have one scheduled for the 15th at 2 P M. You wanna cancel that one?'\n"
        "- 'Hmm, I'm not seeing an appointment under that name for that date. Can you double-check the date for me?'\n"
        "- 'Cool, I'll get that canceled for you. Just to confirm, that's the appointment on the 15th at... two P M... right?'\n"
        "- 'No worries if you don't have your insurance info handy—we can handle that when you come in.'\n"
        "- 'Wait, that sounds pretty urgent. I really think you should call 911, or I can get you to someone here right now. What do you wanna do?'\n"
        "- 'Perfect, you're all set! You'll get a confirmation text and email in just a sec.'\n"
        "- 'That's actually not something I handle—like questions about jobs or salaries. But I can connect you with our HR team if you'd like?'\n"
        "- 'Let me check how many appointments you have... [checking]... looks like you've got two scheduled: one on Monday and one on Wednesday.'\n\n"
        "Remember: You're helpful, warm, and real. Not a robot. Just a friendly person on the other end of the phone trying to make their day a little easier.\n"
        "- After successfully booking an appointment, the system automatically sends a confirmation email to the patient\n"
        "- You don't need to call any special tool - it happens automatically\n"
        "- Simply mention: 'Perfect! You're all set. You'll get a confirmation email in just a moment with all the details.'\n"
        "- If they ask about the email, reassure them: 'You should receive it within the next few minutes. Check your spam folder if you don't see it.'\n\n"
        
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
                logger.info(f"   Status: Under target by {(0.5 - latency)*1000:.0f}ms ✓")
            else:
                logger.info(f"   Status: Over target by {(latency - 0.5)*1000:.0f}ms ✗")

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
    logger.info("✅ Database tables initialized")


async def entrypoint(ctx: JobContext):
    """
    Main entrypoint for LiveKit SIP calls
    Number: +1 (518) 400-6003
    """
    
    # ===== DETECT INCOMING CALL =====
    is_phone_call = False
    caller_number = "Unknown"
    
    try:
        room = ctx.room
        if room:
            # SIP calls have room names starting with 'call-'
            if room.name and room.name.startswith('call-'):
                is_phone_call = True
                logger.info(f"📞 INCOMING CALL TO: {LIVEKIT_SIP_NUMBER}")
            
            # Try to get caller number from participants
            for participant in room.remote_participants.values():
                if participant.identity:
                    caller_number = participant.identity
                    logger.info(f"📱 From: {caller_number}")
                    break
    except Exception as e:
        logger.debug(f"Call detection info: {e}")
    
    latency_tracker = LatencyTracker()
    logger.info("🚀 Initializing Hexaa Clinic Voice Agent...")

    # Initialize database
    await initialize_database()

    # Initialize tools
    router = ToolRouter()
    register_handlers(router, session_factory=AsyncSessionLocal)
    livekit_tools = create_livekit_tools(router)
    logger.info(f"📦 Registered {len(router.list_tools())} tools")

    # ===== USE ELEVENLABS TTS =====
    logger.info("🎙️  Configuring ElevenLabs TTS...")
    
    # Debug: Check if API key is present (masked for security)
    eleven_labs_key = os.getenv("ELEVEN_LABS")
    if not eleven_labs_key:
        logger.error("❌ ELEVEN_LABS environment variable is NOT SET!")
        logger.error("   This will cause TTS to fail. Please set ELEVEN_LABS in Render environment.")
    else:
        masked_key = eleven_labs_key[:4] + "****" + eleven_labs_key[-4:] if len(eleven_labs_key) > 8 else "****"
        logger.info(f"✅ ELEVEN_LABS key found: {masked_key}")
    
    voice_id = "pzxut4zZz4GImZNlqQ3H"
    logger.info(f"   Using Voice ID: {voice_id}")
    logger.info(f"   Model: eleven_turbo_v2_5")
    
    tts_instance = el_tts.TTS(
        voice_id=voice_id, 
        model="eleven_turbo_v2_5",
        api_key=eleven_labs_key,
        enable_ssml_parsing=False,  
        chunk_length_schedule=[100, 160, 220], 
        streaming_latency=2,
    )
    logger.info("✅ ElevenLabs TTS initialized")
    logger.info("   Voice:  (Ultra-Realistic)")
    logger.info("   Latency: ~100-200ms")

   
    logger.info("⚙️  Configuring AgentSession...")
    
    session = AgentSession(
        stt="deepgram/nova-2-phonecall",  # Optimized for phone audio
        llm="openai/gpt-4o-mini",          # Fast and intelligent
        tts=tts_instance,
        turn_detection="vad",  # Use VAD (works on all platforms)
        min_endpointing_delay=0.3,
        min_interruption_duration=0.25,
        allow_interruptions=True,
    )
    
    logger.info("✅ AgentSession configured")
    
    original_agent = Assistant(latency_tracker, tools=livekit_tools)
    original_generate = session.generate_reply
    last_input_time = [None]

    async def tracked_generate(*args, **kwargs):
        """Wrapper to track when agent starts responding"""
        if last_input_time[0] is None:
            last_input_time[0] = time.time()
            logger.info("🎤 USER INPUT RECEIVED")

        logger.info("🤖 GENERATING RESPONSE...")
        result = await original_generate(*args, **kwargs)
        
        if last_input_time[0]:
            latency = time.time() - last_input_time[0]
            latency_tracker.latencies.append(latency)
            latency_tracker.turn_count += 1

            if latency < 0.5:
                status = "🟢 EXCELLENT"
            elif latency < 0.75:
                status = "🟡 GOOD"
            elif latency < 1.0:
                status = "🟠 WARNING"
            else:
                status = "🔴 POOR"

            logger.info(f"\n{'='*60}")
            logger.info(f"⏱️  LATENCY #{latency_tracker.turn_count}: {latency*1000:.0f}ms - {status}")
            
            if len(latency_tracker.latencies) > 1:
                avg = sum(latency_tracker.latencies) / len(latency_tracker.latencies)
                under_500ms = sum(1 for l in latency_tracker.latencies if l < 0.5)
                logger.info(f"📊 Avg: {avg*1000:.0f}ms | Success: {(under_500ms/len(latency_tracker.latencies))*100:.1f}%")
            
            logger.info(f"{'='*60}\n")
            last_input_time[0] = None

        return result
    
    session.generate_reply = tracked_generate
    
    # Start session
    await session.start(
        room=ctx.room,
        agent=original_agent,
        room_input_options=RoomInputOptions(
            noise_cancellation=None  # Disabled for Windows compatibility
        ),
    )

    logger.info("✅ Agent ready!")
    
    # Wait for participant connection (for phone calls)
    if is_phone_call:
        for _ in range(20):
            if len(ctx.room.remote_participants) > 0:
                logger.info(f"✅ Caller connected")
                break
            await asyncio.sleep(0.1)
        await asyncio.sleep(0.2)
    
    # Generate friendly greeting
    await session.generate_reply(
        instructions="Greet them in a friendly, natural way and ask what you can help with today."
    )
    
    logger.info("💬 Conversation started!")


if __name__ == "__main__":
    logger.info("="*70)
    logger.info("🏥 HEXAA CLINIC VOICE AGENT - PRODUCTION")
    logger.info("="*70)
    logger.info(f"📞 LiveKit SIP Number: {LIVEKIT_SIP_NUMBER}")
    logger.info("🌍 International Calling: ENABLED")
    logger.info("🎙️  Voice: ElevenLabs Sarah (Ultra-Realistic)")
    logger.info("⚡ Target Latency: <500ms")
    logger.info("🎯 Status: READY FOR CALLS")
    if platform.system() != "Darwin":
        logger.info("🚀 Production Mode: VAD turn detection (GPU-free)")
    else:
        logger.info("💻 Development Mode: Enhanced turn detection")
    logger.info("="*70)
    
    # Environment variable checks
    logger.info("🔍 Environment Variable Check:")
    env_vars = {
        "DATABASE_URL": os.getenv("DATABASE_URL"),
        "LIVEKIT_URL": os.getenv("LIVEKIT_URL"),
        "LIVEKIT_API_KEY": os.getenv("LIVEKIT_API_KEY"),
        "LIVEKIT_API_SECRET": os.getenv("LIVEKIT_API_SECRET"),
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "ELEVEN_LABS": os.getenv("ELEVEN_LABS"),
        "DEEPGRAM_API_KEY": os.getenv("DEEPGRAM_API_KEY"),
    }
    
    for key, value in env_vars.items():
        if value:
            if "KEY" in key or "SECRET" in key or "LABS" in key:
                masked = value[:4] + "****" + value[-4:] if len(value) > 8 else "****"
                logger.info(f"   ✅ {key}: {masked}")
            else:
                logger.info(f"   ✅ {key}: {value[:30]}..." if len(value) > 30 else f"   ✅ {key}: {value}")
        else:
            logger.warning(f"   ❌ {key}: NOT SET")
    
    logger.info("="*70)
    
    worker_opts = WorkerOptions(
        entrypoint_fnc=entrypoint,
        agent_name="hexaa-clinic-agent",
    )
    
    agents.cli.run_app(worker_opts)