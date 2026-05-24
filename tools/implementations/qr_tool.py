from __future__ import annotations

from models.contracts import BaseTool, ToolContext, ToolDefinition, ToolExecutionResult


class QRTool(BaseTool):
    definition = ToolDefinition(
        name="qr",
        description="Generates a QR code from text.",
        input_schema={"payload_text": {"type": "string"}},
        category="utility",
        capability_tags=["qr-generator"],
        result_type="qr",
    )

    def __init__(self, qr_service, workspace_repository) -> None:
        self.qr_service = qr_service
        self.workspace_repository = workspace_repository

    async def run(self, context: ToolContext, args: dict[str, str]) -> ToolExecutionResult:
        payload_text = args.get("payload_text", "")
        result = await self.qr_service.generate(payload_text)
        await self.workspace_repository.store_qr_result(result.mode, result.payload_text, result.decoded_text, result.image_base64)
        return ToolExecutionResult(
            tool_name=self.definition.name,
            success=True,
            output=f"Generated QR code for {payload_text}.",
            structured_output=result.model_dump(),
            result_type=self.definition.result_type,
            category=self.definition.category,
        )

