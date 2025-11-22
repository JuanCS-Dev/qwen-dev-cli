#!/usr/bin/env python3
"""
Qwen Dev CLI - Minimal Clean Gradio UI

Clean, minimal interface using only native Gradio components.
Built for the MCP Hackathon with 27+ production tools.
"""

from __future__ import annotations

import os
import shutil
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List

import gradio as gr
import pandas as pd

from .cli_bridge import CLIStreamBridge

PROJECT_ROOT = Path.cwd()

# Initialize CLI bridge
_bridge = CLIStreamBridge()

# --- HELPER FUNCTIONS ---

def _blank_metrics() -> Dict[str, Any]:
    """Create blank metrics dict."""
    return {
        "chunks": 0,
        "chars": 0,
        "sec": 0,
        "backend": _bridge.backend_label,
    }

def _get_mcp_tools_df() -> pd.DataFrame:
    """Get real MCP tools from ToolRegistry as DataFrame."""
    try:
        from qwen_dev_cli.tools.base import ToolRegistry
        from qwen_dev_cli.tools.file_ops import (
            ReadFileTool, WriteFileTool, EditFileTool,
            ListDirectoryTool, DeleteFileTool
        )
        from qwen_dev_cli.tools.file_mgmt import (
            MoveFileTool, CopyFileTool, CreateDirectoryTool,
            ReadMultipleFilesTool, InsertLinesTool
        )
        from qwen_dev_cli.tools.search import SearchFilesTool, GetDirectoryTreeTool
        from qwen_dev_cli.tools.exec import BashCommandTool
        from qwen_dev_cli.tools.git_ops import GitStatusTool, GitDiffTool
        from qwen_dev_cli.tools.context import GetContextTool, SaveSessionTool, RestoreBackupTool
        from qwen_dev_cli.tools.terminal import (
            CdTool, LsTool, PwdTool, MkdirTool, RmTool,
            CpTool, MvTool, TouchTool, CatTool
        )
        
        # Build data list
        data = []
        
        # File Operations
        for tool in [
            ReadFileTool(), WriteFileTool(), EditFileTool(),
            ListDirectoryTool(), DeleteFileTool(), MoveFileTool(),
            CopyFileTool(), CreateDirectoryTool(), ReadMultipleFilesTool(),
            InsertLinesTool()
        ]:
            data.append({
                "Category": "File Operations",
                "Tool": tool.name,
                "Description": tool.description[:60] + "..." if len(tool.description) > 60 else tool.description
            })
        
        # Search & Navigation
        for tool in [SearchFilesTool(), GetDirectoryTreeTool()]:
            data.append({
                "Category": "Search & Navigation",
                "Tool": tool.name,
                "Description": tool.description[:60] + "..." if len(tool.description) > 60 else tool.description
            })
        
        # Execution
        data.append({
            "Category": "Execution",
            "Tool": BashCommandTool().name,
            "Description": BashCommandTool().description[:60] + "..." if len(BashCommandTool().description) > 60 else BashCommandTool().description
        })
        
        # Git Operations
        for tool in [GitStatusTool(), GitDiffTool()]:
            data.append({
                "Category": "Git Operations",
                "Tool": tool.name,
                "Description": tool.description[:60] + "..." if len(tool.description) > 60 else tool.description
            })
        
        # Context Management
        for tool in [GetContextTool(), SaveSessionTool(), RestoreBackupTool()]:
            data.append({
                "Category": "Context Management",
                "Tool": tool.name,
                "Description": tool.description[:60] + "..." if len(tool.description) > 60 else tool.description
            })
        
        # Terminal Commands
        for tool in [
            CdTool(), LsTool(), PwdTool(), MkdirTool(), RmTool(),
            CpTool(), MvTool(), TouchTool(), CatTool()
        ]:
            data.append({
                "Category": "Terminal Commands",
                "Tool": tool.name,
                "Description": tool.description[:60] + "..." if len(tool.description) > 60 else tool.description
            })
        
        return pd.DataFrame(data)
    
    except Exception as e:
        # Fallback to minimal data if imports fail
        print(f"Warning: Could not load real tools: {e}")
        return pd.DataFrame([
            {"Category": "File Operations", "Tool": "read_file", "Description": "Read file contents"},
            {"Category": "File Operations", "Tool": "write_file", "Description": "Write content to file"},
            {"Category": "Terminal", "Tool": "bash", "Description": "Execute shell commands"},
        ])

# --- FILE UPLOAD HANDLER ---

