import os
import difflib

base_dir = r'c:\OdooProject\odoo-modules\collection_disputes_base'
mgmt_dir = r'c:\OdooProject\odoo-modules\collection_disputes_management'

output = []

for root, dirs, files in os.walk(mgmt_dir):
    if '__pycache__' in root: continue
    rel_dir = os.path.relpath(root, mgmt_dir)
    for file in files:
        if file.endswith(('.py', '.xml', '.csv')):
            mgmt_path = os.path.join(root, file)
            base_path = os.path.normpath(os.path.join(base_dir, rel_dir, file))
            
            if not os.path.exists(base_path):
                output.append(f'\n--- NEW FILE: {os.path.join(rel_dir, file)} ---')
                continue
            
            with open(mgmt_path, 'r', encoding='utf-8') as f1, open(base_path, 'r', encoding='utf-8') as f2:
                # Read management lines and replace 'collection_disputes_management' with 'collection_disputes_base'
                # to see structural changes ignoring the string rename
                mgmt_content = f1.read().replace('collection_disputes_management', 'collection_disputes_base')
                base_content = f2.read()
                
            mgmt_lines = mgmt_content.splitlines(keepends=True)
            base_lines = base_content.splitlines(keepends=True)
            
            diff = list(difflib.unified_diff(base_lines, mgmt_lines, fromfile=base_path, tofile=mgmt_path, n=0))
            if diff:
                output.append(f'\n--- MODIFIED FILE: {os.path.join(rel_dir, file)} ---')
                output.extend(diff[:30]) # Show first 30 lines of diff
                if len(diff) > 30:
                    output.append(f'... and {len(diff)-30} more lines')

with open(r'c:\OdooProject\odoo-modules\diff_output.txt', 'w', encoding='utf-8') as f:
    f.writelines(output)
