#!/bin/bash
# Script per preparare il pacchetto di distribuzione

echo "📦 Preparazione pacchetto di distribuzione..."
echo ""

# Nome del pacchetto
PACKAGE_NAME="market-monitoring-v1.0"
DIST_DIR="dist"

# Crea directory di distribuzione
mkdir -p "$DIST_DIR"

# Pulisci file temporanei
echo "🧹 Pulizia file temporanei..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete
find . -type f -name "*.log" -delete
find . -type f -name "*.db" -delete
rm -f .env

echo "✓ Pulizia completata"
echo ""

# Crea archivio
echo "📦 Creazione archivio..."
cd ..
tar -czf "$PACKAGE_NAME.tar.gz" \
    --exclude="market-monitoring/__pycache__" \
    --exclude="market-monitoring/*.db" \
    --exclude="market-monitoring/*.log" \
    --exclude="market-monitoring/.env" \
    --exclude="market-monitoring/dist" \
    --exclude="market-monitoring/.git" \
    market-monitoring/

# Crea anche ZIP per Windows
zip -r "$PACKAGE_NAME.zip" market-monitoring/ \
    -x "market-monitoring/__pycache__/*" \
    -x "market-monitoring/*.db" \
    -x "market-monitoring/*.log" \
    -x "market-monitoring/.env" \
    -x "market-monitoring/dist/*" \
    -x "market-monitoring/.git/*" \
    > /dev/null 2>&1

mv "$PACKAGE_NAME.tar.gz" market-monitoring/dist/
mv "$PACKAGE_NAME.zip" market-monitoring/dist/ 2>/dev/null

cd market-monitoring

echo "✓ Archivi creati"
echo ""

# Mostra risultati
echo "✅ Pacchetto pronto per la distribuzione!"
echo ""
echo "📁 File creati in dist/:"
ls -lh dist/
echo ""
echo "📤 Puoi condividere questi file:"
echo "   • $PACKAGE_NAME.tar.gz (per macOS/Linux)"
echo "   • $PACKAGE_NAME.zip (per Windows)"
echo ""
echo "📝 Documenti inclusi:"
echo "   • README.md - Documentazione completa"
echo "   • QUICK_START.md - Setup rapido 5 minuti"
echo "   • INSTALLAZIONE.md - Guida per utenti finali"
echo "   • .env.example - Template configurazione"
echo ""
echo "🎉 Pronto per la condivisione!"
