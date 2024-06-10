from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from apps.notifications.models import Notification
from apps.users.models import User


def send_notification(
    user: User,
    subject: str,
    plain_text: str,
    html_text: str,
    notification_type: Notification.NotificationType = None,
    metadata: dict = None
) -> None:
    """Send a notification email to a specified user with both plain text and HTML content

    Args:
        user: The user object to whom the email will be sent
        subject: The subject line of the email
        plain_text: The plain text version of the email content
        html_text: The HTML version of the email content
        notification_type: Optionally categorize the notification type
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
        metadata=metadata
    )


def send_general_notification(user: User, subject: str, message: str) -> None:
    """Send a general notification email to a specified user

    Args:
        user: The user object to whom the email will be sent
        subject: The subject line of the email
        message: The message content to included
    """

    html_content = render_to_string(
        template_name='general.html',
        context={'user': user, 'subject': subject, 'message': message})

    send_notification(
        user,
        subject,
        message,
        html_content,
        Notification.NotificationType.general_message
    )


def send_usage_ntfication(user: User, subject: str, usage: int) -> None:
    """Send a usage notification email to a specified user

    Args:
        user: The user object to whom the email will be sent
        subject: The subject line of the email
        usage: The usage on a given cluster
    """

    html_content = render_to_string(
        template_name='usage.html',
        context={'user': user, 'subject': subject, 'usage': usage})

    send_notification(
        user,
        subject,
        message,
        html_content,
        Notification.NotificationType.general_message,
        {'usage': usage}
    )
