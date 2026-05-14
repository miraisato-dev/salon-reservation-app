# run.py
from app import create_app

# ================= 
# インスタンス生成
# ＝＝＝＝＝＝＝＝＝＝＝＝＝＝
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)