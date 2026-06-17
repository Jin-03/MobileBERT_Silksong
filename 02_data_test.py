import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def count_text(data_path, output_path):
    # 데이터 확인
    df = pd.read_csv(data_path, encoding = "utf-8")
    text = list(df["review"])
    text_len = []

    # 문장의 길이(문자수) 세기
    for i in range(len(text)):
        text_len.append(len(text[i]))

    df["text_len"] = text_len
    df.to_csv(data_path, index=False)

    text_len_count = []
    for i in range(1, max(text_len)+1):
        text_len_count.append({
            "index": i,
            "value": text_len.count(i)
        })

    pd.DataFrame(text_len_count).to_csv(output_path, index=False)


def main():
    raw_data_path = "silksong_reviews_raw.csv"
    data_path = "silksong_reviews.csv"
    text_len_path = "text_len_count.csv"

    # 결측치 제거
    raw_data = pd.read_csv(raw_data_path, encoding="utf-8")
    data = raw_data.dropna(subset=["review"])
    data.to_csv(data_path, index=False)

    # 제거된 데이터 수 확인
    data = pd.read_csv(data_path, encoding="utf-8")
    print("기존 데이터 수", len(raw_data))
    print("결측치 제거 이후 데이터 수", len(data))
    print("제거된 데이터 수", len(raw_data)-len(data))

    # 리뷰 글자수 카운트
    count_text(data_path, text_len_path)
    df = pd.read_csv(text_len_path)
    print(df[:10])
    df.info()


    # 10 글자 미만
    count = list(pd.read_csv(text_len_path)['value'])
    print(count[:10])
    under_10 = sum(count[:11])
    print("10글자 미만의 리뷰 데이터 수: ", under_10)

    # 학습용 중간값 데이터
    mid_490 = sum(count[11:500])
    print("학습용 10-500자 데이터 수: ", mid_490)

    # 500 글자 이상
    over_500 = sum(count[500:])
    print("500글자 이상의 리뷰 데이터 수: ", over_500)

    # 총 데이터 수
    len_count_sum = sum(count)
    val = under_10 + mid_490 + over_500
    print(val)
    print("전체 데이터 수: ", len_count_sum)


    fig, ax = plt.subplots(figsize=(5, 4))
    sns.barplot(x=['under_10', 'mid_490', 'over_500'], y=[under_10, mid_490, over_500], hue=['under_10', 'mid_490', 'over_500'], legend=False, palette="YlOrRd")
    for p in ax.patches:
        ax.text(p.get_x() + (p.get_width() / 2),  # 가로 위치
                p.get_y() + p.get_height(),  # 세로 위치
                f"{p.get_height()}",  # 값 + 표시방법 소수 둘째자리까지
                ha='center')  # 좌우정렬 중간으로

    plt.savefig("graph/text_len_count.png")
    plt.show()


if __name__ == "__main__":
    main()