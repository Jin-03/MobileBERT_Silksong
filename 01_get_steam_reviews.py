import os
import requests
import pandas as pd
import time
import datetime


def unix_to_date(unix_time):
    date_time = datetime.datetime.fromtimestamp(int(unix_time))
    return date_time.strftime('%Y-%m-%d %H:%M:%S') # 한국시간 = utc +9 기준으로 변환


def main():
    app_id = "1030300"  # Hollow Knight: Silksong
    csv_file = "silksong_reviews_raw.csv"  # 데이터가 저장될 파일
    checkpoint_file = "steam_cursor_checkpoint.txt"  # 커서 위치를 기억할 파일

    # 1. 체크포인트 확인 및 커서 로드
    if os.path.exists(checkpoint_file) and os.path.exists(csv_file):
        with open(checkpoint_file, "r", encoding="utf-8") as f:
            cursor = f.read().strip()
        print(
            f"이전 작업 기록을 발견했습니다. 이어서 수집을 시작합니다. (시작 Cursor: {cursor})"
        )
    else:
        cursor = "*"
        print("기존 기록이 없습니다. 처음부터 데이터 수집을 시작합니다.")

    # API 요청 세팅
    params = {
        "json": 1,
        "language": "english",
        "filter": "recent",  # 중복 방지를 위한 최신순 정렬
        "num_per_page": 100,  # 한 번에 100개씩
        "cursor": cursor,
    }

    max_loops = 2000
    collected_in_this_run = 0

    for i in range(max_loops):  # 100 단위로 수집
        url = f"https://store.steampowered.com/appreviews/{app_id}"
        # 2. 네트워크 에러 및 서버 차단(429) 예외 처리
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 429:
                print(
                    "스팀 서버가 너무 빠른 요청으로 통제했습니다. 30초간 대기 후 다시 시도합니다..."
                )
                time.sleep(30)
                continue
            elif response.status_code != 200:
                print(
                    f"서버 에러 발생 (코드: {response.status_code}). 10초 후 재시도합니다..."
                )
                time.sleep(10)
                continue
            data = response.json()
        except Exception as e:
            print(
                f"인터넷 연결 오류 발생 ({e}). 10초 후 다시 시도합니다..."
            )
            time.sleep(10)
            continue

        # 리뷰 데이터 검증
        reviews = data.get("reviews", [])
        if not reviews:
            print(
                "더 이상 가져올 새로운 리뷰가 없습니다. 모든 수집을 종료합니다."
            )
            # 완료되었으므로 체크포인트 파일 삭제
            # if os.path.exists(checkpoint_file):
            #     os.remove(checkpoint_file)
            break

        # 3. 리뷰 데이터 수집
        current_batch = []
        for rev in reviews:
            current_batch.append({
                'review': rev['review'],  # 리뷰 본문 (텍스트)
                'voted_up': rev['voted_up'],  # 추천 여부 (True/False -> 우리의 정답 라벨!)
                'playtime_at_review': rev['author']['playtime_at_review'] // 60,  # 리뷰 작성 당시 플레이 시간(시간 단위)
                'playtime_forever': rev['author']['playtime_forever'] // 60,    # 작성자의 총 플레이 시간(리뷰 작성 이후 포함)
                'timestamp_created': unix_to_date(rev['timestamp_created']), # 리뷰 작성 시각
                'timestamp_updated': unix_to_date(rev['timestamp_updated']), # 리뷰 수정 시각
                'votes_up': rev['votes_up'], # 리뷰에 대한 유저 평가 helpful
                'weighted_vote_score': rev['weighted_vote_score'] # 리뷰에 대한 스팀 helpful 점수
            })

        # 4. 실시간으로 CSV 파일에 이어쓰기 (Append Mode)
        df_batch = pd.DataFrame(current_batch)
        file_exists = os.path.exists(csv_file)

        # mode='a'는 덮어쓰지 않고 기존 파일 아래에 데이터를 덧붙입니다.
        df_batch.to_csv(
            csv_file,
            mode="a",
            index=False,
            header=not file_exists,
            encoding="utf-8-sig",
        )

        collected_in_this_run += len(reviews)
        print(
            f"[{i + 1}/{max_loops}] {len(reviews)}개 수집 및 실시간 저장 완료 (이번 판 누적: {collected_in_this_run}개)"
        )
        time.sleep(1.0)  # 스팀 서버 차단 방지

        # 5. 다음 커서 위치를 파일에 실시간 기록
        next_cursor = data["cursor"]

        # 스팀 API 간헐적 버그(동일 커서 무한반복) 방지
        if next_cursor == params["cursor"]:
            print(
                "스팀 API가 동일한 위치를 반환했습니다. 무한 루프 방지를 위해 일시 정지합니다."
            )
            break

        params["cursor"] = next_cursor
        with open(checkpoint_file, "w", encoding="utf-8") as f:
            f.write(next_cursor)

    print(
        f"\n{collected_in_this_run}개 데이터 수집을 마쳤습니다. 더 수집하고 싶다면 코드를 다시 실행하면 됩니다!"
    )


if __name__ == "__main__":
    main()