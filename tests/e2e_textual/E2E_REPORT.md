# E2E Test Report - Juan-Dev-Code

**Generated:** 2025-11-27T08:27:07.125128

## Summary

| Metric | Value |
|--------|-------|
| Total Tests | 32 |
| Passed | 32 |
| Failed | 0 |
| Errors | 0 |
| Pass Rate | 100.0% |
| Duration | 0.10s |

## Test Results

### ✅ create_fastapi_app

- **Status:** passed
- **Duration:** 0.02s

**Details:**
```json
{
  "project_type": "FastAPI",
  "path": "/tmp/jdev_e2e_njpxgt8w",
  "files_created": [
    "main.py",
    "tests/test_api.py",
    "requirements.txt",
    "README.md"
  ],
  "total_files": 4,
  "success": true
}
```

---

### ✅ create_cli_tool

- **Status:** passed
- **Duration:** 0.00s

**Details:**
```json
{
  "project_type": "CLI Tool",
  "lines_of_code": 51
}
```

---

### ✅ create_python_package

- **Status:** passed
- **Duration:** 0.00s

**Details:**
```json
{
  "project_type": "Python Package",
  "files_created": 6,
  "package_structure": [
    "mypackage/__init__.py",
    "mypackage/core/engine.py",
    "mypackage/core/__init__.py",
    "mypackage/utils/helpers.py",
    "mypackage/utils/__init__.py",
    "pyproject.toml"
  ]
}
```

---

### ✅ create_microservice

- **Status:** passed
- **Duration:** 0.00s

**Details:**
```json
{
  "project_type": "Microservice",
  "files_created": 10,
  "has_docker": true,
  "has_tests_dir": true
}
```

---

### ✅ detect_hardcoded_secrets

- **Status:** passed
- **Duration:** 0.01s

**Details:**
```json
{
  "audit_type": "secrets",
  "patterns_checked": 5,
  "findings": 2,
  "severity_breakdown": {
    "HIGH": 2
  }
}
```

---

### ✅ detect_security_vulnerabilities

- **Status:** passed
- **Duration:** 0.02s

**Details:**
```json
{
  "audit_type": "vulnerabilities",
  "vulnerabilities_found": 1,
  "by_severity": {
    "HIGH": 1
  }
}
```

---

### ✅ detect_code_smells

- **Status:** passed
- **Duration:** 0.00s

**Details:**
```json
{
  "audit_type": "code_quality",
  "smells_found": 1,
  "smell_types": [
    "Deep Nesting"
  ]
}
```

---

### ✅ check_test_coverage

- **Status:** passed
- **Duration:** 0.00s

**Details:**
```json
{
  "audit_type": "coverage",
  "source_files": 3,
  "test_files": 2,
  "source_functions": 0,
  "test_functions": 0,
  "coverage_ratio": "0.0%"
}
```

---

### ✅ license_compliance

- **Status:** passed
- **Duration:** 0.00s

**Details:**
```json
{
  "audit_type": "license",
  "has_license": true,
  "project_license": "MIT",
  "dependency_licenses": {
    "MIT": 7,
    "BSD": 2,
    "Apache": 0,
    "GPL": 0
  }
}
```

---

### ✅ documentation_audit

- **Status:** passed
- **Duration:** 0.01s

**Details:**
```json
{
  "audit_type": "documentation",
  "has_readme": true,
  "docstrings": 0,
  "typed_functions": 0,
  "doc_score": 30
}
```

---

### ✅ search_read_edit_workflow

- **Status:** passed
- **Duration:** 0.00s

**Details:**
```json
{
  "workflow": "search_read_edit",
  "tools_used": 3,
  "bugs_found": 4,
  "bugs_fixed": 1
}
```

---

### ✅ create_test_run_workflow

- **Status:** passed
- **Duration:** 0.00s

**Details:**
```json
{
  "workflow": "create_test_verify",
  "tools_used": 3,
  "files_created": 2,
  "test_count": 5
}
```

---

### ✅ git_workflow

- **Status:** passed
- **Duration:** 0.01s

**Details:**
```json
{
  "workflow": "git_operations",
  "tools_used": 4,
  "files_modified": 0,
  "has_diff": true
}
```

---

### ✅ full_feature_implementation

- **Status:** passed
- **Duration:** 0.00s

**Details:**
```json
{
  "scenario": "feature_implementation",
  "phases_completed": 4,
  "files_created": 4,
  "feature": "User Authentication"
}
```

---

### ✅ codebase_analysis_and_fix

- **Status:** passed
- **Duration:** 0.01s

