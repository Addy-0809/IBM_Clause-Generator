<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

This project is a fullstack Legal Clause Generator web app. Backend: Python FastAPI, integrates with a language model API (OpenAI or Hugging Face). Frontend: React (Vite). Features: select clause type, provide prompt/examples, generate clause, export as Word or PDF.

- When generating backend code, use FastAPI and provide endpoints for clause generation and document export.
- When generating frontend code, use React and provide a modern UI for clause selection, prompt input, and export options.
- Use python-docx for Word export and reportlab or pdfkit for PDF export.
- Use environment variables for API keys and sensitive config.
