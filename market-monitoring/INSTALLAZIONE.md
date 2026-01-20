# Guida per l'Installazione - Financial News Monitoring System

## Per chi riceve questo progetto

### Requisiti
- Python 3.8 o superiore
- Account Gmail (per invio email)
- Connessione Internet

### Setup Rapido (5 minuti)

#### 1. Estrai l'archivio
```bash
tar -xzf market-monitoring.tar.gz
cd market-monitoring
```

#### 2. Installa dipendenze
```bash
pip install -r requirements.txt
```

#### 3. Configura le tue credenziali email
```bash
cp .env.example .env
nano .env  # o usa qualsiasi editor di testo
```

**Compila nel file .env:**
```
EMAIL_TO=tua-email@gmail.com
SMTP_USER=tua-email@gmail.com
SMTP_PASSWORD=app-password-gmail
SKIP_EMAIL_SEND=false
```

**⚠️ Importante: Devi creare una App Password di Gmail**
1. Vai su https://myaccount.google.com/security
2. Abilita "Verifica in 2 passaggi"
3. Vai su https://myaccount.google.com/apppasswords
4. Crea password per "Mail"
5. Usa quella password (16 caratteri) in SMTP_PASSWORD

#### 4. Test del sistema
```bash
# Prima prova con dati di esempio
python test_populate.py
python generate_digest.py

# Apri il digest generato nel browser per vedere l'output
open output/digest_*.html  # macOS
# oppure apri manualmente il file HTML
```

#### 5. Esegui il monitoraggio
```bash
python monitor.py
```

Riceverai un'email con il digest delle news!

### Personalizzazione

#### Modificare Asset Class e Keywords
Modifica il file `config.py`:
```python
ASSET_CLASSES = {
    "TUA_ASSET_CLASS": {
        "name": "Nome Visualizzato",
        "keywords": ["keyword1", "keyword2"]
    }
}
```

#### Aggiungere Fondi Prioritari
In `config.py`:
```python
PRIORITY_FUNDS = [
    "Nome Fondo 1",
    "Nome Fondo 2"
]
```

#### Cambiare Soglie
In `config.py`:
```python
PRIORITY_DEAL_THRESHOLD = 500  # milioni USD
PRIORITY_FUND_CLOSE_THRESHOLD = 1000  # milioni USD
NEWS_LOOKBACK_HOURS = 24  # ore
```

### Automazione (Opzionale)

#### macOS/Linux - Esecuzione giornaliera alle 8:00
```bash
crontab -e
# Aggiungi questa riga:
0 8 * * * cd /percorso/completo/market-monitoring && python monitor.py
```

#### Windows - Task Scheduler
1. Apri "Utilità di pianificazione"
2. Crea attività di base
3. Imposta trigger: Giornaliera alle 8:00
4. Azione: Avvia programma
   - Programma: `python.exe`
   - Argomenti: `monitor.py`
   - Inizia in: percorso della cartella market-monitoring

### Risoluzione Problemi

**Non ricevo email?**
- Verifica di usare App Password di Gmail (non password normale)
- Controlla che SKIP_EMAIL_SEND=false in .env
- Verifica SMTP_USER sia il tuo indirizzo Gmail completo

**Errore "Module not found"?**
```bash
pip install -r requirements.txt
```

**Nessun articolo trovato?**
- È normale nei primi test (Google News può impiegare tempo)
- Prova con dati di esempio: `python test_populate.py`
- Controlla la tua connessione internet

### Supporto

Per domande o problemi:
1. Leggi il README.md completo
2. Leggi il QUICK_START.md per setup veloce
3. Controlla il file monitoring.log per errori dettagliati

### Asset Class Monitorate

Il sistema è configurato per monitorare:
- **CLO Equity**: CLOs, leveraged loans
- **Secondary Private Equity**: GP-led, continuation funds
- **Private Credit**: Direct lending, BDCs, unitranche
- **Infrastructure**: Energy transition, digital infrastructure
- **Continuation Funds**: Portfolio continuations

### Output

- **Email HTML**: Inviata al tuo indirizzo ogni esecuzione
- **File HTML**: Salvati in `output/` per consultazione offline
- **Database**: `market_monitoring.db` contiene storico articoli
- **Log**: `monitoring.log` per debugging

---

**Nota Sicurezza**: Non condividere mai il file `.env` con le tue credenziali!

---

Creato con Claude Code - Gennaio 2026
