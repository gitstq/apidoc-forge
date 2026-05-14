#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APIDoc Forge - Intelligent API Documentation Generator & Sync Engine
智能API文档自动生成与同步引擎

A lightweight, zero-dependency Python CLI tool for automatically generating
API documentation from Python source code with LLM enhancement.

Author: APIDoc Forge Team
License: MIT
Version: 1.0.0
"""

import ast
import os
import sys
import json
import re
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum


__version__ = "1.0.0"
__author__ = "APIDoc Forge Team"


class DocFormat(Enum):
    """Supported documentation formats."""
    MARKDOWN = "markdown"
    HTML = "html"
    JSON = "json"
    OPENAPI = "openapi"


@dataclass
class Parameter:
    """Represents a function/method parameter."""
    name: str
    type_hint: Optional[str] = None
    default_value: Optional[str] = None
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": self.type_hint,
            "default": self.default_value,
            "description": self.description
        }


@dataclass
class ReturnInfo:
    """Represents return type information."""
    type_hint: Optional[str] = None
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type_hint,
            "description": self.description
        }


@dataclass
class FunctionDoc:
    """Represents a documented function."""
    name: str
    docstring: str = ""
    parameters: List[Parameter] = field(default_factory=list)
    returns: ReturnInfo = field(default_factory=ReturnInfo)
    decorators: List[str] = field(default_factory=list)
    is_async: bool = False
    is_method: bool = False
    is_classmethod: bool = False
    is_staticmethod: bool = False
    is_property: bool = False
    raises: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)
    line_number: int = 0
    source_file: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "docstring": self.docstring,
            "parameters": [p.to_dict() for p in self.parameters],
            "returns": self.returns.to_dict(),
            "decorators": self.decorators,
            "is_async": self.is_async,
            "is_method": self.is_method,
            "is_classmethod": self.is_classmethod,
            "is_staticmethod": self.is_staticmethod,
            "is_property": self.is_property,
            "raises": self.raises,
            "examples": self.examples,
            "line_number": self.line_number,
            "source_file": self.source_file
        }


@dataclass
class ClassDoc:
    """Represents a documented class."""
    name: str
    docstring: str = ""
    methods: List[FunctionDoc] = field(default_factory=list)
    attributes: List[Parameter] = field(default_factory=list)
    bases: List[str] = field(default_factory=list)
    decorators: List[str] = field(default_factory=list)
    line_number: int = 0
    source_file: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "docstring": self.docstring,
            "methods": [m.to_dict() for m in self.methods],
            "attributes": [a.to_dict() for a in self.attributes],
            "bases": self.bases,
            "decorators": self.decorators,
            "line_number": self.line_number,
            "source_file": self.source_file
        }


@dataclass
class ModuleDoc:
    """Represents a documented module."""
    name: str
    docstring: str = ""
    functions: List[FunctionDoc] = field(default_factory=list)
    classes: List[ClassDoc] = field(default_factory=list)
    variables: List[Parameter] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    source_file: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "docstring": self.docstring,
            "functions": [f.to_dict() for f in self.functions],
            "classes": [c.to_dict() for c in self.classes],
            "variables": [v.to_dict() for v in self.variables],
            "imports": self.imports,
            "source_file": self.source_file
        }


class DocstringParser:
    """Parses docstrings to extract structured information."""
    
    @staticmethod
    def parse_google_style(docstring: str) -> Dict[str, Any]:
        """Parse Google-style docstring."""
        if not docstring:
            return {"description": "", "params": {}, "returns": {}, "raises": [], "examples": []}
        
        lines = docstring.strip().split('\n')
        result = {
            "description": "",
            "params": {},
            "returns": {},
            "raises": [],
            "examples": []
        }
        
        current_section = "description"
        current_content = []
        
        section_keywords = {
            'args:': 'params',
            'arguments:': 'params',
            'params:': 'params',
            'parameters:': 'params',
            'returns:': 'returns',
            'return:': 'returns',
            'raises:': 'raises',
            'raise:': 'raises',
            'exceptions:': 'raises',
            'example:': 'examples',
            'examples:': 'examples',
            'note:': 'notes',
            'notes:': 'notes',
            'todo:': 'todos',
        }
        
        for line in lines:
            stripped = line.strip().lower()
            
            # Check for section headers
            matched_section = None
            for keyword, section in section_keywords.items():
                if stripped.startswith(keyword):
                    matched_section = section
                    break
            
            if matched_section:
                # Save previous section content
                if current_section == "description":
                    result["description"] = '\n'.join(current_content).strip()
                elif current_section == "params":
                    result["params"] = DocstringParser._parse_params(current_content)
                elif current_section == "returns":
                    result["returns"] = DocstringParser._parse_returns(current_content)
                elif current_section == "raises":
                    result["raises"] = DocstringParser._parse_raises(current_content)
                elif current_section == "examples":
                    result["examples"] = DocstringParser._parse_examples(current_content)
                
                current_section = matched_section
                current_content = []
            else:
                current_content.append(line)
        
        # Process final section
        if current_section == "description":
            result["description"] = '\n'.join(current_content).strip()
        elif current_section == "params":
            result["params"] = DocstringParser._parse_params(current_content)
        elif current_section == "returns":
            result["returns"] = DocstringParser._parse_returns(current_content)
        elif current_section == "raises":
            result["raises"] = DocstringParser._parse_raises(current_content)
        elif current_section == "examples":
            result["examples"] = DocstringParser._parse_examples(current_content)
        
        return result
    
    @staticmethod
    def _parse_params(lines: List[str]) -> Dict[str, str]:
        """Parse parameter documentation."""
        params = {}
        current_param = None
        current_desc = []
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            
            # Check for parameter definition (name: description or name (type): description)
            match = re.match(r'^(\w+)(?:\s*\([^)]*\))?:\s*(.*)$', stripped)
            if match:
                if current_param:
                    params[current_param] = ' '.join(current_desc)
                current_param = match.group(1)
                current_desc = [match.group(2)] if match.group(2) else []
            elif current_param:
                current_desc.append(stripped)
        
        if current_param:
            params[current_param] = ' '.join(current_desc)
        
        return params
    
    @staticmethod
    def _parse_returns(lines: List[str]) -> Dict[str, str]:
        """Parse return documentation."""
        content = ' '.join(line.strip() for line in lines if line.strip())
        match = re.match(r'^(?:\(([^)]+)\)\s*:\s*)?(.+)$', content)
        if match:
            return {"type": match.group(1), "description": match.group(2)}
        return {"type": None, "description": content}
    
    @staticmethod
    def _parse_raises(lines: List[str]) -> List[str]:
        """Parse raises documentation."""
        raises = []
        for line in lines:
            stripped = line.strip()
            if stripped:
                raises.append(stripped)
        return raises
    
    @staticmethod
    def _parse_examples(lines: List[str]) -> List[str]:
        """Parse example documentation."""
        examples = []
        current_example = []
        
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('>>>') or stripped.startswith('...'):
                current_example.append(line)
            elif current_example:
                examples.append('\n'.join(current_example))
                current_example = []
                if stripped:
                    current_example.append(line)
            elif stripped:
                current_example.append(line)
        
        if current_example:
            examples.append('\n'.join(current_example))
        
        return examples


class ASTAnalyzer(ast.NodeVisitor):
    """Analyzes Python AST to extract API documentation."""
    
    def __init__(self, source_file: str):
        self.source_file = source_file
        self.module = ModuleDoc(name=Path(source_file).stem, source_file=source_file)
        self._current_class: Optional[ClassDoc] = None
    
    def visit_Module(self, node: ast.Module):
        """Visit module node."""
        self.module.docstring = ast.get_docstring(node) or ""
        self.generic_visit(node)
    
    def visit_Import(self, node: ast.Import):
        """Visit import statements."""
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            self.module.imports.append(f"import {alias.name}" + (f" as {alias.asname}" if alias.asname else ""))
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node: ast.ImportFrom):
        """Visit from import statements."""
        module = node.module or ""
        names = [alias.name for alias in node.names]
        self.module.imports.append(f"from {module} import {', '.join(names)}")
        self.generic_visit(node)
    
    def visit_Assign(self, node: ast.Assign):
        """Visit variable assignments."""
        if self._current_class is None and len(node.targets) == 1:
            if isinstance(node.targets[0], ast.Name):
                var_name = node.targets[0].id
                # Skip private variables
                if not var_name.startswith('_'):
                    type_hint = self._get_type_hint(node.value)
                    default_value = self._get_default_value(node.value)
                    self.module.variables.append(Parameter(
                        name=var_name,
                        type_hint=type_hint,
                        default_value=default_value
                    ))
        self.generic_visit(node)
    
    def visit_AnnAssign(self, node: ast.AnnAssign):
        """Visit annotated assignments."""
        if self._current_class is None and isinstance(node.target, ast.Name):
            var_name = node.target.id
            if not var_name.startswith('_'):
                type_hint = self._get_annotation(node.annotation)
                default_value = self._get_default_value(node.value) if node.value else None
                self.module.variables.append(Parameter(
                    name=var_name,
                    type_hint=type_hint,
                    default_value=default_value
                ))
        self.generic_visit(node)
    
    def visit_ClassDef(self, node: ast.ClassDef):
        """Visit class definitions."""
        class_doc = ClassDoc(
            name=node.name,
            docstring=ast.get_docstring(node) or "",
            bases=[self._get_base_name(base) for base in node.bases],
            decorators=[self._get_decorator_name(d) for d in node.decorator_list],
            line_number=node.lineno,
            source_file=self.source_file
        )
        
        # Parse docstring for attributes
        parsed = DocstringParser.parse_google_style(class_doc.docstring)
        
        # Visit class body
        previous_class = self._current_class
        self._current_class = class_doc
        
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self._process_method(item, class_doc)
            elif isinstance(item, ast.AnnAssign):
                if isinstance(item.target, ast.Name):
                    attr_name = item.target.id
                    if not attr_name.startswith('_'):
                        type_hint = self._get_annotation(item.annotation)
                        default_value = self._get_default_value(item.value) if item.value else None
                        class_doc.attributes.append(Parameter(
                            name=attr_name,
                            type_hint=type_hint,
                            default_value=default_value
                        ))
        
        self._current_class = previous_class
        self.module.classes.append(class_doc)
    
    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Visit function definitions."""
        if self._current_class is None:
            func_doc = self._process_function(node)
            self.module.functions.append(func_doc)
    
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        """Visit async function definitions."""
        if self._current_class is None:
            func_doc = self._process_function(node, is_async=True)
            self.module.functions.append(func_doc)
    
    def _process_function(self, node: Union[ast.FunctionDef, ast.AsyncFunctionDef], 
                          is_async: bool = False) -> FunctionDoc:
        """Process a function definition."""
        docstring = ast.get_docstring(node) or ""
        parsed = DocstringParser.parse_google_style(docstring)
        
        func_doc = FunctionDoc(
            name=node.name,
            docstring=parsed["description"],
            decorators=[self._get_decorator_name(d) for d in node.decorator_list],
            is_async=is_async,
            line_number=node.lineno,
            source_file=self.source_file,
            raises=parsed.get("raises", []),
            examples=parsed.get("examples", [])
        )
        
        # Process parameters
        args = node.args
        
        # Regular arguments
        arg_names = [arg.arg for arg in args.args]
        
        # Defaults
        defaults_start = len(arg_names) - len(args.defaults)
        defaults = [None] * defaults_start + [self._get_default_value(d) for d in args.defaults]
        
        # Type annotations
        for i, (arg_name, default) in enumerate(zip(arg_names, defaults)):
            type_hint = None
            if args.args[i].annotation:
                type_hint = self._get_annotation(args.args[i].annotation)
            
            param_desc = parsed["params"].get(arg_name, "")
            
            func_doc.parameters.append(Parameter(
                name=arg_name,
                type_hint=type_hint,
                default_value=default,
                description=param_desc
            ))
        
        # *args
        if args.vararg:
            type_hint = self._get_annotation(args.vararg.annotation) if args.vararg.annotation else None
            func_doc.parameters.append(Parameter(
                name=f"*{args.vararg.arg}",
                type_hint=type_hint,
                description=parsed["params"].get(args.vararg.arg, "")
            ))
        
        # **kwargs
        if args.kwarg:
            type_hint = self._get_annotation(args.kwarg.annotation) if args.kwarg.annotation else None
            func_doc.parameters.append(Parameter(
                name=f"**{args.kwarg.arg}",
                type_hint=type_hint,
                description=parsed["params"].get(args.kwarg.arg, "")
            ))
        
        # Return type
        if node.returns:
            func_doc.returns = ReturnInfo(
                type_hint=self._get_annotation(node.returns),
                description=parsed["returns"].get("description", "")
            )
        
        return func_doc
    
    def _process_method(self, node: Union[ast.FunctionDef, ast.AsyncFunctionDef], 
                        class_doc: ClassDoc):
        """Process a method definition."""
        func_doc = self._process_function(node, isinstance(node, ast.AsyncFunctionDef))
        func_doc.is_method = True
        
        # Check for special method types
        for decorator in func_doc.decorators:
            if 'classmethod' in decorator:
                func_doc.is_classmethod = True
            elif 'staticmethod' in decorator:
                func_doc.is_staticmethod = True
            elif 'property' in decorator:
                func_doc.is_property = True
        
        class_doc.methods.append(func_doc)
    
    def _get_annotation(self, node: Optional[ast.AST]) -> Optional[str]:
        """Get type annotation as string."""
        if node is None:
            return None
        return ast.unparse(node)
    
    def _get_default_value(self, node: Optional[ast.AST]) -> Optional[str]:
        """Get default value as string."""
        if node is None:
            return None
        try:
            return ast.unparse(node)
        except:
            return "..."
    
    def _get_base_name(self, node: ast.AST) -> str:
        """Get base class name."""
        try:
            return ast.unparse(node)
        except:
            return "<unknown>"
    
    def _get_decorator_name(self, node: ast.AST) -> str:
        """Get decorator name."""
        try:
            return ast.unparse(node)
        except:
            return "<unknown>"
    
    def _get_type_hint(self, node: ast.AST) -> Optional[str]:
        """Infer type hint from value."""
        type_map = {
            ast.Constant: lambda n: type(n.value).__name__,
            ast.List: lambda n: "list",
            ast.Dict: lambda n: "dict",
            ast.Set: lambda n: "set",
            ast.Tuple: lambda n: "tuple",
            ast.Str: lambda n: "str",  # Python < 3.8
            ast.Num: lambda n: type(n.n).__name__,  # Python < 3.8
        }
        
        node_type = type(node)
        if node_type in type_map:
            return type_map[node_type](node)
        return None


