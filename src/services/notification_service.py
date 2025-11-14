import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from typing import Dict, Any
from datetime import datetime


class NotificationService:
    def __init__(self):
        self.sendgrid_key = os.getenv("SENDGRID_API_KEY")
        self.notification_email = os.getenv("NOTIFICATION_EMAIL")
        self.confidence_threshold = float(os.getenv("CONFIDENCE_THRESHOLD", 0.8))
        self.human_review_threshold = float(os.getenv("HUMAN_REVIEW_THRESHOLD", 0.6))

    async def send_signal_notification(self, signal: Dict[str, Any]) -> bool:
        """根据置信度发送不同类型的通知"""
        confidence = signal.get("confidence", 0)
        signal_type = signal.get("signal", "HOLD")

        if confidence >= self.confidence_threshold:
            return await self._send_auto_notification(signal)
        elif confidence >= self.human_review_threshold:
            return await self._send_review_notification(signal)

        return False

    async def _send_auto_notification(self, signal: Dict[str, Any]) -> bool:
        """发送自动交易信号通知"""
        subject = (
            f"🚨 BTC交易信号：{signal['signal']} (置信度: {signal['confidence']:.2%})"
        )

        html_content = f"""
        <html>
        <body>
            <h2>比特币交易信号 - 自动通知</h2>
            <p><strong>时间：</strong>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>信号：</strong><span style="color: {'green' if signal['signal'] == 'BUY' else 'red' if signal['signal'] == 'SELL' else 'gray'}; font-size: 20px;">{signal['signal']}</span></p>
            <p><strong>置信度：</strong>{signal['confidence']:.2%}</p>
            <p><strong>当前价格：</strong>${signal.get('price', 'N/A')}</p>
            <hr>
            <h3>分析推理：</h3>
            <p>{signal.get('reasoning', 'N/A')}</p>
            <hr>
            <h3>Agent共识：</h3>
            <pre>{signal.get('agents_consensus', {})}</pre>
        </body>
        </html>
        """

        return await self._send_email(subject, html_content)

    async def _send_review_notification(self, signal: Dict[str, Any]) -> bool:
        """发送需要人工审核的通知"""
        subject = (
            f"⚠️ BTC信号待审核：{signal['signal']} (置信度: {signal['confidence']:.2%})"
        )

        html_content = f"""
        <html>
        <body>
            <h2>比特币交易信号 - 需要人工审核</h2>
            <p style="color: orange;"><strong>⚠️ 此信号置信度中等，建议人工审核后决策</strong></p>
            <p><strong>时间：</strong>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>信号：</strong>{signal['signal']}</p>
            <p><strong>置信度：</strong>{signal['confidence']:.2%}</p>
            <p><strong>当前价格：</strong>${signal.get('price', 'N/A')}</p>
            <hr>
            <h3>分析推理：</h3>
            <p>{signal.get('reasoning', 'N/A')}</p>
        </body>
        </html>
        """

        return await self._send_email(subject, html_content)

    async def _send_email(self, subject: str, html_content: str) -> bool:
        """发送邮件"""
        try:
            message = Mail(
                from_email="btc-agent@system.com",
                to_emails=self.notification_email,
                subject=subject,
                html_content=html_content,
            )

            sg = SendGridAPIClient(self.sendgrid_key)
            response = sg.send(message)

            return response.status_code == 202
        except Exception as e:
            print(f"邮件发送失败: {e}")
            return False
