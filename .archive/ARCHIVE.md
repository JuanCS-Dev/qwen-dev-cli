# 🗄️ Archive Manifest

**Purpose:** Historical artifacts, deprecated code, and backups  
**Retention Policy:** 90 days auto-cleanup  
**Access:** Read-only  

---

## 📦 Contents

### `/backups/` - Configuration & File Backups
- requirements.txt.backup (2025-11-20)
- gradio_ui.backup.* (multiple versions)

### `/deprecated/` - Obsolete Code
- Legacy implementations removed from main codebase
- Kept for reference/rollback purposes

### `/old-configs/` - Historical Configurations
- Version 1.x configs
- Pre-migration settings

---

## 🔄 Cleanup Schedule

**Automated cleanup runs monthly:**
```bash
# Files older than 90 days are automatically removed
find .archive/ -type f -mtime +90 -delete
```

**Manual review required for:**
- Large files (>10MB)
- Critical config backups
- Code snapshots

---

**Last Cleanup:** Never (just created)  
**Next Cleanup:** 2026-02-21
