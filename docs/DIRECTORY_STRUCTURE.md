# 📁 Qwen Dev CLI - Enterprise Directory Structure

**Last Updated:** 2025-11-21  
**Standard:** Enterprise-Grade Organization  
**Principle:** Everything in its place, nothing misplaced.

---

## 🏗️ Root Level (Sacred Ground)

```
qwen-dev-cli/
├── README.md                    # Main project documentation
├── CHANGELOG.md                 # Version history
├── GEMINI.md                    # Operational doctrine
├── RELEASE_NOTES_v0.2.0.md     # Current release notes
├── TEST_RESULTS.md              # Test suite summary
├── pyproject.toml               # Python project config
├── pytest.ini                   # Pytest configuration
├── requirements.txt             # Dependencies
└── .gitignore                   # Git exclusions
```

**Rules:**
- ❌ NO random markdown files
- ❌ NO test scripts  
- ❌ NO backup files
- ✅ ONLY essential project files

---

## 📚 `/docs` - Documentation Hub

### **`/docs/architecture/`** - System Design
```
architecture/
├── CONTEXTO_SISTEMICO.md       # System context
├── PROJECT_STRUCTURE.md        # Codebase organization
├── DESIGN_DECISIONS.md         # ADRs (Architecture Decision Records)
└── diagrams/                   # Architecture diagrams
```

### **`/docs/guides/`** - How-To Documentation
```
guides/
├── GRADIO_6_MIGRATION.md       # Gradio 6 upgrade guide
├── BASH_HARDENING.md           # Bash execution security
├── SECURITY_BEST_PRACTICES.md  # Security guidelines
├── API_KEYS_MANAGEMENT.md      # Credentials handling
└── DEPLOYMENT_GUIDE.md         # Deployment procedures
```

### **`/docs/reports/`** - Historical Records

#### **`/docs/reports/daily/`** - Day-by-Day Progress
```
daily/
├── DAY1_SCIENTIFIC_VALIDATION_REPORT.md
├── DAY2_INTEGRATION_COMPLETE.md
├── DAY3_BASH_HARDENING.md
├── DAY4_GRADIO_MIGRATION.md
├── DAY5_SANDBOX_FINAL_REPORT.md
└── DAY6_HOOKS_IMPLEMENTATION.md
```

#### **`/docs/reports/audit/`** - Quality Audits
```
audit/
├── BRUTAL_AUDIT_REPORT.md
├── BORIS_AUDIT_REPORT_CLI_POLISH.md
├── EMERGENCY_FIX_PLAN.md
└── AUDIT_REPORT_DAY*.md
```

#### **`/docs/reports/boris-sessions/`** - Expert Reviews
```
boris-sessions/
├── BORIS_CHERNY_IMPLEMENTATION_REPORT.md
├── BORIS_CHERNY_SESSION_REPORT.md
└── BORIS_CODE_REVIEW_*.md
```

#### **`/docs/reports/weekly/`** - Weekly Summaries
```
weekly/
├── WEEK1_SUMMARY.md
├── WEEK2_PROGRESS.md
└── WEEK3_FINAL_SPRINT.md
```

### **`/docs/rfcs/`** - Request for Comments
```
rfcs/
├── RFC001_CONSTITUTIONAL_AI.md
├── RFC002_MCP_INTEGRATION.md
└── RFC003_SKILLS_SYSTEM.md
```

---

## 🔧 `/scripts` - Automation Tools

```
scripts/
├── deployment/
│   ├── deploy_hf_spaces.sh     # HuggingFace deployment
│   ├── docker_build.sh         # Container builds
│   └── health_check.sh         # Service monitoring
├── maintenance/
│   ├── cleanup_logs.sh         # Log rotation
│   ├── backup_config.sh        # Config backups
│   └── update_deps.sh          # Dependency updates
└── testing/
    ├── run_full_suite.sh       # All tests
    ├── benchmark.sh            # Performance tests
    └── validate_config.sh      # Config validation
```

---

## 🧪 `/tests` - Test Suite

```
tests/
├── unit/                       # Unit tests
│   ├── test_bash_commands.py
│   ├── test_constitutional_ai.py
│   └── test_mcp_tools.py
├── integration/                # Integration tests
│   ├── test_cli_integration.py
│   ├── test_shell_integration.py
│   └── test_gradio_ui.py
├── e2e/                        # End-to-end tests
│   ├── test_full_workflow.py
│   └── test_dogfooding.py
├── fixtures/                   # Test data
└── conftest.py                 # Pytest config
```

