from dotenv import load_dotenv
import time
import logging
<<<<<<< Updated upstream

from livekit import agents, rtc
from livekit.agents import AgentSession, Agent, RoomInputOptions, llm
from livekit.plugins import openai, deepgram
=======
import os
import platform

from livekit import agents, rtc
from livekit.agents import (
    AgentSession, 
    Agent, 
    RoomInputOptions, 
    WorkerOptions, 
    WorkerType,
    JobContext
)
from livekit.plugins import openai, cartesia

# Conditional imports
>>>>>>> Stashed changes
try:
    from livekit.plugins import noise_cancellation
except Exception:
    noise_cancellation = None
<<<<<<< Updated upstream
=======

EnglishModel = None  # Disabled for Windows compatibility

>>>>>>> Stashed changes
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

TTS_MODEL = "aura-asteria-en"  
TTS_SAMPLE_RATE = 24000  
TTS_ENCODING = "linear16"  

SYSTEM_PROMPT = (
    "Hey! You're a real-time voice assistant for The Hexaa Clinic, and honestly, you're basically just having a friendly phone conversation with folks who call in.\n\n"
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
    "- Always double-check the important stuff—like if you didn't quite catch their name, ask 'em to spell it. Repeat dates and times back to 'em in a natural way.\n"
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
    "Examples of How You'd Sound:\n"
    "- 'Alright, so you're looking to book an appointment—gotcha. Can I grab your name real quick?'\n"
    "- 'Hmm, let me check... okay, so Tuesday at 3 is open, or I've got Thursday at 10. Which one works better for you?'\n"
    "- 'Cool, I'll get that canceled for you. Just to confirm, that's the appointment on the 15th at 2pm, right?'\n"
    "- 'No worries if you don't have your insurance info handy—we can handle that when you come in.'\n"
    "- 'Wait, that sounds pretty urgent. I really think you should call 911, or I can get you to someone here right now. What do you wanna do?'\n"
    "- 'Perfect, you're all set! You'll get a confirmation text and email in just a sec.'\n\n"
    "Remember: You're helpful, warm, and real. Not a robot. Just a friendly person on the other end of the phone trying to make their day a little easier.\n"
)


<<<<<<< Updated upstream

=======
>>>>>>> Stashed changes
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

<<<<<<< Updated upstream
            status = " EXCELLENT" if latency < 1.0 else "  WARNING" if latency < 2.0 else " POOR"
=======
            if latency < 0.5:
                status = "🟢 EXCELLENT"
            elif latency < 0.75:
                status = "🟡 GOOD"
            elif latency < 1.0:
                status = "🟠 WARNING"
            else:
                status = "🔴 POOR"

>>>>>>> Stashed changes
            logger.info(f"\n{'='*60}")
            logger.info(f" LATENCY MEASUREMENT #{self.turn_count}")
            logger.info(f"   Response Time: {latency:.3f}s - {status}")
            logger.info(f"   Target: < 1.000s")

<<<<<<< Updated upstream
            if latency < 1.0:
                logger.info(f"   Status: Under target by {(1.0 - latency):.3f}s ✓")
            else:
                logger.info(f"   Status: Over target by {(latency - 1.0):.3f}s ✗")
=======
            if latency < 0.5:
                logger.info(f"   Status: Under target by {(0.5 - latency)*1000:.0f}ms ✓")
            else:
                logger.info(f"   Status: Over target by {(latency - 0.5)*1000:.0f}ms ✗")
>>>>>>> Stashed changes

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
<<<<<<< Updated upstream
    def __init__(self, latency_tracker: LatencyTracker) -> None:
        super().__init__(instructions=SYSTEM_PROMPT)
=======
    def __init__(self, latency_tracker: LatencyTracker, tools: list = None) -> None:
        super().__init__(instructions=HUMANLY_SYSTEM_PROMPT, tools=tools)
>>>>>>> Stashed changes
        self.latency_tracker = latency_tracker


