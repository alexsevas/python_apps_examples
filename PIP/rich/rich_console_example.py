# conda activate allpy311
# pip install rich

# Код красивого анимированного индикатора загрузки в консоли на Python.
# Для работы с прогресс-баром в коде используется библиотека rich.

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
import time


def cool_loading_animation(description: str = "Загрузка данных...", total_steps: int = 10, delay_per_step: float = 0.3):
    """
    Отображает анимацию загрузки с текстом.

    Args:
        description (str): Текст, отображаемый рядом со спиннером.
        total_steps (int): Общее количество шагов для симуляции загрузки.
        delay_per_step (float): Задержка в секундах для каждого шага.
    """
    console = Console()

    with Progress(
        SpinnerColumn(),
        TextColumn(f"[bold green]{{task.description}}"),
        console=console,
        transient=True,  # Прогресс-бар исчезнет после завершения
    ) as progress:
        task = progress.add_task(description, total=total_steps)
        for _ in range(total_steps):
            time.sleep(delay_per_step)  # Симуляция работы
            progress.advance(task)

    console.print(f"[bold green]✅ {description.replace('...', '')} Готово![/bold green]")


if __name__ == "__main__":
    # Пример использования:
    cool_loading_animation("Инициализация...", total_steps=5, delay_per_step=0.5)
    cool_loading_animation("Обработка файлов...", total_steps=12, delay_per_step=0.2)
    cool_loading_animation("Завершение...", total_steps=3, delay_per_step=0.7)
