$Subs = @("Microsoft Azure Enterprise";"Microsoft Azure Enterprise Travelzoo-Inc";"Microsoft Azure Enterprise Travelzoo-Pub";"Microsoft Azure Enterprise Travelzoo-Pub-Legacy")

$connectionName = "AzureRunAsConnection"
try {
    # Get the connection "AzureRunAsConnection "
    $servicePrincipalConnection = Get-AutomationConnection -Name $connectionName
    # "Logging in to Azure..."
    $connectionResult =  Connect-AzAccount -Tenant $servicePrincipalConnection.TenantID `
                             -ApplicationId $servicePrincipalConnection.ApplicationID   `
                             -CertificateThumbprint $servicePrincipalConnection.CertificateThumbprint `
                             -ServicePrincipal
    # "Logged in."

}
catch {
    if (!$servicePrincipalConnection)
    {
        $ErrorMessage = "Connection $connectionName not found."
        throw $ErrorMessage
    } else{
        Write-Error -Message $_.Exception
        throw $_.Exception
    }
}

foreach ($Sub in $Subs) {
	Select-AzSubscription $Subs
	write-Output "remove old snapshots..."
	$removaldate = get-date -Format 'yyyy-MM-dd'
	$ListToRemove = Get-AzResource -TagName "Remove after" -TagValue $removaldate
	    
	foreach ($snap in $ListToRemove) {
	    Remove-AzResource -ResourceId $snap.ResourceId -Force
	}
}