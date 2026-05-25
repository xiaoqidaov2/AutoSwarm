from dataclasses import dataclass, field
from typing import Optional, Dict, Any
import os
from dotenv import load_dotenv


@dataclass
class AgentConfig:
    max_token_limit: int = 32000
    token_warning_threshold: float = 0.8
    temperature: float = 0.7
    enable_memory_summarization: bool = False
    summarization_threshold: float = 0.7


@dataclass
class LLMConfig:
    model: str = "deepseek-chat"
    api_key: Optional[str] = None
    base_url: str = "https://api.deepseek.com"
    timeout: int = 60
    enable_retries: bool = True
    max_retries: int = 3
    retry_base_delay: float = 1.0


@dataclass
class ExecutionConfig:
    max_parallel_workers: int = 5
    enable_parallel_execution: bool = True


@dataclass
class LoggingConfig:
    level: str = "INFO"
    log_file: Optional[str] = "logs/autoswarm.log"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    max_file_size: int = 10 * 1024 * 1024
    backup_count: int = 5
    output_mode: str = "detailed"  # simple/detailed/quiet


@dataclass
class AutoSwarmConfig:
    agent: AgentConfig = field(default_factory=AgentConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)
    execution: ExecutionConfig = field(default_factory=ExecutionConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    
    @classmethod
    def from_env(cls) -> "AutoSwarmConfig":
        load_dotenv()
        config = cls()
        
        config.llm.api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY")
        config.llm.model = os.getenv("LLM_MODEL", config.llm.model)
        config.llm.base_url = os.getenv("LLM_BASE_URL", config.llm.base_url)
        config.llm.enable_retries = os.getenv("LLM_ENABLE_RETRIES", str(config.llm.enable_retries)).lower() == "true"
        config.llm.max_retries = int(os.getenv("LLM_MAX_RETRIES", str(config.llm.max_retries)))
        config.llm.retry_base_delay = float(os.getenv("LLM_RETRY_BASE_DELAY", str(config.llm.retry_base_delay)))
        
        config.agent.max_token_limit = int(os.getenv("AGENT_MAX_TOKEN_LIMIT", str(config.agent.max_token_limit)))
        config.agent.token_warning_threshold = float(os.getenv("AGENT_TOKEN_WARNING_THRESHOLD", str(config.agent.token_warning_threshold)))
        config.agent.temperature = float(os.getenv("AGENT_TEMPERATURE", str(config.agent.temperature)))
        config.agent.enable_memory_summarization = os.getenv("AGENT_ENABLE_MEMORY_SUMMARIZATION", str(config.agent.enable_memory_summarization)).lower() == "true"
        config.agent.summarization_threshold = float(os.getenv("AGENT_SUMMARIZATION_THRESHOLD", str(config.agent.summarization_threshold)))
        
        config.execution.max_parallel_workers = int(os.getenv("EXECUTION_MAX_PARALLEL_WORKERS", str(config.execution.max_parallel_workers)))
        config.execution.enable_parallel_execution = os.getenv("EXECUTION_ENABLE_PARALLEL", str(config.execution.enable_parallel_execution)).lower() == "true"
        
        config.logging.level = os.getenv("LOG_LEVEL", config.logging.level)
        config.logging.log_file = os.getenv("LOG_FILE", config.logging.log_file)
        config.logging.output_mode = os.getenv("LOG_OUTPUT_MODE", config.logging.output_mode)
        
        return config
