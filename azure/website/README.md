# Irado Chatbot

A Python-based chatbot system for waste management assistance.

## Features

- AI-powered responses
- Session management
- Email notifications
- Service management

## API Usage

The chatbot provides a REST API for chat interactions.

### Request Format

```json
{
  "sessionId": "unique-session-id",
  "action": "sendMessage",
  "chatInput": "user message"
}
```

### Response Format

```json
{
  "output": "bot response"
}
```

## Service Management

The chatbot runs as a systemd service:

```bash
sudo systemctl start irado-chatbot
sudo systemctl stop irado-chatbot
sudo systemctl restart irado-chatbot
sudo systemctl status irado-chatbot | cat
```

## Testing

Use the provided test interface for functionality verification.

## Change Log

- 2025-09-28: Security improvements and comment cleanup