---

## ⚙️ `/config` - Configuration Files

```
config/
├── environments/
│   ├── development.env
│   ├── staging.env
│   └── production.env
├── themes/
│   ├── terminal_dark.json      # Gradio themes
│   └── hacker_green.json
└── model_configs/
    ├── qwen_default.json
    └── gemini_flash.json
```

---

## 🎨 `/gradio_ui` - Web Interface

```
gradio_ui/
├── __init__.py
├── app.py                      # Main Gradio app
├── components/                 # UI components
│   ├── chat_interface.py
│   ├── file_explorer.py
│   └── metrics_dashboard.py
├── styles/
│   ├── custom.css
│   └── themes.py
└── assets/
    ├── logo.svg
    └── screenshots/
```

---

## 📦 `/qwen_dev_cli` - Core Package

```
qwen_dev_cli/
├── __init__.py
├── __main__.py                 # Entry point
├── cli/                        # CLI interface
│   ├── commands.py
│   ├── repl.py
│   └── parser.py
├── core/                       # Core logic
│   ├── llm_engine.py
│   ├── constitutional_ai.py
│   └── skills_system.py
├── mcp_tools/                  # MCP integration
│   ├── bash_commands.py
│   ├── file_operations.py
│   └── search_tools.py
├── shell/                      # Shell mode
│   ├── interactive.py
│   └── history.py
└── utils/                      # Utilities
    ├── logging.py
    ├── config.py
    └── validators.py
```

---

## 🗄️ `/.archive` - Historical Artifacts

```
.archive/
├── backups/                    # Old backups
│   ├── requirements.txt.backup
│   └── gradio_ui.backup.*
├── deprecated/                 # Deprecated code
│   └── old_implementations/
└── old-configs/                # Legacy configs
    └── v1_configs/
```

**Rules:**
- ⏱️ Auto-cleanup after 90 days
- 🔒 Read-only access
- 📝 Requires ARCHIVE.md manifest

---

## 🚫 `.gitignore` Categories

```
# Python
__pycache__/
*.py[cod]
*.egg-info/
venv/

# IDE
.vscode/
.idea/
*.swp

# Logs
*.log
logs/

# Secrets
.env
*.key
secrets/

# Build
dist/
build/

# Test artifacts
.pytest_cache/
.coverage
htmlcov/

# Temporary
*.tmp
*.bak
uploads/
test_screenshots/
```

---

## 📋 Maintenance Checklist

### Weekly
- [ ] Review `docs/reports/daily/` - Archive old reports
- [ ] Check `.archive/` size - Cleanup if > 100MB
- [ ] Validate all symlinks still valid
- [ ] Update DIRECTORY_STRUCTURE.md if changes made

### Monthly
- [ ] Audit root directory - Must stay clean
- [ ] Review deprecated code - Remove if unused
- [ ] Compress old logs
- [ ] Update documentation index

### Pre-Release
- [ ] All reports moved to docs/
- [ ] No test files in root
- [ ] No backup files anywhere
- [ ] README.md is up-to-date
- [ ] CHANGELOG.md has latest entries

---

## 🎯 Directory Philosophy

### **"A Place for Everything, Everything in its Place"**

1. **Root is Sacred** - Only essential project files
2. **Docs are History** - Everything documented and organized
3. **Tests are Separate** - Never pollute source with tests
4. **Scripts are Tools** - Automation in dedicated folder
5. **Archive is Morgue** - Old stuff goes to die gracefully

---

## 🔍 Quick Reference

| Need to find...           | Look in...                    |
|--------------------------|-------------------------------|
| Project overview         | `/README.md`                  |
| Daily progress           | `/docs/reports/daily/`        |
| Architecture decisions   | `/docs/architecture/`         |
| How-to guides            | `/docs/guides/`               |
| Test suite               | `/tests/`                     |
| Deployment scripts       | `/scripts/deployment/`        |
| Old code/configs         | `/.archive/`                  |
| UI components            | `/gradio_ui/components/`      |
| Core logic               | `/qwen_dev_cli/core/`         |

---

**Maintained by:** Vértice-MAXIMUS (Gemini-Native)  
**Standard:** Enterprise-Grade Organization  
**Compliance:** 100%  

*"Clean directories make happy developers."* 🧹✨
