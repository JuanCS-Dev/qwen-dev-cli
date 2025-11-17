"""Gradio web UI for qwen-dev-cli."""

import asyncio
from typing import List, Tuple, Generator
import gradio as gr

from .core.llm import llm_client
from .core.context import context_builder
from .core.mcp import mcp_manager
from .core.config import config


def create_ui() -> gr.Blocks:
    """Create Gradio Blocks UI.
    
    Returns:
        Gradio Blocks interface
    """
    
    with gr.Blocks(
        title="QWEN-DEV-CLI - AI Code Assistant",
        theme=gr.themes.Soft(),
        css="""
        .chat-container {min-height: 600px;}
        .upload-area {border: 2px dashed #ccc; padding: 20px; border-radius: 8px;}
        """
    ) as demo:
        
        # Header
        gr.Markdown("""
        # 🚀 QWEN-DEV-CLI
        **AI-Powered Code Assistant with MCP Integration**
        
        Ask questions about your code, generate new functions, or get explanations with context awareness.
        """)
        
        # Main Layout
        with gr.Row():
            # Left Column: Chat Interface (60%)
            with gr.Column(scale=3):
                chatbot = gr.Chatbot(
                    label="💬 Chat",
                    height=500,
                    show_label=True,
                    container=True,
                    elem_classes=["chat-container"],
                    type="messages"
                )
                
                with gr.Row():
                    msg_input = gr.Textbox(
                        placeholder="Ask about code, request generation, or get explanations...",
                        label="Your Message",
                        lines=2,
                        scale=4
                    )
                    send_btn = gr.Button("Send 🚀", variant="primary", scale=1)
                
                with gr.Row():
                    clear_btn = gr.Button("Clear Chat 🗑️", size="sm")
                    retry_btn = gr.Button("Retry Last ♻️", size="sm")
            
            # Right Column: Controls & Context (40%)
            with gr.Column(scale=2):
                # Model Settings
                gr.Markdown("### ⚙️ Settings")
                
                temperature = gr.Slider(
                    minimum=0.0,
                    maximum=2.0,
                    value=config.temperature,
                    step=0.1,
                    label="Temperature",
                    info="Higher = more creative, Lower = more focused"
                )
                
                max_tokens = gr.Slider(
                    minimum=128,
                    maximum=4096,
                    value=config.max_tokens,
                    step=128,
                    label="Max Tokens",
                    info="Maximum length of response"
                )
                
                stream_enabled = gr.Checkbox(
                    label="Enable Streaming",
                    value=True,
                    info="Show response progressively (better UX)"
                )
                
                # File Upload
                gr.Markdown("### 📁 Context Files")
                file_upload = gr.File(
                    label="Upload Files for Context",
                    file_count="multiple",
                    file_types=[".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".cpp", ".c", ".go", ".rs", ".md", ".txt"],
                    elem_classes=["upload-area"]
                )
                
                context_status = gr.Textbox(
                    label="Context Status",
                    value="No files loaded",
                    interactive=False,
                    lines=3
                )
                
                clear_context_btn = gr.Button("Clear Context 🧹", size="sm")
                
                # MCP Toggle
                gr.Markdown("### 🔧 MCP")
                mcp_enabled = gr.Checkbox(
                    label="Enable MCP Filesystem",
                    value=mcp_manager.enabled,
                    info="Access local files via MCP"
                )
                
                # Stats
                gr.Markdown("### 📊 Stats")
                stats_display = gr.JSON(
                    label="Context Statistics",
                    value={"files": 0, "chars": 0, "tokens": 0}
                )
        
        # State management
        chat_history = gr.State([])
        last_user_msg = gr.State("")
        
        # Event Handlers
        
        def respond_stream(message: str, history: List, temp: float, max_tok: int, stream: bool) -> Generator:
            """Handle chat response with streaming support."""
            if not message.strip():
                yield history
                return
            
            # Add user message to history
            history.append({"role": "user", "content": message})
            history.append({"role": "assistant", "content": ""})
            
            if stream:
                # Streaming mode
                async def stream_response():
                    full_response = ""
                    async for chunk in llm_client.stream_chat(message, temperature=temp, max_tokens=max_tok):
                        full_response += chunk
                        history[-1]["content"] = full_response
                        yield history
                
                # Run async generator in sync context
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    async_gen = stream_response()
                    while True:
                        try:
                            result = loop.run_until_complete(async_gen.__anext__())
                            yield result
                        except StopAsyncIteration:
                            break
                finally:
                    loop.close()
            else:
                # Non-streaming mode
                try:
                    response = asyncio.run(llm_client.generate(message, temperature=temp, max_tokens=max_tok))
                    history[-1]["content"] = response
                except Exception as e:
                    history[-1]["content"] = f"❌ Error: {str(e)}"
                
                yield history
        
        def upload_files(files) -> Tuple[str, dict]:
            """Handle file uploads."""
            if not files:
                return "No files uploaded", context_builder.get_stats()
            
            # Clear previous context
            context_builder.clear()
            
            # Add new files
            results = []
            for file in files:
                success, message = context_builder.add_file(file.name)
                status = "✅" if success else "❌"
                results.append(f"{status} {message}")
            
            status_text = "\n".join(results)
            stats = context_builder.get_stats()
            
            return status_text, stats
        
        def clear_context() -> Tuple[str, dict]:
            """Clear context files."""
            context_builder.clear()
            return "Context cleared", context_builder.get_stats()
        
        def clear_chat() -> Tuple[List, str]:
            """Clear chat history."""
            return [], ""
        
        def retry_last(history: List, last_msg: str, temp: float, max_tok: int, stream: bool) -> Generator:
            """Retry last message."""
            if not last_msg:
                yield history
                return
            
            # Remove last exchange if exists
            if len(history) >= 2 and history[-2].get("role") == "user" and history[-2].get("content") == last_msg:
                history = history[:-2]
            
            # Regenerate
            yield from respond_stream(last_msg, history, temp, max_tok, stream)
        
        def toggle_mcp(enabled: bool) -> str:
            """Toggle MCP on/off."""
            mcp_manager.toggle(enabled)
            return "MCP Enabled" if enabled else "MCP Disabled"
        
        # Wire events
        send_btn.click(
            respond_stream,
            inputs=[msg_input, chatbot, temperature, max_tokens, stream_enabled],
            outputs=[chatbot]
        ).then(
            lambda: ("", context_builder.get_stats()),
            outputs=[msg_input, stats_display]
        ).then(
            lambda hist: hist[-2]["content"] if len(hist) >= 2 else "",
            inputs=[chatbot],
            outputs=[last_user_msg]
        )
        
        msg_input.submit(
            respond_stream,
            inputs=[msg_input, chatbot, temperature, max_tokens, stream_enabled],
            outputs=[chatbot]
        ).then(
            lambda: ("", context_builder.get_stats()),
            outputs=[msg_input, stats_display]
        ).then(
            lambda hist: hist[-2]["content"] if len(hist) >= 2 else "",
            inputs=[chatbot],
            outputs=[last_user_msg]
        )
        
        clear_btn.click(
            clear_chat,
            outputs=[chatbot, last_user_msg]
        )
        
        retry_btn.click(
            retry_last,
            inputs=[chatbot, last_user_msg, temperature, max_tokens, stream_enabled],
            outputs=[chatbot]
        )
        
        file_upload.change(
            upload_files,
            inputs=[file_upload],
            outputs=[context_status, stats_display]
        )
        
        clear_context_btn.click(
            clear_context,
            outputs=[context_status, stats_display]
        )
        
        mcp_enabled.change(
            toggle_mcp,
            inputs=[mcp_enabled],
            outputs=[context_status]
        )
        
        # Examples
        gr.Examples(
            examples=[
                ["Explain this Python function and suggest improvements"],
                ["Generate a FastAPI endpoint for user authentication"],
                ["What are the best practices for error handling in this code?"],
                ["Refactor this function to be more efficient"],
            ],
            inputs=msg_input,
        )
        
        # Footer
        gr.Markdown("""
        ---
        **Built for MCP 1st Birthday Hackathon** | [GitHub](https://github.com/JuanCS-Dev/qwen-dev-cli) | *Soli Deo Gloria* 🙏
        """)
    
    return demo


if __name__ == "__main__":
    demo = create_ui()
    demo.launch()