class MarkdownGenerator:
    """Generates Markdown documentation."""
    
    @staticmethod
    def generate(module: ModuleDoc, title: Optional[str] = None) -> str:
        """Generate Markdown documentation for a module."""
        lines = []
        
        # Title
        doc_title = title or f"API Documentation: {module.name}"
        lines.append(f"# {doc_title}")
        lines.append("")
        
        # Module description
        if module.docstring:
            lines.append(module.docstring)
            lines.append("")
        
        # Table of Contents
        lines.append("## Table of Contents")
        lines.append("")
        
        if module.functions:
            lines.append("- [Functions](#functions)")
            for func in module.functions:
                anchor = func.name.lower().replace('_', '-')
                lines.append(f"  - [{func.name}](#{anchor})")
        
        if module.classes:
            lines.append("- [Classes](#classes)")
            for cls in module.classes:
                anchor = cls.name.lower().replace('_', '-')
                lines.append(f"  - [{cls.name}](#{anchor})")
        
        lines.append("")
        
        # Functions section
        if module.functions:
            lines.append("## Functions")
            lines.append("")
            
            for func in module.functions:
                lines.extend(MarkdownGenerator._generate_function_doc(func))
        
        # Classes section
        if module.classes:
            lines.append("## Classes")
            lines.append("")
            
            for cls in module.classes:
                lines.extend(MarkdownGenerator._generate_class_doc(cls))
        
        # Module variables
        if module.variables:
            lines.append("## Module Variables")
            lines.append("")
            lines.append("| Name | Type | Default |")
            lines.append("|------|------|---------|")
            for var in module.variables:
                type_str = var.type_hint or "-"
                default_str = f"`{var.default_value}`" if var.default_value else "-"
                lines.append(f"| `{var.name}` | {type_str} | {default_str} |")
            lines.append("")
        
        return '\n'.join(lines)
    
    @staticmethod
    def _generate_function_doc(func: FunctionDoc) -> List[str]:
        """Generate documentation for a function."""
        lines = []
        
        # Function signature
        prefix = "async " if func.is_async else ""
        params_str = ", ".join(
            MarkdownGenerator._format_param(p) for p in func.parameters
        )
        
        anchor = func.name.lower().replace('_', '-')
        lines.append(f"### {func.name}")
        lines.append("")
        lines.append(f"```python")
        lines.append(f"{prefix}def {func.name}({params_str})")
        lines.append(f"```")
        lines.append("")
        
        # Description
        if func.docstring:
            lines.append(func.docstring)
            lines.append("")
        
        # Parameters
        if func.parameters:
            lines.append("**Parameters:**")
            lines.append("")
            for param in func.parameters:
                type_str = f" (*{param.type_hint}*)" if param.type_hint else ""
                default_str = f", default: `{param.default_value}`" if param.default_value else ""
                desc = f" - {param.description}" if param.description else ""
                lines.append(f"- `{param.name}`{type_str}{default_str}{desc}")
            lines.append("")
        
        # Returns
        if func.returns.type_hint or func.returns.description:
            lines.append("**Returns:**")
            lines.append("")
            if func.returns.type_hint:
                lines.append(f"*{func.returns.type_hint}*")
            if func.returns.description:
                lines.append(func.returns.description)
            lines.append("")
        
        # Raises
        if func.raises:
            lines.append("**Raises:**")
            lines.append("")
            for exc in func.raises:
                lines.append(f"- {exc}")
            lines.append("")
        
        # Examples
        if func.examples:
            lines.append("**Examples:**")
            lines.append("")
            lines.append("```python")
            for example in func.examples:
                lines.append(example)
            lines.append("```")
            lines.append("")
        
        # Source location
        lines.append(f"*Source: [{func.source_file}]({func.source_file}):{func.line_number}*")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        return lines
    
    @staticmethod
    def _generate_class_doc(cls: ClassDoc) -> List[str]:
        """Generate documentation for a class."""
        lines = []
        
        anchor = cls.name.lower().replace('_', '-')
        lines.append(f"### {cls.name}")
        lines.append("")
        
        # Class signature
        bases_str = f"({', '.join(cls.bases)})" if cls.bases else ""
        lines.append(f"```python")
        lines.append(f"class {cls.name}{bases_str}")
        lines.append(f"```")
        lines.append("")
        
        # Description
        if cls.docstring:
            lines.append(cls.docstring)
            lines.append("")
        
        # Attributes
        if cls.attributes:
            lines.append("**Attributes:**")
            lines.append("")
            for attr in cls.attributes:
                type_str = f" (*{attr.type_hint}*)" if attr.type_hint else ""
                default_str = f" = `{attr.default_value}`" if attr.default_value else ""
                lines.append(f"- `{attr.name}`{type_str}{default_str}")
            lines.append("")
        
        # Methods
        if cls.methods:
            lines.append("**Methods:**")
            lines.append("")
            for method in cls.methods:
                prefix = "async " if method.is_async else ""
                decorator_prefix = ""
                if method.is_classmethod:
                    decorator_prefix = "@classmethod "
                elif method.is_staticmethod:
                    decorator_prefix = "@staticmethod "
                elif method.is_property:
                    decorator_prefix = "@property "
                
                params = [p for p in method.parameters if p.name not in ('self', 'cls')]
                params_str = ", ".join(MarkdownGenerator._format_param(p) for p in params)
                
                sig = f"{decorator_prefix}{prefix}def {method.name}({params_str})"
                lines.append(f"- `{sig}`")
            lines.append("")
        
        # Source location
        lines.append(f"*Source: [{cls.source_file}]({cls.source_file}):{cls.line_number}*")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        return lines
    
    @staticmethod
    def _format_param(param: Parameter) -> str:
        """Format parameter for signature."""
        if param.name.startswith('*') or param.name.startswith('**'):
            return param.name
        
        result = param.name
        if param.type_hint:
            result += f": {param.type_hint}"
        if param.default_value:
            result += f" = {param.default_value}"
        return result


