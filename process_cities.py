#!/usr/bin/env python3
"""
Script per processare automaticamente tutte le città configurate
"""

import os
import subprocess
import sys
from cities_config import get_available_cities, get_city_config

def process_city(city_name: str):
    """Processa una singola città"""
    print(f"\n🏙️ Processing city: {city_name}")
    print("=" * 50)
    
    # Verifica che la configurazione della città esista
    city_config = get_city_config(city_name)
    if not city_config:
        print(f"❌ Configuration not found for city: {city_name}")
        return False
    
    # Verifica che il database ID sia configurato
    if not city_config.notion_database_id:
        print(f"❌ NOTION_DATABASE_ID not configured for city: {city_name}")
        return False
    
    try:
        # Imposta le variabili d'ambiente per la città corrente
        env = os.environ.copy()
        env['CITY'] = city_name
        
        # Esegui il processing Python
        print(f"📊 Running Python processing for {city_name}...")
        result = subprocess.run([sys.executable, 'main.py'], 
                              env=env, 
                              capture_output=True, 
                              text=True)
        
        if result.returncode == 0:
            print(f"✅ Python processing completed for {city_name}")
            print(result.stdout)
        else:
            print(f"❌ Python processing failed for {city_name}")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
        
        # Esegui il fetch Notion
        print(f"📥 Running Notion fetch for {city_name}...")
        result = subprocess.run(['node', 'scripts/fetch_notion.js'], 
                              env=env, 
                              capture_output=True, 
                              text=True)
        
        if result.returncode == 0:
            print(f"✅ Notion fetch completed for {city_name}")
            print(result.stdout)
        else:
            print(f"❌ Notion fetch failed for {city_name}")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error processing city {city_name}: {e}")
        return False

def main():
    """Processa tutte le città configurate"""
    print("🚀 Starting multi-city processing...")
    print("=" * 60)
    
    # Ottieni la lista delle città disponibili
    cities = get_available_cities()
    print(f"📋 Found {len(cities)} cities: {', '.join(cities)}")
    
    # Verifica le variabili d'ambiente richieste
    required_env_vars = ['NOTION_API_KEY', 'OPENROUTER_API_KEY']
    missing_vars = [var for var in required_env_vars if not os.environ.get(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        sys.exit(1)
    
    # Processa ogni città
    successful_cities = []
    failed_cities = []
    
    for city in cities:
        if process_city(city):
            successful_cities.append(city)
        else:
            failed_cities.append(city)
    
    # Riepilogo finale
    print("\n" + "=" * 60)
    print("📊 PROCESSING SUMMARY")
    print("=" * 60)
    print(f"✅ Successful: {len(successful_cities)} cities")
    if successful_cities:
        print(f"   - {', '.join(successful_cities)}")
    
    print(f"❌ Failed: {len(failed_cities)} cities")
    if failed_cities:
        print(f"   - {', '.join(failed_cities)}")
    
    if failed_cities:
        print(f"\n⚠️ Some cities failed to process. Check the logs above.")
        sys.exit(1)
    else:
        print(f"\n🎉 All cities processed successfully!")
        sys.exit(0)

if __name__ == "__main__":
    main()
