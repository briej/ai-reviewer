import * as vscode from 'vscode';
import * as child_process from 'child_process';
import * as path from 'path';

interface Issue {
    severity: string;
    type: string;
    location: string;
    message: string;
}

interface ScanResults {
    critical: Issue[];
    warning: Issue[];
    info: Issue[];
}

let resultsPanel: vscode.WebviewPanel | undefined = undefined;
let scanResults: ScanResults = { critical: [], warning: [], info: [] };

export function activate(context: vscode.ExtensionContext) {
    console.log('ai-reviewer extension is now active!');

    // Register commands
    const scanWorkspaceDisposable = vscode.commands.registerCommand(
        'ai-reviewer.scanWorkspace',
        scanWorkspace
    );

    const scanFileDisposable = vscode.commands.registerCommand(
        'ai-reviewer.scanFile',
        scanActiveFile
    );

    const showResultsDisposable = vscode.commands.registerCommand(
        'ai-reviewer.showResults',
        showResults
    );

    const clearResultsDisposable = vscode.commands.registerCommand(
        'ai-reviewer.clearResults',
        clearResults
    );

    context.subscriptions.push(
        scanWorkspaceDisposable,
        scanFileDisposable,
        showResultsDisposable,
        clearResultsDisposable
    );

    // Create results panel
    const resultsTreeProvider = new ResultsTreeProvider();
    vscode.window.registerTreeDataProvider('ai-reviewer.results', resultsTreeProvider);
}