def handle_file_upload(files):
    """Process uploaded files, copy to workspace, and return status message."""
    if not files:
        return "No files uploaded"
    
    # Create uploads directory in workspace if it doesn't exist
    uploads_dir = PROJECT_ROOT / "uploads"
    uploads_dir.mkdir(exist_ok=True)
    
    uploaded_info = []
    copied_count = 0
    
    for file_path in files:
        if file_path:
            source_path = Path(file_path)
            if source_path.exists():
                size = source_path.stat().st_size
                size_str = f"{size / 1024:.1f} KB" if size < 1024 * 1024 else f"{size / (1024 * 1024):.1f} MB"
                
                # Copy file to workspace uploads directory
                try:
                    dest_path = uploads_dir / source_path.name
                    
                    # Handle duplicate names
                    counter = 1
                    while dest_path.exists():
                        stem = source_path.stem
                        suffix = source_path.suffix
                        dest_path = uploads_dir / f"{stem}_{counter}{suffix}"
                        counter += 1
                    
                    # Copy file
                    shutil.copy2(source_path, dest_path)
                    
                    relative_path = dest_path.relative_to(PROJECT_ROOT)
                    uploaded_info.append(f"✓ **{source_path.name}** ({size_str}) → `{relative_path}`")
                    copied_count += 1
                except Exception as e:
                    uploaded_info.append(f"✗ **{source_path.name}** - Error: {str(e)}")
    
    if uploaded_info:
        status_msg = f"**✅ Uploaded {copied_count}/{len([f for f in files if f])} file(s) to workspace:**\n\n" + "\n".join(uploaded_info)
        if copied_count > 0:
            status_msg += f"\n\n📁 Files saved to: `uploads/` directory"
        return status_msg
    return "No files uploaded"

# --- CORE LOGIC ---

async def stream_conversation(
    message: str,
    history: List[Dict[str, Any]],
    session_id: str,
):
    """Stream output from CLI backend."""
    if not message.strip():
        yield history, "", session_id, _blank_metrics()
        return

    # Initialize session
    session_value = session_id or f"session-{uuid.uuid4().hex[:8]}"
    
    # Update history with user message
    history = history or []
    history.append({"role": "user", "content": message})
    
    # Add thinking state
    history.append({"role": "assistant", "content": "⏳ Analyzing request..."})
    terminal_output = "# Starting execution...\n"
    
    yield history, terminal_output, session_value, _blank_metrics()

    start = time.monotonic()
    live_text = ""
    chunk_count = 0
    
    try:
        # Stream execution
        async for chunk in _bridge.stream_command(message, session_value):
            chunk_text = chunk or ""
            chunk_count += 1
            live_text += chunk_text
            
            # Build terminal output
            terminal_lines = [
                f"# Execution Log (Session: {session_value[:8]})",
                f"# Time: {round(time.monotonic() - start, 2)}s | Chunks: {chunk_count}",
                "",
                "## Output Stream:",
                live_text if live_text else "(waiting for output...)",
            ]
            terminal_output = "\n".join(terminal_lines)
            
            # Update metrics
            metrics = {
                "chunks": chunk_count,
                "chars": len(live_text),
                "sec": round(time.monotonic() - start, 2),
                "backend": _bridge.backend_label,
            }
            
            # Update chat with streaming cursor
            history[-1]["content"] = live_text + " ▌"
            
            yield history, terminal_output, session_value, metrics
            
    except Exception as e:
        # Error state
        error_msg = f"❌ **Error**: {str(e)}"
        history[-1]["content"] = error_msg
        terminal_output += f"\n\n❌ ERROR: {str(e)}"
        yield history, terminal_output, session_value, _blank_metrics()
        return

    # Complete state - remove cursor
    history[-1]["content"] = live_text
    
    # Final terminal output
    terminal_lines = [
        f"# Execution Log (Session: {session_value[:8]})",
        f"# Time: {round(time.monotonic() - start, 2)}s | Chunks: {chunk_count}",
        "",
        "## Output Stream:",
        live_text if live_text else "(no output)",
        "",
        "✓ Execution complete",
    ]
    terminal_output = "\n".join(terminal_lines)
    
    final_metrics = {
        "chunks": chunk_count,
        "chars": len(live_text),
        "sec": round(time.monotonic() - start, 2),
        "backend": _bridge.backend_label,
    }
    
    yield history, terminal_output, session_value, final_metrics

# --- MINIMAL CSS (only essential adjustments) ---

MINIMAL_CSS = """
/* Minimal CSS for contrast and spacing only */

/* Ensure terminal text is readable in both themes */
.gr-code, .cm-editor {
    font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
    font-size: 13px;
    line-height: 1.5;
}

/* Chat message spacing */
.chat-message {
    padding: 12px 16px;
    margin: 8px 0;
    border-radius: 8px;
}

/* Dark mode adjustments (Gradio Soft theme handles most of this) */
@media (prefers-color-scheme: dark) {
    .gr-code {
        background: #1a1a1a !important;
        color: #e5e5e5 !important;
    }
}

/* Light mode adjustments */
@media (prefers-color-scheme: light) {
    .gr-code {
        background: #f5f5f5 !important;
        color: #1a1a1a !important;
    }
}
"""

# --- UI CONSTRUCTION ---

