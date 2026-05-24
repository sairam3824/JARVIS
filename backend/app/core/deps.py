from __future__ import annotations

from dataclasses import dataclass

from agents.orchestrator import AgentOrchestrator
from app.core.config import Settings
from app.providers.openrouter_provider import OpenRouterProvider
from app.repositories.conversation import ConversationRepository
from app.repositories.database import Database
from app.repositories.memory import MemoryRepository
from app.repositories.tool_trace import ToolTraceRepository
from app.repositories.workspace import WorkspaceRepository
from app.services.chat_service import ChatService
from app.services.integrations.desktop import MacOSDesktopAutomationAdapter
from app.services.integrations.home_assistant import HomeAssistantAdapter
from app.services.intelligence.analytics import AnalyticsService
from app.services.intelligence.audio_features import LightweightAudioFeatureExtractor
from app.services.intelligence.planner import PlannerEngine
from app.services.intelligence.qr import QRService
from app.services.intelligence.recipe import RecipePlanner
from app.services.intelligence.sentiment import HeuristicSentimentHumorScorer
from app.services.intelligence.task_router import TaskModelRouter
from app.services.intelligence.text_classifier import KeywordTextClassifier
from app.services.intelligence.vision import VisionAnalyzer
from app.services.system_service import SystemService
from app.services.voice_service import VoiceService
from app.services.workspace_service import WorkspaceService
from models.chat import ProviderType
from tools.registry import ToolRegistry


@dataclass(slots=True)
class AppContainer:
    settings: Settings
    database: Database
    conversation_repository: ConversationRepository
    memory_repository: MemoryRepository
    tool_trace_repository: ToolTraceRepository
    workspace_repository: WorkspaceRepository
    tool_registry: ToolRegistry
    providers: dict
    text_classifier: KeywordTextClassifier
    task_router: TaskModelRouter
    sentiment_scorer: HeuristicSentimentHumorScorer
    audio_feature_extractor: LightweightAudioFeatureExtractor
    analytics_service: AnalyticsService
    planner_engine: PlannerEngine
    recipe_planner: RecipePlanner
    vision_analyzer: VisionAnalyzer
    qr_service: QRService
    desktop_automation: MacOSDesktopAutomationAdapter
    home_assistant_adapter: HomeAssistantAdapter
    orchestrator: AgentOrchestrator
    chat_service: ChatService
    voice_service: VoiceService
    system_service: SystemService
    workspace_service: WorkspaceService


def build_container(settings: Settings) -> AppContainer:
    database = Database(settings.database_path)
    conversation_repository = ConversationRepository(database)
    memory_repository = MemoryRepository(database)
    tool_trace_repository = ToolTraceRepository(database)
    workspace_repository = WorkspaceRepository(database)
    text_classifier = KeywordTextClassifier()
    task_router = TaskModelRouter(text_classifier, settings)
    sentiment_scorer = HeuristicSentimentHumorScorer()
    audio_feature_extractor = LightweightAudioFeatureExtractor()
    analytics_service = AnalyticsService()
    planner_engine = PlannerEngine()
    recipe_planner = RecipePlanner()
    vision_analyzer = VisionAnalyzer()
    qr_service = QRService()
    desktop_automation = MacOSDesktopAutomationAdapter()
    home_assistant_adapter = HomeAssistantAdapter(settings)
    tool_registry = ToolRegistry(
        settings.allowed_roots,
        settings.terminal_timeout_seconds,
        analytics_service=analytics_service,
        planner_engine=planner_engine,
        qr_service=qr_service,
        desktop_automation=desktop_automation,
        sentiment_scorer=sentiment_scorer,
        home_assistant_adapter=home_assistant_adapter,
        workspace_repository=workspace_repository,
        memory_repository=memory_repository,
    )
    openrouter_provider = OpenRouterProvider(settings)
    providers = {ProviderType.OPENROUTER: openrouter_provider}
    orchestrator = AgentOrchestrator(
        providers=providers,
        tool_registry=tool_registry,
        conversation_repository=conversation_repository,
        memory_repository=memory_repository,
        trace_repository=tool_trace_repository,
        task_router=task_router,
        sentiment_scorer=sentiment_scorer,
    )
    chat_service = ChatService(orchestrator=orchestrator)
    voice_service = VoiceService(
        orchestrator=orchestrator,
        speech_provider=providers[ProviderType.OPENROUTER],
        audio_feature_extractor=audio_feature_extractor,
    )
    system_service = SystemService(tool_registry=tool_registry, trace_repository=tool_trace_repository)
    workspace_service = WorkspaceService(
        analytics_service=analytics_service,
        planner_engine=planner_engine,
        recipe_planner=recipe_planner,
        vision_analyzer=vision_analyzer,
        qr_service=qr_service,
        home_assistant_adapter=home_assistant_adapter,
        workspace_repository=workspace_repository,
    )
    return AppContainer(
        settings=settings,
        database=database,
        conversation_repository=conversation_repository,
        memory_repository=memory_repository,
        tool_trace_repository=tool_trace_repository,
        workspace_repository=workspace_repository,
        tool_registry=tool_registry,
        providers=providers,
        text_classifier=text_classifier,
        task_router=task_router,
        sentiment_scorer=sentiment_scorer,
        audio_feature_extractor=audio_feature_extractor,
        analytics_service=analytics_service,
        planner_engine=planner_engine,
        recipe_planner=recipe_planner,
        vision_analyzer=vision_analyzer,
        qr_service=qr_service,
        desktop_automation=desktop_automation,
        home_assistant_adapter=home_assistant_adapter,
        orchestrator=orchestrator,
        chat_service=chat_service,
        voice_service=voice_service,
        system_service=system_service,
        workspace_service=workspace_service,
    )
