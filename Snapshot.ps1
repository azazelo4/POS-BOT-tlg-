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

$vmNameTar = 'SCQASQL2'
$resourceGroupNameTar = 'AZ-INC-CUS-INFR-RG-CORPORATE-01'

# Variables for creating Disk
$SnapshotResourceGroup = $resourceGroupName
$DiskNameOS = "$snapshotName-disk"

# Get the disk that you need to backup by creating snapshot
$yourDisk = Get-AzDisk -DiskName $diskName -ResourceGroupName $resourceGroupName

# Create snapshot by setting the SourceUri property with the value of the Id property of the disk
$snapshotConfig = New-AzSnapshotConfig -SourceUri $yourDisk.Id -Location $yourDisk.Location -CreateOption Copy
New-AzSnapshot -ResourceGroupName $resourceGroupName -SnapshotName $snapshotName -Snapshot $snapshotConfig

# Chek that snapshot exist
Start-Sleep -s 180
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

#Attach Disk to targeted VM
$vm = Get-AzVM -Name $vmNameTar -ResourceGroupName $resourceGroupNameTar
$vm = Add-AzVMDataDisk -CreateOption Attach -Lun 0 -VM $vm -ManagedDiskId $DiskNameOS
Update-AzVM -VM $vm -ResourceGroupName $resourceGroupNameTar
