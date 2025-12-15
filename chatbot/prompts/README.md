# Chatbot Prompts Configuration

This directory contains the external prompt configuration files for the Irado chatbot.

## Files

- `system_prompt.txt` - The main system prompt that defines the chatbot's behavior, rules, and instructions

## Usage

The chatbot automatically loads the system prompt from `system_prompt.txt` when it starts. This allows you to:

- ✅ **Edit prompts without code changes** - Modify the prompt file and restart the service
- ✅ **Version control prompts** - Track changes to prompts separately from code
- ✅ **Easy maintenance** - Update chatbot behavior without touching Python code
- ✅ **Backup and restore** - Keep prompt backups and restore previous versions

## Editing the Prompt

1. Edit the `system_prompt.txt` file
2. Restart the chatbot service:
   ```bash
   sudo systemctl restart irado-chatbot
   ```
3. Test the changes

## File Format

- **Encoding**: UTF-8
- **Line endings**: Unix (LF)
- **Language**: Dutch (Nederlands)

## Important Notes

- The prompt file must be readable by the chatbot service
- Changes require a service restart to take effect
- Always test changes in a development environment first
- Keep backups of working prompt versions

## Troubleshooting

If the prompt file cannot be loaded, the chatbot will fall back to a basic default prompt. Check the service logs for any file access errors:

```bash
journalctl -u irado-chatbot --no-pager -n 20
```
