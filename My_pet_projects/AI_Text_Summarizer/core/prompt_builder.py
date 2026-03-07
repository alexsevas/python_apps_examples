def domain_instruction(domain):

    return {
        "technical": "Используй технический стиль.",
        "legal": "Используй юридический анализ.",
        "scientific": "Используй научную структуру."
    }[domain]


def build_prompt(mode, domain, text):

    mode_text = {
        "bullet": "Сделай краткое резюме в bullet-пунктах.",
        "outline": "Сделай структурированный outline.",
        "executive": "Сделай executive summary."
    }[mode]

    return f"""
{mode_text}

{domain_instruction(domain)}

Текст:

{text}
"""