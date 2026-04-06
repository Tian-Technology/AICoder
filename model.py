ALL_MODELS = [
    ('deepseek-r1', 'DeepSeek-R1 (深度求索推理模型)'),
    ('deepseek-v3.2', 'DeepSeek-V3.2 (深度求索最新版本)'),
    ('deepseek-v3.1', 'DeepSeek-V3.1 (深度求索)'),
    ('deepseek-v3', 'DeepSeek-V3 (深度求索)'),
    ('deepseek-v2.5', 'DeepSeek-V2.5 (深度求索)'),
    ('deepseek-v2', 'DeepSeek-V2 (深度求索)'),
    ('deepseek-chat', 'DeepSeek-Chat (深度求索对话模型)'),
    ('deepseek-reasoner', 'DeepSeek-Reasoner (深度求索推理)'),
    ('deepseek-coder', 'DeepSeek-Coder (深度求索代码)'),
    ('deepseek-coder-3.0', 'DeepSeek-Coder 3.0 (深度求索代码)'),
    ('deepseek-coder-2.0', 'DeepSeek-Coder 2.0 (深度求索代码)'),
    ('deepseek-coder-1.0', 'DeepSeek-Coder 1.0 (深度求索代码)'),
    ('deepseek-llm-70b', 'DeepSeek-LLM 70B (深度求索)'),
    ('deepseek-llm-16b', 'DeepSeek-LLM 16B (深度求索)'),
    ('deepseek-llm-7b', 'DeepSeek-LLM 7B (深度求索)'),
    
    ('gpt-4o', 'GPT-4o (OpenAI 最新模型)'),
    ('gpt-4o-mini', 'GPT-4o-mini (OpenAI 经济版)'),
    ('gpt-4o-2024-08-06', 'GPT-4o 2024-08-06'),
    ('gpt-4o-2024-11-20', 'GPT-4o 2024-11-20 (最新版本)'),
    ('gpt-4', 'GPT-4 (OpenAI 高级模型)'),
    ('gpt-4-0314', 'GPT-4 2023-03-14'),
    ('gpt-4-0613', 'GPT-4 2023-06-13'),
    ('gpt-4-1106-preview', 'GPT-4 2023-11-06 Preview'),
    ('gpt-4-turbo', 'GPT-4 Turbo (OpenAI)'),
    ('gpt-4-turbo-preview', 'GPT-4 Turbo Preview'),
    ('gpt-3.5-turbo', 'GPT-3.5-turbo (OpenAI 快速模型)'),
    ('gpt-3.5-turbo-0613', 'GPT-3.5-turbo 2023-06-13'),
    ('gpt-3.5-turbo-1106', 'GPT-3.5-turbo 2023-11-06'),
    ('gpt-3.5-turbo-16k', 'GPT-3.5-turbo 16K'),
    ('o1', 'OpenAI o1'),
    ('o1-mini', 'OpenAI o1-mini'),
    ('o1-preview', 'OpenAI o1-preview'),
    ('o3-mini', 'OpenAI o3-mini'),
    
    ('claude-sonnet-4-5', 'Claude Sonnet 4.5 (Anthropic)'),
    ('claude-haiku-4-5', 'Claude Haiku 4.5 (Anthropic)'),
    ('claude-opus-4-5', 'Claude Opus 4.5 (Anthropic)'),
    ('claude-3-5-sonnet-20240620', 'Claude 3.5 Sonnet (Anthropic)'),
    ('claude-3-5-sonnet-20241022', 'Claude 3.5 Sonnet 20241022'),
    ('claude-3-5-sonnet-20241201', 'Claude 3.5 Sonnet 20241201'),
    ('claude-3-opus-20240229', 'Claude 3 Opus (Anthropic)'),
    ('claude-3-sonnet-20240229', 'Claude 3 Sonnet (Anthropic)'),
    ('claude-3-haiku-20240229', 'Claude 3 Haiku (Anthropic)'),
    ('claude-3-5-opus-20240620', 'Claude 3.5 Opus (Anthropic)'),
    ('claude-3-5-opus-20241022', 'Claude 3.5 Opus 20241022'),
    
    ('gemini-1.5-pro', 'Gemini 1.5 Pro (Google)'),
    ('gemini-1.5-pro-002', 'Gemini 1.5 Pro 002'),
    ('gemini-1.5-flash', 'Gemini 1.5 Flash (Google)'),
    ('gemini-1.5-flash-8b', 'Gemini 1.5 Flash-8B'),
    ('gemini-2.0-flash', 'Gemini 2.0 Flash (Google)'),
    ('gemini-2.0-flash-exp', 'Gemini 2.0 Flash 实验版'),
    ('gemini-2.5-pro-preview-03-25', 'Gemini 2.5 Pro Preview'),
    ('gemini-pro', 'Gemini Pro (Google)'),
    ('gemini-1.0-pro', 'Gemini 1.0 Pro (Google)'),
    ('gemini-1.0-ultra', 'Gemini 1.0 Ultra (Google)'),
    
    ('qwen-plus', 'Qwen-Plus (阿里通义千问)'),
    ('qwen-max', 'Qwen-Max (阿里通义千问)'),
    ('qwen-turbo', 'Qwen-Turbo (阿里通义千问)'),
    ('qwen-2.5-plus', 'Qwen 2.5 Plus (阿里通义千问)'),
    ('qwen-2.5-max', 'Qwen 2.5 Max (阿里通义千问)'),
    ('qwen-2.5-turbo', 'Qwen 2.5 Turbo (阿里通义千问)'),
    ('qwen-long', 'Qwen-Long (通义长文本)'),
    ('qwen2.5-72b-instruct', 'Qwen2.5 72B Instruct'),
    ('qwen2.5-32b-instruct', 'Qwen2.5 32B Instruct'),
    ('qwen2.5-14b-instruct', 'Qwen2.5 14B Instruct'),
    ('qwen2.5-coder-32b-instruct', 'Qwen2.5 Coder 32B'),
    ('qwen2.5-coder-7b-instruct', 'Qwen2.5 Coder 7B'),
    
    ('ernie-4.0', 'ERNIE 4.0 (百度文心一言)'),
    ('ernie-3.5', 'ERNIE 3.5 (百度文心一言)'),
    ('ernie-3.0', 'ERNIE 3.0 (百度文心一言)'),
    
    ('spark-v4.0', 'Spark V4.0 (讯飞星火)'),
    ('spark-v3.5', 'Spark V3.5 (讯飞星火)'),
    ('spark-v3.0', 'Spark V3.0 (讯飞星火)'),
    
    ('kwaipilot', 'Kwaipilot (快手)'),
    ('kimi', 'Kimi (月之暗面)'),
    ('kimi-k2.5', 'Kimi K2.5 (月之暗面)'),
    ('kimi-k2', 'Kimi K2 (月之暗面)'),
    ('kimi-k1', 'Kimi K1 (月之暗面)'),
    ('kimi-vision', 'Kimi Vision (月之暗面)'),
    ('kimi-code', 'Kimi Code (月之暗面)'),
    ('kimi-scientific', 'Kimi Scientific (月之暗面)'),
    ('moonshot-v1-8k', 'Moonshot v1 8k (月之暗面)'),
    ('moonshot-v1-32k', 'Moonshot v1 32k (月之暗面)'),
    ('moonshot-v1-128k', 'Moonshot v1 128k (月之暗面)'),
    
    ('glm-4', 'GLM-4 (智谱清言)'),
    ('glm-4-flash', 'GLM-4 Flash (智谱清言)'),
    ('glm-4.7-flash', 'GLM-4.7 Flash (智谱清言)'),
    ('glm-4.5-flash', 'GLM-4.5 Flash (智谱清言)'),
    ('glm-4-air', 'GLM-4 Air (智谱清言)'),
    ('glm-4-airx', 'GLM-4 Airx (智谱清言)'),
    ('glm-4-plus', 'GLM-4 Plus (智谱清言)'),
    ('glm-4v', 'GLM-4V 多模态 (智谱清言)'),
    ('glm-z1-flash', 'GLM-Z1 Flash 推理 (智谱)'),
    ('glm-z1-air', 'GLM-Z1 Air (智谱)'),
    ('glm-z1-flashx', 'GLM-Z1 FlashX (智谱)'),
    ('glm-z1-airx', 'GLM-Z1 AirX (智谱)'),
    ('glm-4-9b-chat', 'GLM-4-9B Chat (智谱)'),
    ('glm-4-32b', 'GLM-4-32B (智谱)'),
    ('glm-4-long', 'GLM-4 Long 长文本 (智谱)'),
    ('glm-4-flashx', 'GLM-4 FlashX (智谱)'),
    ('glm-4-air-250414', 'GLM-4 Air 250414 快照 (智谱)'),
    ('glm-4-flash-250414', 'GLM-4 Flash 250414 快照 (智谱)'),
    ('glm-4-flashx-250414', 'GLM-4 FlashX 250414 快照 (智谱)'),
    ('glm-4.6', 'GLM-4.6 (智谱)'),
    ('glm-4.6-flash', 'GLM-4.6 Flash (智谱)'),
    ('glm-4-coder', 'GLM-4 Coder 代码 (智谱)'),
    ('glm-4v-flash', 'GLM-4V Flash 多模态 (智谱)'),
    ('glm-4v-plus', 'GLM-4V Plus 多模态 (智谱)'),
    ('chatglm3-turbo', 'ChatGLM3 Turbo (智谱)'),
    ('chatglm3-6b', 'ChatGLM3-6B (智谱)'),
    ('glm-3-turbo', 'GLM-3 Turbo (智谱清言)'),
    ('glm-3', 'GLM-3 (智谱清言)'),
    
    ('llama-3.1-70b', 'Llama 3.1 70B (Meta)'),
    ('llama-3.1-8b', 'Llama 3.1 8B (Meta)'),
    ('llama-3.3-70b-versatile', 'Llama 3.3 70B Versatile'),
    ('llama-3.3-70b-instruct', 'Llama 3.3 70B Instruct'),
    ('llama-3.3-8b-versatile', 'Llama 3.3 8B Versatile'),
    ('llama-3.3-8b-instruct', 'Llama 3.3 8B Instruct'),
    ('llama-3.2-3b', 'Llama 3.2 3B'),
    ('llama-3.2-1b', 'Llama 3.2 1B'),
    ('llama-3-70b', 'Llama 3 70B (Meta)'),
    ('llama-3-8b', 'Llama 3 8B (Meta)'),
    ('llama-2-70b', 'Llama 2 70B (Meta)'),
    ('llama-2-13b', 'Llama 2 13B (Meta)'),
    ('llama-2-7b', 'Llama 2 7B (Meta)'),
    
    ('mistral-large', 'Mistral Large (Mistral AI)'),
    ('mistral-large-latest', 'Mistral Large Latest'),
    ('mistral-medium-latest', 'Mistral Medium Latest'),
    ('mistral-small-latest', 'Mistral Small Latest'),
    ('mixtral-8x7b', 'Mixtral 8x7B (Mistral AI)'),
    ('mixtral-8x22b', 'Mixtral 8x22B'),
    ('mistral-7b', 'Mistral 7B (Mistral AI)'),
    ('mistral-small', 'Mistral Small (Mistral AI)'),
    ('codestral-latest', 'Codestral Latest'),
    ('pixtral-12b-2409', 'Pixtral 12B'),
    
    ('cohere-command-r', 'Command R (Cohere)'),
    ('cohere-command-r-plus', 'Command R+ (Cohere)'),
    ('cohere-command', 'Command (Cohere)'),
    ('cohere-command-light', 'Command Light (Cohere)'),
    ('cohere-command-r-04-2024', 'Command R 04-2024 (Cohere)'),
    ('cohere-command-r-plus-04-2024', 'Command R+ 04-2024 (Cohere)'),
    
    ('pplx-70b-online', 'Perplexity 70B Online'),
    ('pplx-7b-online', 'Perplexity 7B Online'),
    ('pplx-34b-online', 'Perplexity 34B Online'),
    ('pplx-70b-chat', 'Perplexity 70B Chat'),
    ('pplx-7b-chat', 'Perplexity 7B Chat'),
    
    ('inflection-2', 'Inflection-2 (Inflection AI)'),
    ('inflection-2.5', 'Inflection-2.5 (Inflection AI)'),
    
    ('stablelm-3b-4e1t', 'StableLM 3B 4e1t (Stability AI)'),
    ('stablelm-7b-4e1t', 'StableLM 7B 4e1t (Stability AI)'),
    ('stablelm-15b-4e1t', 'StableLM 15B 4e1t (Stability AI)'),
    
    ('luminous-supreme', 'Luminous Supreme (Aleph Alpha)'),
    ('luminous-extended', 'Luminous Extended (Aleph Alpha)'),
    ('luminous-base', 'Luminous Base (Aleph Alpha)'),
    
    ('grok-1', 'Grok-1 (xAI)'),
    ('grok-1.5', 'Grok-1.5 (xAI)'),
    ('grok-2', 'Grok-2 (xAI)'),
    
    ('hunyuan-turbo', '腾讯混元 Turbo'),
    ('hunyuan-pro', '腾讯混元 Pro'),
    
    ('doubao-pro', '豆包 Pro (字节跳动)'),
    ('doubao-turbo', '豆包 Turbo (字节跳动)'),
    ('doubao-vision', '豆包 Vision (字节跳动)'),
    
    ('360-gpt', '360 智脑 (360)'),
    ('360-gpt-s', '360 智脑 S (360)'),
    
    ('pangu-2.0', '盘古 2.0 (华为)'),
    ('pangu-2.0-turbo', '盘古 2.0 Turbo (华为)'),
    
    ('falcon-180b', 'Falcon 180B (TII)'),
    ('falcon-40b', 'Falcon 40B (TII)'),
    ('bloom-176b', 'BLOOM 176B (BigScience)'),
    ('gpt-j-6b', 'GPT-J 6B (EleutherAI)'),
    ('gpt-neo-2.7b', 'GPT-Neo 2.7B (EleutherAI)')
]

