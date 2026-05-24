"""Cross-file analysis: dependency graph, data flow, project context."""
import ast
import json
from pathlib import Path
from typing import Dict, List, Any, Set, Tuple
from collections import defaultdict


class CodeGraph:
    """Builds and analyzes code dependency graph."""
    
    def __init__(self, root_path: Path):
        self.root = root_path
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.edges: List[Tuple[str, str]] = []
        self.imports: Dict[str, List[str]] = defaultdict(list)
        self.functions: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.classes: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    
    def scan_project(self, extensions: Set[str] = {".py", ".js", ".ts"}) -> None:
        """Scan project and build graph."""
        for ext in extensions:
            for file_path in self.root.rglob(f"*{ext}"):
                self._analyze_file(file_path)
    
    def _analyze_file(self, file_path: Path) -> None:
        """Analyze single file for imports, functions, classes."""
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            rel_path = str(file_path.relative_to(self.root))
            
            self.nodes[rel_path] = {
                "path": rel_path,
                "size": len(content),
                "lines": len(content.splitlines()),
            }
            
            # Python-specific analysis
            if file_path.suffix == ".py":
                self._analyze_python(file_path, rel_path, content)
            
            # JavaScript/TypeScript analysis
            elif file_path.suffix in (".js", ".ts", ".jsx", ".tsx"):
                self._analyze_js(file_path, rel_path, content)
        
        except (OSError, SyntaxError):
            pass
    
    def _analyze_python(
        self,
        file_path: Path,
        rel_path: str,
        content: str,
    ) -> None:
        """Parse Python file for functions, classes, imports."""
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return
        
        for node in ast.walk(tree):
            # Track imports
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self.imports[rel_path].append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    self.imports[rel_path].append(node.module)
                    # Track cross-file imports
                    for alias in node.names:
                        if alias.name == "*":
                            continue
                        self.edges.append((rel_path, node.module))
            
            # Track functions
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                decorators_list = [
                    self._get_decorator_name(d)
                    for d in node.decorator_list
                ]
                func_info = {
                    "name": node.name,
                    "line": node.lineno,
                    "args": [arg.arg for arg in node.args.args],
                    "decorators": decorators_list,
                    "calls": self._extract_calls(node),
                }
                self.functions[rel_path].append(func_info)
            
            # Track classes
            elif isinstance(node, ast.ClassDef):
                bases = [self._get_base_name(b) for b in node.bases]
                methods = [
                    n.name
                    for n in node.body
                    if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                ]
                class_info = {
                    "name": node.name,
                    "line": node.lineno,
                    "bases": bases,
                    "methods": methods,
                }
                self.classes[rel_path].append(class_info)
    
    def _analyze_js(
        self,
        file_path: Path,
        rel_path: str,
        content: str,
    ) -> None:
        """Basic JS/TS analysis (regex-based, not full AST)."""
        import re
        
        # Extract imports
        import_pattern = r"(?:import|require)\(['\"]([^'\"]+)['\"]\)"
        for match in re.finditer(import_pattern, content):
            self.imports[rel_path].append(match.group(1))
        
        # Extract function declarations
        func_pattern = r"(?:function\s+)?(\w+)\s*\(([^)]*)\)"
        for match in re.finditer(func_pattern, content):
            func_info = {
                "name": match.group(1),
                "line": content[:match.start()].count("\n") + 1,
                "args": [a.strip() for a in match.group(2).split(",") if a.strip()],
                "decorators": [],
                "calls": [],
            }
            self.functions[rel_path].append(func_info)
    
    def _get_decorator_name(self, node: ast.AST) -> str:
        """Extract decorator name from AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_decorator_name(node.value)}.{node.attr}"
        elif isinstance(node, ast.Call):
            return self._get_decorator_name(node.func)
        return "unknown"
    
    def _get_base_name(self, node: ast.AST) -> str:
        """Extract base class name from AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_base_name(node.value)}.{node.attr}"
        return "unknown"
    
    def _extract_calls(self, func_node: ast.FunctionDef) -> List[str]:
        """Extract function calls from a function body."""
        calls = []
        for node in ast.walk(func_node):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    calls.append(node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    calls.append(node.func.attr)
        return list(set(calls))
    
    def get_related_files(self, file_path: str, depth: int = 1) -> List[str]:
        """Get files related to given file (imports, dependencies)."""
        related = set()
        to_visit = [file_path]
        visited = {file_path}
        
        for _ in range(depth):
            next_visit = []
            for current in to_visit:
                # Files that current imports
                for edge in self.edges:
                    if edge[0] == current and edge[1] not in visited:
                        related.add(edge[1])
                        next_visit.append(edge[1])
                        visited.add(edge[1])
                
                # Files that import current
                for edge in self.edges:
                    if edge[1] == current and edge[0] not in visited:
                        related.add(edge[0])
                        next_visit.append(edge[0])
                        visited.add(edge[0])
            
            to_visit = next_visit
        
        return list(related)
    
    def find_entry_points(self) -> List[str]:
        """Find potential entry points (main functions, routes, etc.)."""
        entry_points = []
        
        for file_path, funcs in self.functions.items():
            for func in funcs:
                # Python main
                if func["name"] == "main":
                    entry_points.append(f"{file_path}:main")
                
                # Flask/FastAPI routes
                if "route" in func.get("decorators", []) or \
                   "get" in func.get("decorators", []) or \
                   "post" in func.get("decorators", []):
                    entry_points.append(f"{file_path}:{func['name']}")
                
                # Express routes
                if func["name"] in ("get", "post", "put", "delete", "patch"):
                    entry_points.append(f"{file_path}:{func['name']}")
        
        return entry_points
    
    def get_context_for_file(self, file_path: str) -> Dict[str, Any]:
        """Get contextual information about a file's role in project."""
        related = self.get_related_files(file_path)
        entry_points = self.find_entry_points()
        
        is_entry = f"{file_path}:main" in entry_points or \
                   any(f"{file_path}:" in ep for ep in entry_points)
        
        has_tests = any("test" in p.lower() for p in related)
        
        return {
            "project_type": self._detect_project_type(),
            "related_files": related,
            "is_entry_point": is_entry,
            "has_tests": has_tests,
            "total_functions": sum(len(f) for f in self.functions.values()),
            "total_classes": sum(len(c) for c in self.classes.values()),
        }
    
    def _detect_project_type(self) -> str:
        """Detect project type from structure and imports."""
        web_indicators = {"flask", "fastapi", "django", "express", "next"}
        data_indicators = {"pandas", "numpy", "tensorflow", "pytorch"}
        infra_indicators = {"docker", "kubernetes", "aws", "azure"}
        
        all_imports = set()
        for imports in self.imports.values():
            all_imports.update(imports)
        
        if all_imports & web_indicators:
            return "web-application"
        elif all_imports & data_indicators:
            return "data-science"
        elif all_imports & infra_indicators:
            return "infrastructure"
        elif self.imports and any("test" in str(p) for p in self.imports.keys()):
            return "test-suite"
        else:
            return "library"
    
    def to_dict(self) -> Dict[str, Any]:
        """Export graph to dictionary."""
        return {
            "nodes": self.nodes,
            "edges": self.edges,
            "imports": dict(self.imports),
            "functions": {k: v for k, v in list(self.functions.items())[:20]},
            "classes": {k: v for k, v in list(self.classes.items())[:20]},
        }
    
    def save(self, path: Path) -> None:
        """Save graph to JSON file."""
        path.write_text(json.dumps(self.to_dict(), indent=2))
    
    @classmethod
    def load(cls, path: Path) -> "CodeGraph":
        """Load graph from JSON file."""
        graph = cls(Path("."))
        data = json.loads(path.read_text())
        graph.nodes = data.get("nodes", {})
        graph.edges = [tuple(e) for e in data.get("edges", [])]
        graph.imports = defaultdict(list, data.get("imports", {}))
        graph.functions = defaultdict(list, data.get("functions", {}))
        graph.classes = defaultdict(list, data.get("classes", {}))
        return graph
