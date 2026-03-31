# Compare using powershell script
$base = Get-Content c:\OdooProject\odoo-modules\collection_disputes_base\models\collection_dispute_case.py
$mgmt = Get-Content c:\OdooProject\odoo-modules\collection_disputes_management\models\collection_dispute_case.py
$mgmt_clean = $mgmt -replace 'collection_disputes_management', 'collection_disputes_base'

$diff = Compare-Object $base $mgmt_clean
$diff | Out-File c:\OdooProject\odoo-modules\diff.txt
