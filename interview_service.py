import os
from dotenv import load_dotenv
from services.llm_service import stream_llm_response
from services.prompts import INTERVIEWER_SYSTEM_PROMPT
from services.tavily_web_search import search_and_extract
from services.logger_service import get_logger

load_dotenv()

logger = get_logger("interview_service")
introductory_line = "welcome to the interview! Please introduce yourself."

class InterviewSession:
    def __init__(self, session):
        self.session = session
        self.sudden_death = False
        self.sudden_death_counter = 0

    async def summarise_history(self):
        if len(self.session["history"]) > 5:
            logger.info("Summarizing history due to length.")
            history_to_summarize = self.session["history"][:-1]
            summary_prompt = "/nothink" \
            "Summarize the following conversation between an interviewer and a candidate in a concise manner, retaining key details about the candidate's skills and experience. The format for the summarisation is : [ Interviewer : 'some question' , Candidate : 'summary of answer']\n"
            for msg in history_to_summarize:
                role = "Interviewer" if msg["role"] == "Interviewer" else "Candidate"
                summary_prompt += f"{role}: {msg['content']}\n"

            summary = ""
            async for token in stream_llm_response(
                summary_prompt,
                "You are a helpful assistant that summarizes interview conversations.",
                stop_tag="</think>"
            ):
                summary += token
            logger.info(f"History summarized: {summary.strip()}")
            self.session["history"] = [{"role": "system", "content": "Summary of previous conversation: " + summary.strip()}] + self.session["history"][-2:]

    async def get_web_context(self, question):
        try:
            web_context = await search_and_extract("Microsoft Excel question : " + question)
            logger.info("Web context successfully retrieved.")
        except Exception as e:
            logger.error(f"Web search failed: {e}")
            web_context = ""
        
        return web_context

    async def guardrail_input(self, user_input, preface):
        guardrail_prompt = f"/think You are a content filter. Only allow responses that are relevant to a technical interview about Microsoft Excel. If the input is off-topic respond only with 'INVALID_INPUT'. Otherwise, respond only with 'VALID_INPUT'. Use the interview preface to get the context of the conversation and compare it to the user's input.\nInterview Preface: {preface}\nUser Input: {user_input}"
        validation = ""
        async for token in stream_llm_response(
            guardrail_prompt,
            "You are a strict content filter.",
            stop_tag="</think>"
        ):
            validation += token
        validation = validation.strip().upper()
        logger.info(f"Guardrail validation result: {validation}")
        return validation == "VALID_INPUT"

    async def generate_response(self, request):
        prompt = request.user_input
        logger.warning("History at response time: " + str(self.session["history"]))

        if self.sudden_death_counter >= int(os.getenv("MAX_HISTORY_LENGTH", 8)):
            logger.info("Crossed the physical limit for interview duration. Terminating Interview.")
            prompt = "The interview has reached its maximum duration. INTERVIEW CONCLUDED. Please provide a brief summary of the candidate's performance and areas for improvement."
            self.sudden_death = True
        self.sudden_death_counter += 1

        # Find the last interviewer question by traversing history backwards
        prev_question = None
        for message in reversed(self.session["history"]):
            if message.get("role") == "Interviewer":
                prev_question = message["content"]
                break

        logger.info(f"Generating response for session. Previous question: {prev_question}")

        # Guardrail check
        if len(self.session["history"]) > 3 and not self.sudden_death:
            logger.warning(f"Checking guardrail for user input: {prompt}")
            is_valid = await self.guardrail_input(prompt, self.session["history"][3:])
            if not is_valid:
                logger.critical("User input failed guardrail check.")
                prompt = f"The user has entered {prompt},\nThis response has been flagged as an attempt to divert the interview."
            logger.info("User input passed guardrail check.")

        # Web search for gaining context
        web_context = ""
        if introductory_line not in prev_question and not self.sudden_death:
            web_context = await self.get_web_context(prev_question)

        # Summarize history if too long
        if not self.sudden_death:
            await self.summarise_history()

        # Streaming response generator
        async def response_generator():
            system_prompt = INTERVIEWER_SYSTEM_PROMPT.replace("<<history>>", str(self.session["history"])) \
                                                    .replace("<<interviewer_question>>", prev_question) \
                                                    .replace("<<context>>", web_context)
            logger.debug(f"System prompt prepared for LLM.")
            async for token in stream_llm_response(
                prompt,
                system_prompt,
                stop_tag="</think>",
                session=self.session
            ):
                yield token
        return response_generator()