MODEL_DISPLAY_MAP = {model_id: display_name for model_id, display_name in ALL_MODELS}

MODEL_MAX_TOKENS_MAP = {
    'gpt-4o': 128000,
    'gpt-4o-mini': 128000,
    'gpt-4o-2024-08-06': 128000,
    'gpt-4o-2024-11-20': 128000,
    'gpt-4': 8192,
    'gpt-4-0314': 8192,
    'gpt-4-0613': 8192,
    'gpt-4-1106-preview': 128000,
    'gpt-4-turbo': 128000,
    'gpt-4-turbo-preview': 128000,
    'gpt-3.5-turbo': 16384,
    'gpt-3.5-turbo-0613': 16384,
    'gpt-3.5-turbo-1106': 16384,
    'gpt-3.5-turbo-16k': 16384,
    'o1': 200000,
    'o1-mini': 128000,
    'o1-preview': 128000,
    'o3-mini': 200000,
    
    'deepseek-r1': 64000,
    'deepseek-v3.2': 64000,
    'deepseek-v3.1': 64000,
    'deepseek-v3': 64000,
    'deepseek-v2.5': 64000,
    'deepseek-v2': 64000,
    'deepseek-chat': 64000,
    'deepseek-reasoner': 64000,
    'deepseek-coder': 64000,
    'deepseek-coder-3.0': 64000,
    'deepseek-coder-2.0': 64000,
    'deepseek-coder-1.0': 64000,
    'deepseek-llm-70b': 64000,
    'deepseek-llm-16b': 64000,
    'deepseek-llm-7b': 64000,
    
    'claude-sonnet-4-5': 200000,
    'claude-haiku-4-5': 200000,
    'claude-opus-4-5': 200000,
    'claude-3-5-sonnet-20240620': 200000,
    'claude-3-5-sonnet-20241022': 200000,
    'claude-3-5-sonnet-20241201': 200000,
    'claude-3-opus-20240229': 200000,
    'claude-3-sonnet-20240229': 200000,
    'claude-3-haiku-20240229': 200000,
    'claude-3-5-opus-20240620': 200000,
    'claude-3-5-opus-20241022': 200000,
    
    'gemini-1.5-pro': 1048576,
    'gemini-1.5-pro-002': 1048576,
    'gemini-1.5-flash': 1048576,
    'gemini-1.5-flash-8b': 1048576,
    'gemini-2.0-flash': 1048576,
    'gemini-2.0-flash-exp': 1048576,
    'gemini-2.5-pro-preview-03-25': 1048576,
    'gemini-pro': 1048576,
    'gemini-1.0-pro': 32768,
    'gemini-1.0-ultra': 32768,
    
    'qwen-plus': 128000,
    'qwen-max': 128000,
    'qwen-turbo': 128000,
    'qwen-2.5-plus': 128000,
    'qwen-2.5-max': 128000,
    'qwen-2.5-turbo': 128000,
    'qwen-long': 10000000,
    'qwen2.5-72b-instruct': 128000,
    'qwen2.5-32b-instruct': 128000,
    'qwen2.5-14b-instruct': 128000,
    'qwen2.5-coder-32b-instruct': 128000,
    'qwen2.5-coder-7b-instruct': 128000,
    
    'ernie-4.0': 128000,
    'ernie-3.5': 128000,
    'ernie-3.0': 128000,
    
    'spark-v4.0': 128000,
    'spark-v3.5': 128000,
    'spark-v3.0': 128000,
    
    'kwaipilot': 128000,
    'kimi': 128000,
    'kimi-k2.5': 128000,
    'kimi-k2': 128000,
    'kimi-k1': 128000,
    'kimi-vision': 128000,
    'kimi-code': 128000,
    'kimi-scientific': 128000,
    'moonshot-v1-8k': 8192,
    'moonshot-v1-32k': 32768,
    'moonshot-v1-128k': 128000,
    
    'glm-4': 128000,
    'glm-4-flash': 128000,
    'glm-4.7-flash': 128000,
    'glm-4.5-flash': 128000,
    'glm-4-air': 128000,
    'glm-4-airx': 128000,
    'glm-4-plus': 128000,
    'glm-4v': 128000,
    'glm-z1-flash': 128000,
    'glm-z1-air': 128000,
    'glm-z1-flashx': 128000,
    'glm-z1-airx': 32768,
    'glm-4-9b-chat': 128000,
    'glm-4-32b': 128000,
    'glm-4-long': 1000000,
    'glm-4-flashx': 128000,
    'glm-4-air-250414': 128000,
    'glm-4-flash-250414': 128000,
    'glm-4-flashx-250414': 128000,
    'glm-4.6': 128000,
    'glm-4.6-flash': 128000,
    'glm-4-coder': 128000,
    'glm-4v-flash': 128000,
    'glm-4v-plus': 128000,
    'chatglm3-turbo': 128000,
    'chatglm3-6b': 8192,
    'glm-3-turbo': 128000,
    'glm-3': 128000,
    
    'llama-3.1-70b': 128000,
    'llama-3.1-8b': 128000,
    'llama-3.3-70b-versatile': 128000,
    'llama-3.3-70b-instruct': 128000,
    'llama-3.3-8b-versatile': 128000,
    'llama-3.3-8b-instruct': 128000,
    'llama-3.2-3b': 128000,
    'llama-3.2-1b': 128000,
    'llama-3-70b': 128000,
    'llama-3-8b': 128000,
    'llama-2-70b': 4096,
    'llama-2-13b': 4096,
    'llama-2-7b': 4096,
    
    'mistral-large': 128000,
    'mistral-large-latest': 128000,
    'mistral-medium-latest': 128000,
    'mistral-small-latest': 128000,
    'mixtral-8x7b': 128000,
    'mixtral-8x22b': 128000,
    'mistral-7b': 8192,
    'mistral-small': 8192,
    'codestral-latest': 256000,
    'pixtral-12b-2409': 128000,
    
    'cohere-command-r': 128000,
    'cohere-command-r-plus': 128000,
    'cohere-command': 2048,
    'cohere-command-light': 2048,
    
    'hunyuan-turbo': 256000,
    'hunyuan-pro': 256000,
    'hunyuan-standard': 256000,
    'doubao-pro-32k': 32768,
    'doubao-lite-32k': 32768,
    'doubao-pro-128k': 128000,
    
    'falcon-180b': 4096,
    'falcon-40b': 4096,
    'bloom-176b': 4096,
    'gpt-j-6b': 4096,
    'gpt-neo-2.7b': 4096
}

