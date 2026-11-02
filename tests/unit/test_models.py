from app.db.models import User


def test_user_model_has_no_admin_flag():
    assert "is_admin" not in User.__table__.columns
    assert "telegram_id" in User.__table__.columns
    assert "referral_code" in User.__table__.columns
