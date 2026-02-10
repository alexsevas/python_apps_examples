'''
Удобный скрипт, который помогает очистить CSV-файлы от почти-идентичных строк. Он находит строки, которые отличаются лишь
незначительно (например, из-за опечаток), и оставляет только уникальные — идеально для подготовки качественных данных перед анализом.
Модули: pandas, rapidfuzz
Python 3.8+
'''


import pandas as pd
from rapidfuzz import process, fuzz
import argparse

def dedupe_csv(input_file: str, output_file: str, col: str, threshold: float = 90.0):
    df = pd.read_csv(input_file)
    txts = df[col].astype(str).tolist()

    # Построение матрицы схожести
    sim_matrix = process.cdist(
        txts, txts,
        scorer=fuzz.token_set_ratio,
        score_cutoff=threshold
    )

    # Выявляем индексы уникальных строк
    unique_idxs = set()
    for i in range(len(txts)):
        # если нет других строк похожих на i (кроме самой i), считаем уникальной
        if not any(j != i and sim_matrix[i, j] >= threshold for j in range(len(txts))):
            unique_idxs.add(i)

    df_unique = df.iloc[sorted(unique_idxs)]
    df_unique.to_csv(output_file, index=False)
    print(f"Сохранено уникальных строк: {len(df_unique)} из {len(df)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Удаление почти дублирующихся строк в CSV по текстовой колонке."
    )
    parser.add_argument("input", help="путь к входному CSV")
    parser.add_argument("output", help="путь к выходному CSV без дубликатов")
    parser.add_argument("--column", "-c", required=True, help="имя текстовой колонки для сравнения")
    parser.add_argument("--threshold", "-t", type=float, default=90.0, help="порог сходства (0-100)")
    args = parser.parse_args()

    dedupe_csv(args.input, args.output, args.column, args.threshold)