async def entrypoint(ctx: JobContext):
    """
    Main entrypoint for the telephony voice agent
    When using SIP trunk, this is automatically triggered when a call comes in
    """
    
    # Detect phone call via SIP
    is_phone_call = False
    caller_number = "Unknown"
    
    try:
        # Check if this is a SIP call by examining the room
        room = ctx.room
        if room:
            # SIP calls typically have room names starting with 'call-'
            if room.name and room.name.startswith('call-'):
                is_phone_call = True
                logger.info("📞 INCOMING PHONE CALL via SIP!")
            
            # Try to get caller number from participants
            async for participant in room.remote_participants.values():
                if participant.identity:
                    caller_number = participant.identity
                    logger.info(f"📱 Caller Number: {caller_number}")
                    break
    except Exception as e:
        logger.debug(f"Could not detect SIP call info: {e}")
    
    latency_tracker = LatencyTracker()
<<<<<<< Updated upstream
    logger.info(" Initializing Optimized Medical Clinic Voice Agent...")
    logger.info(f"  TTS: Deepgram Aura - {TTS_MODEL} | Sample Rate: {TTS_SAMPLE_RATE}Hz")

    tts_instance = deepgram.TTS(
        model=TTS_MODEL,
        sample_rate=TTS_SAMPLE_RATE,
        encoding=TTS_ENCODING,
    )
    session = AgentSession(
        stt="deepgram/nova-2",
        llm="openai/gpt-4o-mini",  
        tts=tts_instance,
    )
    
    original_agent = Assistant(latency_tracker)
=======
    logger.info("🚀 Initializing Hexaa Clinic Telephony Voice Agent...")

    # Initialize tool router and handlers
    router = ToolRouter()
    register_handlers(router)

    # Create LiveKit-compatible tools
    livekit_tools = create_livekit_tools(router)
    logger.info(f"📦 Registered {len(router.list_tools())} tools")

    # Configure TTS - OPTIMIZED FOR PHONE CALLS (16kHz)
    logger.info("🎙️  Configuring Cartesia TTS for telephony...")
    tts_instance = cartesia.TTS(
        model="sonic-english",
        voice="79a125e8-cd45-4c13-8a67-188112f4dd22",
        encoding="pcm_s16le",
        sample_rate=16000,  # 16kHz for phone quality (standard telephony)
    )
    logger.info("✅ TTS initialized for phone calls (16kHz)")

    # Configure session - OPTIMIZED FOR PHONE CONVERSATIONS
    logger.info("⚙️  Configuring session for telephony...")
    
    session = AgentSession(
        stt="deepgram/nova-2-phonecall",  # Optimized for phone calls
        llm="openai/gpt-4o-mini",  # Fast response
        tts=tts_instance,
        min_endpointing_delay=0.5,  # Slightly higher for phone latency
        min_interruption_duration=0.4,  # Allow natural phone interruptions
        allow_interruptions=True,
    )
    
    original_agent = Assistant(latency_tracker, tools=livekit_tools)
>>>>>>> Stashed changes
    original_generate = session.generate_reply
    last_input_time = [None]

    async def tracked_generate(*args, **kwargs):
<<<<<<< Updated upstream

        if last_input_time[0] is None:
            last_input_time[0] = time.time()
            logger.info(" USER INPUT RECEIVED - Processing...")

        logger.info("AGENT GENERATING RESPONSE...")
=======
        """Wrapper to track response latency"""
        if last_input_time[0] is None:
            last_input_time[0] = time.time()
            logger.info("🎤 USER SPEAKING...")

        logger.info("🤖 GENERATING RESPONSE...")
>>>>>>> Stashed changes
        result = await original_generate(*args, **kwargs)
        
        if last_input_time[0]:
            latency = time.time() - last_input_time[0]
            latency_tracker.latencies.append(latency)
            latency_tracker.turn_count += 1

<<<<<<< Updated upstream
            status = " EXCELLENT" if latency < 1.0 else "  WARNING" if latency < 2.0 else " POOR"
=======
            if latency < 0.5:
                status = "🟢 EXCELLENT"
            elif latency < 0.75:
                status = "🟡 GOOD"
            elif latency < 1.0:
                status = "🟠 WARNING"
            else:
                status = "🔴 POOR"

>>>>>>> Stashed changes
            logger.info(f"\n{'='*60}")
            logger.info(f" LATENCY MEASUREMENT #{latency_tracker.turn_count}")
            logger.info(f"   Response Time: {latency:.3f}s - {status}")
            logger.info(f"   Target: < 1.000s")

