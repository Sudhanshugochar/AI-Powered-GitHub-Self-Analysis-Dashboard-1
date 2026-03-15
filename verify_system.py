import os
import sys
import requests
import importlib

def check_import(module_name):
    try:
        importlib.import_module(module_name)
        print(f"[OK] Import {module_name}")
        return True
    except ImportError as e:
        print(f"[FAIL] Import {module_name}: {e}")
        return False

def check_ollama():
    try:
        response = requests.get("http://localhost:11434")
        if response.status_code == 200:
            print("[OK] Ollama is running")
            return True
        else:
            print(f"[WARN] Ollama responded with status {response.status_code}")
            return True # It's running, just maybe not root 200
    except requests.exceptions.ConnectionError:
        print("[FAIL] Ollama is NOT running on localhost:11434")
        return False

def check_env_vars():
    # Load dotenv
    from dotenv import load_dotenv
    load_dotenv()
    
    required = ["GITHUB_TOKEN", "GITHUB_USERNAME"]
    missing = []
    for var in required:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        print(f"[WARN] Missing environment variables: {', '.join(missing)}. API calls will be limited/mocked.")
    else:
        print("[OK] Environment variables check")

def check_local_modules():
    sys.path.append(os.getcwd())
    modules = ["src.data_collection", "src.llm_analysis", "src.traditional_ds", "src.resume_builder", "src.mock_data"]
    results = [check_import(m) for m in modules]
    return all(results)

def main():
    print("--- Verifying System ---")
    
    # 1. Imports
    req_modules = ["streamlit", "pandas", "numpy", "plotly", "sklearn", "prophet", "ollama", "fpdf"]
    imports_ok = all([check_import(m) for m in req_modules])
    
    # 2. Local Modules
    local_ok = check_local_modules()
    
    # 3. Ollama
    ollama_ok = check_ollama()
    
    # 4. Env
    check_env_vars()
    
    if imports_ok and local_ok:
        print("\n[SUCCESS] System verification passed (with potential warnings).")
    else:
        print("\n[FAILURE] System verification failed.")

if __name__ == "__main__":
    main()
