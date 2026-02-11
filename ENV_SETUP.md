# Environment Setup

## API Key Configuration

This project uses Groq Cloud API for LLM inference. The API key is stored securely in environment variables.

### Setup Instructions

1. **Create a `.env` file** in the project root:

   ```bash
   cp .env.example .env
   ```

2. **Add your Groq API key** to the `.env` file:

   ```
   GROQ_API_KEY=your_actual_api_key_here
   ```

3. **Get your API key** from [Groq Console](https://console.groq.com/keys)

4. **Install dependencies**:
   ```bash
   pip install python-dotenv
   ```

### Important Notes

- ⚠️ **Never commit `.env` file** - It's already in `.gitignore`
- ✅ **Commit `.env.example`** - This provides a template for others
- 🔒 **Keep your API key secure** - Don't share it publicly

### Files

- `.env` - Contains your actual API key (not tracked by git)
- `.env.example` - Template file (tracked by git)
- `config.py` - Loads environment variables using `python-dotenv`

### Troubleshooting

If you see "GROQ_API_KEY not found" error:

1. Check that `.env` file exists in project root
2. Verify the key is spelled correctly: `GROQ_API_KEY`
3. Ensure no extra spaces or quotes in the `.env` file
4. Make sure `python-dotenv` is installed
