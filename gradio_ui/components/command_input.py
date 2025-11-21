"""Command input component with suggestions."""
import gradio as gr
from typing import Tuple


def create_command_interface() -> Tuple[gr.Textbox, gr.HTML]:
    """
    Create command input with smart suggestions.
    
    Returns:
        Tuple of (input_box, suggestions_html)
    """
    
    # Command input
    command_input = gr.Textbox(
        label="💬 What would you like to do?",
        placeholder="read main.py, refactor legacy code, fix all TODOs...",
        lines=2,
        elem_classes=["command-input"],
        show_label=True
    )
    
    # Minimal suggestions
    suggestions = gr.HTML(
        """
        <div style="margin-top: 16px;">
            <p style="
                color: #4A5568;
                font-size: 0.875rem;
                margin-bottom: 12px;
                font-weight: 500;
            ">Suggestions:</p>
            <div style="display: flex; flex-wrap: wrap; gap: 8px;">
                <span style="
                    display: inline-block;
                    background: #EFF6FF;
                    border: 1px solid #DBEAFE;
                    color: #1E40AF;
                    padding: 6px 12px;
                    border-radius: 6px;
                    cursor: pointer;
                    transition: all 150ms;
                    font-size: 0.875rem;
                    font-weight: 500;
                ">Read README.md</span>
                <span style="
                    display: inline-block;
                    background: #EFF6FF;
                    border: 1px solid #DBEAFE;
                    color: #1E40AF;
                    padding: 6px 12px;
                    border-radius: 6px;
                    cursor: pointer;
                    transition: all 150ms;
                    font-size: 0.875rem;
                    font-weight: 500;
                ">Search imports</span>
                <span style="
                    display: inline-block;
                    background: #EFF6FF;
                    border: 1px solid #DBEAFE;
                    color: #1E40AF;
                    padding: 6px 12px;
                    border-radius: 6px;
                    cursor: pointer;
                    transition: all 150ms;
                    font-size: 0.875rem;
                    font-weight: 500;
                ">Fix TODOs</span>
                <span style="
                    display: inline-block;
                    background: #EFF6FF;
                    border: 1px solid #DBEAFE;
                    color: #1E40AF;
                    padding: 6px 12px;
                    border-radius: 6px;
                    cursor: pointer;
                    transition: all 150ms;
                    font-size: 0.875rem;
                    font-weight: 500;
                ">LSP diagnostics</span>
            </div>
        </div>
        """
    )
    
    return command_input, suggestions
