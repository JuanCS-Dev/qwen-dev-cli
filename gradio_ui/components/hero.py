"""Hero section component - Emotional entry point."""
import gradio as gr


def create_hero_section():
    """
    Create hero section with emotional impact.
    
    Design goals:
    - Immediate "wow" factor
    - Clear value proposition
    - Inviting call-to-action
    """
    gr.HTML(
        """
        <div style="
            text-align: center;
            padding: 48px 24px;
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 12px;
            margin-bottom: 32px;
            box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        ">
            <div style="
                font-size: 2.25rem;
                font-weight: 600;
                color: #1A202C;
                margin-bottom: 12px;
                letter-spacing: -0.02em;
            ">
                QWEN-DEV-CLI
            </div>
            <div style="
                font-size: 1.125rem;
                color: #4A5568;
                margin-bottom: 8px;
                font-weight: 400;
            ">
                AI-Powered Development Partner
            </div>
            <div style="
                font-size: 0.875rem;
                color: #A0AEC0;
                display: flex;
                gap: 12px;
                justify-content: center;
                flex-wrap: wrap;
                margin-top: 16px;
            ">
                <span>Multi-language LSP</span>
                <span>•</span>
                <span>Smart Refactoring</span>
                <span>•</span>
                <span>Context-Aware AI</span>
            </div>
        </div>
        """
    )
