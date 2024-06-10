from pathlib import Path

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template import Template

from apps.notifications.models import Notification
from apps.users.models import User


def send_notification(
    user: User,
    subject: str,
    plain_text: str,
    html_text: str,
    notification_type: Notification.NotificationType = None,
    notification_metadata: dict = None
) -> None:
    """Send a notification email to a specified user with both plain text and HTML content

    Args:
        user: The user object to whom the email will be sent
        subject: The subject line of the email
        plain_text: The plain text version of the email content
        html_text: The HTML version of the email content
        notification_type: Optionally categorize the notification type
        notification_metadata: Metadata to store alongside the notification
    """

    email = EmailMultiAlternatives(
        subject=subject,
        body=plain_text,
        from_email=settings.NOTIFY_FROM_EMAIL,
        to=[user.email]
    )

    email.attach_alternative(html_text, "text/html")
    email.send()

    Notification.objects.create(
        user=user,
        message=plain_text,
        notification_type=notification_type,
        metadata=notification_metadata
    )


def send_notification_template(
    user: User,
    subject: str,
    template: str,
    notification_type: Notification.NotificationType = None,
    notification_metadata: dict = None
) -> None:
    """Render an email template and send it to a specified user

    Args:
        user: The user object to whom the email will be sent
        subject: The subject line of the email
        template: The name of the template to render
        notification_type: Optionally categorize the notification type
        notification_metadata: Metadata to store alongside the notification
    """

    template_path = Path(template)
    text_template_name = str(template_path.with_suffix('.txt'))
    html_template_name = str(template_path.with_suffix('.html'))

    html_content = Template(html_template_name).render(notification_metadata)
    text_content = Template(text_template_name).render(notification_metadata)

    send_notification(
        user,
        subject,
        text_content,
        html_content,
        notification_type,
        notification_metadata
    )


def send_general_notification(user: User, subject: str, message: str) -> None:
    """Send a general notification email to a specified user

    Args:
        user: The user object to whom the email will be sent
        subject: The subject line of the email
        message: The message content to included
    """

    send_notification_template(
        user=user,
        subject=subject,
        template='general',
        notification_type=Notification.NotificationType.general_message,
        notification_metadata={'message': message}
    )