**Details:**
```json
{
  "scenario": "analysis_and_fix",
  "issues_found": [
    {
      "type": "hardcoded_secret",
      "count": 1
    },
    {
      "type": "marked_bugs",
      "count": 3
    }
  ],
  "issues_fixed": [
    "hardcoded_secret"
  ]
}
```

---

### ✅ enter_exit_plan_mode

- **Status:** passed
- **Duration:** 0.00s

**Details:**
```json
{
  "test_type": "plan_mode_lifecycle",
  "plan_file": "/tmp/jdev_e2e_2to01nzu/.jdev/plans/test_plan.md",
  "plan_size": 1172
}
```

---

### ✅ create_architecture_plan

- **Status:** passed
- **Duration:** 0.00s

**Details:**
```json
{
  "test_type": "architecture",
  "sections": [
    "Overview",
    "System Components",
    "Data Flow",
    "Security",
    "Scalability",
    "Monitoring"
  ],
  "components": 5
}
```

---

### ✅ create_implementation_checklist

- **Status:** passed
- **Duration:** 0.00s

**Details:**
```json
{
  "test_type": "checklist",
  "total_tasks": 35,
  "completed_tasks": 12,
  "phases": 7
}
```

---

### ✅ architect_analyzes_requirements

- **Status:** passed
- **Duration:** 0.00s

**Details:**
```json
{
  "agent": "architect",
  "user_stories": 4,
  "estimated_weeks": 8
}
```

---

### ✅ write_and_read_file

- **Status:** passed
- **Duration:** 0.00s

**Details:**
```json
{
  "tools": [
    "WriteFileTool",
    "ReadFileTool"
  ],
  "file_size": 173,
  "lines": 9
}
```

---

### ✅ edit_file

- **Status:** passed
- **Duration:** 0.00s

**Details:**
```json
{
  "tools": [
    "WriteFileTool",
    "EditFileTool",
    "ReadFileTool"
  ],
  "changes": 1
}
```

---

### ✅ search_in_files

- **Status:** passed
- **Duration:** 0.00s

**Details:**
```json
{
  "tools": [
    "SearchFilesTool"
  ],
  "matches_found": 8
}
```

---

### ✅ search_for_bugs

- **Status:** passed
- **Duration:** 0.00s

**Details:**
```json
{
  "tools": [
    "SearchFilesTool"
  ],
  "bugs_found": 4
}
```

---

### ✅ create_python_module

- **Status:** passed
- **Duration:** 0.00s

**Details:**
```json
{
  "project_type": "python_module",
  "files_created": 7
}
```

---

### ✅ git_status

- **Status:** passed
- **Duration:** 0.01s

**Details:**
```json
{
  "tools": [
    "GitStatusTool"
  ],
  "status_data": "{'branch': 'main', 'modified': ['jdev_cli/core/context_tracker.py', 'jdev_cli/core/error_presenter.py', 'jdev_cli/core/execution.py', 'jdev_cli/core/input_enhancer.py', 'jdev_cli/core/input_validator."
}
```

---

### ✅ plan_mode_cycle

- **Status:** passed
- **Duration:** 0.00s

**Details:**
```json
{
  "tools": [
    "EnterPlanModeTool",
    "ExitPlanModeTool"
  ],
  "plan_file": "/tmp/jdev_e2e_niexhw4e/.jdev/plans/e2e_plan.md"
}
```

---

### ✅ search_and_fix_workflow

- **Status:** passed
- **Duration:** 0.00s

**Details:**
```json
{
  "workflow": "search_fix",
  "tools": 3,
  "fixed": true,
  "issues_found": 3
}
```

---

### ✅ add_type_hints

- **Status:** passed
- **Duration:** 0.00s

**Details:**
```json
{
  "refactor_type": "type_hints",
  "type_hints_added": 8
}
```

---

### ✅ extract_function

- **Status:** passed
- **Duration:** 0.00s

**Details:**
```json
{
  "refactor_type": "extract_function",
  "lines_before": 35,
  "lines_after": 37,
  "reduction_percent": 13.0
}
```

---

### ✅ fix_security_issues

- **Status:** passed
- **Duration:** 0.00s

**Details:**
```json
{
  "refactor_type": "security_fix",
  "issues_fixed": [
    "hardcoded_secret",
    "missing_validation"
  ]
}
```

---

### ✅ add_error_handling

- **Status:** passed
- **Duration:** 0.00s

**Details:**
```json
{
  "refactor_type": "error_handling",
  "bugs_fixed": 2
}
```

---

### ✅ rename_across_files

- **Status:** passed
- **Duration:** 0.00s

**Details:**
```json
{
  "refactor_type": "rename",
  "files_modified": 2
}
```

---

