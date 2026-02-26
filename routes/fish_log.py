import os
import base64
import json
import requests
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import current_user
from models import db

fish_log_bp = Blueprint("fish_log", __name__, url_prefix="/fish")


@fish_log_bp.route("/")
def index():
    from models import FishLog
    if current_user.is_authenticated:
        fishes = FishLog.query.filter_by(user_id=current_user.id).order_by(FishLog.caught_at.desc()).all()
        best = FishLog.query.filter_by(user_id=current_user.id).order_by(FishLog.size_cm.desc()).first()
    else:
        fishes = []
        best = None
    return render_template("fish_log.html", fishes=fishes, best=best)


@fish_log_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        fish_name = request.form.get("fish_name", "").strip()
        size_cm   = request.form.get("size_cm", "").strip()
        photo     = request.files.get("photo")

        if not fish_name or not size_cm:
            flash("魚の名前とサイズを入力してください", "error")
            return redirect(url_for("fish_log.register"))

        try:
            size_cm = float(size_cm)
        except ValueError:
            flash("サイズは数字で入力してください", "error")
            return redirect(url_for("fish_log.register"))

        photo_data = None
        if photo and photo.filename:
            photo_bytes = photo.read()
            mime = photo.mimetype or "image/jpeg"
            photo_data = f"data:{mime};base64," + base64.b64encode(photo_bytes).decode("utf-8")

        ai_result = analyze_with_ai(fish_name, size_cm)

        from models import FishLog, User

        user_id = current_user.id if current_user.is_authenticated else None

        entry = FishLog(
            user_id         = user_id,
            fish_name       = fish_name,
            size_cm         = size_cm,
            photo_data      = photo_data,
            scientific_name = ai_result.get("scientificName"),
            description     = ai_result.get("description"),
            danger_level    = ai_result.get("dangerLevel"),
            danger_reason   = ai_result.get("dangerReason"),
            rarity_level    = ai_result.get("rarityLevel"),
            rarity_reason   = ai_result.get("rarityReason"),
            habitat         = ai_result.get("habitat"),
        )

        db.session.add(entry)
        db.session.commit()


        # ===============================
        # 🔥 ここから追加（ポイント加算）
        # ===============================
        if current_user.is_authenticated:
            earned_points = int(size_cm)  # 1cm = 1ポイント
            current_user.total_points += earned_points
            flash(f"+{earned_points}ポイント獲得！", "success")

        flash(f"「{fish_name}」を図鑑に登録しました！", "success")
        return redirect(url_for("fish_log.detail", fish_id=entry.id))



        # ===============================
        # 🏆 バッジ判定
        # ===============================
        if current_user.is_authenticated:
            from routes.badge import check_and_award_badges
            check_and_award_badges(current_user)

        flash(f"「{fish_name}」を図鑑に登録しました！", "success")
        return redirect(url_for("fish_log.detail", fish_id=entry.id))

    return render_template("fish_register.html")


@fish_log_bp.route("/<int:fish_id>")
def detail(fish_id):
    from models import FishLog
    fish = FishLog.query.get_or_404(fish_id)
    return render_template("fish_detail.html", fish=fish)


@fish_log_bp.route("/delete/<int:fish_id>", methods=["POST"])
def delete(fish_id):
    from models import FishLog
    fish = FishLog.query.get_or_404(fish_id)
    db.session.delete(fish)
    db.session.commit()
    flash("記録を削除しました", "info")
    return redirect(url_for("fish_log.index"))


def analyze_with_ai(fish_name: str, size_cm: float) -> dict:
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        return _fallback_result()

    prompt = f"""あなたは魚の専門家です。「{fish_name}」（サイズ: {size_cm}cm）について以下を必ずJSON形式だけで返してください。説明文や前置きは不要です。

{{
  "scientificName": "学名（英語）",
  "description": "その魚の特徴を2〜3文で日本語で説明",
  "dangerLevel": 1から5の整数（1=安全、5=非常に危険）,
  "dangerReason": "危険度の理由を一文で",
  "rarityLevel": 1から5の整数（1=よく見る、5=非常にレア）,
  "rarityReason": "レア度の理由を一文で",
  "habitat": "生息地を一文で"
}}"""

    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except Exception as e:
        print(f"AI分析エラー: {e}")
        return _fallback_result()


def _fallback_result():
    return {
        "scientificName": "—",
        "description": "AI分析に失敗しました。後でもう一度お試しください。",
        "dangerLevel": 1,
        "dangerReason": "分析不可",
        "rarityLevel": 1,
        "rarityReason": "分析不可",
        "habitat": "—",
    }