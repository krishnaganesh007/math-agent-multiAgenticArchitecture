# """
# Memory Layer: Stores and retrieves user preferences and state
# Deterministic: Simple JSON-based storage and retrieval
# """

# from pydantic import BaseModel, Field
# from typing import Optional, Any
# import json
# from pathlib import Path


# # Pydantic Models
# class UserPreferences(BaseModel):
#     """User preferences stored in memory"""
#     name: Optional[str] = Field(default="User", description="User's name")

#     # === Math Assistant Preferences ===
#     preferred_explanation_style: str = Field(
#         default="stepwise",
#         description="How to explain solutions: 'stepwise', 'concise', 'detailed'"
#     )
#     preferred_method: Optional[str] = Field(
#         default=None,
#         description="Preferred integration method: 'manual', 'symbolic', 'auto'"
#     )
#     notation_preference: str = Field(
#         default="latex",
#         description="Output notation: 'latex', 'plain'"
#     )
#     show_reasoning: bool = Field(default=True, description="Whether to show reasoning steps")
#     verification_required: bool = Field(default=True, description="Whether to verify results")
#     math_level: str = Field(
#         default="intermediate",
#         description="User's math proficiency: 'beginner', 'intermediate', 'advanced'"
#     )
#     favorite_topics: list[str] = Field(
#         default_factory=lambda: ["integration"],
#         description="Topics user enjoys"
#     )
#     disliked_topics: list[str] = Field(default_factory=list, description="Topics user struggles with")

#     # === New Communication Preferences ===
#     tone: str = Field(
#         default="friendly",
#         description="Preferred communication tone: 'formal', 'friendly', 'humorous', 'professional'"
#     )
#     font_style: str = Field(
#         default="Arial",
#         description="Preferred font for outgoing communication"
#     )
#     font_color: str = Field(
#         default="#000000",
#         description="Preferred text color in hex format"
#     )
#     signature: str = Field(
#         default="Best regards,\nUser",
#         description="Preferred email or message signature"
#     )
#     include_signature: bool = Field(
#         default=True,
#         description="Whether to include signature in messages"
#     )



# class SessionState(BaseModel):
#     """Current session state"""
#     current_problem: Optional[str] = None
#     iteration_count: int = 0
#     parsed_terms: Optional[Any] = None
#     integrated_terms: list = Field(default_factory=list)
#     differentiated_terms: list = Field(default_factory=list)
#     history: list[dict] = Field(default_factory=list)


# class MemoryContext(BaseModel):
#     """Complete memory context passed to other layers"""
#     preferences: UserPreferences
#     session: SessionState


# class MemoryLayer:
#     """Memory cognitive layer - manages state and preferences"""
    
#     def __init__(self, memory_file: str = "user_memory.json"):
#         self.memory_file = Path(memory_file)
#         self.preferences = self._load_preferences()
#         self.session = SessionState()
    
#     def _load_preferences(self) -> UserPreferences:
#         """Load user preferences from JSON file"""
#         if self.memory_file.exists():
#             try:
#                 with open(self.memory_file, 'r') as f:
#                     data = json.load(f)
#                     return UserPreferences(**data)
#             except Exception as e:
#                 print(f"Warning: Could not load preferences: {e}")
#                 return UserPreferences()
#         return UserPreferences()
    
#     def save_preferences(self):
#         """Save preferences to JSON file"""
#         with open(self.memory_file, 'w') as f:
#             json.dump(self.preferences.model_dump(), f, indent=2)
    
#     def get_context(self) -> MemoryContext:
#         """Get complete memory context for other layers"""
#         return MemoryContext(
#             preferences=self.preferences,
#             session=self.session
#         )
    
#     def update_session(self, **kwargs):
#         """Update session state"""
#         for key, value in kwargs.items():
#             if hasattr(self.session, key):
#                 setattr(self.session, key, value)
    
#     def add_to_history(self, entry: dict):
#         """Add entry to session history"""
#         self.session.history.append(entry)
    
#     def reset_session(self):
#         """Reset session state (keeps preferences)"""
#         self.session = SessionState()
    
#     def collect_preferences_interactive(self):
#         """Interactively collect user preferences before agent starts"""
#         print("\n=== User Preference Collection ===")
#         print("Let's personalize your mathematical assistant!\n")
        
#         name = input("What's your name? [User]: ").strip() or "User"
#         self.preferences.name = name
        
#         print(f"\nHi {name}! Let's set up your preferences.\n")
        