def get_model_display_name(model_id):
    return MODEL_DISPLAY_MAP.get(model_id, model_id)

def get_model_provider(model_id):
    if model_id.startswith('deepseek'):
        return 'deepseek'
    elif model_id.startswith('gpt'):
        return 'openai'
    elif model_id.startswith(('o1', 'o3')):
        return 'openai'
    elif model_id.startswith('claude'):
        return 'anthropic'
    elif model_id.startswith('gemini'):
        return 'google'
    elif model_id.startswith('qwen'):
        return 'aliyun'
    elif model_id.startswith('ernie'):
        return 'baidu'
    elif model_id.startswith('spark'):
        return 'xfyun'
    elif model_id.startswith('moonshot') or model_id.startswith('kimi') or model_id == 'kwaipilot':
        return 'moonshot'
    elif model_id.startswith('hunyuan'):
        return 'tencent'
    elif model_id.startswith('doubao'):
        return 'volcengine'
    elif model_id.startswith('glm') or model_id.startswith('chatglm'):
        return 'zhipu'
    elif model_id.startswith('llama'):
        return 'meta'
    elif model_id.startswith('mistral') or model_id.startswith('mixtral') or model_id.startswith('codestral') or model_id.startswith('pixtral'):
        return 'mistral'
    elif model_id.startswith('cohere'):
        return 'cohere'
    elif model_id.startswith('falcon'):
        return 'tii'
    elif model_id.startswith('bloom'):
        return 'bigscience'
    elif model_id.startswith('gpt-j') or model_id.startswith('gpt-neo'):
        return 'eleutherai'
    else:
        return 'unknown'

def get_model_max_tokens(model_id):
    return MODEL_MAX_TOKENS_MAP.get(model_id, 16384)

def get_default_base_url_for_model(model_id):
    mid = (model_id or "").strip().lower()
    if not mid:
        return ""
    if mid.startswith("deepseek"):
        return "https://api.deepseek.com/v1/chat/completions"
    if mid.startswith(("o1", "o3")):
        return "https://api.openai.com/v1/chat/completions"
    if mid.startswith("gpt-"):
        if mid.startswith(("gpt-j", "gpt-neo")):
            return ""
        return "https://api.openai.com/v1/chat/completions"
    if mid.startswith(("glm", "chatglm")):
        return "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    if mid.startswith("qwen"):
        return "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
    if mid.startswith(("moonshot", "kimi")):
        return "https://api.moonshot.cn/v1/chat/completions"
    if mid.startswith(("claude-opus", "claude-sonnet", "claude-")):
        return "https://api.anthropic.com/v1/messages"
    raise ValueError(f"Unknown model ID: {model_id}")
