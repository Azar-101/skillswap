from app.extensions import db
from app.models.notification import Notification


def create_notification(user_id: int, type: str, title: str, message: str, link: str = None) -> Notification:
    notification = Notification(
        user_id=user_id,
        type=type,
        title=title,
        message=message,
        link=link,
        is_read=False,
    )
    db.session.add(notification)
    db.session.commit()
    return notification


def mark_notification_read(notification_id: int, user_id: int) -> bool:
    notif = Notification.query.filter_by(id=notification_id, user_id=user_id).first()
    if notif:
        notif.is_read = True
        db.session.commit()
        return True
    return False


def mark_all_notifications_read(user_id: int):
    Notification.query.filter_by(user_id=user_id, is_read=False).update({"is_read": True})
    db.session.commit()


def get_unread_count(user_id: int) -> int:
    return Notification.query.filter_by(user_id=user_id, is_read=False).count()
