# services/dashboard_service.py

# 予約の開始・終了時間からカレンダーUI表示用の座標（top・height）を計算する
def calc_position(res):
    base_hour = 9
    px_per_hour = 80

    # チェック
    if not res.start_time or not res.end_time:
        res.top = 0
        res.height = 0
        return

    # 計算処理
    start_min = (res.start_time.hour - base_hour) * 60 + res.start_time.minute

    duration = (
        (res.end_time.hour * 60 + res.end_time.minute) -
        (res.start_time.hour * 60 + res.start_time.minute)
    )

    res.top = start_min / 60 * px_per_hour
    res.height = duration / 60 * px_per_hour