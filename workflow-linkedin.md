name: "LinkedIn Content Creator with Voice & Research"
description: "Research-driven LinkedIn content creation using your personal voice and curated articles"

variables:
  profile:
    voice_file_path: "C:\\Users\\ic\\OneDrive\\Desktop\\Other Things\\Content - My Articles\\my_writing_voice_prompt.md"
    voice_style: null  # Will be loaded from file

steps:
  # Phase 1: Load Personal Voice Style
  - load_file:
      path: "{{profile.voice_file_path}}"
      store: profile.voice_style
      
  - if: not profile.voice_style
    then:
      - output: "⚠️ Could not load voice file. Please check the path: {{profile.voice_file_path}}"
      - exit

  # Phase 2: Topic and Keywords Collection
  - ask: "What topic would you like to write about?"
    store: content.topic
    
  - ask: "What are the key words/phrases to focus on? (separate with commas)"
    store: content.keywords
    
  - ask: "What's your target audience for this content?"
    store: content.audience

  # Phase 3: Comprehensive Article Search
  - output: "🔍 Searching for recent articles on '{{content.topic}}'..."
  
  - call_tool: web.search("{{content.topic}} {{content.keywords}} 2024 recent")
    store: search.results1
    
  - call_tool: web.search("{{content.topic}} latest news trends")
    store: search.results2
    
  - call_tool: web.search("{{content.keywords}} insights analysis 2024")
    store: search.results3
    
  - call_tool: web.search("{{content.topic}} best practices guide")
    store: search.results4
    
  - call_tool: web.search("{{content.topic}} case study examples")
    store: search.results5

  # Phase 4: Compile and Present Article Options
  - call_model:
      prompt: |
        From these search results, extract the 10 most relevant and recent articles:
        
        Search Results 1: {{search.results1}}
        Search Results 2: {{search.results2}}
        Search Results 3: {{search.results3}}
        Search Results 4: {{search.results4}}
        Search Results 5: {{search.results5}}
        
        Topic: {{content.topic}}
        Keywords: {{content.keywords}}
        
        For each article, provide:
        1. Title
        2. Source/Publication
        3. Date (if available)
        4. Brief summary (2-3 sentences)
        5. Key insights relevant to the topic
        6. URL
        
        Format as a numbered list, prioritizing the most recent and relevant articles.
        Only include articles that are directly related to the topic and keywords.
      store: articles.curated_list

  - output: |
      📚 **FOUND ARTICLES ON '{{content.topic.upper()}}'**
      
      {{articles.curated_list}}

  # Phase 5: Article Selection
  - ask: |
      Which articles would you like to use as reference? 
      (Enter numbers separated by commas, e.g., "1,3,5,7" or type "more" to search for different articles)
    store: articles.selection

  # Phase 6: Handle "More" Request
  - if: articles.selection == "more"
    then:
      - ask: "What specific angle or type of articles would you like me to search for?"
        store: search.refinement
      - call_tool: web.search("{{content.topic}} {{search.refinement}} {{content.keywords}}")
        store: search.additional
      - call_model:
          prompt: |
            From these additional search results, extract 10 more relevant articles:
            
            {{search.additional}}
            
            Topic: {{content.topic}}
            Refinement: {{search.refinement}}
            Keywords: {{content.keywords}}
            
            Same format as before - numbered list with title, source, date, summary, insights, and URL.
          store: articles.additional_list
      - output: |
          📚 **ADDITIONAL ARTICLES FOUND**
          
          {{articles.additional_list}}
      - ask: "Now which articles would you like to use? (Enter numbers from either list)"
        store: articles.final_selection
      - set: articles.selection = articles.final_selection

  # Phase 7: Extract Selected Articles Content
  - call_model:
      prompt: |
        Based on the selected articles ({{articles.selection}}), extract the key information:
        
        Original curated list: {{articles.curated_list}}
        {{#if articles.additional_list}}
        Additional articles: {{articles.additional_list}}
        {{/if}}
        
        Selected articles: {{articles.selection}}
        
        For each selected article, provide:
        1. Main points and insights
        2. Key statistics or data
        3. Quotes worth referencing
        4. Unique perspectives or angles
        5. Actionable takeaways
        
        Compile this into a comprehensive research summary.
      store: articles.research_summary

  # Phase 8: Content Angle and Structure
  - ask: |
      Based on your research, what angle would you like to take?
      
      Research Summary:
      {{articles.research_summary}}
    options: [personal_experience, industry_analysis, contrarian_view, practical_guide, trend_commentary, case_study_breakdown]
    store: content.angle

  - ask: "What's the main message or takeaway you want to convey?"
    store: content.main_message

  - ask: "Do you have any personal experiences or examples related to this topic?"
    store: content.personal_angle

  # Phase 9: Content Generation with Voice
  - call_model:
      prompt: |
        Create a LinkedIn post using the following:
        
        PERSONAL VOICE STYLE:
        {{profile.voice_style}}
        
        CONTENT SPECIFICATIONS:
        - Topic: {{content.topic}}
        - Keywords to include: {{content.keywords}}
        - Target audience: {{content.audience}}
        - Content angle: {{content.angle}}
        - Main message: {{content.main_message}}
        - Personal angle: {{content.personal_angle}}
        
        RESEARCH FOUNDATION:
        {{articles.research_summary}}
        
        REQUIREMENTS:
        - Write in the exact voice style provided above
        - Incorporate insights from the selected articles naturally
        - Include relevant statistics or data points from research
        - Start with a compelling hook
        - Use LinkedIn-optimized formatting
        - Include 3-5 relevant hashtags
        - Add a clear call-to-action that encourages engagement
        - Length: 200-350 words
        - Make it feel authentic and personal while being informative
        - Reference or build upon the research without directly copying
        
        The post should sound like it's written by someone with deep expertise who has done their homework.
      store: content.draft1

  # Phase 10: Review and Refinement
  - ask: |
      Here's your research-based LinkedIn post:
      
      {{content.draft1}}
      
      What would you like to do?
    options: [approve, edit_voice_alignment, add_more_research, change_angle, make_more_personal, adjust_length]
    store: content.action

  # Phase 11: Handle Different Actions
  - if: content.action == "edit_voice_alignment"
    then:
      - ask: "How should I adjust the voice? (e.g., 'more conversational', 'more authoritative', 'more personal')"
        store: content.voice_adjustment
      - call_model:
          prompt: |
            Adjust the voice of this LinkedIn post: {{content.voice_adjustment}}
            
            Original post: {{content.draft1}}
            
            Your voice style reference: {{profile.voice_style}}
            
            Keep all the research insights and structure, just adjust the tone and voice.
          store: content.draft2
      - set: content.final_draft = content.draft2

  - if: content.action == "add_more_research"
    then:
      - ask: "What additional research aspect would you like me to search for?"
        store: content.additional_research
      - call_tool: web.search("{{content.topic}} {{content.additional_research}} latest")
        store: search.additional_research
      - call_model:
          prompt: |
            Enhance this LinkedIn post with additional research:
            
            Additional research: {{search.additional_research}}
            Search query: {{content.additional_research}}
            
            Current post: {{content.draft1}}
            
            Voice style: {{profile.voice_style}}
            
            Integrate the new research naturally while maintaining the original structure and voice.
          store: content.draft2
      - set: content.final_draft = content.draft2

  - if: content.action == "change_angle"
    then:
      - ask: "What new angle would you like to take?"
        options: [more_controversial, more_practical, more_storytelling, more_data_driven, more_forward_looking]
        store: content.new_angle
      - call_model:
          prompt: |
            Rewrite this LinkedIn post with a {{content.new_angle}} angle:
            
            Original post: {{content.draft1}}
            Research: {{articles.research_summary}}
            Voice style: {{profile.voice_style}}
            
            Keep the core insights but change the approach and framing.
          store: content.draft2
      - set: content.final_draft = content.draft2

  - if: content.action == "make_more_personal"
    then:
      - ask: "What personal story, experience, or perspective would you like to add?"
        store: content.personal_story
      - call_model:
          prompt: |
            Add this personal element to the LinkedIn post: {{content.personal_story}}
            
            Current post: {{content.draft1}}
            Voice style: {{profile.voice_style}}
            
            Integrate the personal story naturally while maintaining the research foundation.
          store: content.draft2
      - set: content.final_draft = content.draft2

  - if: content.action == "adjust_length"
    then:
      - ask: "Make it:"
        options: [shorter_punchy, longer_detailed, medium_balanced]
        store: content.length_preference
      - call_model:
          prompt: |
            Adjust the length of this LinkedIn post to be {{content.length_preference}}:
            
            {{content.draft1}}
            
            Voice style: {{profile.voice_style}}
            
            Maintain all key insights and research while adjusting length.
          store: content.draft2
      - set: content.final_draft = content.draft2

  - if: content.action == "approve"
    then:
      - set: content.final_draft = content.draft1

  # Phase 12: Final Review (if changes were made)
  - if: content.action != "approve"
    then:
      - ask: |
          Here's your updated post:
          
          {{content.final_draft}}
          
          Final approval?
        options: [approve, make_final_tweaks]
        store: content.final_action
      - if: content.final_action == "make_final_tweaks"
        then:
          - ask: "What final tweaks would you like?"
            store: content.final_tweaks
          - call_model:
              prompt: |
                Make these final tweaks: {{content.final_tweaks}}
                
                Current post: {{content.final_draft}}
                Voice style: {{profile.voice_style}}
              store: content.final_draft

  # Phase 13: Analytics and Source Attribution
  - calculate:
      word_count: "{{len(content.final_draft.split())}}"
      character_count: "{{len(content.final_draft)}}"
      hashtag_count: "{{content.final_draft.count('#')}}"
      reading_time: "{{len(content.final_draft.split()) / 200}} minutes"
    store: content.analytics

  # Phase 14: Final Output with Source Attribution
  - output: |
      📋 **RESEARCH-BASED LINKEDIN POST READY**
      
      📝 **Post Content:**
      {{content.final_draft}}
      
      📊 **Post Analytics:**
      - Word count: {{content.analytics.word_count}}
      - Character count: {{content.analytics.character_count}}
      - Reading time: {{content.analytics.reading_time}}
      - Hashtag count: {{content.analytics.hashtag_count}}
      
      📚 **Research Foundation:**
      - Topic: {{content.topic}}
      - Keywords used: {{content.keywords}}
      - Selected articles: {{articles.selection}}
      - Content angle: {{content.angle}}
      
      🎯 **Posting Strategy:**
      - Best posting times: Tuesday-Thursday, 9-10 AM or 12-1 PM
      - Engage with comments immediately for algorithm boost
      - Consider mentioning sources in comments if relevant
      - Pin if performance is strong in first 24 hours
      
      💡 **Engagement Tactics:**
      - Ask follow-up questions in comments
      - Share contrarian viewpoints to spark discussion
      - Tag relevant industry leaders mentioned in research
      - Create polls based on the data you found
      
      📈 **Success Metrics:**
      - Track engagement rate (aim for 3-5% minimum)
      - Monitor profile visits and connection requests
      - Note which research insights resonate most
      - Save high-performing formats for future use

  # Phase 15: Save Session Data
  - save_to_history:
      timestamp: "{{now()}}"
      topic: "{{content.topic}}"
      keywords: "{{content.keywords}}"
      selected_articles: "{{articles.selection}}"
      research_summary: "{{articles.research_summary}}"
      content_angle: "{{content.angle}}"
      final_post: "{{content.final_draft}}"
      analytics: "{{content.analytics}}"
      voice_file_used: "{{profile.voice_file_path}}"
      performance_metrics: null  # Update manually later

# Configuration
config:
  max_search_results: 10
  research_timeout: 45
  model_temperature: 0.7
  auto_save: true
  voice_file_required: true