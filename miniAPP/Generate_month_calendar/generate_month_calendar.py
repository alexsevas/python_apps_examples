# conda activate allpy311

import calendar
import matplotlib.pyplot as plt

def generate_month_calendar(year, month):
    cal = calendar.monthcalendar(year, month)
    days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_axis_off()
    table = ax.table(cellText=cal,
                     colLabels=days,
                     cellLoc='center',
                     loc='upper center')

    table.scale(1, 2)

    for i in range(len(cal)):
        for j in [5, 6]:  # Выделим сб/вс
            cell = table[i + 1, j]
            if cell.get_text().get_text().strip():
                cell.set_facecolor("#ffe0e0")

    plt.title(f"{calendar.month_name[month]} {year}", fontsize=20)
    plt.savefig(f"calendar_{month}_{year}.png", bbox_inches='tight')
    print(f"✅ Календарь сохранён: calendar_{month}_{year}.png")

# Пример использования
generate_month_calendar(2025, 8)
