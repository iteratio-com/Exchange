function Export-Registry {
    param (
        [parameter(Mandatory = $true)][string]$Path,
        [parameter(Mandatory = $true)][string]$cmksection
    )
    
    #Test if $Path is accessible
    if (Test-Path $path -ErrorAction stop) {
        Write-Host ("<<<{0}:sep(59)>>>" -f $cmksection) 
    }
    else {
        return
    }

    #Set $keys variable
    $keys = Get-ChildItem -Path $path -Recurse -ErrorAction SilentlyContinue

    foreach ($key in $keys) {
        foreach ($property in $key) {
            foreach ($name in $key.Property) {
                try {   
                    $Value = Get-ItemPropertyValue -Path $key.PSPath -Name $name
                    Write-Host ("{1};{2}" -f $property, $name, $Value )
                }
                catch {
                    Write-Warning ("Error processing {0} in {1}" -f $property, $key.name)
                }
            }
        }
    }
    $timezone = [System.TimeZoneInfo]::Local.GetUtcOffset((Get-Date)).TotalSeconds
    $timeZone = $timeZone -replace '^','BaseUtcOffsetSeconds;' 
    Write-Host $timeZone
    
}

Export-Registry -cmksection wsus_next_reboot -path 'HKLM:SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\' 