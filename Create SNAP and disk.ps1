$connectionName = "AzureRunAsConnection"
try
{
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

# Variables
$diskName = "AZCUSPUBSQL-R01_DataDisk_1"
$resourceGroupName = "AZ-PUB-CUS-RELEASE-RG-LEGACY-01"
$snapshotName = "AZCUSPUBSQL-R01_DataDisk_1-$(get-date -Format 'yyyy-MM-dd-hh')"

# Variables for creating Disk
$SnapshotResourceGroup = $resourceGroupName
$DiskNameOS = Get-AutomationVariable -Name "DiskNameClone"

# Variables for targeted subs and vm
$SubscriptionIDTar = 'eccfd49a-5eb8-42f4-b4cf-5edd76960aad'
$resourceGroupNameTar = 'AZ-INC-CUS-INFR-RG-CORPORATE-01'
$vmNameTar = 'SCQASQL2'

# Get the disk that you need to backup by creating snapshot
Select-AzSubscription -SubscriptionName "Microsoft Azure Enterprise Travelzoo-Pub-Legacy"
$yourDisk = Get-AzDisk -DiskName $DiskName -ResourceGroupName $resourceGroupName

# Create snapshot by setting the SourceUri property with the value of the Id property of the disk
$snapshotConfig = New-AzSnapshotConfig -SourceUri $yourDisk.Id -Location $yourDisk.Location -CreateOption Copy
New-AzSnapshot -ResourceGroupName $resourceGroupName -SnapshotName $snapshotName -Snapshot $snapshotConfig

# Chek that snapshot exist
Start-Sleep -s 60
try {
    $snapshotinfo = Get-AzSnapshot -ResourceGroupName $SnapshotResourceGroup -SnapshotName $snapshotName
}
catch {
    if (!$snapshotinfo)
    {
        $ErrorMessage = " $snapshotName not found."
    throw $ErrorMessage
    } else {
        Write-Error -Message $_.Exception
        throw $_.Exception
    }
}

# Create Disk
$snapshotinfo = Get-AzSnapshot -ResourceGroupName $SnapshotResourceGroup -SnapshotName $snapshotName
New-AzDisk -DiskName $DiskNameOS (New-AzDiskConfig -Location CentralUS -CreateOption Copy -SourceResourceId $snapshotinfo.Id) -ResourceGroupName $SnapshotResourceGroup

# Move disk to another subscription (assign contributor role to RunAs account for both subsription)
$Move = Get-AzResource -ResourceGroupName $resourceGroupName -ResourceName $DiskNameOS
Move-AzResource -DestinationSubscriptionId $SubscriptionIDTar -DestinationResourceGroupName $resourceGroupNameTar -ResourceId $Move.ResourceId -Force

# Remove snapshot
Remove-AzSnapshot -ResourceGroupName $resourceGroupName -SnapshotName $snapshotName -Force

#Attach Disk to targeted VM
Set-AzContext -Subscription $SubscriptionIDTar
$vm = Get-AzVM -Name $vmNameTar -ResourceGroupName $resourceGroupNameTar
$diskURI = Get-AzDisk -DiskName $DiskNameOS
$vm = Add-AzVMDataDisk -CreateOption Attach -Lun 0 -VM $vm -ManagedDiskId $diskURI.id
Update-AzVM -VM $vm -ResourceGroupName $resourceGroupNameTar

# Create Schedule for second script that deattach and remove disk
$automationAccountName = "Create-Snapshot-and-disk"
$runbookName = "ScanDeattachAndRemoveDIsk"
$scheduleName = "test"
$TimeZone = ([System.TimeZoneInfo]::Local).Id

Select-AzSubscription -SubscriptionName "Microsoft Azure Enterprise Travelzoo-Pub-Legacy"
New-AzAutomationSchedule -AutomationAccountName $automationAccountName -Name $scheduleName -StartTime ((get-date).AddHours(8)) -OneTime -ResourceGroupName $resourceGroupName -TimeZone $TimeZone
Register-AzAutomationScheduledRunbook -AutomationAccountName $automationAccountName -Name $runbookName -ScheduleName $scheduleName -ResourceGroupName $resourceGroupName

