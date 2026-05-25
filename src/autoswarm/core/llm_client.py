import time
import logging
from typing import Optional, List, Dict, Any
from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)


class RetryableLLMClient:
    def __init__(
        self,
        llm: ChatOpenAI,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0
    ):
        self.llm = llm
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay

    def invoke(
        self,
        messages: List[Any],
        **kwargs: Any
    ) -> Any:
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return self.llm.invoke(messages, **kwargs)
            except Exception as e:
                last_exception = e
                
                if attempt >= self.max_retries:
                    logger.error(f"LLM invocation failed after {self.max_retries} retries: {e}")
                    raise
                
                delay = min(
                    self.base_delay * (2 ** attempt),
                    self.max_delay
                )
                
                logger.warning(
                    f"LLM invocation failed (attempt {attempt + 1}/{self.max_retries + 1}), "
                    f"retrying in {delay:.2f}s: {e}"
                )
                
                time.sleep(delay)
        
        raise last_exception  # Should not reach here
