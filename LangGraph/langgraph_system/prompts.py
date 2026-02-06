"""
[Prompt Management System]
생성용 프롬프트(GenerationPrompts)는 영어로, 
검증용 프롬프트(VerificationPrompts)는 한국어로 관리합니다.
"""

class GenerationPrompts:
    """
    [Generation Prompts - English]
    Used for generating high-quality content using LLMs.
    """
    
    # Step 1: Diagnosis
    DIAGNOSIS_SYSTEM = (
        "You are a Brand Strategy Consultant. "
        "You will receive Q&A data in JSON format from answers.json. "
        "Analyze it from Business, User, and Market perspectives to provide comprehensive brand diagnosis."
    )
    
    DIAGNOSIS_USER = """
    [Brand Q&A Data - JSON Format]
    {qa_data_json}
    
    [JSON Parsing Instructions]
    The above data follows this structure:
    - "questions" array contains question-answer pairs
    - Each item has: "id", "question_text" (Korean), "answer"
    - If "answer" is a dict with "value" field, use the "value" (English key)
    - If "answer" is plain text, use it as-is (Korean text is acceptable)
    - If "answer" is a list, it's multiple selections
    
    [Task]
    Analyze the business context and provide:
    
    1. Multi-Perspective Analysis:
       - Business Perspective: Revenue model, scalability, competitive strengths
       - User Perspective: Target audience needs, pain points, benefits
       - Market Perspective: Market trends, competition, differentiation
       
    2. Core Insights:
       - Diagnosis Summary: Overall brand status (2-3 sentences)
       - Core Keywords: 3 keywords that best represent the brand
       - Target Persona: Descriptive name for core audience
       - Brand Essence: One-sentence essence of the brand (for naming foundation)
       - Emotional Core: Primary emotional trigger point (for concept development)
       - Differentiation Point: Key competitive advantage summary (for storytelling)
    
    [Output Format - JSON]
    {{
      "summary": "Overall diagnosis in Korean...",
      "keywords": ["Keyword1", "Keyword2", "Keyword3"],
      "persona": "Target Persona",
      "perspectives": {{
        "business_perspective": "Analysis in Korean...",
        "user_perspective": "Analysis in Korean...",
        "market_perspective": "Analysis in Korean..."
      }},
      "brand_essence": "One-sentence brand essence in Korean",
      "emotional_core": "Primary emotional trigger in Korean",
      "differentiation_point": "Key competitive advantage in Korean"
    }}
    
    IMPORTANT: All output values must be in KOREAN.
    """

    # Step 2: Naming
    NAMING_SYSTEM = (
        "You are a Creative Brand Naming Expert. "
        "Generate creative and market-fit brand names based on the brand diagnosis and user preferences."
    )
    
    NAMING_USER = """
    [Brand Context]
    - Diagnosis Summary: {diagnosis_summary}
    - Core Keywords: {core_keywords}
    - Target Persona: {target_persona}
    
    [User Q&A Data - JSON Format]
    {qa_data_json}
    
    {feedback_section}
    
    [Task]
    1. First, analyze the Q&A data to extract key insights about naming preferences.
    2. Generate 3 DISTINCT brand name candidates based on the analysis.
    
    For each candidate, provide:
    - Brand Name: The proposed name (Korean or English as appropriate).
    - Rationale: Why this name fits the brand strategy (in Korean).
    - Q&A Analysis Summary: Brief summary of how Q&A insights influenced this name (2-3 sentences in Korean).
    - Q&A Keywords: 3-5 key terms extracted from Q&A that support this naming choice.
    
    [Output Format - JSON]
    {{
      "options": [
        {{
          "brand_name": "Name1",
          "name_rationale": "Reasoning in Korean...",
          "qa_analysis_summary": "Q&A 분석 요약 (2-3문장)...",
          "qa_keywords": ["키워드1", "키워드2", "키워드3"]
        }},
        ... (3 options total)
      ]
    }}
    """

    # Step 3: Concept
    CONCEPT_SYSTEM = (
        "You are a Brand Concept Architect. "
        "Develop a compelling brand concept statement and positioning strategy."
    )
    
    CONCEPT_USER = """
    [Brand Context]
    - Diagnosis Summary: {diagnosis_summary}
    - Selected Brand Name: {brand_name}
    - Naming Rationale: {name_rationale}
    
    [User Q&A Data - JSON Format]
    {qa_data_json}
    
    {feedback_section}
    
    [Task]
    1. First, analyze the Q&A data to understand concept direction preferences.
    2. Develop 3 unique concept directions for the brand '{brand_name}'.
    
    For each direction, provide:
    - Concept Statement: A catchy slogan or concept sentence.
    - Rationale: The strategic reasoning behind this concept (in Korean).
    - Brand Values: 3-5 core brand values that this concept embodies (in Korean).
    - Q&A Analysis Summary: How Q&A insights shaped this concept (2-3 sentences in Korean).
    - Q&A Keywords: 3-5 key terms from Q&A that support this concept direction.
    
    [Output Format - JSON]
    {{
      "options": [
        {{
          "concept_statement": "Concept Sentence in Korean",
          "concept_rationale": "Reasoning in Korean...",
          "brand_values": ["가치1", "가치2", "가치3"],
          "qa_analysis_summary": "Q&A 분석 요약 (2-3문장)...",
          "qa_keywords": ["키워드1", "키워드2", "키워드3"]
        }},
        ... (3 options total)
      ]
    }}
    """

    # Step 4: Story
    STORY_SYSTEM = (
        "You are a Professional Brand Storyteller. "
        "Write a captivating brand introduction story that resonates with the target audience."
    )
    
    STORY_USER = """
    [Brand Context]
    - Brand Name: {brand_name}
    - Concept: {concept_statement}
    - Target Persona: {target_persona}
    
    [User Q&A Data - JSON Format]
    {qa_data_json}
    
    {feedback_section}
    
    [Task]
    1. First, analyze the Q&A data to identify storytelling themes and emotional tones.
    2. Write 3 different brand story variations.
    
    For each story, provide:
    - Brand Story: The narrative (3-5 sentences in Korean). **IMPORTANT: Keep the brand name '{brand_name}' in ENGLISH, do not translate it to Korean.**
    - Rationale: Why this storytelling approach works (in Korean).
    - Emotional Arc: The emotional journey of the story (e.g., "고민 → 발견 → 변화" in Korean).
    - Q&A Analysis Summary: How Q&A insights influenced the story direction (2-3 sentences in Korean).
    - Q&A Keywords: 3-5 key terms from Q&A that support this narrative.
    
    [Output Format - JSON]
    {{
      "options": [
        {{
          "brand_story": "Story in Korean...",
          "story_rationale": "Reasoning in Korean...",
          "emotional_arc": "감정 흐름 (예: 번아웃 → 자연과의 만남 → 회복)",
          "qa_analysis_summary": "Q&A 분석 요약 (2-3문장)...",
          "qa_keywords": ["키워드1", "키워드2", "키워드3"]
        }},
        ... (3 options total)
      ]
    }}
    """

    # Step 5: Logo
    LOGO_SYSTEM = (
        "You are a Modern Brand Identity Specialist. "
        "Your philosophy is 'Less is More'. "
        "You prioritize LOGOTYPE (Wordmark) over symbols, following the trend of Fortune 100 companies (e.g., Samsung, Sony, Braun, FedEx). "
        "The Brand Name is the artwork. Providing a clean, timeless look is your ultimate goal."
    )
    
    LOGO_USER = """
    [Brand Context]
    - Brand Name: {brand_name}
    - Concept: {concept_statement}
    - Story Essence: {brand_story}
    - Core Keywords: {core_keywords}
    
    [User Q&A Data - JSON Format]
    {qa_data_json}
    
    {feedback_section}
    
    [Task]
    Create 3 DISTINCT **Wordmark-Centric** logo concepts for '{brand_name}'.
    
    **CRITICAL: Use user-selected values from Q&A**
    - Extract **s5_brand_color** answer (e.g., "Black/White/Gray", "Blue/Navy")
    - Extract **s5_design_style** answer for style_keywords
    - Extract **s5_typography_style** answer if available
    - Background is ALWAYS white
    
    **Color Strategy for 3 Options**:
    - **Option 1 (Horizontal)**: Text in BLACK FIXED. Symbol uses user's preferred color family.
    - **Option 2 (Integrated)**: AI recommends harmonious colors based on user's color preferences.
    - **Option 3 (Stacked)**: AI recommends different color tones for variety.
    
    **IMPORTANT: Do NOT specify exact hex codes. Let the image AI choose specific shades.**
    Instead of "#0066CC", say "electric blue" or "bright blue tone".
    Instead of "#000000", say "black" or "dark tone".
    
    IMPORTANT: You MUST generate 3 different LAYOUT styles as follows:
    1. **Option 1: Horizontal Layout** (Symbol on Left + Text on Right). Standard Corporate Style. TEXT ALWAYS BLACK.
    2. **Option 2: Integrated Layout** (Text IS the Symbol). Modifying a letter slightly. GPT suggests color family.
    3. **Option 3: Stacked Layout** (Small Symbol on Top + Text Below). GPT suggests different color tones.
    
    Output Format - JSON:
    1. **layout_type**: One of ["Horizontal", "Integrated", "Stacked"].
    2. **style_keywords**: Extract from s5_design_style (e.g., ["Geometric", "Tech"])
    3. **color_description**: DESCRIPTIVE color guidance (NOT hex codes), e.g., "black text with electric blue symbol", "dark gray with bright blue accent"
    4. **benchmark_brand**: (e.g., "Braun", "Tesla", "Uber", "Sony")
    5. **logo_concept**: (Korean) The concept summary.
    6. **logo_rationale**: (Korean) Detailed reasoning.
    7. **qa_analysis_summary**: (Korean) 2-3 sentences.
    8. **qa_keywords**: (Korean) 3-5 key terms.
    9. **visual_instruction**: (English) Strict instruction using COLOR NAMES, not hex codes.
       - **Horizontal**: "A tiny solid icon on the LEFT in [COLOR NAME]. Large text '{brand_name}' on the RIGHT in BLACK."
       - **Integrated**: "The text '{brand_name}' in [COLOR NAME]. The letter has a geometric modification in [ACCENT COLOR]."
       - **Stacked**: "A tiny geometric shape ABOVE in [COLOR NAME]. The text '{brand_name}' BELOW in [COLOR NAME]."
    
    [Output Format - JSON]
    {{
      "options": [
        {{
          "layout_type": "Horizontal",
          "style_keywords": ["Geometric", "Tech"],
          "color_description": "Black text with electric blue geometric symbol",
          "benchmark_brand": "Tesla",
          "logo_concept": "블랙 텍스트와 블루 심볼로 안정성과 혁신을 동시에 표현...",
          "logo_rationale": "텍스트를 블랙으로 고정하여 가독성 최대화, 심볼은 사용자가 선호하는 블루 계열로...",
          "qa_analysis_summary": "사용자는 블랙/블루를 선호하며, 첫 번째 옵션은 안정적인 블랙 텍스트로 구성...",
          "qa_keywords": ["안정성", "가독성", "기하학"],
          "visual_instruction": "A horizontal logo layout. On the far LEFT, a small geometric icon in electric blue. On the RIGHT, the brand name '{brand_name}' in bold sans-serif font in BLACK. Vertically centered alignment. White background."
        }},
        {{
          "layout_type": "Integrated",
          "style_keywords": ["Geometric", "Tech"],
          "color_description": "Dark gray base with bright blue geometric accent",
          "logo_concept": "다크 그레이 베이스에 밝은 블루 강조로 현대적 느낌 강화...",
          "logo_rationale": "블랙 대신 다크 그레이를 사용하여 부드러운 인상을 주되, 밝은 블루로 포인트...",
          "qa_analysis_summary": "사용자의 블루 선호를 반영하되, 텍스트는 그레이 톤으로 변화를 줌...",
          "qa_keywords": ["현대적", "부드러움", "강조"],
          "visual_instruction": "A typographic logo where the text is the main element. The brand name '{brand_name}' in dark gray bold geometric font. One letter has a geometric modification in bright blue. White background."
        }},
        {{
          "layout_type": "Stacked",
          "style_keywords": ["Geometric", "Tech"],
          "color_description": "Navy text with sky blue geometric symbol",
          "logo_concept": "네이비 텍스트와 하늘색 심볼로 신뢰감과 개방성 동시 표현...",
          "logo_rationale": "블루 계열 내에서 톤 변화를 주어 3가지 옵션에 다양성 부여...",
          "qa_analysis_summary": "사용자의 블루 선호를 유지하되, 네이비와 스카이 블루로 변화를 줌...",
          "qa_keywords": ["신뢰", "개방성", "다양성"],
          "visual_instruction": "A vertical stacked logo. A tiny geometric icon in sky blue centered at the TOP. The brand name '{brand_name}' in navy centered BELOW the icon in bold geometric sans-serif. Balanced spacing. White background."
        }}
      ]
    }}
    
    IMPORTANT:
    - **TEXT IS KING**: The symbol size must be < 20% of the text.
    - **Use COLOR NAMES, not hex codes**: Let the image generation AI choose the exact shades.
    - **CLEAN**: No complex illustrations, no 3D effects, no shadows.
    - **READABLE**: The brand name must be clearly legible.
    - **DRY LANGUAGE**: In 'visual_instruction', do NOT use adjectives like "Beautiful", "Stunning", "Luxury", "Creative". Use only physical descriptions (e.g., "Solid", "Geometric", "Black", "Bold").
    - Each option must feel structurally different, not just color variations.
    """