#         # Explanation style
#         print("How do you prefer explanations?")
#         print("1. Stepwise (detailed step-by-step)")
#         print("2. Concise (brief summaries)")
#         print("3. Detailed (comprehensive with context)")
#         style_choice = input("Choice [1]: ").strip() or "1"
#         style_map = {"1": "stepwise", "2": "concise", "3": "detailed"}
#         self.preferences.preferred_explanation_style = style_map.get(style_choice, "stepwise")
        
#         # Method preference
#         print("\nPreferred integration method?")
#         print("1. Manual (step-by-step using rules)")
#         print("2. Symbolic (using SymPy library)")
#         print("3. Auto (let the system decide)")
#         method_choice = input("Choice [3]: ").strip() or "3"
#         method_map = {"1": "manual", "2": "symbolic", "3": "auto"}
#         self.preferences.preferred_method = method_map.get(method_choice, "auto")
        
#         # Reasoning visibility
#         show = input("\nShow reasoning steps? (y/n) [y]: ").strip().lower() or "y"
#         self.preferences.show_reasoning = (show == "y")
        
#         # Math level
#         print("\nYour math level?")
#         print("1. Beginner")
#         print("2. Intermediate")
#         print("3. Advanced")
#         level_choice = input("Choice [2]: ").strip() or "2"
#         level_map = {"1": "beginner", "2": "intermediate", "3": "advanced"}
#         self.preferences.math_level = level_map.get(level_choice, "intermediate")
        
#         # --- New Communication Preferences ---
#         print("\nNow let's personalize your communication style.\n")
#         tone = input("Preferred tone (friendly/formal/humorous/professional) [friendly]: ").strip().lower() or "friendly"
#         self.preferences.tone = tone

#         font = input("Preferred font style (Arial/Times New Roman/Calibri) [Arial]: ").strip() or "Arial"
#         self.preferences.font_style = font

#         color = input("Preferred text color (can be a color name like 'red' or a hex code like '#FF5733'): ").strip() or "#000000"
#         self.preferences.font_color = color

#         signature = input("Your preferred signature [Best regards, <name>]: ").strip() or f"Best regards,\n{name}"
#         self.preferences.signature = signature

#         include_sig = input("Include signature in messages? (y/n) [y]: ").strip().lower() or "y"
#         self.preferences.include_signature = (include_sig == "y")

#         # Save preferences
#         self.save_preferences()
#         print(f"\n✓ Preferences saved! Welcome, {name}!\n")


"""
Memory Layer: Stores and retrieves user preferences and state
Deterministic: Simple JSON-based storage and retrieval
"""

from pydantic import BaseModel, Field
from typing import Optional, Any
import json
from pathlib import Path
import webcolors


# ===== Utility Function =====
def get_hex_color(color_name: str) -> str:
    """Convert color name to hex if needed."""
    try:
        # If already a valid hex, return as-is
        if color_name.startswith("#") and len(color_name) in [4, 7]:
            return color_name
        # Otherwise, convert from color name
        return webcolors.name_to_hex(color_name.lower())
    except ValueError:
        print(f"⚠️ Warning: Unknown color '{color_name}', defaulting to black.")
        return "#000000"


# ===== Pydantic Models =====
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

    # === NEW PERSONALIZATION FIELDS ===
    font_style: str = Field(
        default="Arial",
        description="Preferred font for communication (e.g., Arial, Times New Roman, Calibri)"
    )

    font_color: str = Field(
        default="black",
        description="Preferred text color (can be a color name like 'red' or a hex code like '#FF5733')"
    )

    communication_tone: str = Field(
        default="friendly",
        description="Tone for responses or emails: 'friendly', 'professional', 'casual'"
    )

    signature: str = Field(
        default="Best regards,\nYour AI Assistant",
        description="Custom email signature text"
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


# ===== Memory Layer =====
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

        # Font style
        font = input("\nPreferred font style (e.g., Arial, Calibri, Times New Roman) [Arial]: ").strip() or "Arial"
        self.preferences.font_style = font

        # Font color
        color = input("Preferred font color (name or hex, e.g., red or #FF0000) [black]: ").strip() or "black"
        self.preferences.font_color = get_hex_color(color)

        # Communication tone
        print("\nPreferred tone of communication?")
        print("1. Friendly")
        print("2. Professional")
        print("3. Casual")
        tone_choice = input("Choice [1]: ").strip() or "1"
        tone_map = {"1": "friendly", "2": "professional", "3": "casual"}
        self.preferences.communication_tone = tone_map.get(tone_choice, "friendly")

        # Signature
        signature = input("\nEnter your preferred signature (leave blank for default): ").strip()
        if signature:
            self.preferences.signature = signature

        # Save preferences
        self.save_preferences()
        print(f"\n✓ Preferences saved! Welcome, {name}!\n")

