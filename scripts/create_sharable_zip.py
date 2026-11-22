import os
import zipfile
import shutil

def should_exclude(rel_path):
    parts = rel_path.replace('\\', '/').split('/')
    excluded_dirs = {
        '.git', '.pytest_cache', '.ruff_cache', '.hypothesis',
        '__pycache__', '.system_generated', '.user_uploaded',
        'node_modules'
    }
    for part in parts:
        if part in excluded_dirs:
            return True
        if part.endswith('.pyc') or part.endswith('.pyo'):
            return True
        if part.endswith('.log') or part.endswith('.tmp'):
            return True
    
    # Exclude zip archives themselves to avoid recursion
    if rel_path.lower().endswith('.zip'):
        return True

    return False

def create_distribution_zip():
    base_dir = os.path.abspath('.')
    zip_filename = 'SportStats_Distribution.zip'
    zip_path = os.path.join(base_dir, zip_filename)

    print(f"Creating clean, minimized distribution ZIP from: {base_dir}")
    
    file_count = 0
    total_uncompressed_bytes = 0

    with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for root, dirs, files in os.walk(base_dir):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, base_dir)

                if should_exclude(rel_path):
                    continue

                zf.write(full_path, rel_path)
                file_count += 1
                total_uncompressed_bytes += os.path.getsize(full_path)

    zip_size = os.path.getsize(zip_path)
    print(f"Successfully created {zip_path}")
    print(f"Total files packaged: {file_count}")
    print(f"Uncompressed size: {total_uncompressed_bytes / (1024*1024):.2f} MB")
    print(f"Compressed ZIP size: {zip_size / (1024*1024):.2f} MB ({zip_size} bytes)")

    # Copy to brain artifact directory
    brain_dir = r'C:\Users\Piyush\.gemini\antigravity\brain\e80a0907-f942-45fe-b22f-7b2e9569397a'
    brain_zip_path = os.path.join(brain_dir, zip_filename)
    try:
        shutil.copy(zip_path, brain_zip_path)
        print(f"Copied to brain artifact directory: {brain_zip_path}")
    except Exception as e:
        print(f"Note copying to artifact: {e}")

    return zip_path, zip_size, file_count

if __name__ == '__main__':
    create_distribution_zip()
