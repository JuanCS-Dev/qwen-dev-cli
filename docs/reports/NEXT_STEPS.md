# Próximos Passos - Git Clone no Notebook

## Situação Atual

✅ Repositório completamente organizado
✅ API keys protegidas
✅ Estrutura limpa e profissional
✅ Pronto para sincronizar com GitHub

---

## Passo 1: Commit e Push (Neste Computador)

```bash
# 1. Verificar mudanças
git status

# 2. Adicionar todas as mudanças
git add .

# 3. Commit com mensagem descritiva
git commit -m "chore: organize repository structure and protect sensitive data

- Move documentation to docs/ directory
- Organize tests into tests/ directory
- Archive old files in .backup/ (git-ignored)
- Update .gitignore with comprehensive security patterns
- Create detailed .env.example template
- Add SECURITY.md with key management guidelines
- Clean up root directory for better organization
"

# 4. Push para o GitHub
git push origin main
```

---

## Passo 2: Clone no Notebook

```bash
# 1. Clone o repositório
cd ~/projects  # ou onde você quiser
git clone <URL-DO-SEU-REPO> qwen-dev-cli
cd qwen-dev-cli

# 2. Verificar estrutura
ls -la
# Você verá: docs/, tests/, qwen_dev_cli/, etc.
# Você NÃO verá: .backup/ (ignorado), .env (local)

# 3. Criar ambiente
cp .env.example .env

# 4. Editar com suas keys
nano .env
# Ou: code .env
# Ou: vim .env

# Adicione suas keys:
# GEMINI_API_KEY=AIzaSy...
# NEBIUS_API_KEY=v1.CmQ...
# HF_TOKEN=hf_my...

# 5. Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou: venv\Scripts\activate  # Windows

# 6. Instalar dependências
pip install -e .

# 7. Testar
qwen shell
```

---

## Passo 3: Verificação de Segurança

```bash
# Verificar que .env não está rastreado
git check-ignore .env
# Deve retornar: .env

# Verificar status
git status
# .env NÃO deve aparecer na lista

# Verificar arquivos rastreados
git ls-files | grep .env
# Deve retornar apenas: .env.example
```

---

## Estrutura que Será Clonada

```
✅ Arquivos Incluídos:
   - Código fonte (qwen_dev_cli/)
   - Testes (tests/)
   - Documentação (docs/)
   - Scripts (scripts/)
   - Configurações (pyproject.toml, requirements.txt)
   - .env.example (template)
   - .gitignore (proteção)

❌ Arquivos Excluídos (ficam locais):
   - .env (suas keys)
   - .backup/ (arquivos antigos)
   - venv/ (ambiente virtual)
   - __pycache__/ (cache Python)
   - *.log (logs)
   - .coverage* (relatórios)
```

---

## Troubleshooting

### Problema: .env aparece no git status

```bash
# Solução: Garantir que está no .gitignore
echo ".env" >> .gitignore
git rm --cached .env  # Remove do index
git commit -m "fix: ensure .env is ignored"
```

### Problema: API key não funciona no notebook

```bash
# Verificar o arquivo
cat .env | grep API_KEY

# Verificar formato (sem espaços, sem aspas extras)
# Correto:   GEMINI_API_KEY=AIzaSy...
# Incorreto: GEMINI_API_KEY = "AIzaSy..."
```

### Problema: Import error

```bash
# Reinstalar em modo desenvolvimento
pip install -e .

# Verificar instalação
pip list | grep qwen
```

---

## Arquivos Importantes Criados

1. **SECURITY.md** - Guia completo de segurança
2. **ORGANIZATION_SUMMARY.md** - Resumo das mudanças
3. **FINAL_SECURITY_REPORT.md** - Relatório de auditoria
4. **.env.example** - Template detalhado
5. **docs/README.md** - Índice da documentação

---

## Checklist Final

Antes de fazer push:

- [ ] Verificou que .env não está no git: `git status`
- [ ] .gitignore está atualizado: `cat .gitignore | grep .env`
- [ ] .env.example não tem keys reais: `cat .env.example`
- [ ] Testes funcionando: `pytest`
- [ ] README.md atualizado

Depois do clone no notebook:

- [ ] Clonou o repositório
- [ ] Criou .env a partir do .env.example
- [ ] Adicionou suas API keys
- [ ] Instalou dependências: `pip install -e .`
- [ ] Testou: `qwen shell`
- [ ] Verificou que .env está ignorado

---

## Sincronização Futura

Sempre que fizer mudanças:

```bash
# Máquina 1
git add .
git commit -m "feat: minha feature"
git push

# Máquina 2 (notebook)
git pull
pip install -e .  # se requirements.txt mudou
```

**Lembre-se**: `.env` sempre fica local em cada máquina!

---

✅ Tudo pronto! Pode fazer push com segurança.
