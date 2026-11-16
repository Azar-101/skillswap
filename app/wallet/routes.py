from flask import render_template
from flask_login import login_required, current_user
from app.wallet import bp
from app.services.wallet_service import get_or_create_wallet
from app.models.wallet import WalletTransaction


@bp.route("/")
@login_required
def index():
    wallet = get_or_create_wallet(current_user.id)
    transactions = (
        WalletTransaction.query.filter_by(wallet_id=wallet.id)
        .order_by(WalletTransaction.created_at.desc())
        .all()
    )

    return render_template(
        "wallet/index.html",
        wallet=wallet,
        transactions=transactions,
    )
