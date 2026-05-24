from dataclasses import dataclass, field
from typing import Optional, Dict, Any
import os
from dotenv import load_dotenv


@dataclass
class AgentConfig:
    max_token_limit: int = 32000
    token_warning_threshold: float = 0.8
    temperature: float = 0.7


@dataclass
class LLMConfig:
    model: str = "deepseek-chat"
    api_key: Optional[str] = None
    base_url: str = "https://api.deepseek.com"
    timeout: int = 60


@dataclass
class LoggingConfig:
    level: str = "INFO"
    log_file: Optional[str] = "logs/autoswarm.log"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    max_file_size: int = 10 * 1024 * 1024
    backup_count: int = 5


@dataclass
class AutoSwarmConfig:
    agent: AgentConfig = field(default_factory=AgentConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    
    @classmethod
    def from_env(cls) -> "AutoSwarmConfig":
        load_dotenv()
        config = cls()
        
        config.llm.api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY")
        config.llm.model = os.getenv("LLM_MODEL", config.llm.model)
        config.llm.base_url = os.getenv("LLM_BASE_URL", config.llm.base_url)
        
        config.agent.max_token_limit = int(os.getenv("AGENT_MAX_TOKEN_LIMIT", str(config.agent.max_token_limit)))
        config.agent.token_warning_threshold = float(os.getenv("AGENT_TOKEN_WARNING_THRESHOLD", str(config.agent.token_warning_threshold)))
        config.agent.temperature = float(os.getenv("AGENT_TEMPERATURE", str(config.agent.temperature)))
        
        config.logging.level = os.getenv("LOG_LEVEL", config.logging.level)
        config.logging.log_file = os.getenv("LOG_FILE", config.logging.log_file)
        
        return config
