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
        "Analyze the user's business Q&A from three strategic perspectives: "
        "Business, User Experience, and Market. "
        "Provide a comprehensive diagnosis and extract core insights."
    )
    
    DIAGNOSIS_USER = """
    [User Q&A Answers - Diagnosis]
    {qa_data}
    
    [Task]
    Analyze the business context based on the Q&A and provide:
    
    1. Multi-Perspective Analysis:
       - Business Perspective: Revenue model, scalability, strengths.
       - User Perspective: Target audience needs, pain points, benefits.
       - Market Perspective: Market trends, competition, uniqueness.
       
    2. Comprehensive Analysis:
       - Diagnosis Summary: An overall summary of the brand's current status (2-3 sentences).
       - Core Keywords: 3 keywords that best represent the brand.
       - Target Persona: A descriptive name for the core target audience (e.g., "Eco-conscious Millennials").
    
    [Output Format - JSON]
    {{
      "summary": "Overall diagnosis summary in Korean...",
      "keywords": ["Keyword1", "Keyword2", "Keyword3"],
      "persona": "Target Persona Name",
      "perspectives": {{
        "business_perspective": "Analysis in Korean...",
        "user_perspective": "Analysis in Korean...",
        "market_perspective": "Analysis in Korean..."
      }}
    }}
    
    IMPORTANT: All values in the JSON output must be in KOREAN.
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
    
    [User Q&A Answers - Naming]
    {qa_data}
    
    {feedback_section}
    
    [Task]
    Generate 3 DISTINCT brand name candidates.
    For each candidate, provide:
    1. Brand Name: The proposed name (Korean or English as appropriate).
    2. Rationale: Why this name fits the brand strategy (in Korean).
    
    [Output Format - JSON]
    {{
      "options": [
        {{
          "brand_name": "Name1",
          "name_rationale": "Reasoning in Korean..."
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
    
    [User Q&A Answers - Concept]
    {qa_data}
    
    {feedback_section}
    
    [Task]
    Develop 3 unique concept directions for the brand '{brand_name}'.
    For each direction, provide:
    1. Concept Statement: A catchy slogan or concept sentence.
    2. Rationale: The strategic reasoning behind this concept.
    
    [Output Format - JSON]
    {{
      "options": [
        {{
          "concept_statement": "Concept Sentence in Korean",
          "concept_rationale": "Reasoning in Korean..."
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
    
    [User Q&A Answers - Story]
    {qa_data}
    
    {feedback_section}
    
    [Task]
    Write 3 different versions of the Brand Introduction Story (About Us).
    Each version should have a different tone or focus (e.g., emotional, functional, visionary).
    
    For each version, provide:
    1. Brand Story: The actual introduction text (3-5 sentences).
    2. Rationale: The intent and focus of this story version.
    
    [Output Format - JSON]
    {{
      "options": [
        {{
          "brand_story": "Story text in Korean...",
          "story_rationale": "Intent of this story in Korean..."
        }},
        ... (3 options total)
      ]
    }}
    """

    # Step 5: Logo
    LOGO_SYSTEM = (
        "You are a Visual Identity Director. "
        "Design 3 distinct visual concepts. "
        "For each, write a detailed DALL-E 3 prompt and explaining the concept in Korean."
    )
    
    LOGO_USER = """
    [Brand Context]
    - Brand Name: {brand_name}
    - Concept: {concept_statement}
    - Story Snippet: {brand_story}
    - Keywords: {core_keywords}
    
    [User Q&A Answers - Logo]
    {qa_data}
    
    {feedback_section}
    
    [Task]
    Propose 3 distinct visual logo concepts. 
    (The generated DALL-E prompts will be executed immediately to create images.)
    
    For each concept, provide:
    1. DALL-E Prompt: A highly detailed prompt to generate this logo (in English).
    2. Logo Concept: A description of the visual style and elements (in Korean), written as if explaining the generated image.
    3. Rationale: Why this visual style fits the brand (in Korean).
    4. Color Palette: Recommended colors (Hex codes or names).
    
    [Output Format - JSON]
    {{
      "options": [
        {{
          "dalle_prompt": "High quality logo design prompt in English...",
          "logo_concept": "Visual description in Korean...",
          "logo_rationale": "Design intent in Korean...",
          "color_palette": ["#Hex1", "#Hex2", ...]
        }},
        ... (3 options total)
      ]
    }}
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
