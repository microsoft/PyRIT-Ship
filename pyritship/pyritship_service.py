# pyritship_service.py
import asyncio
import os
import time
import uuid
import inspect
import importlib
import threading
from dataclasses import dataclass
from typing import Optional, Any
from concurrent.futures import Future

from pyrit.setup import initialize_pyrit_async, IN_MEMORY
from pyrit.converter import Converter
from pyrit.prompt_target import OpenAIChatTarget
from pyrit.executor.attack import (
    PromptSendingAttack, RTASystemPromptPaths,
    AttackAdversarialConfig, AttackScoringConfig, RedTeamingAttack,
)
from pyrit.score import SelfAskTrueFalseScorer, TrueFalseQuestion
from azure.identity import InteractiveBrowserCredential, get_bearer_token_provider

from external_control_target import ExternalControlTarget


# --- Custom Exceptions ---

class AttackNotFoundError(Exception):
    """Raised when an attack_id does not exist."""
    pass

class AttackConflictError(Exception):
    """Raised when an operation is called out of order."""
    pass


# --- Attack Session ---

@dataclass
class AttackSession:
    id: str
    external_target: Optional[ExternalControlTarget] = None
    future: Optional[Future] = None
    status: str = "starting"
    result: Optional[Any] = None
    error: Optional[str] = None
    prompt_retrieved: bool = False


# --- Service ---

