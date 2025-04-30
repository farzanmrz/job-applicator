# Streamlined AI Models for PLAN, ACT Copilot Tool

## Most Capable Models (Top Tier)

### gpt-4.1
- **API Name**: "gpt-4.1"
- **Description**: OpenAI's newest model optimized for coding and long-context tasks. Excels at software engineering, planning, and handling complex instructions.
- **Pricing (Input)**: $2/million tokens GPT-4.1 costs $2 per million input tokens
- **Pricing (Output)**: $8/million tokens $8 per million output tokens.
- **Context Window**: 1M tokens
- **Image Support**: Yes
- **Computer Use**: No
- **Prompt Caching**: No
- **Max Output Tokens**: 32,768 tokens
- **Notes**: 26% cheaper than previous flagship models with superior coding abilities

### claude-3-7-sonnet-20250219
- **API Name**: "claude-3-7-sonnet-20250219"
- **Description**: Most advanced Claude model with hybrid reasoning and native computer use capabilities for direct UI interaction.
- **Pricing (Input)**: $3/million tokens
- **Pricing (Output)**: $15/million tokens
- **Context Window**: 128K tokens standard
- **Image Support**: Yes
- **Computer Use**: Yes By integrating Claude via API, developers can direct Claude to use computers the way people do
- **Prompt Caching**: No
- **Max Output Tokens**: 64,000 tokens default
- **Notes**: Only major model with built-in computer interaction capability

### gemini-2.5-pro-preview-03-25
- **API Name**: "gemini-2.5-pro-preview-03-25"
- **Description**: Google's latest Pro model with thinking capabilities, strong reasoning and multimodal understanding.
- **Pricing (Input)**: $1.25/million tokens (up to 200K tokens), $2.50/million tokens (>200K tokens)
- **Pricing (Output)**: $10/million tokens (up to 200K tokens), $15/million tokens (>200K tokens)
- **Context Window**: 1M tokens
- **Image Support**: Yes
- **Computer Use**: No
- **Prompt Caching**: Yes
- **Max Output Tokens**: Not disclosed
- **Notes**: 2M token context window coming soon; excellent for complex reasoning tasks

## Cost-Effective Models (Mid Tier)

### gpt-4.1-mini
- **API Name**: "gpt-4.1-mini"
- **Description**: Mid-tier model that performs surprisingly well, sometimes matching or exceeding full GPT-4.1 on certain tasks.
- **Pricing (Input)**: $0.40/million tokens
- **Pricing (Output)**: $1.60/million tokens
- **Context Window**: 1M tokens
- **Image Support**: Yes
- **Computer Use**: No
- **Prompt Caching**: No
- **Max Output Tokens**: ~16K tokens
- **Notes**: Excellent performance/cost ratio One surprise: GPT-4.1 Mini performs almost as well as the full version on some of these benchmarks.

### gemini-2.5-flash-preview-04-17
- **API Name**: "gemini-2.5-flash-preview-04-17"
- **Description**: Latest Gemini Flash model with thinking capabilities balanced for speed and performance.
- **Pricing (Input)**: Not yet disclosed (recently released)
- **Pricing (Output)**: Not yet disclosed (recently released)
- **Context Window**: 1M tokens
- **Image Support**: Yes
- **Computer Use**: No
- **Prompt Caching**: Yes
- **Max Output Tokens**: Not disclosed
- **Notes**: Allows control over reasoning budget from 0-24576 tokens The budget can range from 0 to 24576 tokens for 2.5 Flash.

### o3-mini
- **API Name**: "o3-mini"
- **Description**: Efficient reasoning model with strong performance on planning and multi-step tasks.
- **Pricing (Input)**: $1.10/million tokens
- **Pricing (Output)**: $4.40/million tokens
- **Context Window**: 128K tokens
- **Image Support**: Yes
- **Computer Use**: No
- **Prompt Caching**: No
- **Max Output Tokens**: Not disclosed
- **Notes**: Good balance of reasoning capabilities and cost

## Budget-Friendly Models (Cost-Optimized)

### gpt-4.1-nano
- **API Name**: "gpt-4.1-nano"
- **Description**: Smallest, fastest model in the 4.1 family, designed for high-speed, cost-sensitive applications.
- **Pricing (Input)**: $0.10/million tokens GPT-4.1 nano is $0.10/million input tokens
- **Pricing (Output)**: $0.40/million tokens $0.40/million output tokens
- **Context Window**: 1M tokens
- **Image Support**: Yes
- **Computer Use**: No
- **Prompt Caching**: No
- **Max Output Tokens**: Not disclosed
- **Notes**: OpenAI's most affordable model, still with 1M token context window

### gemini-2.0-flash
- **API Name**: "gemini-2.0-flash"
- **Description**: Fast, efficient model with excellent price-performance ratio and multimodal capabilities.
- **Pricing (Input)**: $0.10/million tokens
- **Pricing (Output)**: $0.40/million tokens
- **Context Window**: 1M tokens
- **Image Support**: Yes
- **Computer Use**: No
- **Prompt Caching**: Yes
- **Max Output Tokens**: Not disclosed
- **Notes**: Extremely cost-effective for routine planning and analysis tasks The new simplified pricing for Gemini 2.0 Flash of $0.10 per 1 million input tokens makes huge context windows 33% more affordable

### deepseek-reasoner
- **API Name**: "deepseek-reasoner"
- **Description**: Reasoning-focused model with explicit chain-of-thought capabilities for structured problem-solving.
- **Pricing (Input)**: $0.55/million tokens
- **Pricing (Output)**: $2.19/million tokens
- **Context Window**: 64K tokens
- **Image Support**: Limited
- **Computer Use**: No
- **Prompt Caching**: Yes
- **Max Output Tokens**: 8,000 tokens
- **Notes**: Chain-of-Thought capability up to 32K tokens; excellent value for reasoning tasks

## Key Recommendations:

1. **For Computer Interaction**: Claude 3.7 Sonnet is the only model with native computer use capabilities.

2. **Best Value Overall**: GPT-4.1-mini offers exceptional performance at 20% the cost of GPT-4.1 Mini is 20% of the cost for most of the value.

3. **Most Budget-Friendly**: Both GPT-4.1-nano and Gemini 2.0 Flash are excellent choices at $0.10/million input tokens.

4. **Best for Complex Planning**: GPT-4.1 offers the best balance of planning capabilities, long context (1M tokens), and reasonable cost.