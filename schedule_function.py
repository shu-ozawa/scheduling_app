import pandas as pd
import numpy as np
from math import floor
from openpyxl import load_workbook
from openpyxl.styles import PatternFill
import openpyxl
from openpyxl.utils.dataframe import dataframe_to_rows
import os
import xlwings as xw

#関数を定義します

# Modified function to create subject table considering first choice, second choice, or undecided teacher
def create_subject_table(student_name, subject, choice, student_subjects_df, teacher_schedule_df, teacher_schedule_update, student_schedule_update):
    # Determine the teacher's name based on the choice
    teacher_name = None
    if choice == "first":
        teacher_name = student_subjects_df.loc[student_subjects_df['生徒の名前'] == student_name, f'{subject}の第1希望の先生'].values[0]
    elif choice == "second":
        teacher_name = student_subjects_df.loc[student_subjects_df['生徒の名前'] == student_name, f'{subject}の第2希望の先生'].values[0]
    elif choice == "undecided":
        teacher_name = "未定"  # Assuming the undecided teacher is represented by the column name "未定"
    else:
        raise ValueError("Invalid choice. Please use 'first', 'second', or 'undecided'.")

    # If teacher name is 0 (no preference) or NaN, return None
    if teacher_name == 0 or pd.isnull(teacher_name):
        return None

    # Create the subject table based on the teacher's schedule and student's schedule
    subject_table = pd.DataFrame({
        '日付': teacher_schedule_df['日付'],
        '時限': teacher_schedule_df['限数'],
        '先生のスケジュール': teacher_schedule_update[teacher_name].values,
        '生徒のスケジュール': student_schedule_update[student_name].values,
        'スケジュールの可否': [0] * len(teacher_schedule_df),
        '確定': [0] * len(teacher_schedule_df),
    })
    return subject_table


# 生徒の名前と科目を引数として受け取り、対応するコマ数を返す関数
def get_number_of_classes(student_name, subject, student_info_dict_with_priority):
    # 生徒の情報を辞書から取得
    student_info = student_info_dict_with_priority.get(student_name, {})
    # 指定された科目のコマ数を取得
    number_of_classes = student_info.get("科目", {}).get(subject, None)
    return number_of_classes


def check_first_choice_teacher(student_name, subject, student_subjects_df):
    # 第1希望の先生の名前を取得
    first_choice_teacher_name = student_subjects_df.loc[student_subjects_df['生徒の名前'] == student_name, f'{subject}の第1希望の先生'].values[0]
        
    # 第1希望の先生がいるかどうかを判断
    if first_choice_teacher_name == 0 or pd.isna(first_choice_teacher_name):
        return 0
    else:
        return 1


def check_second_choice_teacher(student_name, subject, student_subjects_df):
    # 第1希望の先生の名前を取得
    first_choice_teacher_name = student_subjects_df.loc[student_subjects_df['生徒の名前'] == student_name, f'{subject}の第2希望の先生'].values[0]
    
    # 第2希望の先生がいるかどうかを判断
    if first_choice_teacher_name == 0 or pd.isna(first_choice_teacher_name):
        return 0
    else:
        return 1

def calculate_schedule_possibility(student_name, subject_name, choice, schedule_table_by_date, num_classes, seat_schedule_update, student_subjects_df, teacher_schedule_df, teacher_schedule_update, student_schedule_update):
    subject_table = create_subject_table(student_name, subject_name, choice, student_subjects_df, teacher_schedule_df, teacher_schedule_update, student_schedule_update)
    teacher_schedule_column = subject_table['先生のスケジュール']
    student_schedule_column = subject_table['生徒のスケジュール']

    # 条件に基づいて「スケジュールの可否」カラムを更新
    # 一つの時限に入れる先生の数を考慮する
    for i, row in subject_table.iterrows():
        date = row['日付']
        period = row['時限']
        teacher_schedule = row['先生のスケジュール']
        student_schedule = row['生徒のスケジュール']
        teacher_count = seat_schedule_update[(seat_schedule_update['日付'] == date) & (seat_schedule_update['限数'] == period)]['先生数'].iloc[0]
        
        if teacher_schedule > 0 and student_schedule > 0 and teacher_count > 0:
            subject_table.at[i, 'スケジュールの可否'] = 1
        else:
            subject_table.at[i, 'スケジュールの可否'] = 0
    
    schedule_table_by_date["授業を入れた日付"] = subject_table["確定"]
    schedule_table_by_date["可能コマ数"] = subject_table["スケジュールの可否"]

    grouped_schedule_table = schedule_table_by_date.groupby('日付').sum().reset_index()
    grouped_schedule_table['授業可能日'] = np.where((grouped_schedule_table['可能コマ数'] > 0) & (grouped_schedule_table['授業を入れた日付'] == 0), 1, 0)

    sum_first_possible_day_updated = grouped_schedule_table['授業可能日'].sum()
    interval_classes = floor(sum_first_possible_day_updated / num_classes)
    
    return subject_table, interval_classes