class PyRITShipService:
    def __init__(self):
        self._chat_target = None
        self._browser_credential = None
        self._attack_sessions: dict[str, AttackSession] = {}

        # Persistent asyncio event loop for running async PyRIT operations
        self._loop = asyncio.new_event_loop()
        self._loop_thread = threading.Thread(target=self._loop.run_forever, daemon=True)
        self._loop_thread.start()

    def shutdown(self):
        """Dispose DB connections on the event loop thread, then stop it cleanly."""
        async def _dispose():
            try:
                from pyrit.memory.central_memory import CentralMemory
                mem = CentralMemory.get_memory_instance()
                if hasattr(mem, 'dispose_engine'):
                    mem.dispose_engine()
                elif hasattr(mem, '_engine'):
                    mem._engine.dispose()
            except Exception:
                pass

        try:
            future = asyncio.run_coroutine_threadsafe(_dispose(), self._loop)
            future.result(timeout=5)
        except Exception:
            pass

        self._loop.call_soon_threadsafe(self._loop.stop)
        self._loop_thread.join(timeout=5)

    def authenticate_interactive(self):
        """Authenticate interactively on the calling thread (call before starting server)."""
        endpoint = os.environ.get("OPENAI_CHAT_ENDPOINT", "")
        api_key = os.environ.get("OPENAI_CHAT_KEY", "")
        if not api_key and "azure.com/" in endpoint:
            print("No API key set for Azure endpoint — launching browser for interactive login...")
            self._browser_credential = InteractiveBrowserCredential()
            self._browser_credential.authenticate(scopes=["https://cognitiveservices.azure.com/.default"])
            print("Authentication successful.")

    # --- Internal helpers ---

    def _run_on_loop(self, coro):
        """Schedule a coroutine on the shared event loop and block until it completes."""
        return asyncio.run_coroutine_threadsafe(coro, self._loop).result()

    def _build_chat_target(self):
        """Build the OpenAI chat target instance."""
        endpoint = os.environ.get("OPENAI_CHAT_ENDPOINT", "")
        api_key = os.environ.get("OPENAI_CHAT_KEY", "")

        if not api_key and "azure.com/" in endpoint:
            if self._browser_credential is None:
                self._browser_credential = InteractiveBrowserCredential()
                self._browser_credential.authenticate(scopes=["https://cognitiveservices.azure.com/.default"])
            token_provider = get_bearer_token_provider(
                self._browser_credential,
                "https://cognitiveservices.azure.com/.default",
            )
            api_key = token_provider

        return OpenAIChatTarget(
            model_name=os.environ.get("OPENAI_CHAT_MODEL_NAME"),
            endpoint=endpoint,
            api_key=api_key,
        )

    def _ensure_chat_target(self):
        """Initialize PyRIT memory and chat target if not already done."""
        if self._chat_target is None:
            self._run_on_loop(initialize_pyrit_async(memory_db_type=IN_MEMORY))
            self._chat_target = self._build_chat_target()

    def _sync_session_status(self, session: AttackSession):
        """Update session status from its future if the coroutine has finished."""
        if session.future and session.future.done():
            try:
                session.result = session.future.result()
                session.status = "completed"
            except Exception as e:
                session.error = str(e)
                session.status = "error"

    def _get_session(self, attack_id: str) -> AttackSession:
        """Get an attack session by ID, raising AttackNotFoundError if not found."""
        session = self._attack_sessions.get(attack_id)
        if not session:
            raise AttackNotFoundError(f"Unknown attack_id: {attack_id}")
        self._sync_session_status(session)
        return session

    # --- Business methods ---

    def list_converters(self) -> list[str]:
        """Return a list of converter class names that can be instantiated without arguments."""
        converters = Converter.__subclasses__()
        converter_list = []
        for converter in converters:
            params = inspect.signature(converter.__init__).parameters
            if ((len(params) == 1 and "self" in params) or
                (len(params) == 3 and "self" in params and "kwargs" in params and "args" in params)):
                converter_list.append(converter.__name__)
            else:
                defaults = [p for p in params if params[p].default != inspect.Parameter.empty]
                if len(defaults) == len(params) - 1:
                    converter_list.append(converter.__name__)
        return converter_list

    def convert_text(self, converter_name: str, text: str) -> str:
        """Convert text using the named converter. Returns the converted text."""
        c = next((cls for cls in Converter.__subclasses__() if cls.__name__ == converter_name), None)
        if c is None:
            raise ValueError(f"Unknown converter: {converter_name}")

        module = importlib.import_module(c.__module__)
        converter_class = getattr(module, c.__name__)
        instance = converter_class()

        converted_prompt = self._run_on_loop(instance.convert_async(prompt=text, input_type="text"))
        return converted_prompt.output_text

    def generate_prompt(self, prompt_goal: str) -> str:
        """Generate a prompt for the given goal. Returns the generated prompt text."""
        self._ensure_chat_target()
        prompt_sending_attack = PromptSendingAttack(objective_target=self._chat_target)
        result = self._run_on_loop(prompt_sending_attack.execute_async(objective=prompt_goal))
        return result.last_response.converted_value

    def score_true_false(self, true_description: str, false_description: str, prompt_response: str) -> dict:
        """Score a prompt response using SelfAskTrueFalseScorer. Returns scoring dict."""
        self._ensure_chat_target()
        scorer = SelfAskTrueFalseScorer(
            chat_target=self._chat_target,
            true_false_question={
                "category": "pyritship",
                "true_description": true_description,
                "false_description": false_description,
            }
        )
        scored_response = self._run_on_loop(scorer.score_text_async(text=prompt_response))[0]
        return {
            "scoring_text": str(scored_response.get_value()),
            "scoring_metadata": scored_response.score_metadata,
            "scoring_rationale": scored_response.score_rationale,
        }

    def start_attack(self, objective: str, success_description: str, max_turns: int = 3) -> dict:
        """Start a new red teaming attack. Returns dict with attack_id and status."""
        attack_id = str(uuid.uuid4())
        session = AttackSession(id=attack_id)
        self._attack_sessions[attack_id] = session

        session.future = asyncio.run_coroutine_threadsafe(
            self._run_attack(objective, success_description, max_turns, session),
            self._loop,
        )

        return {"attack_id": attack_id, "status": "starting"}

    def get_attack_prompt(self, attack_id: str, timeout: float = 30) -> dict:
        """Get the next prompt from an attack. Blocks up to timeout seconds."""
        session = self._get_session(attack_id)

        if session.status == "completed":
            self._attack_sessions.pop(attack_id, None)
            return {"attack_id": attack_id, "status": "completed", "result": str(session.result)}

        if session.status == "error":
            self._attack_sessions.pop(attack_id, None)
            return {"attack_id": attack_id, "status": "error", "error": session.error}

        if session.prompt_retrieved and session.external_target and session.external_target.is_waiting():
            raise AttackConflictError("Prompt already retrieved, submit response first")

        deadline = time.time() + timeout
        while time.time() < deadline:
            if session.external_target:
                prompt = session.external_target.get_current_prompt()
                if prompt:
                    session.status = "waiting_for_response"
                    session.prompt_retrieved = True
                    text = prompt.message_pieces[0].converted_value
                    return {"attack_id": attack_id, "status": "waiting_for_response", "prompt": text}

            if session.future and session.future.done():
                self._sync_session_status(session)
                if session.status in ("completed", "error"):
                    self._attack_sessions.pop(attack_id, None)
                    resp = {"attack_id": attack_id, "status": session.status}
                    if session.result:
                        resp["result"] = str(session.result)
                    if session.error:
                        resp["error"] = session.error
                    return resp

            time.sleep(0.1)

        return {"attack_id": attack_id, "status": "generating", "message": "Prompt not ready yet, try again"}

    def submit_attack_response(self, attack_id: str, response_text: str) -> dict:
        """Submit a response for the current prompt."""
        session = self._get_session(attack_id)

        if session.status == "completed":
            return {"attack_id": attack_id, "status": "completed", "result": str(session.result)}

        if session.status == "error":
            return {"attack_id": attack_id, "status": "error", "error": session.error}

        if not session.prompt_retrieved or not session.external_target or not session.external_target.is_waiting():
            raise AttackConflictError("No prompt outstanding")

        session.external_target.submit_response(response_text)
        session.prompt_retrieved = False
        session.status = "processing_response"

        return {"attack_id": attack_id, "status": "processing_response"}

    def get_attack_status(self, attack_id: str) -> dict:
        """Check the status of an attack."""
        session = self._get_session(attack_id)

        response = {"attack_id": attack_id, "status": session.status}
        if session.status == "completed":
            response["result"] = str(session.result)
            self._attack_sessions.pop(attack_id, None)
        if session.status == "error":
            response["error"] = session.error
            self._attack_sessions.pop(attack_id, None)

        return response

    # --- Internal attack coroutine ---

    async def _run_attack(self, objective: str, success_description: str, max_turns: int, session: AttackSession):
        """Coroutine that initializes and runs the attack on the event loop thread."""
        await initialize_pyrit_async(memory_db_type=IN_MEMORY)

        if self._chat_target is None:
            self._chat_target = self._build_chat_target()

        session.external_target = ExternalControlTarget()

        adversarial_config = AttackAdversarialConfig(
            target=self._chat_target,
            system_prompt_path=RTASystemPromptPaths.TEXT_GENERATION.value,
        )

        scoring_config = AttackScoringConfig(
            objective_scorer=SelfAskTrueFalseScorer(
                chat_target=self._chat_target,
                true_false_question=TrueFalseQuestion(true_description=success_description),
            ),
        )

        red_teaming_attack = RedTeamingAttack(
            objective_target=session.external_target,
            attack_adversarial_config=adversarial_config,
            attack_scoring_config=scoring_config,
            max_turns=max_turns,
        )

        return await red_teaming_attack.execute_async(objective=objective)
