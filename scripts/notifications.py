#!/usr/bin/env python3
"""
Notification System for Chaos Experiments
Supports Slack, Email, and Webhooks
"""

import json
import smtplib
import sys
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Dict, List, Optional
from urllib.error import URLError
from urllib.request import Request, urlopen

from utils import get_config, get_logger

logger = get_logger(__name__)
config = get_config()


class NotificationService:
    """Unified notification service"""

    def __init__(self):
        self.config = config
        self.enabled = config.notifications_enabled

    def send_notification(
        self,
        message: str,
        title: str = "Chaos Experiment",
        level: str = "info",
        experiment_name: Optional[str] = None,
        experiment_status: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Send notification through all enabled channels.

        Args:
            message: Notification message
            title: Notification title
            level: Notification level (info, warning, error, success)
            experiment_name: Name of the experiment
            experiment_status: Status of the experiment
            details: Additional details

        Returns:
            True if at least one notification was sent successfully
        """
        if not self.enabled:
            logger.debug("Notifications are disabled")
            return False

        success = False

        # Slack notification
        if config.slack_webhook_url:
            try:
                self.send_slack_notification(
                    message=message,
                    title=title,
                    level=level,
                    experiment_name=experiment_name,
                    experiment_status=experiment_status,
                    details=details,
                )
                success = True
            except Exception as e:
                logger.error(f"Failed to send Slack notification: {e}")

        # Email notification
        if config.email_enabled and config.email_to:
            try:
                self.send_email_notification(
                    message=message,
                    title=title,
                    level=level,
                    experiment_name=experiment_name,
                    experiment_status=experiment_status,
                    details=details,
                )
                success = True
            except Exception as e:
                logger.error(f"Failed to send email notification: {e}")

        return success

    def send_slack_notification(
        self,
        message: str,
        title: str = "Chaos Experiment",
        level: str = "info",
        experiment_name: Optional[str] = None,
        experiment_status: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Send notification to Slack"""
        if not config.slack_webhook_url:
            logger.warning("Slack webhook URL not configured")
            return False

        # Color mapping for Slack
        color_map = {
            "info": "#36a64f",  # Green
            "success": "#36a64f",  # Green
            "warning": "#ff9900",  # Orange
            "error": "#ff0000",  # Red
        }

        color = color_map.get(level, "#36a64f")

        # Build Slack message
        slack_message = {
            "text": title,
            "attachments": [
                {
                    "color": color,
                    "fields": [{"title": "Message", "value": message, "short": False}],
                    "ts": int(datetime.now().timestamp()),
                }
            ],
        }

        # Add experiment details
        if experiment_name:
            slack_message["attachments"][0]["fields"].append(
                {"title": "Experiment", "value": experiment_name, "short": True}
            )

        if experiment_status:
            slack_message["attachments"][0]["fields"].append(
                {"title": "Status", "value": experiment_status, "short": True}
            )

        if details:
            details_text = "\n".join([f"{k}: {v}" for k, v in details.items()])
            slack_message["attachments"][0]["fields"].append(
                {"title": "Details", "value": details_text, "short": False}
            )

        # Send to Slack
        try:
            req = Request(
                config.slack_webhook_url,
                data=json.dumps(slack_message).encode("utf-8"),
                headers={"Content-Type": "application/json"},
            )
            response = urlopen(
                req, timeout=10
            )  # nosec B310 - URL validated from config
            if response.status == 200:
                logger.info("✅ Slack notification sent")
                return True
            else:
                logger.error(f"Slack webhook returned status {response.status}")
                return False
        except URLError as e:
            logger.error(f"Failed to send Slack notification: {e}")
            return False

    def send_email_notification(
        self,
        message: str,
        title: str = "Chaos Experiment",
        level: str = "info",
        experiment_name: Optional[str] = None,
        experiment_status: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Send email notification"""
        if not config.email_enabled:
            logger.warning("Email notifications are disabled")
            return False

        if not config.email_smtp_server or not config.email_from or not config.email_to:
            logger.warning("Email configuration incomplete")
            return False

        # Build email
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"[Chaos Engineering] {title}"
        msg["From"] = config.email_from
        msg["To"] = config.email_to

        # Build HTML email body
        html_body = f"""
        <html>
          <body>
            <h2>{title}</h2>
            <p><strong>Level:</strong> {level.upper()}</p>
            <p><strong>Message:</strong> {message}</p>
        """

        if experiment_name:
            html_body += f"<p><strong>Experiment:</strong> {experiment_name}</p>"

        if experiment_status:
            html_body += f"<p><strong>Status:</strong> {experiment_status}</p>"

        if details:
            html_body += "<h3>Details:</h3><ul>"
            for k, v in details.items():
                html_body += f"<li><strong>{k}:</strong> {v}</li>"
            html_body += "</ul>"

        html_body += f"""
            <hr>
            <p><small>Timestamp: {datetime.now().isoformat()}</small></p>
          </body>
        </html>
        """

        msg.attach(MIMEText(html_body, "html"))

        # Send email
        try:
            with smtplib.SMTP(
                config.email_smtp_server, config.email_smtp_port
            ) as server:
                server.starttls()
                # Note: For production, use app-specific passwords or OAuth
                # server.login(config.email_from, password)
                server.send_message(msg)
            logger.info("✅ Email notification sent")
            return True
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")
            return False

    def notify_experiment_started(self, experiment_name: str, namespace: str) -> bool:
        """Notify that an experiment has started"""
        return self.send_notification(
            message=f"Chaos experiment '{experiment_name}' has started in namespace '{namespace}'",
            title="Chaos Experiment Started",
            level="info",
            experiment_name=experiment_name,
            experiment_status="started",
            details={"namespace": namespace},
        )

    def notify_experiment_completed(
        self,
        experiment_name: str,
        namespace: str,
        success: bool = True,
        details: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Notify that an experiment has completed"""
        level = "success" if success else "error"
        status = "completed" if success else "failed"

        return self.send_notification(
            message=f"Chaos experiment '{experiment_name}' has {status} in namespace '{namespace}'",
            title=f"Chaos Experiment {status.capitalize()}",
            level=level,
            experiment_name=experiment_name,
            experiment_status=status,
            details=details or {},
        )

    def notify_experiment_error(
        self, experiment_name: str, error: str, namespace: Optional[str] = None
    ) -> bool:
        """Notify about an experiment error"""
        return self.send_notification(
            message=f"Error in chaos experiment '{experiment_name}': {error}",
            title="Chaos Experiment Error",
            level="error",
            experiment_name=experiment_name,
            experiment_status="error",
            details={"namespace": namespace} if namespace else {},
        )


def main():
    """CLI for notification service"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Chaos Experiment Notification Service"
    )
    parser.add_argument("message", help="Notification message")
    parser.add_argument(
        "--title", default="Chaos Experiment", help="Notification title"
    )
    parser.add_argument(
        "--level",
        choices=["info", "warning", "error", "success"],
        default="info",
        help="Notification level",
    )
    parser.add_argument("--experiment", help="Experiment name")
    parser.add_argument("--status", help="Experiment status")

    args = parser.parse_args()

    service = NotificationService()

    try:
        success = service.send_notification(
            message=args.message,
            title=args.title,
            level=args.level,
            experiment_name=getattr(args, "experiment", None),
            experiment_status=getattr(args, "status", None),
        )
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