class HTMLGenerator:
    """Generates HTML documentation."""
    
    CSS_STYLES = """
    <style>
        * { box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
            background: #f5f5f5;
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }
        h2 { color: #34495e; margin-top: 40px; border-bottom: 2px solid #ecf0f1; padding-bottom: 8px; }
        h3 { color: #7f8c8d; margin-top: 30px; }
        .function-sig, .class-sig {
            background: #2d2d2d;
            color: #f8f8f2;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 14px;
            margin: 15px 0;
        }
        .keyword { color: #ff79c6; }
        .function { color: #50fa7b; }
        .class { color: #8be9fd; }
        .param { color: #ffb86c; }
        .type { color: #bd93f9; }
        .docstring {
            background: #f8f9fa;
            padding: 15px;
            border-left: 4px solid #3498db;
            margin: 15px 0;
            border-radius: 0 5px 5px 0;
        }
        .section { margin: 20px 0; }
        .section-title {
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 10px;
        }
        .param-list { margin: 10px 0; }
        .param-item {
            padding: 8px 0;
            border-bottom: 1px solid #ecf0f1;
        }
        .param-name {
            font-family: monospace;
            font-weight: bold;
            color: #e74c3c;
        }
        .param-type { color: #9b59b6; font-style: italic; }
        .param-default { color: #27ae60; }
        .source-link {
            font-size: 12px;
            color: #95a5a6;
            text-align: right;
            margin-top: 10px;
        }
        .toc {
            background: #ecf0f1;
            padding: 20px;
            border-radius: 5px;
            margin: 20px 0;
        }
        .toc ul { margin: 5px 0; padding-left: 20px; }
        .toc a { color: #3498db; text-decoration: none; }
        .toc a:hover { text-decoration: underline; }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th { background: #34495e; color: white; }
        tr:hover { background: #f5f5f5; }
        .divider {
            border: none;
            border-top: 1px solid #ecf0f1;
            margin: 30px 0;
        }
    </style>
    """
    
    @staticmethod
    def generate(module: ModuleDoc, title: Optional[str] = None) -> str:
        """Generate HTML documentation for a module."""
        doc_title = title or f"API Documentation: {module.name}"
        
        html_parts = [
            "<!DOCTYPE html>",
            "<html lang=\"en\">",
            "<head>",
            f"<title>{doc_title}</title>",
            "<meta charset=\"UTF-8\">",
            "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">",
            HTMLGenerator.CSS_STYLES,
            "</head>",
            "<body>",
            "<div class=\"container\">",
            f"<h1>{doc_title}</h1>",
        ]
        
        # Module description
        if module.docstring:
            html_parts.append(f'<div class="docstring">{module.docstring}</div>')
        
        # Table of Contents
        html_parts.append('<div class="toc">')
        html_parts.append('<h2>Table of Contents</h2>')
        html_parts.append('<ul>')
        
        if module.functions:
            html_parts.append('<li><a href="#functions">Functions</a>')
            html_parts.append('<ul>')
            for func in module.functions:
                anchor = func.name.lower().replace('_', '-')
                html_parts.append(f'<li><a href="#{anchor}">{func.name}</a></li>')
            html_parts.append('</ul>')
            html_parts.append('</li>')
        
        if module.classes:
            html_parts.append('<li><a href="#classes">Classes</a>')
            html_parts.append('<ul>')
            for cls in module.classes:
                anchor = cls.name.lower().replace('_', '-')
                html_parts.append(f'<li><a href="#{anchor}">{cls.name}</a></li>')
            html_parts.append('</ul>')
            html_parts.append('</li>')
        
        html_parts.append('</ul>')
        html_parts.append('</div>')
        
        # Functions section
        if module.functions:
            html_parts.append('<h2 id="functions">Functions</h2>')
            for func in module.functions:
                html_parts.extend(HTMLGenerator._generate_function_html(func))
        
        # Classes section
        if module.classes:
            html_parts.append('<h2 id="classes">Classes</h2>')
            for cls in module.classes:
                html_parts.extend(HTMLGenerator._generate_class_html(cls))
        
        # Module variables
        if module.variables:
            html_parts.append('<h2>Module Variables</h2>')
            html_parts.append('<table>')
            html_parts.append('<tr><th>Name</th><th>Type</th><th>Default</th></tr>')
            for var in module.variables:
                type_str = var.type_hint or "-"
                default_str = f"<code>{var.default_value}</code>" if var.default_value else "-"
                html_parts.append(f'<tr><td><code>{var.name}</code></td><td>{type_str}</td><td>{default_str}</td></tr>')
            html_parts.append('</table>')
        
        # Footer
        html_parts.append('<hr class="divider">')
        html_parts.append(f'<p style="text-align: center; color: #95a5a6;">Generated by APIDoc Forge v{__version__}</p>')
        
        html_parts.extend([
            "</div>",
            "</body>",
            "</html>"
        ])
        
        return '\n'.join(html_parts)
    
    @staticmethod
    def _generate_function_html(func: FunctionDoc) -> List[str]:
        """Generate HTML for a function."""
        anchor = func.name.lower().replace('_', '-')
        parts = [f'<h3 id="{anchor}">{func.name}</h3>']
        
        # Signature
        prefix = "async " if func.is_async else ""
        params_str = ", ".join(
            HTMLGenerator._format_param_html(p) for p in func.parameters
        )
        
        parts.append('<div class="function-sig">')
        parts.append(f'<span class="keyword">{prefix}def</span> ')
        parts.append(f'<span class="function">{func.name}</span>({params_str})')
        parts.append('</div>')
        
        # Description
        if func.docstring:
            parts.append(f'<div class="docstring">{func.docstring}</div>')
        
        # Parameters
        if func.parameters:
            parts.append('<div class="section">')
            parts.append('<div class="section-title">Parameters:</div>')
            parts.append('<div class="param-list">')
            for param in func.parameters:
                parts.append('<div class="param-item">')
                parts.append(f'<span class="param-name">{param.name}</span>')
                if param.type_hint:
                    parts.append(f' <span class="param-type">({param.type_hint})</span>')
                if param.default_value:
                    parts.append(f' <span class="param-default">= {param.default_value}</span>')
                if param.description:
                    parts.append(f' - {param.description}')
                parts.append('</div>')
            parts.append('</div>')
            parts.append('</div>')
        
        # Returns
        if func.returns.type_hint or func.returns.description:
            parts.append('<div class="section">')
            parts.append('<div class="section-title">Returns:</div>')
            if func.returns.type_hint:
                parts.append(f'<span class="param-type">{func.returns.type_hint}</span><br>')
            if func.returns.description:
                parts.append(func.returns.description)
            parts.append('</div>')
        
        # Source
        parts.append(f'<div class="source-link">Source: {func.source_file}:{func.line_number}</div>')
        parts.append('<hr class="divider">')
        
        return parts
    
    @staticmethod
    def _generate_class_html(cls: ClassDoc) -> List[str]:
        """Generate HTML for a class."""
        anchor = cls.name.lower().replace('_', '-')
        parts = [f'<h3 id="{anchor}">{cls.name}</h3>']
        
        # Signature
        bases_str = f"({', '.join(cls.bases)})" if cls.bases else ""
        parts.append('<div class="function-sig">')
        parts.append(f'<span class="keyword">class</span> ')
        parts.append(f'<span class="class">{cls.name}</span>{bases_str}')
        parts.append('</div>')
        
        # Description
        if cls.docstring:
            parts.append(f'<div class="docstring">{cls.docstring}</div>')
        
        # Attributes
        if cls.attributes:
            parts.append('<div class="section">')
            parts.append('<div class="section-title">Attributes:</div>')
            parts.append('<div class="param-list">')
            for attr in cls.attributes:
                parts.append('<div class="param-item">')
                parts.append(f'<span class="param-name">{attr.name}</span>')
                if attr.type_hint:
                    parts.append(f' <span class="param-type">({attr.type_hint})</span>')
                if attr.default_value:
                    parts.append(f' <span class="param-default">= {attr.default_value}</span>')
                parts.append('</div>')
            parts.append('</div>')
            parts.append('</div>')
        
        # Methods summary
        if cls.methods:
            parts.append('<div class="section">')
            parts.append('<div class="section-title">Methods:</div>')
            parts.append('<ul>')
            for method in cls.methods:
                prefix = "async " if method.is_async else ""
                parts.append(f'<li><code>{prefix}{method.name}()</code></li>')
            parts.append('</ul>')
            parts.append('</div>')
        
        # Source
        parts.append(f'<div class="source-link">Source: {cls.source_file}:{cls.line_number}</div>')
        parts.append('<hr class="divider">')
        
        return parts
    
    @staticmethod
    def _format_param_html(param: Parameter) -> str:
        """Format parameter for HTML signature."""
        if param.name.startswith('*') or param.name.startswith('**'):
            return f'<span class="param">{param.name}</span>'
        
        result = f'<span class="param">{param.name}</span>'
        if param.type_hint:
            result += f'<span class="type">: {param.type_hint}</span>'
        if param.default_value:
            result += f' = {param.default_value}'
        return result


