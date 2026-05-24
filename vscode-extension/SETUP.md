# VS Code Extension Setup

## Prerequisites

To build and publish the VS Code extension, you need:

1. **Node.js** (v16 or higher)
2. **npm** (v8 or higher)
3. **@vscode/vsce** (VS Code extension packaging tool)

## Installation

### 1. Install Node.js

Download from: https://nodejs.org/

Verify installation:

```bash
node --version
npm --version
```

### 2. Install VSCE

```bash
npm install -g @vscode/vsce
```

### 3. Install Dependencies

```bash
cd vscode-extension
npm install
```

### 4. Compile Extension

```bash
npm run compile
```

This creates the `out/` directory with compiled JavaScript.

### 5. Package Extension

```bash
vsce package
```

This creates `ai-reviewer-vscode-1.3.1.vsix`

### 6. Install Locally (Testing)

```bash
code --install-extension ai-reviewer-vscode-1.3.1.vsix
```

### 7. Publish to Marketplace (Optional)

```bash
# Create account at https://marketplace.visualstudio.com
vsce publish
```

## Troubleshooting

### PowerShell Execution Policy

If you get "execution policy" errors:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### TypeScript Errors

Make sure `node_modules` is installed:

```bash
npm install
```

### Missing Dependencies

```bash
npm install --save-dev @types/node @types/vscode
```

## Development

Watch mode for automatic compilation:

```bash
npm run watch
```

Linting:

```bash
npm run lint
```

## Testing in VS Code

1. Open `vscode-extension/` folder in VS Code
2. Press `F5` to run extension host
3. Test commands from command palette

## File Structure

```
vscode-extension/
├── src/
│   └── extension.ts      # Main extension code
├── package.json          # Extension manifest
├── tsconfig.json         # TypeScript config
├── .vscodeignore         # Files to exclude
└── README.md             # User documentation
```

## Commands

After installation, these commands are available:

- `ai-reviewer: Scan Workspace` - Scan entire project
- `ai-reviewer: Scan Current File` - Scan active file
- `ai-reviewer: Show Results` - Display results panel
- `ai-reviewer: Clear Results` - Clear all results

## Settings

Configure in VS Code settings (`settings.json`):

```json
{
  "ai-reviewer.mode": "fast",
  "ai-reviewer.provider": "ollama",
  "ai-reviewer.model": "llama3.1:8b",
  "ai-reviewer.severity": "all",
  "ai-reviewer.ignore": ["__pycache__", ".git", "node_modules"]
}
```
