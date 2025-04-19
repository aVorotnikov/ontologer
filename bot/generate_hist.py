#!/usr/bin/python3

from db_connector import DbConnector
from bot_types import AssessmentType, assessment_type_to_string

import matplotlib.pyplot as plt
import numpy as np

import os


DIAGRAMS_DIRECTORY = "_runtime_diagrams"
if not os.path.exists(DIAGRAMS_DIRECTORY):
    os.makedirs(DIAGRAMS_DIRECTORY)


def create_stat_hist(db: DbConnector, id):
    stat = db.get_stat_domains(id)
    if len(stat) == 0:
        return None

    labels = []
    val1 = []
    val2 = []
    val3 = []
    val4 = []
    for column in stat:
        labels.append(f"{column[0]}\n({assessment_type_to_string(AssessmentType(column[1]))})")
        val1.append(column[2])
        val2.append(column[3])
        val3.append(column[4])
        val4.append(column[5])

    fig, ax = plt.subplots()
    fig.set_size_inches(18.5, 10.5)
    width = 0.2
    x = np.arange(len(labels))
    ax.bar(x - 3 * width / 2, val1, width, label='Зачтены', color='g')
    ax.bar(x - 1 * width / 2, val2, width, label='Зачтены, оспорены', color='y')
    ax.bar(x + 1 * width / 2, val3, width, label='Незачтены', color='r')
    ax.bar(x + 3 * width / 2, val4, width, label='Незачтены, оспорены', color='b')
    ax.grid(axis='y')
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=19)
    ax.legend()

    file_name = f"{DIAGRAMS_DIRECTORY}/{id}_hist.png"
    fig.savefig(file_name, dpi=100)
    return file_name


if __name__ == "__main__":
    db = DbConnector("ontologer", "postgres", "aaaaaa", "localhost", 5432)
    print(create_stat_hist(db, 1))