class OpenAPIGenerator:
    """Generates OpenAPI/Swagger specification."""
    
    @staticmethod
    def generate(modules: List[ModuleDoc], title: str = "API", version: str = "1.0.0") -> Dict[str, Any]:
        """Generate OpenAPI 3.0 specification."""
        spec = {
            "openapi": "3.0.0",
            "info": {
                "title": title,
                "version": version,
                "description": "Auto-generated API documentation"
            },
            "paths": {},
            "components": {
                "schemas": {}
            }
        }
        
        for module in modules:
            # Add schemas for classes
            for cls in module.classes:
                schema = OpenAPIGenerator._class_to_schema(cls)
                spec["components"]["schemas"][cls.name] = schema
            
            # Add paths for functions (if they look like API endpoints)
            for func in module.functions:
                if OpenAPIGenerator._is_endpoint(func):
                    path = OpenAPIGenerator._function_to_path(func)
                    spec["paths"][f"/api/{func.name}"] = path
        
        return spec
    
    @staticmethod
    def _class_to_schema(cls: ClassDoc) -> Dict[str, Any]:
        """Convert class to OpenAPI schema."""
        properties = {}
        required = []
        
        for attr in cls.attributes:
            prop = {}
            if attr.type_hint:
                prop["type"] = OpenAPIGenerator._python_type_to_openapi(attr.type_hint)
            if attr.default_value is None:
                required.append(attr.name)
            properties[attr.name] = prop
        
        return {
            "type": "object",
            "properties": properties,
            "required": required
        }
    
    @staticmethod
    def _function_to_path(func: FunctionDoc) -> Dict[str, Any]:
        """Convert function to OpenAPI path."""
        parameters = []
        
        for param in func.parameters:
            if not param.name.startswith('*'):
                param_spec = {
                    "name": param.name,
                    "in": "query",
                    "schema": {"type": "string"}
                }
                if param.type_hint:
                    param_spec["schema"]["type"] = OpenAPIGenerator._python_type_to_openapi(param.type_hint)
                if param.description:
                    param_spec["description"] = param.description
                parameters.append(param_spec)
        
        return {
            "get": {
                "summary": func.docstring.split('\n')[0] if func.docstring else func.name,
                "description": func.docstring,
                "parameters": parameters,
                "responses": {
                    "200": {
                        "description": "Success",
                        "content": {
                            "application/json": {
                                "schema": {"type": "object"}
                            }
                        }
                    }
                }
            }
        }
    
    @staticmethod
    def _is_endpoint(func: FunctionDoc) -> bool:
        """Check if function looks like an API endpoint."""
        endpoint_decorators = ['route', 'get', 'post', 'put', 'delete', 'patch']
        return any(d in dec for dec in func.decorators for d in endpoint_decorators)
    
    @staticmethod
    def _python_type_to_openapi(py_type: str) -> str:
        """Convert Python type to OpenAPI type."""
        type_map = {
            'str': 'string',
            'int': 'integer',
            'float': 'number',
            'bool': 'boolean',
            'list': 'array',
            'dict': 'object',
            'None': 'null'
        }
        return type_map.get(py_type, 'string')


