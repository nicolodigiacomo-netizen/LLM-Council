#!/usr/bin/env python3
"""Test della webapp per verificare funzionamento"""

import sys
import os
import time
import subprocess
import requests
from threading import Thread

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def start_server():
    """Avvia il server Flask in background"""
    os.environ['FLASK_ENV'] = 'testing'
    subprocess.run([sys.executable, 'app.py'],
                   stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL)

def test_webapp():
    """Testa le route principali della webapp"""
    base_url = "http://localhost:5000"

    # Aspetta che il server sia pronto
    print("⏳ Attendere avvio server...")
    time.sleep(3)

    tests_passed = 0
    tests_failed = 0

    # Test 1: Homepage redirect to login
    print("\n🧪 Test 1: Homepage (redirect a login)")
    try:
        r = requests.get(base_url, allow_redirects=False, timeout=5)
        if r.status_code in [302, 303]:  # Redirect
            print("   ✅ PASS - Redirect a login funziona")
            tests_passed += 1
        else:
            print(f"   ❌ FAIL - Status code: {r.status_code}")
            tests_failed += 1
    except Exception as e:
        print(f"   ❌ FAIL - Errore: {e}")
        tests_failed += 1

    # Test 2: Login page
    print("\n🧪 Test 2: Pagina di login")
    try:
        r = requests.get(f"{base_url}/login", timeout=5)
        if r.status_code == 200 and 'login' in r.text.lower():
            print("   ✅ PASS - Pagina login carica correttamente")
            tests_passed += 1
        else:
            print(f"   ❌ FAIL - Status: {r.status_code}")
            tests_failed += 1
    except Exception as e:
        print(f"   ❌ FAIL - Errore: {e}")
        tests_failed += 1

    # Test 3: Login con credenziali
    print("\n🧪 Test 3: Login con credenziali default")
    try:
        session = requests.Session()
        r = session.post(f"{base_url}/login",
                        data={'username': 'admin', 'password': 'admin123'},
                        timeout=5)
        if r.status_code in [200, 302, 303]:
            print("   ✅ PASS - Login accettato")
            tests_passed += 1

            # Test 4: Dashboard dopo login
            print("\n🧪 Test 4: Dashboard (autenticato)")
            r = session.get(base_url, timeout=5)
            if r.status_code == 200 and 'dashboard' in r.text.lower():
                print("   ✅ PASS - Dashboard accessibile")
                tests_passed += 1
            else:
                print(f"   ❌ FAIL - Dashboard non accessibile")
                tests_failed += 1

            # Test 5: Articles page
            print("\n🧪 Test 5: Pagina articoli")
            r = session.get(f"{base_url}/articles", timeout=5)
            if r.status_code == 200:
                print("   ✅ PASS - Pagina articoli carica")
                tests_passed += 1
            else:
                print(f"   ❌ FAIL - Status: {r.status_code}")
                tests_failed += 1

            # Test 6: Digests page
            print("\n🧪 Test 6: Pagina digests")
            r = session.get(f"{base_url}/digests", timeout=5)
            if r.status_code == 200:
                print("   ✅ PASS - Pagina digests carica")
                tests_passed += 1
            else:
                print(f"   ❌ FAIL - Status: {r.status_code}")
                tests_failed += 1

            # Test 7: Configuration page
            print("\n🧪 Test 7: Pagina configurazione")
            r = session.get(f"{base_url}/config", timeout=5)
            if r.status_code == 200:
                print("   ✅ PASS - Pagina config carica")
                tests_passed += 1
            else:
                print(f"   ❌ FAIL - Status: {r.status_code}")
                tests_failed += 1

            # Test 8: API Stats
            print("\n🧪 Test 8: API Statistics")
            r = session.get(f"{base_url}/api/stats", timeout=5)
            if r.status_code == 200:
                data = r.json()
                if 'total_articles' in data:
                    print(f"   ✅ PASS - API restituisce dati: {data.get('total_articles')} articoli")
                    tests_passed += 1
                else:
                    print("   ❌ FAIL - Dati API non validi")
                    tests_failed += 1
            else:
                print(f"   ❌ FAIL - Status: {r.status_code}")
                tests_failed += 1
        else:
            print(f"   ❌ FAIL - Login fallito: {r.status_code}")
            tests_failed += 1
    except Exception as e:
        print(f"   ❌ FAIL - Errore: {e}")
        tests_failed += 1

    # Risultati finali
    print("\n" + "="*60)
    print("📊 RISULTATI TEST")
    print("="*60)
    print(f"✅ Test passati: {tests_passed}")
    print(f"❌ Test falliti: {tests_failed}")
    print(f"📈 Percentuale successo: {(tests_passed/(tests_passed+tests_failed)*100):.1f}%")
    print("="*60)

    if tests_failed == 0:
        print("\n🎉 TUTTI I TEST PASSATI! Webapp funziona correttamente!")
    else:
        print(f"\n⚠️  Alcuni test falliti. Verifica i log sopra.")

if __name__ == "__main__":
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║        TEST AUTOMATICO WEB APPLICATION                         ║")
    print("╚════════════════════════════════════════════════════════════════╝")

    # Avvia server in thread separato
    print("\n🚀 Avvio server Flask...")
    server_thread = Thread(target=start_server, daemon=True)
    server_thread.start()

    # Esegui test
    test_webapp()
