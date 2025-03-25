

try{
	$Quotas = @(Get-FsrmQuota | Select-Object Path, Size, Usage)
	Write-Output "<<<win_fsrmquota:sep(59)>>>"
	foreach ($Quota in $Quotas) {
		Write-Host( $Quota.Path + ";" + $Quota.Size + ";" + $Quota.Usage)
    
	} 
}catch{}
