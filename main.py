# streamlit_z_score_with_input.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

menu = st.sidebar.selectbox('Meun',('개인성적조회','학교평균 및 점수분포'))

def calculate_z_score(data, column_name, global_mean, global_std_dev):
    z_score_col_name = f'{column_name.replace(" ", "_")}_Z_Score'
    data[column_name] = pd.to_numeric(data[column_name], errors='coerce')  # 문자열을 숫자로 변환
    data[z_score_col_name] = (data[column_name] - global_mean) / global_std_dev
    return data


def calculate_rank(data, column_name):
    rank_col_name = f'{column_name.replace(" ", "_")}_Rank'
    data[rank_col_name] = data[column_name].rank(ascending=False, method="min").astype(int)
    return data


def calculate_modified_score(z_score, multiplier=20, addition=100):
    return z_score * multiplier + addition


def main():
    st.title("개인성적조회 시스템")

    # CSV 데이터를 데이터프레임으로 읽기
    data = pd.read_csv("202401test.csv")

    # 전체 데이터의 평균과 표준편차 계산
    global_mean_korean = data['국어 점수'].mean()
    global_std_dev_korean = data['국어 점수'].std()

    global_mean_math = data['수학 점수'].mean()
    global_std_dev_math = data['수학 점수'].std()

    # 전체 데이터에 대한 국어와 수학 등수 계산
    for subject, global_mean, global_std_dev in [('국어 점수', global_mean_korean, global_std_dev_korean),
                                                 ('수학 점수', global_mean_math, global_std_dev_math)]:
        data = calculate_z_score(data, subject, global_mean, global_std_dev)
        data = calculate_rank(data, subject)

    # 등수를 CSV 파일로 저장
    data.to_csv("ranked_data.csv", index=False)

    # 사용자로부터 이름 입력 받기
    student_name = st.text_input("제출했던 비밀번호를 입력하세요.")

    # 입력된 이름이 데이터에 있는 경우에만 계산 및 결과 출력
    if student_name in data['이름'].values:
        student_data = data[data['이름'] == student_name]

        # 새로운 열 추가: 20을 곱하고 100을 더한 값
        for subject in ['국어', '수학']:
            z_score_col = f'{subject}_점수_Z_Score'
            rank_col = f'{subject}_점수_Rank'
            modified_score_col = f'Modified_Z_Score_{subject}'

            student_data[modified_score_col] = calculate_modified_score(student_data[z_score_col])

        # 결과 출력
        st.write(f"{student_name}'s Scores:")
        st.write(student_data[['이름', '국어 점수', '국어_점수_Rank', 'Modified_Z_Score_국어', '수학 점수', '수학_점수_Rank',
                               'Modified_Z_Score_수학']])
        st.write("* Modified_Z_Score : 표준점수")
    elif student_name:
        st.warning(f"No data found for student with name: {student_name}")



if menu == '개인성적조회':
        main()


elif menu == '학교평균 및 점수분포':
    data = pd.read_csv("202401test.csv")
    # 학교별 국어와 수학의 평균 점수 계산
    school_avg_scores = data.groupby('학교')[['국어 점수', '수학 점수']].mean()

    # 테이블 형식으로 출력
    st.subheader("학교 평균")
    st.write(school_avg_scores)


    st.subheader("과목별 점수분포도(국어, 수학)")

    # 국어 점수와 수학 점수에 대한 히스토그램을 그리기
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 10))

    # 국어 점수 히스토그램
    ax1.hist(data['국어 점수'], bins=30, range=(25,60), color='skyblue', edgecolor='black')
    ax1.set_title('Korea Frequency histogram')
    ax1.set_xlabel('Score')
    ax1.set_ylabel('Number')

    # 수학 점수 히스토그램
    ax2.hist(data['수학 점수'], bins=30, range=(25,60), color='lightcoral', edgecolor='black')
    ax2.set_title('Math Frequency histogram ')
    ax2.set_xlabel('Score')
    ax2.set_ylabel('Number')

    # 그림을 Streamlit에 전달
    st.pyplot(fig)
