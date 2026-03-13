def domain_instruction(domain):
    """Возвращает инструкцию для домена с валидацией"""
    domains = {
        "technical": "Используй технический стиль.",
        "legal": "Используй юридический анализ.",
        "scientific": "Используй научную структуру."
    }
    
    if domain not in domains:
        raise ValueError(f"Unknown domain: {domain}. Available: {', '.join(domains.keys())}")
    
    return domains[domain]


def build_prompt(mode, domain, text):
    """Строит промпт с валидацией параметров"""
    modes = {
        "bullet": "Сделай краткое резюме в bullet-пунктах.",
        "outline": "Сделай структурированный outline.",
        "executive": "Сделай executive summary."
    }
    
    if mode not in modes:
        raise ValueError(f"Unknown mode: {mode}. Available: {', '.join(modes.keys())}")
    
    if not text or not text.strip():
        raise ValueError("Text is empty")
    
    # Ограничиваем размер текста (максимум 100k символов)
    max_length = 100000
    if len(text) > max_length:
        text = text[:max_length] + "\n\n[Text truncated due to length limit]"
    
    mode_text = modes[mode]

    return f"""
{mode_text}

{domain_instruction(domain)}

Текст:

{text}
"""