def create_ui() -> gr.Blocks:
    """Build minimal clean UI using only native Gradio components."""
    
    # Import heroic theme (Gradio 6 with glassmorphism)
    from .heroic_theme import create_heroic_theme, get_glassmorphism_css
    
    theme = create_heroic_theme()
    
    # Combine minimal CSS with glassmorphism CSS
    combined_css = MINIMAL_CSS + "\n\n" + get_glassmorphism_css()

    # Gradio 6: theme and css go in launch(), not Blocks()
    with gr.Blocks(
        title="Qwen Dev CLI · 27 MCP Tools · Constitutional AI",
        fill_height=True,  # Gradio 6: Better layout
    ) as demo:
        
        # State Management
        session_state = gr.State(value=None)
        
        # Header
        gr.Markdown(
            "### **Qwen Dev CLI** · 27 MCP Tools · Constitutional AI-Powered Development",
            elem_id="header"
        )
        
        # Main Layout: 3-Pane
        with gr.Row(equal_height=False):
            
            # Left: Files + Telemetry
            with gr.Column(scale=1, min_width=250, variant="panel"):
                gr.Markdown("**FILES**")
                
                # File Upload - User can upload files/folders from their computer
                file_upload = gr.File(
                    label="Upload Files or Folder",
                    file_count="multiple",
                    file_types=None,  # Accept all file types
                    height=100,
                )
                
                # Upload status
                upload_status = gr.Markdown(
                    value="Ready to upload files...",
                    visible=True,
                    elem_id="upload-status"
                )
                
                # File Explorer - Shows workspace files (will refresh after upload)
                file_explorer = gr.FileExplorer(
                    glob="**/*",
                    root_dir=str(PROJECT_ROOT),
                    height=150,
                    label="Workspace",
                    file_count="multiple",
                )
                
                # Telemetry
                metrics_display = gr.JSON(
                    value=_blank_metrics(),
                    label="Telemetry",
                )

            # Center: Chat + Input
            with gr.Column(scale=3, min_width=500):
                
                # Chat (Gradio 6: always uses "messages" format, no type parameter)
                chatbot = gr.Chatbot(
                    label="Dev Session",
                    height=400,
                    render_markdown=True,
                    avatar_images=(None, None),
                )
                
                # Input Bar
                with gr.Row():
                    msg_input = gr.Textbox(
                        show_label=False,
                        placeholder="Instruct the agent (e.g., 'Run tests and fix errors')...",
                        container=False,
                        scale=9,
                    )
                    run_btn = gr.Button(
                        "Run", 
                        variant="primary", 
                        scale=1,
                        min_width=80,
                    )

            # Right: Terminal + Tools
            with gr.Column(scale=2, min_width=300, variant="panel"):
                with gr.Tabs():
                    with gr.Tab("Terminal"):
                        # Terminal output
                        shell_output = gr.Code(
                            language="shell",
                            label="Live Output",
                            interactive=False,
                            lines=15,
                        )
                    
                    with gr.Tab("MCP Tools"):
                        # MCP Tools table
                        mcp_df = gr.Dataframe(
                            value=_get_mcp_tools_df(),
                            headers=["Category", "Tool", "Description"],
                            interactive=False,
                            wrap=True,
                        )
        
        # Footer
        gr.Markdown(
            f"Backend: {_bridge.backend_label} · Tokens: 0 · Cost: $0.00",
            elem_id="footer"
        )

        # Event Handlers
        
        # File upload handler - copies files to workspace and updates status
        file_upload.upload(
            fn=handle_file_upload,
            inputs=[file_upload],
            outputs=[upload_status]
        ).then(
            # Refresh file explorer after upload
            fn=lambda: gr.update(),
            outputs=[file_explorer]
        )
        
        # Submit message
        msg_input.submit(
            fn=stream_conversation,
            inputs=[msg_input, chatbot, session_state],
            outputs=[chatbot, shell_output, session_state, metrics_display]
        ).then(
            fn=lambda: "", outputs=[msg_input]
        )
        
        # Run button
        run_btn.click(
            fn=stream_conversation,
            inputs=[msg_input, chatbot, session_state],
            outputs=[chatbot, shell_output, session_state, metrics_display]
        ).then(
            fn=lambda: "", outputs=[msg_input]
        )

    # Gradio 6: Return theme and css for launch()
    return demo, theme, combined_css

# --- LAUNCHER ---

if __name__ == "__main__":
    port = int(os.getenv("GRADIO_SERVER_PORT", "7861"))
    
    # Gradio 6: create_ui returns demo, theme, css
    demo, theme, css = create_ui()
    
    print(f"🚀 Launching Qwen Dev CLI UI on port {port}")
    
    # Gradio 6: theme and css go in launch()
    demo.launch(
        server_name="0.0.0.0",
        server_port=port,
        share=False,
        show_error=True,
        theme=theme,
        css=css,
    )
