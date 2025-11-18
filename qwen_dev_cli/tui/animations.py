"""
🎬 TUI Animations - Apple-style smooth transitions
Implements cubic bezier easing, fade effects, and smooth state changes
"""

import time
import math
from typing import Callable, Optional
from dataclasses import dataclass


@dataclass
class AnimationConfig:
    """Configuration for animations"""
    duration: float = 0.3  # seconds
    easing: str = "ease-out"  # ease-in, ease-out, ease-in-out, linear
    fps: int = 60


class Easing:
    """Easing functions for smooth animations"""
    
    @staticmethod
    def linear(t: float) -> float:
        """Linear easing"""
        return t
    
    @staticmethod
    def ease_in(t: float) -> float:
        """Ease-in (cubic)"""
        return t * t * t
    
    @staticmethod
    def ease_out(t: float) -> float:
        """Ease-out (cubic) - Apple's favorite"""
        return 1 - pow(1 - t, 3)
    
    @staticmethod
    def ease_in_out(t: float) -> float:
        """Ease-in-out (cubic)"""
        if t < 0.5:
            return 4 * t * t * t
        return 1 - pow(-2 * t + 2, 3) / 2
    
    @staticmethod
    def spring(t: float) -> float:
        """Spring easing (bouncy)"""
        return 1 - math.cos(t * math.pi * 2) * (1 - t)
    
    @staticmethod
    def elastic(t: float) -> float:
        """Elastic easing"""
        if t == 0 or t == 1:
            return t
        p = 0.3
        return pow(2, -10 * t) * math.sin((t - p / 4) * (2 * math.pi) / p) + 1


def get_easing_function(name: str) -> Callable[[float], float]:
    """Get easing function by name"""
    easing_map = {
        "linear": Easing.linear,
        "ease-in": Easing.ease_in,
        "ease-out": Easing.ease_out,
        "ease-in-out": Easing.ease_in_out,
        "spring": Easing.spring,
        "elastic": Easing.elastic,
    }
    return easing_map.get(name, Easing.ease_out)


class Animator:
    """Handles smooth animations"""
    
    def __init__(self, config: Optional[AnimationConfig] = None):
        self.config = config or AnimationConfig()
        self.easing_func = get_easing_function(self.config.easing)
    
    def animate(
        self,
        start: float,
        end: float,
        callback: Callable[[float], None],
        duration: Optional[float] = None,
    ) -> None:
        """
        Animate from start to end value
        
        Args:
            start: Starting value
            end: Ending value
            callback: Function to call with interpolated value
            duration: Override default duration
        """
        duration = duration or self.config.duration
        frame_time = 1.0 / self.config.fps
        elapsed = 0.0
        
        while elapsed < duration:
            t = elapsed / duration
            eased = self.easing_func(t)
            value = start + (end - start) * eased
            callback(value)
            
            time.sleep(frame_time)
            elapsed += frame_time
        
        # Final frame
        callback(end)
    
    def fade_in(self, callback: Callable[[float], None]) -> None:
        """Fade in from 0 to 1"""
        self.animate(0.0, 1.0, callback)
    
    def fade_out(self, callback: Callable[[float], None]) -> None:
        """Fade out from 1 to 0"""
        self.animate(1.0, 0.0, callback)


class StateTransition:
    """Manages state transitions with animations"""
    
    def __init__(self, initial_state: str):
        self.current_state = initial_state
        self.animator = Animator(AnimationConfig(duration=0.2))
    
    def transition_to(
        self,
        new_state: str,
        on_exit: Optional[Callable] = None,
        on_enter: Optional[Callable] = None,
    ) -> None:
        """
        Transition from current state to new state
        
        Args:
            new_state: Target state
            on_exit: Callback when leaving current state
            on_enter: Callback when entering new state
        """
        if new_state == self.current_state:
            return
        
        # Exit current state with fade-out
        if on_exit:
            self.animator.fade_out(lambda opacity: on_exit(opacity))
        
        # Update state
        old_state = self.current_state
        self.current_state = new_state
        
        # Enter new state with fade-in
        if on_enter:
            self.animator.fade_in(lambda opacity: on_enter(opacity))


class LoadingAnimation:
    """Smooth loading animations"""
    
    SPINNERS = {
        "dots": ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"],
        "line": ["—", "\\", "|", "/"],
        "arrow": ["←", "↖", "↑", "↗", "→", "↘", "↓", "↙"],
        "box": ["◰", "◳", "◲", "◱"],
        "bounce": ["⠁", "⠂", "⠄", "⡀", "⢀", "⠠", "⠐", "⠈"],
    }
    
    def __init__(self, style: str = "dots", speed: float = 0.08):
        self.frames = self.SPINNERS.get(style, self.SPINNERS["dots"])
        self.speed = speed
        self.current_frame = 0
    
    def next_frame(self) -> str:
        """Get next frame in animation"""
        frame = self.frames[self.current_frame]
        self.current_frame = (self.current_frame + 1) % len(self.frames)
        return frame
    
    def animate_pulse(self, text: str, width: int = 40) -> str:
        """Animate a pulsing progress bar"""
        frame = self.current_frame % width
        bar = " " * width
        
        if frame < width // 2:
            pos = frame
        else:
            pos = width - frame - 1
        
        bar = bar[:pos] + "█" + bar[pos + 1:]
        self.current_frame += 1
        
        return f"{text} [{bar}]"


class SlideTransition:
    """Slide-in/slide-out transitions"""
    
    @staticmethod
    def slide_in(text: str, width: int, progress: float) -> str:
        """Slide text in from right"""
        visible_chars = int(len(text) * progress)
        return text[:visible_chars].rjust(width)
    
    @staticmethod
    def slide_out(text: str, width: int, progress: float) -> str:
        """Slide text out to left"""
        visible_chars = int(len(text) * (1 - progress))
        return text[:visible_chars].ljust(width)


# Pre-configured animators
smooth_animator = Animator(AnimationConfig(duration=0.3, easing="ease-out"))
quick_animator = Animator(AnimationConfig(duration=0.15, easing="ease-out"))
spring_animator = Animator(AnimationConfig(duration=0.4, easing="spring"))
