"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.activate = activate;
exports.deactivate = deactivate;
const vscode = __importStar(require("vscode"));
const child_process = __importStar(require("child_process"));
const fs = __importStar(require("fs"));
const os = __importStar(require("os"));
const path = __importStar(require("path"));
let resultsPanel = undefined;
let scanResults = { critical: [], warning: [], info: [] };
let resultsTreeProvider = undefined;
function activate(context) {
    // Register commands
    const scanWorkspaceDisposable = vscode.commands.registerCommand('ai-reviewer.scanWorkspace', scanWorkspace);
    const scanFileDisposable = vscode.commands.registerCommand('ai-reviewer.scanFile', scanActiveFile);
    const showResultsDisposable = vscode.commands.registerCommand('ai-reviewer.showResults', showResults);
    const clearResultsDisposable = vscode.commands.registerCommand('ai-reviewer.clearResults', clearResults);
    context.subscriptions.push(scanWorkspaceDisposable, scanFileDisposable, showResultsDisposable, clearResultsDisposable);
    // Create results panel
    resultsTreeProvider = new ResultsTreeProvider();
    vscode.window.registerTreeDataProvider('ai-reviewer.results', resultsTreeProvider);
}
async function scanWorkspace() {
    const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
    if (!workspaceFolder) {
        vscode.window.showErrorMessage('No workspace folder open');
        return;
    }
    await runScan(workspaceFolder.uri.fsPath);
}
async function scanActiveFile() {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
        vscode.window.showErrorMessage('No file is open');
        return;
    }
    const filePath = editor.document.uri.fsPath;
    await runScan(filePath);
}
async function runScan(targetPath) {
    const config = vscode.workspace.getConfiguration('ai-reviewer');
    const mode = config.get('mode', 'fast');
    const provider = config.get('provider', 'ollama');
    const model = config.get('model', 'llama3.1:8b');
    const severity = config.get('severity', 'all');
    const ignore = config.get('ignore', []);
    const statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 100);
    statusBarItem.text = '$(sync~spin) ai-reviewer: Scanning...';
    statusBarItem.show();
    const outputPath = path.join(os.tmpdir(), `ai-reviewer-${Date.now()}.json`);
    try {
        const args = [targetPath, '--mode', mode, '--format', 'json', '--output', outputPath, '--severity', severity];
        if (mode === 'ai') {
            args.push('--provider', provider, '--model', model);
        }
        else if (mode === 'cloud') {
            args.push('--provider', provider);
        }
        ignore.forEach(pattern => args.push('--ignore', pattern));
        const result = await executeCommand('ai-review', args);
        if (result.error && !fs.existsSync(outputPath)) {
            const message = result.stderr.trim() || result.error.message;
            vscode.window.showErrorMessage(`Scan failed: ${message}`);
            statusBarItem.dispose();
            return;
        }
        const jsonOutput = await fs.promises.readFile(outputPath, 'utf8');
        const parsedResults = JSON.parse(jsonOutput);
        // Convert to our format
        scanResults = {
            critical: parsedResults.issues?.filter((i) => i.severity === 'critical') || [],
            warning: parsedResults.issues?.filter((i) => i.severity === 'warning') || [],
            info: parsedResults.issues?.filter((i) => i.severity === 'info') || []
        };
        resultsTreeProvider?.refresh();
        const totalIssues = scanResults.critical.length + scanResults.warning.length + scanResults.info.length;
        vscode.window.showInformationMessage(`ai-reviewer: Found ${totalIssues} issues (${scanResults.critical.length} critical, ${scanResults.warning.length} warning, ${scanResults.info.length} info)`);
        statusBarItem.text = totalIssues > 0
            ? `$(warning) ai-reviewer: ${totalIssues} issues`
            : '$(check) ai-reviewer: clean';
        statusBarItem.command = 'ai-reviewer.showResults';
        showResults();
    }
    catch (error) {
        vscode.window.showErrorMessage(`Scan error: ${error}`);
    }
    finally {
        fs.promises.unlink(outputPath).catch(() => undefined);
        setTimeout(() => statusBarItem.dispose(), 3000);
    }
}
function executeCommand(command, args) {
    return new Promise((resolve) => {
        child_process.execFile(command, args, {
            maxBuffer: 1024 * 1024 * 10,
            windowsHide: true
        }, (error, stdout, stderr) => {
            resolve({ stdout, stderr, error: error || undefined });
        });
    });
}
function showResults() {
    if (!resultsPanel) {
        resultsPanel = vscode.window.createWebviewPanel('aiReviewerResults', 'ai-reviewer Results', vscode.ViewColumn.One, {
            enableScripts: true,
            retainContextWhenHidden: true
        });
        resultsPanel.onDidDispose(() => {
            resultsPanel = undefined;
        });
    }
    resultsPanel.webview.html = getWebviewContent(scanResults);
    resultsPanel.reveal(vscode.ViewColumn.One);
}
function clearResults() {
    scanResults = { critical: [], warning: [], info: [] };
    resultsTreeProvider?.refresh();
    vscode.window.showInformationMessage('ai-reviewer: Results cleared');
    if (resultsPanel) {
        resultsPanel.webview.html = getWebviewContent(scanResults);
    }
}
function getWebviewContent(results) {
    const totalIssues = results.critical.length + results.warning.length + results.info.length;
    const score = Math.max(0, Math.round((10 - results.critical.length * 1.5 - results.warning.length * 0.5) * 10) / 10);
    const statusClass = results.critical.length > 0 ? 'critical' : results.warning.length > 0 ? 'warning' : 'clean';
    const statusText = results.critical.length > 0 ? 'Action required' : results.warning.length > 0 ? 'Review recommended' : 'Clean';
    return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ai-reviewer Results</title>
    <style>
        :root {
            --surface: var(--vscode-sideBar-background);
            --surface-soft: var(--vscode-editorWidget-background);
            --border: var(--vscode-panel-border);
            --muted: var(--vscode-descriptionForeground);
            --critical: #e94560;
            --warning: #f4a261;
            --info: #2a9d8f;
            --clean: #4ecca3;
        }

        * {
            box-sizing: border-box;
        }

        body {
            font-family: var(--vscode-font-family);
            color: var(--vscode-foreground);
            background: var(--vscode-editor-background);
            padding: 0;
            margin: 0;
            line-height: 1.45;
        }

        .page {
            width: min(1120px, 100%);
            margin: 0 auto;
            padding: 24px;
        }

        .hero {
            display: grid;
            grid-template-columns: minmax(0, 1fr) auto;
            gap: 20px;
            align-items: center;
            padding: 22px;
            margin-bottom: 18px;
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 8px;
        }

        .eyebrow {
            color: var(--muted);
            font-size: 12px;
            font-weight: 600;
            letter-spacing: 0;
            text-transform: uppercase;
            margin-bottom: 6px;
        }

        h1 {
            color: var(--vscode-foreground);
            font-size: 28px;
            line-height: 1.1;
            font-weight: 700;
            letter-spacing: 0;
            margin: 0;
        }

        .subtitle {
            color: var(--muted);
            margin: 8px 0 0;
            max-width: 640px;
        }

        .status-pill {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            min-width: 144px;
            min-height: 36px;
            padding: 8px 12px;
            border-radius: 999px;
            font-weight: 700;
            border: 1px solid;
            white-space: nowrap;
        }

        .status-pill.critical {
            color: var(--critical);
            border-color: rgba(233, 69, 96, 0.55);
            background: rgba(233, 69, 96, 0.13);
        }

        .status-pill.warning {
            color: var(--warning);
            border-color: rgba(244, 162, 97, 0.55);
            background: rgba(244, 162, 97, 0.13);
        }

        .status-pill.clean {
            color: var(--clean);
            border-color: rgba(78, 204, 163, 0.55);
            background: rgba(78, 204, 163, 0.13);
        }

        .summary {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 12px;
            margin-bottom: 22px;
        }

        .card {
            min-height: 112px;
            background: var(--surface);
            padding: 16px;
            border-radius: 8px;
            border: 1px solid var(--border);
            border-top: 3px solid var(--muted);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }

        .card.critical { border-top-color: var(--critical); }
        .card.warning { border-top-color: var(--warning); }
        .card.info { border-top-color: var(--info); }
        .card.score { border-top-color: var(--clean); }

        .card-label {
            color: var(--muted);
            font-size: 12px;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 0;
        }

        .number {
            font-size: 34px;
            line-height: 1;
            font-weight: 800;
            margin-top: 18px;
            letter-spacing: 0;
        }

        .card.critical .number { color: var(--critical); }
        .card.warning .number { color: var(--warning); }
        .card.info .number { color: var(--info); }
        .card.score .number { color: var(--clean); }

        .section-header {
            display: flex;
            align-items: baseline;
            justify-content: space-between;
            gap: 16px;
            margin: 24px 0 10px;
            border-bottom: 1px solid var(--border);
            padding-bottom: 8px;
        }

        h2 {
            margin: 0;
            font-size: 18px;
            line-height: 1.2;
            letter-spacing: 0;
        }

        .section-count {
            color: var(--muted);
            font-size: 12px;
            white-space: nowrap;
        }

        .issue {
            display: grid;
            grid-template-columns: 120px minmax(0, 1fr);
            gap: 14px;
            background: var(--surface);
            padding: 14px;
            margin: 10px 0;
            border-radius: 8px;
            border: 1px solid var(--border);
            border-left: 4px solid;
        }

        .issue.critical { border-left-color: var(--critical); }
        .issue.warning { border-left-color: var(--warning); }
        .issue.info { border-left-color: var(--info); }

        .severity {
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 30px;
            padding: 5px 8px;
            border-radius: 999px;
            font-size: 11px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0;
            border: 1px solid;
        }

        .severity.critical {
            color: var(--critical);
            border-color: rgba(233, 69, 96, 0.45);
            background: rgba(233, 69, 96, 0.10);
        }

        .severity.warning {
            color: var(--warning);
            border-color: rgba(244, 162, 97, 0.45);
            background: rgba(244, 162, 97, 0.10);
        }

        .severity.info {
            color: var(--info);
            border-color: rgba(42, 157, 143, 0.45);
            background: rgba(42, 157, 143, 0.10);
        }

        .issue-body {
            min-width: 0;
        }

        .issue-topline {
            display: flex;
            align-items: baseline;
            justify-content: space-between;
            gap: 14px;
            margin-bottom: 6px;
        }

        .issue-type {
            font-weight: 600;
            color: var(--vscode-foreground);
            overflow-wrap: anywhere;
        }

        .issue-location {
            font-family: var(--vscode-editor-font-family), monospace;
            color: var(--muted);
            font-size: 12px;
            text-align: right;
            overflow-wrap: anywhere;
        }

        .issue-message {
            color: var(--vscode-foreground);
            overflow-wrap: anywhere;
        }

        .empty {
            display: grid;
            place-items: center;
            min-height: 220px;
            color: var(--muted);
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 32px;
            text-align: center;
        }

        .empty strong {
            display: block;
            color: var(--clean);
            font-size: 18px;
            margin-bottom: 6px;
        }

        @media (max-width: 760px) {
            .page {
                padding: 16px;
            }

            .hero {
                grid-template-columns: 1fr;
            }

            .summary {
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }

            .issue {
                grid-template-columns: 1fr;
            }

            .severity {
                width: max-content;
            }

            .issue-topline {
                display: block;
            }

            .issue-location {
                text-align: left;
                margin-top: 4px;
            }
        }
    </style>
</head>
<body>
    <main class="page">
        <section class="hero">
            <div>
                <div class="eyebrow">AI code review</div>
                <h1>Scan Results</h1>
                <p class="subtitle">${totalIssues} total findings across critical, warning, and info levels.</p>
            </div>
            <div class="status-pill ${statusClass}">${statusText}</div>
        </section>

        <section class="summary" aria-label="Scan summary">
            ${renderSummaryCard('critical', 'Critical', results.critical.length)}
            ${renderSummaryCard('warning', 'Warning', results.warning.length)}
            ${renderSummaryCard('info', 'Info', results.info.length)}
            ${renderSummaryCard('score', 'Score', `${score}/10`)}
        </section>

        ${totalIssues === 0
        ? '<section class="empty"><div><strong>No issues found</strong><span>The current scan did not report critical, warning, or info findings.</span></div></section>'
        : `
                ${renderIssueSection('critical', 'Critical', results.critical)}
                ${renderIssueSection('warning', 'Warnings', results.warning)}
                ${renderIssueSection('info', 'Info', results.info)}
            `}
    </main>
</body>
</html>`;
}
function renderSummaryCard(kind, label, value) {
    return `
        <article class="card ${kind}">
            <div class="card-label">${escapeHtml(label)}</div>
            <div class="number">${escapeHtml(String(value))}</div>
        </article>
    `;
}
function renderIssueSection(severity, title, issues) {
    if (issues.length === 0) {
        return '';
    }
    return `
        <section>
            <div class="section-header">
                <h2>${escapeHtml(title)}</h2>
                <span class="section-count">${issues.length} ${issues.length === 1 ? 'finding' : 'findings'}</span>
            </div>
            ${issues.map(issue => renderIssueCard(severity, issue)).join('')}
        </section>
    `;
}
function renderIssueCard(severity, issue) {
    return `
        <article class="issue ${severity}">
            <div class="severity ${severity}">${escapeHtml(severity)}</div>
            <div class="issue-body">
                <div class="issue-topline">
                    <div class="issue-type">${escapeHtml(issue.type)}</div>
                    <div class="issue-location">${escapeHtml(issue.location)}</div>
                </div>
                <div class="issue-message">${escapeHtml(issue.message)}</div>
            </div>
        </article>
    `;
}
function escapeHtml(value) {
    return value
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}
class ResultsTreeProvider {
    constructor() {
        this._onDidChangeTreeData = new vscode.EventEmitter();
        this.onDidChangeTreeData = this._onDidChangeTreeData.event;
    }
    refresh() {
        this._onDidChangeTreeData.fire(undefined);
    }
    getTreeItem(element) {
        return new vscode.TreeItem(element, vscode.TreeItemCollapsibleState.None);
    }
    getChildren() {
        const items = [];
        scanResults.critical.forEach(issue => {
            items.push(`🔴 [CRITICAL] ${issue.type} - ${issue.location}`);
        });
        scanResults.warning.forEach(issue => {
            items.push(`🟡 [WARNING] ${issue.type} - ${issue.location}`);
        });
        scanResults.info.forEach(issue => {
            items.push(`🔵 [INFO] ${issue.type} - ${issue.location}`);
        });
        return items;
    }
}
function deactivate() { }
//# sourceMappingURL=extension.js.map