class APIDocForge:
    """Main class for API documentation generation."""
    
    def __init__(self):
        self.modules: List[ModuleDoc] = []
    
    def analyze_file(self, file_path: str) -> Optional[ModuleDoc]:
        """Analyze a single Python file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            tree = ast.parse(source)
            analyzer = ASTAnalyzer(file_path)
            analyzer.visit(tree)
            
            return analyzer.module
        except SyntaxError as e:
            print(f"Syntax error in {file_path}: {e}")
            return None
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
            return None
    
    def analyze_directory(self, directory: str, pattern: str = "*.py") -> List[ModuleDoc]:
        """Analyze all Python files in a directory."""
        modules = []
        path = Path(directory)
        
        for file_path in path.rglob(pattern):
            # Skip hidden directories and common non-source directories
            if any(part.startswith('.') or part in ('__pycache__', 'venv', 'env', 'node_modules') 
                   for part in file_path.parts):
                continue
            
            module = self.analyze_file(str(file_path))
            if module:
                modules.append(module)
                self.modules.append(module)
        
        return modules
    
    def generate_documentation(self, output_dir: str, format: DocFormat = DocFormat.MARKDOWN,
                               title: Optional[str] = None) -> None:
        """Generate documentation in specified format."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        if format == DocFormat.MARKDOWN:
            self._generate_markdown_docs(output_path, title)
        elif format == DocFormat.HTML:
            self._generate_html_docs(output_path, title)
        elif format == DocFormat.JSON:
            self._generate_json_docs(output_path)
        elif format == DocFormat.OPENAPI:
            self._generate_openapi_docs(output_path, title)
    
    def _generate_markdown_docs(self, output_path: Path, title: Optional[str] = None) -> None:
        """Generate Markdown documentation."""
        # Generate index file
        index_lines = [f"# {title or 'API Documentation'}", ""]
        index_lines.append("## Modules")
        index_lines.append("")
        
        for module in self.modules:
            doc_content = MarkdownGenerator.generate(module)
            output_file = output_path / f"{module.name}.md"
            output_file.write_text(doc_content, encoding='utf-8')
            
            index_lines.append(f"- [{module.name}]({module.name}.md) - {module.source_file}")
        
        # Write index
        (output_path / "README.md").write_text('\n'.join(index_lines), encoding='utf-8')
        print(f"Generated Markdown documentation in {output_path}")
    
    def _generate_html_docs(self, output_path: Path, title: Optional[str] = None) -> None:
        """Generate HTML documentation."""
        for module in self.modules:
            doc_content = HTMLGenerator.generate(module, title)
            output_file = output_path / f"{module.name}.html"
            output_file.write_text(doc_content, encoding='utf-8')
        
        # Generate index
        index_html = HTMLGenerator.generate(self.modules[0] if self.modules else ModuleDoc(name="index"), title)
        (output_path / "index.html").write_text(index_html, encoding='utf-8')
        print(f"Generated HTML documentation in {output_path}")
    
    def _generate_json_docs(self, output_path: Path) -> None:
        """Generate JSON documentation."""
        data = {
            "generated_at": datetime.now().isoformat(),
            "modules": [m.to_dict() for m in self.modules]
        }
        
        output_file = output_path / "api_documentation.json"
        output_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
        print(f"Generated JSON documentation: {output_file}")
    
    def _generate_openapi_docs(self, output_path: Path, title: Optional[str] = None) -> None:
        """Generate OpenAPI specification."""
        spec = OpenAPIGenerator.generate(self.modules, title or "API")
        
        output_file = output_path / "openapi.json"
        output_file.write_text(json.dumps(spec, indent=2, ensure_ascii=False), encoding='utf-8')
        print(f"Generated OpenAPI specification: {output_file}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="APIDoc Forge - Intelligent API Documentation Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s analyze ./src -o ./docs
  %(prog)s analyze ./src -o ./docs -f html
  %(prog)s analyze ./src -o ./docs -f openapi --title "My API"
        """
    )
    
    parser.add_argument("command", choices=["analyze", "version"],
                       help="Command to execute")
    parser.add_argument("path", nargs="?", help="Path to Python file or directory")
    parser.add_argument("-o", "--output", default="./docs",
                       help="Output directory for documentation (default: ./docs)")
    parser.add_argument("-f", "--format", choices=["markdown", "html", "json", "openapi"],
                       default="markdown", help="Output format (default: markdown)")
    parser.add_argument("--title", help="Documentation title")
    parser.add_argument("--pattern", default="*.py",
                       help="File pattern for directory analysis (default: *.py)")
    parser.add_argument("-v", "--verbose", action="store_true",
                       help="Verbose output")
    
    args = parser.parse_args()
    
    if args.command == "version":
        print(f"APIDoc Forge v{__version__}")
        return
    
    if not args.path:
        parser.error("Path is required for analyze command")
    
    if not os.path.exists(args.path):
        print(f"Error: Path not found: {args.path}")
        sys.exit(1)
    
    # Initialize forge
    forge = APIDocForge()
    
    # Analyze
    if os.path.isfile(args.path):
        if args.verbose:
            print(f"Analyzing file: {args.path}")
        module = forge.analyze_file(args.path)
        if module:
            forge.modules.append(module)
    else:
        if args.verbose:
            print(f"Analyzing directory: {args.path}")
        forge.analyze_directory(args.path, args.pattern)
    
    if not forge.modules:
        print("No modules found to document.")
        sys.exit(1)
    
    if args.verbose:
        print(f"Found {len(forge.modules)} module(s)")
    
    # Generate documentation
    format_map = {
        "markdown": DocFormat.MARKDOWN,
        "html": DocFormat.HTML,
        "json": DocFormat.JSON,
        "openapi": DocFormat.OPENAPI
    }
    
    doc_format = format_map[args.format]
    forge.generate_documentation(args.output, doc_format, args.title)
    
    print(f"✅ Documentation generated successfully in {args.output}")


if __name__ == "__main__":
    main()
