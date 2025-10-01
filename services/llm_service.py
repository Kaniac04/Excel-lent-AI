
import aiohttp
import asyncio
import json
import os
from dotenv import load_dotenv
from services.logger_service import get_logger
load_dotenv()
LLM_URL = os.getenv("LLM_URL")
LLM_MODEL = os.getenv("LLM_MODEL")

logger = get_logger("llm_service")


async def stream_llm_response(prompt, system_prompt, stop_tag="</think>", session = None):
    """
    Streams tokens from LMStudio but only yields content AFTER stop_tag.
    Handles cases where stop_tag is split across multiple chunks.
    """
    logger.info("Streaming LLM response...")
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=600)) as session_http:
        payload = {
            "model": LLM_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "stream": True
        }

        async with session_http.post(LLM_URL, json=payload) as resp:
            if resp.status != 200:
                text = await resp.text()
                logger.error(f"Error from LMStudio: {text}")
                raise Exception(f"Error from LMStudio: {text}")

            buffer = ""
            content_buffer = ""
            buffering = True  # True until stop_tag is found
            try:
                async for line in resp.content:
                    line = line.decode().strip()
                    if not line or line == "data: [DONE]":
                        continue
                    if line.startswith("data: "):
                        data = json.loads(line[6:])
                        if "choices" in data:
                            delta = data["choices"][0].get("delta", {})
                            if "content" in delta:
                                text = delta["content"]
                                if buffering:
                                    buffer += text
                                    # Check if stop_tag is fully in buffer
                                    if stop_tag in buffer:
                                        buffering = False
                                        # Yield only content after stop_tag
                                        idx = buffer.index(stop_tag) + len(stop_tag)
                                        content_buffer += buffer[idx:]
                                        yield buffer[idx:]
                                        buffer = ""  # reset buffer
                                else:
                                    content_buffer += text
                                    yield text
                if session is not None:
                    session["history"].append({"role": "Interviewer", "content": content_buffer})
                
            except Exception as e:
                logger.error(f"Error while streaming LLM response: {e}", exc_info=True)
                raise e


async def llm_chat(prompt, system_prompt, session_id=None):
    """
    Sends a prompt to LMStudio and returns the full response (non-streaming).
    """
    logger.info("Sending chat prompt to LLM...")
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=600)) as session_http:
        payload = {
            "model": LLM_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "stream": False
        }

        async with session_http.post(LLM_URL, json=payload) as resp:
            if resp.status != 200:
                text = await resp.text()
                logger.error(f"Connection Elapsed: {text}")
                raise Exception("Connection Elapsed.")

            data = await resp.json()
            # Extract the response content
            if "choices" in data and data["choices"]:
                logger.info("LLM chat response received.")
                return data["choices"][0]["message"]["content"]
            else:
                logger.error("Connection Elapsed: No choices in response.")
                raise Exception("Connection Elapsed.")