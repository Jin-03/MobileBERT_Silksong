import pandas as pd
import re


def clean_steam_reviews(file_path, output_path):
    # 1. CSV 파일 로드
    df = pd.read_csv(file_path)
    initial_count = len(df)
    print(f"초기 수집된 데이터 개수: {initial_count}개")
    print("-" * 50)

    # 2. 결측치(NaN) 제거 및 문자열 강제 변환
    # 리뷰 본문이 비어있는 행을 제거합니다.
    df = df.dropna(subset=['review'])
    df['review'] = df['review'].astype(str).str.strip()

    # 3. 너무 짧은 리뷰 제거 (의미 없는 단답형 필터링)
    # 총 글자 수가 10자 이상, 500자 미만인 리뷰만 필터링(500자 이상은 따로 저장)
    # 예: "nice game", "trash", "good" 등 원인 분석에 도움 안 되는 데이터 탈락
    df = df[df['review'].apply(lambda x: len(x) >= 10 and len(x) < 500)]
    after_length_filter = len(df)
    print(f"[1차 필터링] 너무 짧은 단답형 리뷰 제거 완료: {initial_count - after_length_filter}개 삭제")

    # 4. 영어가 아니거나 이모지/특수문자 도배 스팸 리뷰 필터링
    def is_valid_english_review(text):
        # 알파벳, 숫자, 공백, 문장부호(.,!?'-")만 남기는 정규식
        english_only = re.sub(r'[^a-zA-Z0-9\s.,!?\'"-]', '', text)

        if len(text) == 0:
            return False

        # 전체 텍스트 중 순수 영어 관련 글자의 비율 계산
        # 이 비율이 70% 미만이면 러시아어, 중국어, 한국어가 섞였거나 이모지 도배 스팸일 확률이 높음
        english_ratio = len(english_only) / len(text)
        return english_ratio >= 0.7

    df = df[df['review'].apply(is_valid_english_review)]
    after_lang_filter = len(df)
    print(f"[2차 필터링] 비영어 및 특수문자 도배 리뷰 제거 완료: {after_length_filter - after_lang_filter}개 삭제")
    print("-" * 50)

    # 5. 최종 데이터 확인 및 저장
    print(f"최종 정제 완료된 데이터 개수: {after_lang_filter}개 (초기 데이터의 {after_lang_filter / initial_count * 100:.1f}% 보존)")

    # 인덱스를 깔끔하게 정리하고 저장
    df = df.reset_index(drop=True)
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"정제된 데이터가 '{output_path}' 파일로 성공적으로 저장되었습니다.")

    return df


def main():
    data_path = "silksong_reviews.csv"
    cleaned_data_path = "silksong_reviews_cleaned.csv"

    # 코드 실행
    cleaned_df = clean_steam_reviews(data_path, cleaned_data_path)
    cleaned_df.info()


if __name__ == "__main__":
    main()