def process_final_schedule(student_name, subject_name, choice, student_subjects_df, student_schedule_final, student_schedule_update, teacher_schedule_update, subject_table, interval_classes, num_classes, schedule_table_by_date, seat_schedule_update):

    # 確定カラムの更新
    last_confirmed_date = -1
    for i, row in subject_table.iterrows():
        if row['スケジュールの可否'] == 1 and row['日付'] >= last_confirmed_date:
            subject_table.loc[i, '確定'] = 1
            last_confirmed_date = row['日付'] + interval_classes
            num_classes -= 1
            if num_classes == 0:
                break


    schedule_table_by_date["授業を入れた日付"] = subject_table["確定"]

    schedule_table_by_date["可能コマ数"] = subject_table["スケジュールの可否"]
    # 日付ごとにグループ化して、各カラムの合計を計算
    grouped_schedule_table = schedule_table_by_date.groupby('日付').sum().reset_index()

    # 条件に基づいて「授業可能日」カラムを更新
    grouped_schedule_table['授業可能日'] = np.where((grouped_schedule_table['可能コマ数'] > 0) & (grouped_schedule_table['授業を入れた日付'] == 0), 1, 0)

    # 科目名と先生名の定義
    if choice == 'first':
        column_name = f'{subject_name}の第1希望の先生'
    elif choice == 'second':
        column_name = f'{subject_name}の第2希望の先生'
    else:
        column_name = None
        teacher_name = '未定'

    if column_name is not None:
        teacher_name = student_subjects_df.loc[student_subjects_df['生徒の名前'] == student_name, column_name].values[0]

    # 生徒スケジュール確定版の更新
    for index, row in subject_table.iterrows():
        if row['確定'] == 1:
            student_schedule_final.loc[index, student_name] = f'{subject_name}・{teacher_name}'
            # 生徒スケジュール更新用と先生スケジュール更新用から1を引く
            student_schedule_update.loc[index, student_name] -= 1
            teacher_schedule_update.loc[index, teacher_name] -= 1
            seat_schedule_update.loc[index, "先生数"] -= 1

    
    print(teacher_name, "と", student_name, "のスケジュールを実行")

    return student_schedule_final, student_schedule_update, teacher_schedule_update, num_classes, schedule_table_by_date, seat_schedule_update

# Function to transform the data for a given day, separating all "未定" teachers into different rows
def transform_day_data(day_data):
    # Creating a DataFrame for the transformed data
    transformed_data = pd.DataFrame(columns=['時限', '席番号', '先生名', '生徒a', '科目a', '生徒名b', '科目b'])
    seat_number = 1

    # Iterate through the day's data
    for index, row in day_data.iterrows():
        time_slot = row['限数']
        current_teacher = None

        for student_col, student_name in enumerate(row[2:].index):
            subject_teacher = row[2 + student_col]
            if subject_teacher != 0:
                subject, teacher = subject_teacher.split("・")

                # Separate all "未定" teachers into different rows
                if teacher == "未定":
                    transformed_data.loc[len(transformed_data)] = [time_slot, seat_number, teacher, student_name, subject, 0, 0]
                    seat_number += 1
                else:
                    if current_teacher == teacher:
                        transformed_data.loc[len(transformed_data) - 1, ['生徒名b', '科目b']] = [student_name, subject]
                    else:
                        transformed_data.loc[len(transformed_data)] = [time_slot, seat_number, teacher, student_name, subject, 0, 0]
                        seat_number += 1
                        current_teacher = teacher
        
        # Fill the remaining seats with 0
        while seat_number <= 10:
            transformed_data.loc[len(transformed_data)] = [time_slot, seat_number, 0, 0, 0, 0, 0]
            seat_number += 1
        
        seat_number = 1

    return transformed_data

def get_subject_and_teacher(schedule_df, student_name, date, period):
    # dateとperiodを使って、対象のセルを抽出
    subject_teacher = schedule_df[(schedule_df['日付'] == date) & (schedule_df['限数'] == period)][student_name].values[0]
    
    # セルが0ではない場合、科目と先生名を分割して返す
    if subject_teacher != 0:
        subject, teacher = subject_teacher.split('・')
        return subject, teacher
    else:
        return None, None

def update_student_info(schedule_df, student_name, date, period, student_info_dict):
    # dateとperiodを使って、対象のセルから科目と先生名を抽出
    subject, teacher = get_subject_and_teacher(schedule_df, student_name, date, period)

    # セルが0ではない場合、情報を更新
    if subject and teacher:
        # 科目の値を+1
        student_info_dict[student_name]['科目'][subject] += 1

        # 先生名を第一希望の先生として上書き
        student_info_dict[student_name]['希望先生'][subject][0] = teacher

def set_schedule_to_zero(schedule_df, student_name, date, period):
    schedule_df.loc[(schedule_df['日付'] == date) & (schedule_df['限数'] == period), student_name] = 0

