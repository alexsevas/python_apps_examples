# Merge files column
# - Читает несколько CSV файлов
# - Выбирает одну колонку (индекс) из каждой строки
# - Объединяет эти колонки в один выходной файл
# - Полезно при аналитике, когда нужно “собрать” один показатель из разных источников


import os
import csv
import argparse

def merge_columns(input_files, output_file, column_index):
    with open(output_file, 'w', newline='', encoding='utf-8') as out:
        writer = csv.writer(out)
        for infile in input_files:
            with open(infile, newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) > column_index:
                        writer.writerow([row[column_index]])
                    else:
                        writer.writerow([''])
    print("Merged into", output_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('inputs', nargs='+', help='Input CSV files')
    parser.add_argument('-o', '--output', required=True, help='Output file')
    parser.add_argument('-c', '--col', type=int, default=0, help='Column index to merge')
    args = parser.parse_args()
    merge_columns(args.inputs, args.output, args.col)
