#!/usr/bin/env bash
# Merge origin/Master into pilanomiweb y deja intacta la integración PILA de pilanomiweb.
# Uso (desde la raíz del repo, donde está este archivo):
#   chmod +x merge_master_keep_pila.sh
#   ./merge_master_keep_pila.sh
#
# Requisitos: working tree limpio (sin cambios sin commitear).

set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$REPO_ROOT"

echo "==> Fetch origin"
git fetch origin

CURRENT="$(git rev-parse --abbrev-ref HEAD)"
if [[ "$CURRENT" != "pilanomiweb" ]]; then
  echo "==> Cambiando a rama pilanomiweb (estabas en: $CURRENT)"
  git checkout pilanomiweb
fi

if [[ -n "$(git status --porcelain)" ]]; then
  echo "ERROR: Hay cambios sin commitear. Commitea o stash antes de continuar."
  git status -sb
  exit 1
fi

echo "==> Merge Master (sin commit todavía): origin/Master"
# --no-ff: siempre merge commit; ORIG_HEAD queda en el tip de pilanomiweb antes del merge.
if ! git merge origin/Master --no-commit --no-ff; then
  echo ""
  echo "Hay conflictos. Resuélvelos en archivos que NO sean PILA (apps/pila, liquidación, templates PILA, urls PILA)."
  echo "Luego ejecuta de nuevo desde el paso de 'checkout ORIG_HEAD' o continúa manualmente:"
  echo "  git checkout ORIG_HEAD -- apps/pila apps/payroll/views/liquidacion_pila.py \\"
  echo "    templates/payroll/vista_plano_pila.html templates/payroll/liquidacion_pila.html"
  echo "  # urls.py: revisar diff con Master antes de restaurar (ver comentario abajo)"
  echo "  git add -A && git commit -m \"Merge origin/Master into pilanomiweb; mantener integración PILA\""
  exit 1
fi

echo "==> Restaurar desde pilanomiweb (ORIG_HEAD) los paths de integración PILA"
git checkout ORIG_HEAD -- \
  apps/pila \
  apps/payroll/views/liquidacion_pila.py \
  templates/payroll/vista_plano_pila.html \
  templates/payroll/liquidacion_pila.html

# urls.py: en pilanomiweb suele convivir PILA + otras rutas. Restaurar todo desde ORIG_HEAD
# evita que Master pise rutas PILA, pero puede ocultar rutas nuevas solo en Master.
echo "==> apps/payroll/urls.py: restaurando versión pilanomiweb (revisa diff con Master si añadieron rutas)"
git checkout ORIG_HEAD -- apps/payroll/urls.py

echo "==> Staging y commit del merge"
git add -A
git status -sb
echo ""
echo "Revisa especialmente:"
echo "  - apps/payroll/urls.py  → si Master añadió rutas, fusiónalas a mano y vuelve a git add"
echo "  - templates/base/navbar_payroll.html  → si hubo cambios PILA en menú, comparar con Master"
echo ""
read -r -p "¿Confirmar commit del merge? [y/N] " ok
if [[ "${ok,,}" != "y" ]]; then
  echo "Abortado. Estado: merge en curso. Para deshacer: git merge --abort"
  exit 1
fi

git commit -m "Merge origin/Master into pilanomiweb; mantener integración PILA (apps/pila, liquidacion_pila, urls/templates PILA)"

echo "==> Listo. Último commit:"
git log -1 --oneline
