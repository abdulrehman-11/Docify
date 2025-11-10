from dotenv import load_dotenv
import time
import logging

from livekit import agents, rtc
from livekit.agents import AgentSession, Agent, RoomInputOptions, llm
from livekit.plugins import openai, deepgram
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
                logger.info(f"   Status: Under target by {(1.0 - latency):.3f}s ✓")
            else:
                logger.info(f"   Status: Over target by {(latency - 1.0):.3f}s ✗")

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
    original_generate = session.generate_reply
    last_input_time = [None]

    async def tracked_generate(*args, **kwargs):

        if last_input_time[0] is None:
            last_input_time[0] = time.time()
            logger.info(" USER INPUT RECEIVED - Processing...")

        logger.info("AGENT GENERATING RESPONSE...")
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
                logger.info(f"   Status: Under target by {(1.0 - latency):.3f}s ✓")
            else:
                logger.info(f"   Status: Over target by {(latency - 1.0):.3f}s ✗")
                
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


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))