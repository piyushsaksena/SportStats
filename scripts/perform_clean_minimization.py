import os
import shutil

def remove_path(path):
    if not os.path.exists(path):
        return
    try:
        if os.path.isdir(path):
            shutil.rmtree(path)
            print(f"Removed DIR:  {path}")
        else:
            os.remove(path)
            print(f"Removed FILE: {path}")
    except Exception as e:
        print(f"Error removing {path}: {e}")

def clean_project():
    print("=== STARTING SPORTSTATS PROJECT CLEANUP & MINIMIZATION ===")
    
    # 1. Remove cache directories
    remove_path('.hypothesis')
    remove_path('.ruff_cache')
    remove_path('.github')
    remove_path('backend/.pytest_cache')
    remove_path('backend/.ruff_cache')
    remove_path('scripts/__pycache__')

    # Remove all __pycache__ recursively
    for root, dirs, files in os.walk('.', topdown=False):
        for d in dirs:
            if d == '__pycache__':
                full_d = os.path.join(root, d)
                remove_path(full_d)

    # 2. Remove redundant root files
    remove_path('sportStats_sharable.zip')  # Duplicate of SportStats_Distribution.zip
    remove_path('.env.example')            # .env is present
    remove_path('Makefile')                # Linux makefile not needed
    remove_path('docker-compose.yml')       # Docker compose not needed
    remove_path('start.bat')               # Replaced by run_dashboard.bat
    remove_path('start.ps1')               # Replaced by run_dashboard.bat

    # 3. Remove raw unzipped dump (8 MB of duplicate match JSONs already ingested)
    remove_path('data/uploaded_cricket_zip')

    # 4. Remove unused frontend Next.js stub
    remove_path('frontend')

    # 5. Clean scripts directory - keep only core functional scripts
    core_scripts = {
        'build_datasets.py',
        'build_word_document.py',
        'build_full_viva_guide.py',
        'create_sharable_zip.py',
        'verify_all_requirements.py',
        'parse_cricsheet.py',
        'capture_precise_screenshots.py',
        'generate_viva_pdf.py',
        'cricket_team_matches.py',
        'icc_rankings_data.py',
        'perform_clean_minimization.py'
    }

    if os.path.exists('scripts'):
        for s in os.listdir('scripts'):
            s_path = os.path.join('scripts', s)
            if os.path.isfile(s_path) and s not in core_scripts:
                remove_path(s_path)

    print("=== CLEANUP COMPLETED SUCCESSFULLY ===")

if __name__ == '__main__':
    clean_project()
