from typing import Dict, Any, List, Tuple, Optional
import re
from backend.llm_service import LLMService

class BlogGenerator:
    """
    Generates blog content by creating prompts for an LLM 
    and using the LLMService to get the generated content.
    Enhanced with multi-language, cleanup, humanization, and code detection.
    """
    
    def __init__(self):
        """Initializes the BlogGenerator and the LLMService."""
        try:
            self.llm_service = LLMService()
            self.llm_enabled = True
        except ValueError:
            self.llm_service = None
            self.llm_enabled = False
            print("⚠️ WARNING: LLM Service not initialized. NEBIUS_API_KEY may be missing.")

        self.templates = {
            "article": self._create_article_prompt,
            "tutorial": self._create_tutorial_prompt,
            "review": self._create_review_prompt,
            "summary": self._create_summary_prompt
        }
        
        # Language configurations
        self.languages = {
            "en": {"name": "English", "instruction": "Write in clear, professional English."},
            "hi": {"name": "Hindi", "instruction": "Write in clear, professional Hindi. Use Devanagari script."},
            "es": {"name": "Spanish", "instruction": "Write in clear, professional Spanish."},
            "fr": {"name": "French", "instruction": "Write in clear, professional French."},
            "de": {"name": "German", "instruction": "Write in clear, professional German."},
            "pt": {"name": "Portuguese", "instruction": "Write in clear, professional Portuguese."},
            "ja": {"name": "Japanese", "instruction": "Write in clear, professional Japanese."},
            "ko": {"name": "Korean", "instruction": "Write in clear, professional Korean."}
        }
    
    def generate_blog(self, video_data: Dict[str, Any], template: str, transcript: Optional[str], 
                     language: str = "en", fact_cleanup: bool = True, humanize: bool = True,
                     is_code_tutorial: bool = False) -> str:
        """Generate blog content based on template and video data using an LLM."""
        if not self.llm_enabled:
            return "## LLM Service Not Available\n\nPlease ensure your `NEBIUS_API_KEY` is correctly set in your `.env` file and restart the server."

        if template not in self.templates:
            raise ValueError(f"Unknown template: {template}")
        
        # Clean transcript if fact cleanup is enabled
        if transcript and fact_cleanup:
            transcript = self._clean_transcript_advanced(transcript)
        
        # Detect if it's a code tutorial and adjust template accordingly
        if is_code_tutorial and template == "tutorial":
            system_prompt, user_prompt = self._create_code_tutorial_prompt(video_data, transcript, language, humanize)
        else:
            system_prompt, user_prompt = self.templates[template](video_data, transcript, language, humanize)
        
        content = self.llm_service.generate_content(system_prompt, user_prompt)
        
        # Apply content gap filling
        content = self._fill_content_gaps(content)
        
        return content

    def detect_code_content(self, transcript: Optional[str]) -> bool:
        """Detect if the video content is related to coding or tutorials."""
        if not transcript:
            return False
            
        code_indicators = [
            # Programming languages
            'javascript', 'python', 'java', 'react', 'node', 'html', 'css',
            'typescript', 'angular', 'vue', 'php', 'ruby', 'go', 'rust',
            
            # Code-related terms
            'function', 'class', 'import', 'export', 'console.log', 'print(',
            'def ', 'var ', 'let ', 'const ', 'if (', 'for (', 'while (',
            
            # Development tools
            'git', 'github', 'npm', 'yarn', 'pip', 'docker', 'kubernetes',
            'api', 'database', 'sql', 'mongodb', 'postgresql',
            
            # Tutorial indicators
            'tutorial', 'coding', 'programming', 'development', 'build',
            'create', 'install', 'setup', 'configure', 'deploy'
        ]
        
        transcript_lower = transcript.lower()
        code_mentions = sum(1 for indicator in code_indicators if indicator in transcript_lower)
        
        # If more than 3 code-related terms are mentioned, consider it a code tutorial
        return code_mentions >= 3

    def _clean_transcript_advanced(self, transcript: str) -> str:
        """Advanced transcript cleaning to remove filler content and promotional segments."""
        if not transcript:
            return transcript
            
        # Remove promotional content patterns
        promo_patterns = [
            r'this video is sponsored by.*?(?=\.|$)',
            r'before we start.*?subscribe.*?(?=\.|$)',
            r'don\'t forget to like and subscribe.*?(?=\.|$)',
            r'check out the description.*?(?=\.|$)',
            r'link in the description.*?(?=\.|$)',
            r'thanks to.*?for sponsoring.*?(?=\.|$)',
            r'use code.*?for.*?discount.*?(?=\.|$)',
        ]
        
        # Remove greeting patterns
        greeting_patterns = [
            r'^(hey|hi|hello|what\'s up).*?(?=\.|$)',
            r'welcome back to.*?(?=\.|$)',
            r'in today\'s video.*?(?=\.|$)',
        ]
        
        # Remove filler words and phrases
        filler_patterns = [
            r'\b(um|uh|like|you know|so basically|okay|alright|actually)\b',
            r'\b(sort of|kind of|i mean|you see|right\?)\b',
            r'\[.*?\]',  # Remove bracketed content like [Music]
            r'\(.*?\)'   # Remove parenthetical content
        ]
        
        cleaned = transcript
        
        # Apply promotional content removal
        for pattern in promo_patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
        
        # Apply greeting removal (only at the beginning)
        for pattern in greeting_patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
        
        # Apply filler removal
        for pattern in filler_patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
        
        # Remove repetitive phrases
        cleaned = self._remove_repetitions(cleaned)
        
        # Clean up extra spaces and normalize
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        return cleaned

    def _remove_repetitions(self, text: str) -> str:
        """Remove repetitive phrases and sentences."""
        sentences = text.split('.')
        unique_sentences = []
        seen = set()
        
        for sentence in sentences:
            sentence = sentence.strip().lower()
            if sentence and sentence not in seen and len(sentence) > 10:
                seen.add(sentence)
                unique_sentences.append(sentence)
        
        return '. '.join(unique_sentences)

    def _fill_content_gaps(self, content: str) -> str:
        """Intelligently fill content gaps and add explanations where needed."""
        # This is a simplified implementation
        # In a full implementation, this would use NLP to detect gaps
        
        # Add transitions between abrupt topic changes
        paragraphs = content.split('\n\n')
        enhanced_paragraphs = []
        
        for i, paragraph in enumerate(paragraphs):
            enhanced_paragraphs.append(paragraph)
            
            # Add transition if needed (simplified logic)
            if i < len(paragraphs) - 1 and len(paragraph) > 100:
                next_paragraph = paragraphs[i + 1]
                if self._needs_transition(paragraph, next_paragraph):
                    enhanced_paragraphs.append("\nLet's explore this further.")
        
        return '\n\n'.join(enhanced_paragraphs)

    def _needs_transition(self, current: str, next_paragraph: str) -> bool:
        """Determine if a transition is needed between paragraphs."""
        # Simplified logic - in practice, this would be more sophisticated
        current_words = set(current.lower().split())
        next_words = set(next_paragraph.lower().split())
        
        # If there's little word overlap, might need a transition
        overlap = len(current_words.intersection(next_words))
        return overlap < 3

    def _get_content_source(self, video_data: Dict[str, Any], transcript: Optional[str]) -> Tuple[str, str]:
        """Determines the best content source (transcript or description) to use for the prompt."""
        description = video_data.get('description', '')
        if transcript and len(transcript.strip()) > 100:
            return transcript, "video transcript"
        return description, "video description"

    def _get_language_instruction(self, language: str, humanize: bool) -> str:
        """Get language-specific instructions for the LLM."""
        lang_config = self.languages.get(language, self.languages["en"])
        instruction = lang_config["instruction"]
        
        if humanize:
            instruction += " Use a natural, conversational tone that sounds human-written, not AI-generated."
        
        return instruction

    def _create_code_tutorial_prompt(self, video_data: Dict[str, Any], transcript: Optional[str], 
                                   language: str, humanize: bool) -> Tuple[str, str]:
        """Create specialized prompt for code tutorials."""
        system_prompt = (
            "You are an expert technical writer who creates detailed coding tutorials from video content. "
            "Format code properly with syntax highlighting, include copy buttons, and structure content "
            "with Prerequisites, Steps, Code Blocks, and Expected Output sections. "
            f"{self._get_language_instruction(language, humanize)}"
        )
        
        content_source, source_type = self._get_content_source(video_data, transcript)

        user_prompt = f"""
Create a comprehensive coding tutorial in Markdown format based on the video information below.

**Video Title:** {video_data.get('title')}
**Channel:** {video_data.get('channel_name')}
**Content Source (from {source_type}):**
---
{content_source[:4000]}
---

**Instructions:**
1. Create an engaging tutorial title
2. Add a brief overview of what will be built/learned
3. List Prerequisites (tools, knowledge, dependencies)
4. Break down into clear, numbered steps
5. For each code section, use proper markdown code blocks with language specification
6. Include expected output or results after code blocks
7. Add troubleshooting tips where relevant
8. Conclude with next steps or additional resources

**Code Block Format:**
```language
// Your code here
```

**Language:** {self.languages.get(language, {}).get('name', 'English')}
"""
        return system_prompt, user_prompt

    # --------------------------------------------------------
    # ARTICLE PROMPT (Enhanced with multi-language and humanization)
    # --------------------------------------------------------
    def _create_article_prompt(self, video_data: Dict[str, Any], transcript: Optional[str], 
                              language: str = "en", humanize: bool = True) -> Tuple[str, str]:
        system_prompt = (
            "You are an expert blog writer who turns video content into rich, well-structured, SEO-friendly articles. "
            "Write with clarity, depth, and flow. Use Markdown formatting, including headings, subheadings, bold, "
            "lists, and examples when useful. Maintain an informative but engaging tone throughout. "
            f"{self._get_language_instruction(language, humanize)}"
        )
        
        content_source, source_type = self._get_content_source(video_data, transcript)

        user_prompt = f"""
Please generate a comprehensive blog article in Markdown format based on the video information below.

**Video Title:** {video_data.get('title')}
**Channel:** {video_data.get('channel_name')}
**Content Source (from {source_type}):**
---
{content_source[:4000]}
---

**Instructions:**
1. Create a compelling headline inspired by the video title.
2. Write an introduction that explains the topic, why it matters, and what readers will learn.
3. Identify the 3–6 main themes or takeaways from the content.
4. For each theme, create a detailed section with a descriptive subheading. Expand clearly with explanations, insights, and helpful context.
5. Add examples or clarifications when they improve reader understanding.
6. Conclude with a meaningful summary and final insight.
7. Produce a polished Markdown article with no meta commentary.

**Language:** {self.languages.get(language, {}).get('name', 'English')}
"""
        return system_prompt, user_prompt

    # --------------------------------------------------------
    # TUTORIAL PROMPT (Enhanced)
    # --------------------------------------------------------
    def _create_tutorial_prompt(self, video_data: Dict[str, Any], transcript: Optional[str], 
                               language: str = "en", humanize: bool = True) -> Tuple[str, str]:
        system_prompt = (
            "You are a technical writer who creates clear, structured, deeply detailed tutorials from video content. "
            "Write step-by-step, with explanations that make each step easy to follow. Use Markdown formatting, "
            "numbered steps, subheadings, and code blocks when helpful. "
            f"{self._get_language_instruction(language, humanize)}"
        )
        
        content_source, source_type = self._get_content_source(video_data, transcript)

        user_prompt = f"""
Please generate a detailed step-by-step tutorial in Markdown format using the information below.

**Video Title:** {video_data.get('title')}
**Channel:** {video_data.get('channel_name')}
**Content Source (from {source_type}):**
---
{content_source[:4000]}
---

**Instructions:**
1. Create an action-focused headline.
2. Write an overview explaining what the tutorial teaches and the final result.
3. Add prerequisites if necessary (tools, software, knowledge).
4. Break the process into a sequence of detailed, logical steps.
5. For each step:
   - Add a subheading.
   - Explain what to do and why it matters.
   - Add warnings, notes, or tips where useful.
   - Include code blocks if applicable.
6. Conclude with what the user accomplished and optional next steps.
7. Output the whole tutorial in clean Markdown.

**Language:** {self.languages.get(language, {}).get('name', 'English')}
"""
        return system_prompt, user_prompt

    # --------------------------------------------------------
    # REVIEW PROMPT (Enhanced)
    # --------------------------------------------------------
    def _create_review_prompt(self, video_data: Dict[str, Any], transcript: Optional[str], 
                             language: str = "en", humanize: bool = True) -> Tuple[str, str]:
        system_prompt = (
            "You are a professional reviewer who writes balanced, in-depth evaluations of products, tools, or content "
            "explained in videos. Your reviews should feel structured, fair, and insightful. Use Markdown formatting, "
            "with sections like Overview, Pros, Cons, Performance, and Final Verdict. "
            f"{self._get_language_instruction(language, humanize)}"
        )

        content_source, source_type = self._get_content_source(video_data, transcript)

        user_prompt = f"""
Please generate a detailed and balanced review in Markdown format based on the video content.

**Video Title:** {video_data.get('title')}
**Channel:** {video_data.get('channel_name')}
**Content Source (from {source_type}):**
---
{content_source[:4000]}
---

**Instructions:**
1. Create a strong review headline.
2. Begin with an overview of the product/topic and what it aims to achieve.
3. Provide a deeper analysis covering features, performance, usability, strengths, and weaknesses.
4. Add the following sections:
   - **Pros:** meaningful positive points in bullets.
   - **Cons:** realistic drawbacks, not generic filler.
5. Include a **Final Verdict** summarizing who it is for and whether it is worth considering.
6. Add a star rating out of 5 with a one-line justification.
7. Output the result as a clean Markdown review.

**Language:** {self.languages.get(language, {}).get('name', 'English')}
"""
        return system_prompt, user_prompt

    # --------------------------------------------------------
    # SUMMARY PROMPT (Enhanced)
    # --------------------------------------------------------
    def _create_summary_prompt(self, video_data: Dict[str, Any], transcript: Optional[str], 
                              language: str = "en", humanize: bool = True) -> Tuple[str, str]:
        system_prompt = (
            "You are an efficient summarizer who extracts the most important insights from video content. "
            "Write summaries that are short but meaningful, structured, and easy to skim. Use Markdown headings and bullet points. "
            f"{self._get_language_instruction(language, humanize)}"
        )

        content_source, source_type = self._get_content_source(video_data, transcript)

        user_prompt = f"""
Please produce a clear and slightly detailed summary in Markdown format.

**Video Title:** {video_data.get('title')}
**Channel:** {video_data.get('channel_name')}
**Content Source (from {source_type}):**
---
{content_source[:4000]}
---

**Instructions:**
1. Use the video title as the main heading.
2. Write a one-paragraph overview explaining the main idea and purpose of the video.
3. Provide a bulleted list of the 6–10 most important insights, lessons, or events.
4. Keep the language simple, clear, and direct.
5. Deliver the final result as a complete Markdown summary.

**Language:** {self.languages.get(language, {}).get('name', 'English')}
"""
        return system_prompt, user_prompt
