# pip install PyPDF2
# pip install pdfplumber

import pdfplumber
import pandas as pd
import csv
import re

# 참고용 성적표 PDF 파일 경로 설정
pdf_path = 'ex_transcript.pdf'

# 페이지를 세로로 나누는 구분선을 정의하는 함수
def get_column_texts(page, num_columns):
    width = page.width
    height = page.height
    column_width = width / num_columns

    columns_texts = []
    for col in range(num_columns):
        # 각 열의 좌표 영역 설정
        left = col * column_width
        right = (col + 1) * column_width
        top = 0
        bottom = height

        # 해당 영역의 텍스트 추출
        crop_box = (left, top, right, bottom)
        cropped_page = page.within_bbox(crop_box)
        column_text = cropped_page.extract_text()
        columns_texts.append(column_text.strip() if column_text else '')

    return columns_texts

# PDF 파일 열기 및 텍스트 추출
all_columns_texts = []
with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:
        num_columns = 2  # 페이지를 세로로 2등분 (pdf에 따라 조정 가능)
        columns_texts = get_column_texts(page, num_columns)
        all_columns_texts.append(columns_texts)

# 텍스트를 필요한 형태로 가공 (위치에 따른 재배치)
ordered_texts = []
num_rows = len(all_columns_texts[0])  # 첫 페이지의 열 수 기준으로 행 수 결정

for row in range(num_rows):
    for page_columns in all_columns_texts:
        if row < len(page_columns):
            ordered_texts.append(page_columns[row])

# 학기 정보 및 과목 정보 추출을 위한 정규 표현식 패턴
semester_pattern = re.compile(r"\d학년 \d{4}학년도 [^ ]+기")
course_pattern = re.compile(r"([A-Z]{3}[0-9]{4})\s+(.+?)\s+([0-9]+\.[0-9])\s+([-A-Z][0-9]?\+?)\s+([가-힣]+)")

# 학기 및 과목 정보를 저장할 리스트
semesters = []
courses = []

# 정렬된 텍스트에서 학기 및 과목 정보 추출
current_semester = None
for text in ordered_texts:
    # 텍스트를 줄 단위로 분리
    lines = text.split('\n')
    for line in lines:
        sem_match = semester_pattern.search(line)
        if sem_match:
            current_semester = sem_match.group()
            semesters.append(current_semester)
        elif "금학기 수강내역" in line:
            current_semester = "금학기 수강내역"
        else:
            course_matches = course_pattern.findall(line)
            if course_matches:
                courses.append((current_semester, course_matches))

# # 추출된 정보를 구조화하여 출력
# for semester, course_list in courses:
#     print(f"--- {semester} ---")
#     for course in course_list:
#         print(course)
#     print("\n")

# 참고용 성적표 내용 저장할 CSV 파일 이름
csv_filename = 'transcript_contents.csv'

# CSV 파일 저장
with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
    csv_writer = csv.writer(csvfile)

    # CSV 헤더 작성
    csv_writer.writerow(['수강 시기', '과목 코드', '과목명', '학점', '성적', '과목 유형'])

    # 과목 정보를 CSV에 작성
    for semester, course_list in courses:
        for course in course_list:
            csv_writer.writerow([semester] + list(course))

print(f'{csv_filename} 파일이 성공적으로 저장되었습니다.')

# CSV 파일 불러오기
df = pd.read_csv('courses.csv')

# 데이터프레임 출력
display(df)
