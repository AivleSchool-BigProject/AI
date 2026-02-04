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
        "You are a Senior Visual Identity Director with 15+ years of experience. "
        "You specialize in creating sophisticated, timeless logos for premium brands. "
        "Design 3 distinct, professional visual concepts with detailed DALL-E 3 prompts."
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
    Create 3 DISTINCT, PROFESSIONAL logo concepts for '{brand_name}'.
    Each DALL-E prompt will be executed immediately to generate actual images.
    
    CRITICAL QUALITY REQUIREMENTS:
    1. **Sophistication Level**: Comparable to Airbnb, Aesop, Patagonia, Apple
    2. **Design Principles**:
       - Ultra-minimalist, clean, timeless
       - Scalable from 16px (favicon) to billboard size
       - Works on both light and dark backgrounds
       - Flat design, no gradients or shadows
       - Vector-ready aesthetic
    
    3. **Structure Options**:
       - Wordmark only (typography-focused)
       - Symbol + Wordmark (combination mark)
       - Abstract symbol only (iconic)
    
    4. **Typography** (if applicable):
       - Modern sans-serif or elegant serif
       - Clean letterforms, balanced spacing
       - Avoid decorative or script fonts
    
    STRICT AVOIDANCES:
    - Cliché icons: suitcase, airplane, map pin, compass, globe
    - Overly decorative or busy elements
    - Generic stock imagery aesthetics
    - Childish or playful cartoon styles
    - Trendy effects that will age poorly
    - Multiple colors (prefer 1-2 colors max)
    
    For each concept, provide:
    1. **DALL-E Prompt** (English): 
       - Start with "A single clean logo design combining symbol and text for {brand_name}"
       - **CRITICAL RULES**:
         * Generate ONE complete logo: symbol/icon + brand name text
         * The logo should show the symbol and "{brand_name}" text together in a unified design
         * NO multiple variations in one image
         * NO mockups (no business cards, packaging, etc.)
         * NO size variations or color alternatives shown together
         * Just ONE clean, complete logo on white background
       - Include: 
         * Symbol/icon concept (abstract shape, geometric form)
         * Typography style for brand name
         * Color palette (1-2 colors max)
         * Layout (symbol above/beside text, integrated design, etc.)
       - Specify: "minimalist logo design, flat style, vector-ready, clean white background, centered composition"
       - Add: "Single professional logo presentation, similar to how Apple or Nike would present their logo"
       - Length: 120-180 words
    
    2. **Logo Concept** (Korean): Visual description as if explaining the generated image
    3. **Rationale** (Korean): Why this design fits the brand strategy
    4. **Color Palette**: Hex codes (1-2 colors max)
    5. **Q&A Analysis Summary**: How Q&A insights influenced the visual direction (2-3 sentences in Korean)
    6. **Q&A Keywords**: 3-5 key visual/style terms from Q&A
    
    [Output Format - JSON]
    {{
      "options": [
        {{
          "dalle_prompt": "A single clean logo design for {brand_name}. [Describe the symbol/icon and how it combines with the text]. The logo features [symbol description] with the text '{brand_name}' in [typography style]. Color palette: [color 1] and [color 2]. Minimalist design, flat style, clean white background, centered. ONE complete logo only. NO variations, NO mockups, NO multiple versions. Just one professional logo presentation.",
          "logo_concept": "Visual description in Korean...",
          "logo_rationale": "Design reasoning in Korean...",
          "color_palette": ["#Hex1", "#Hex2"],
          "qa_analysis_summary": "Q&A 분석 요약 (2-3문장)...",
          "qa_keywords": ["키워드1", "키워드2", "키워드3"]
        }},
        ... (3 options total, each DISTINCT in approach)
      ]
    }}
    
    IMPORTANT: 
    - Each of the 3 concepts must take a DIFFERENT visual approach (different symbols, layouts, typography).
    - Each DALL-E prompt MUST generate ONLY ONE complete logo (symbol + text), absolutely NO variations or mockups in the same image.
    - The logo should be a unified design with both symbol and brand name text.
    - You MUST provide ALL 6 fields for each option: dalle_prompt, logo_concept, logo_rationale, color_palette, qa_analysis_summary, qa_keywords.
    - Do NOT leave any field empty. If uncertain, provide a reasonable default value.
    """


class VerificationPrompts:
    """
    [Verification Prompts - Korean]
    결과물이 한국 정서와 사용자 의도에 부합하는지 검증합니다.
    """
    
    QUALITY_CHECK_SYSTEM = (
        "당신은 꼼꼼한 브랜드 컨설팅 품질 검수자입니다. "
        "생성된 결과물이 한국의 비즈니스 환경과 문화적 맥락에 자연스러운지, "
        "그리고 사용자의 요구사항을 충실히 반영했는지 평가합니다."
    )
    
    QUALITY_CHECK_USER = """
    [검증 대상 데이터]
    단계: {step_name}
    생성 결과: 
    {generated_result}
    
    [검증 기준]
    1. 한국어 표현이 자연스럽고 비즈니스 격식에 맞는가? (오역, 부자연스러운 문투 확인)
    2. 사용자의 핵심 요구사항이 누락되지 않았는가?
    3. 내용은 구체적이고 논리적인가? (모호한 표현 지양)
    
    [Task]
    위 기준에 따라 Pass(통과) 또는 Fail(반려)을 판정하고, 
    Fail인 경우 구체적인 이유와 개선 제안을 작성해주세요.
    
    Pass인 경우에도 개선할 점이 있다면 '조언'으로 남겨주세요.
    
    [출력 포맷 - JSON]
    {{
      "passed": true / false,
      "reason": "판정 이유 (Fail일 경우 필수)",
      "improvement_suggestion": "개선 제안 또는 조언",
      "score": 85 (0~100점 평가)
    }}
    """