function getExtensionPath(): string {
    return vscode.extensions.getExtension('briej.ai-reviewer-vscode')?.extensionPath || '';
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

async function runScan(targetPath: string) {
    const mode = vscode.workspace.getConfiguration('ai-reviewer').get('mode') || 'fast';
    const provider = vscode.workspace.getConfiguration('ai-reviewer').get('provider') || 'ollama';
    const model = vscode.workspace.getConfiguration('ai-reviewer').get('model') || 'llama3.1:8b';

    const statusBarItem = vscode.window.createStatusBarItem(
        vscode.StatusBarAlignment.Left,
        100
    );
    statusBarItem.text = '$(sync~spin) ai-reviewer: Scanning...';
    statusBarItem.show();

    try {
        let args = [targetPath, '--mode', mode];
        
        if (mode === 'ai') {
            args.push('--provider', provider, '--model', model);
        } else if (mode === 'cloud') {
            args.push('--provider', provider);
        }

        args.push('--format', 'json');

        const cmd = `ai-review ${args.join(' ')}`;
        
        const result = await executeCommand(cmd);
        
        if (result.error) {
            vscode.window.showErrorMessage(`Scan failed: ${result.error}`);
            statusBarItem.dispose();
            return;
        }

        const jsonOutput = result.stdout;
        const parsedResults = JSON.parse(jsonOutput);
        
        // Convert to our format
        scanResults = {
            critical: parsedResults.issues?.filter((i: Issue) => i.severity === 'critical') || [],
            warning: parsedResults.issues?.filter((i: Issue) => i.severity === 'warning') || [],
            info: parsedResults.issues?.filter((i: Issue) => i.severity === 'info') || []
        };

        const totalIssues = scanResults.critical.length + scanResults.warning.length + scanResults.info.length;
        
        vscode.window.showInformationMessage(
            `ai-reviewer: Found ${totalIssues} issues (${scanResults.critical} critical, ${scanResults.warning} warning, ${scanResults.info} info)`
        );

        statusBarItem.text = `$(check) ai-reviewer: ${totalIssues} issues`;
        statusBarItem.command = 'ai-reviewer.showResults';

        showResults();

    } catch (error) {
        vscode.window.showErrorMessage(`Scan error: ${error}`);
    } finally {
        setTimeout(() => statusBarItem.dispose(), 3000);
    }
}

function executeCommand(cmd: string): Promise<{ stdout: string; stderr: string; error?: Error }> {
    return new Promise((resolve) => {
        const process = child_process.exec(cmd, {
            maxBuffer: 1024 * 1024 * 10 // 10MB buffer
        });

        let stdout = '';
        let stderr = '';

        process.stdout?.on('data', (data) => {
            stdout += data;
        });

        process.stderr?.on('data', (data) => {
            stderr += data;
        });

        process.on('close', (code) => {
            if (code === 0 || stdout) {
                resolve({ stdout, stderr });
            } else {
                resolve({ stdout, stderr, error: new Error(stderr) });
            }
        });

        process.on('error', (error) => {
            resolve({ stdout: '', stderr: '', error });
        });
    });
}

function showResults() {
    if (!resultsPanel) {
        resultsPanel = vscode.window.createWebviewPanel(
            'aiReviewerResults',
            'ai-reviewer Results',
            vscode.ViewColumn.One,
            {
                enableScripts: true,
                retainContextWhenHidden: true
            }
        );

        resultsPanel.onDidDispose(() => {
            resultsPanel = undefined;
        });
    }

    resultsPanel.webview.html = getWebviewContent(scanResults);
    resultsPanel.reveal(vscode.ViewColumn.One);
}

function clearResults() {
    scanResults = { critical: [], warning: [], info: [] };
    vscode.window.showInformationMessage('ai-reviewer: Results cleared');
    
    if (resultsPanel) {
        resultsPanel.webview.html = getWebviewContent(scanResults);
    }
}

function getWebviewContent(results: ScanResults): string {
    const totalIssues = results.critical.length + results.warning.length + results.info.length;

    return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ai-reviewer Results</title>
    <style>
        body {
            font-family: var(--vscode-font-family);
            color: var(--vscode-foreground);
            background: var(--vscode-editor-background);
            padding: 20px;
        }
        h1 { color: var(--vscode-descriptionForeground); }
        .summary {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }
        .card {
            background: var(--vscode-sideBar-background);
            padding: 15px;
            border-radius: 6px;
            border-left: 4px solid;
        }
        .card.critical { border-left-color: #e94560; }
        .card.warning { border-left-color: #f4a261; }
        .card.info { border-left-color: #2a9d8f; }
        .card .number {
            font-size: 2em;
            font-weight: bold;
        }
        .card.critical .number { color: #e94560; }
        .card.warning .number { color: #f4a261; }
        .card.info .number { color: #2a9d8f; }
        .issue {
            background: var(--vscode-sideBar-background);
            padding: 12px;
            margin: 8px 0;
            border-radius: 4px;
            border-left: 3px solid;
        }
        .issue.critical { border-left-color: #e94560; }
        .issue.warning { border-left-color: #f4a261; }
        .issue.info { border-left-color: #2a9d8f; }
        .issue-header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 6px;
        }
        .issue-type {
            font-weight: 600;
            color: var(--vscode-descriptionForeground);
        }
        .issue-location {
            font-family: monospace;
            color: var(--vscode-descriptionForeground);
            font-size: 0.9em;
        }
        .issue-message {
            color: var(--vscode-foreground);
        }
        .empty {
            text-align: center;
            color: var(--vscode-descriptionForeground);
            padding: 40px;
        }
    </style>
</head>
<body>
    <h1>🤖 ai-reviewer Results</h1>
    
    <div class="summary">
        <div class="card critical">
            <div class="number">${results.critical.length}</div>
            <div>Critical</div>
        </div>
        <div class="card warning">
            <div class="number">${results.warning.length}</div>
            <div>Warning</div>
        </div>
        <div class="card info">
            <div class="number">${results.info.length}</div>
            <div>Info</div>
        </div>
    </div>

    <h2>Issues (${totalIssues} total)</h2>
    
    ${results.critical.length > 0 ? '<h3>Critical</h3>' : ''}
    ${results.critical.map(issue => `
        <div class="issue critical">
            <div class="issue-header">
                <span class="issue-type">${issue.type}</span>
                <span class="issue-location">${issue.location}</span>
            </div>
            <div class="issue-message">${issue.message}</div>
        </div>
    `).join('')}

    ${results.warning.length > 0 ? '<h3>Warning</h3>' : ''}
    ${results.warning.map(issue => `
        <div class="issue warning">
            <div class="issue-header">
                <span class="issue-type">${issue.type}</span>
                <span class="issue-location">${issue.location}</span>
            </div>
            <div class="issue-message">${issue.message}</div>
        </div>
    `).join('')}

    ${results.info.length > 0 ? '<h3>Info</h3>' : ''}
    ${results.info.map(issue => `
        <div class="issue info">
            <div class="issue-header">
                <span class="issue-type">${issue.type}</span>
                <span class="issue-location">${issue.location}</span>
            </div>
            <div class="issue-message">${issue.message}</div>
        </div>
    `).join('')}

    ${totalIssues === 0 ? '<div class="empty">No issues found! ✅</div>' : ''}
</body>
</html>`;
}

class ResultsTreeProvider implements vscode.TreeDataProvider<string> {
    private _onDidChangeTreeData = new vscode.EventEmitter<string | undefined>();
    readonly onDidChangeTreeData = this._onDidChangeTreeData.event;

    refresh(): void {
        this._onDidChangeTreeData.fire(undefined);
    }

    getTreeItem(element: string): vscode.TreeItem {
        return new vscode.TreeItem(element, vscode.TreeItemCollapsibleState.None);
    }

    getChildren(): string[] {
        const items: string[] = [];
        
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

export function deactivate() {}