<<<<<<< Updated upstream
            if latency < 1.0:
                logger.info(f"   Status: Under target by {(1.0 - latency):.3f}s ✓")
            else:
                logger.info(f"   Status: Over target by {(latency - 1.0):.3f}s ✗")
=======
            if latency < 0.5:
                logger.info(f"   Status: Under target by {(0.5 - latency)*1000:.0f}ms ✓")
            else:
                logger.info(f"   Status: Over target by {(latency - 0.5)*1000:.0f}ms ✗")
>>>>>>> Stashed changes
                
            if len(latency_tracker.latencies) > 1:
                avg = sum(latency_tracker.latencies) / len(latency_tracker.latencies)
                min_lat = min(latency_tracker.latencies)
                max_lat = max(latency_tracker.latencies)
                logger.info(f"\n STATISTICS:")
                logger.info(f"   Average: {avg:.3f}s")
                logger.info(f"   Best:    {min_lat:.3f}s")
                logger.info(f"   Worst:   {max_lat:.3f}s")
                logger.info(f"   Turns:   {len(latency_tracker.latencies)}")

                under_1s = sum(1 for l in latency_tracker.latencies if l < 1.0)
                success_rate = (under_1s / len(latency_tracker.latencies)) * 100
                logger.info(f"   Success Rate: {success_rate:.1f}% (under 1s)")

            logger.info(f"{'='*60}\n")
            last_input_time[0] = None

        return result
    
    session.generate_reply = tracked_generate
    
<<<<<<< Updated upstream
    await session.start(
        room=ctx.room,
        agent=original_agent,
        room_input_options=RoomInputOptions(
            noise_cancellation=(noise_cancellation.BVC()
                                if noise_cancellation is not None
                                else None),
        ),
    )

    logger.info(" Agent ready! Monitoring latency...\n")
    
    await session.generate_reply(
        instructions="Say: 'Hello! How can I help you today?' Keep it under 10 words."
    )
    
    router = ToolRouter()
    register_handlers(router)
=======
    # Configure room input options - TELEPHONY OPTIMIZED
    room_input_opts = RoomInputOptions()
    
    # Enable telephony-grade noise cancellation
    if noise_cancellation is not None:
        try:
            room_input_opts.noise_cancellation = noise_cancellation.BVCTelephony()
            logger.info("✅ Telephony noise cancellation enabled")
        except Exception as e:
            logger.warning(f"⚠️  Could not enable noise cancellation: {e}")
    
    # Start the session
    logger.info("🔌 Connecting to room...")
    await session.start(
        room=ctx.room,
        agent=original_agent,
        room_input_options=room_input_opts,
    )

    logger.info("✅ Agent connected and ready!")
    
    # Generate phone-specific greeting
    if is_phone_call:
        logger.info("📞 Starting phone conversation...")
        greeting_instruction = (
            "Greet them warmly as if answering the phone at Hexaa Clinic. "
            "Say something like 'Hey, thanks for calling Hexaa Clinic! What can I help you with today?' "
            "Keep it natural and friendly."
        )
    else:
        greeting_instruction = (
            "Greet them in a friendly, natural way and ask what you can help with today."
        )
    
    await session.generate_reply(instructions=greeting_instruction)
    
    logger.info("💬 Conversation started!")

>>>>>>> Stashed changes


if __name__ == "__main__":
    # Disable inference executor on Windows to avoid timeout issues
    worker_opts = WorkerOptions(entrypoint_fnc=entrypoint)
    
    if platform.system() == "Windows":
        logger.info("🪟 Windows detected - disabling inference executor")
        worker_opts.worker_type = WorkerType.ROOM
    
    logger.info("="*60)
    logger.info("🏥 HEXAA CLINIC TELEPHONY VOICE AGENT")
    logger.info("="*60)
    logger.info("📞 Ready to receive phone calls via Twilio SIP Trunk")
    logger.info("🔊 Optimized for phone audio (16kHz)")
    logger.info("🎯 Direct SIP connection - no webhooks needed!")
    logger.info("="*60)
    
    agents.cli.run_app(worker_opts)