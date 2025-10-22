"""
Memory Layer: Stores and retrieves user preferences and state
Deterministic: Simple JSON-based storage and retrieval
"""

from pydantic import BaseModel, Field
from typing import Optional, Any
import json
from pathlib import Path


# Pydantic Models
class UserPreferences(BaseModel):
    """User preferences stored in memory"""
    name: Optional[str] = Field(default="User", description="User's name")
    preferred_explanation_style: str = Field(
        default="stepwise",
        description="How to explain solutions: 'stepwise', 'concise', 'detailed'"
    )
    preferred_method: Optional[str] = Field(
        default=None,
        description="Preferred integration method: 'manual', 'symbolic', 'auto'"
    )
    notation_preference: str = Field(
        default="latex",
        description="Output notation: 'latex', 'plain'"
    )
    show_reasoning: bool = Field(
        default=True,
        description="Whether to show reasoning steps"
    )
    verification_required: bool = Field(
        default=True,
        description="Whether to verify results"
    )
    math_level: str = Field(
        default="intermediate",
        description="User's math proficiency: 'beginner', 'intermediate', 'advanced'"
    )
    favorite_topics: list[str] = Field(
        default_factory=lambda: ["integration"],
        description="Topics user enjoys"
    )
    disliked_topics: list[str] = Field(
        default_factory=list,
        description="Topics user struggles with"
    )


class SessionState(BaseModel):
    """Current session state"""
    current_problem: Optional[str] = None
    iteration_count: int = 0
    parsed_terms: Optional[Any] = None
    integrated_terms: list = Field(default_factory=list)
    differentiated_terms: list = Field(default_factory=list)
    history: list[dict] = Field(default_factory=list)


class MemoryContext(BaseModel):
    """Complete memory context passed to other layers"""
    preferences: UserPreferences
    session: SessionState


class MemoryLayer:
    """Memory cognitive layer - manages state and preferences"""
    
    def __init__(self, memory_file: str = "user_memory.json"):
        self.memory_file = Path(memory_file)
        self.preferences = self._load_preferences()
        self.session = SessionState()
    
    def _load_preferences(self) -> UserPreferences:
        """Load user preferences from JSON file"""
        if self.memory_file.exists():
            try:
                with open(self.memory_file, 'r') as f:
                    data = json.load(f)
                    return UserPreferences(**data)
            except Exception as e:
                print(f"Warning: Could not load preferences: {e}")
                return UserPreferences()
        return UserPreferences()
    
    def save_preferences(self):
        """Save preferences to JSON file"""
        with open(self.memory_file, 'w') as f:
            json.dump(self.preferences.model_dump(), f, indent=2)
    
    def get_context(self) -> MemoryContext:
        """Get complete memory context for other layers"""
        return MemoryContext(
            preferences=self.preferences,
            session=self.session
        )
    
    def update_session(self, **kwargs):
        """Update session state"""
        for key, value in kwargs.items():
            if hasattr(self.session, key):
                setattr(self.session, key, value)
    
    def add_to_history(self, entry: dict):
        """Add entry to session history"""
        self.session.history.append(entry)
    
    def reset_session(self):
        """Reset session state (keeps preferences)"""
        self.session = SessionState()
    
    def collect_preferences_interactive(self):
        """Interactively collect user preferences before agent starts"""
        print("\n=== User Preference Collection ===")
        print("Let's personalize your mathematical assistant!\n")
        
        name = input("What's your name? [User]: ").strip() or "User"
        self.preferences.name = name
        
        print(f"\nHi {name}! Let's set up your preferences.\n")
        
        # Explanation style
        print("How do you prefer explanations?")
        print("1. Stepwise (detailed step-by-step)")
        print("2. Concise (brief summaries)")
        print("3. Detailed (comprehensive with context)")
        style_choice = input("Choice [1]: ").strip() or "1"
        style_map = {"1": "stepwise", "2": "concise", "3": "detailed"}
        self.preferences.preferred_explanation_style = style_map.get(style_choice, "stepwise")
        
        # Method preference
        print("\nPreferred integration method?")
        print("1. Manual (step-by-step using rules)")
        print("2. Symbolic (using SymPy library)")
        print("3. Auto (let the system decide)")
        method_choice = input("Choice [3]: ").strip() or "3"
        method_map = {"1": "manual", "2": "symbolic", "3": "auto"}
        self.preferences.preferred_method = method_map.get(method_choice, "auto")
        
        # Reasoning visibility
        show = input("\nShow reasoning steps? (y/n) [y]: ").strip().lower() or "y"
        self.preferences.show_reasoning = (show == "y")
        
        # Math level
        print("\nYour math level?")
        print("1. Beginner")
        print("2. Intermediate")
        print("3. Advanced")
        level_choice = input("Choice [2]: ").strip() or "2"
        level_map = {"1": "beginner", "2": "intermediate", "3": "advanced"}
        self.preferences.math_level = level_map.get(level_choice, "intermediate")
        
        # Save preferences
        self.save_preferences()
        print(f"\n✓ Preferences saved! Welcome, {name}!\n")
