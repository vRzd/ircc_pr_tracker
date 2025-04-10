import unittest
from unittest.mock import patch, MagicMock
from src.email_notifier import EmailNotifier

class TestEmailNotifier(unittest.TestCase):
    def setUp(self):
        self.smtp_server = "smtp.example.com"
        self.smtp_port = 587
        self.sender_email = "sender@example.com"
        self.sender_password = "password"
        self.recipient_emails = ["recipient1@example.com", "recipient2@example.com"]
        self.notifier = EmailNotifier(
            self.smtp_server,
            self.smtp_port,
            self.sender_email,
            self.sender_password,
            self.recipient_emails
        )

    @patch("smtplib.SMTP")
    def test_send_email_success(self, mock_smtp):
        # Arrange
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        # Act
        self.notifier.send_email("Test Subject", "Test Message")

        # Assert
        mock_smtp.assert_called_with(self.smtp_server, self.smtp_port)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_with(self.sender_email, self.sender_password)
        mock_server.sendmail.assert_called_once_with(
            self.sender_email,
            self.recipient_emails,
            unittest.mock.ANY
        )
        mock_server.quit.assert_not_called()  # 'quit' isn't needed when using a context manager

    @patch("smtplib.SMTP")
    def test_send_email_failure(self, mock_smtp):
        # Arrange
        mock_smtp.side_effect = Exception("SMTP error")

        # Act
        with self.assertLogs(level="ERROR") as log:
            self.notifier.send_email("Test Subject", "Test Message")

        # Assert
        self.assertIn("Failed to send email", log.output[0])

if __name__ == "__main__":
    unittest.main()
