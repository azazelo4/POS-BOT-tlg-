Import-Module Az

# function Show-Menu
# {
#     param (
#         [string]$Title = 'Travelzoo deploy process'
#     )
#     Clear-Host
#     # Write-Host "================ $Title ================"
    
    # Write-Host "1: Press '1' To deploy WEB server."
    # Write-Host "2: Press '2' To start test migration."
    # Write-Host "3: Press '3' To start migration."
    # Write-Host "4: Press '4' To exclude server from replication list."
    # Write-Host "Q: Press 'Q' to quit."

    # $selection = Read-Host "Please make a selection"
    # return $selection
# }

###################################  Variables ###################################################################################

$subscriptionName = "Microsoft Azure Enterprise Travelzoo-Pub-Legacy"
$azRegion = "centraluS"

$DOM           = "PUB"
$ROLE          = "WEB"
$ENV           = "P"
$NUM           = "25"
$vmSize        = "Standard_B2s" 
$vmName        = "AZCUS$DOM$ROLE-$ENV$NUM"
$vNicName      = "$vmName-vNic-01"
$userName      = "localadmin"
$Password      = (ConvertTo-SecureString "Passw0rd123!" -Force -AsPlainText)
$Credential    = New-Object System.Management.Automation.PSCredential ($UserName, $Password)
$publisherName = "MicrosoftWindowsServer"
$offer         = "WindowsServer"
$sku           = "2019-Datacenter"
$version       = "Latest"
$privateIP     = "10.190.40.$NUM"

$VirtualNetwork = "AZ-PUB-CUS-RELEASE-VNET-WEBSRV-01"
$vnetResourceGroupName = "AZ-PUB-CUS-RELEASE-RG-LEGACY-01"  #resource group of the existing subnet
$Subnet = "AZ-PUB-CUS-RELEASE-SNET-WEBSRV-01"               #existing subnet on different resource group


###################################### Main Script ################################################################################

$null = Connect-AzAccount #-Credential $Credential
$null = Set-AzContext  -SubscriptionName $subscriptionName

# Show-menu

$resourceGroup = Get-AzresourceGroup -Name "AZ-PUB-CUS-RELEASE-RG-LEGACY-01"
#set Availability Set
if ($resourceGroup.count -eq 1) {
    $yn = Read-Host "We've fount just one Resource Group: $($resourceGroup.ResourceGroupName). Do you want to use it? y/[n] "
    if ($yn -eq "Y" -or $yn -eq "y") {$resourceGroupName = $resourceGroup.ResourceGroupName}
} 
elseif ($resourceGroup.count -gt 1) {
    Write-host "There is more than one Resource Group. Please select a number or press ENTER if you'd like to create a new one" 
    $i=0 
    $num=0
    $resourceGroup | % {$i++;write-host $i,$_.ResourceGroupName}
    $num = Read-Host "Select an Resource Group number"
    if ($num -gt 0 -and $num -le $resourceGroup.count) {
        $yn=Read-host "You've selected $($resourceGroup[$num-1].ResourceGroupName) Continue? y/[n]"
        if ($yn -eq "Y" -or $yn -eq "y") {$resourceGroupName = $resourceGroup[$num-1].ResourceGroupName}
    }
}   
if (!$resourceGroupName) {while (!$resourceGroupName){$resourceGroupName = Read-Host "Enter Resource Group name"} }

write-host "Creating the new VM..." -ForegroundColor Yellow


$vNet = Get-AzVirtualNetwork -Name $VirtualNetwork -ResourceGroupName $vnetResourceGroupName
$subnetId = $vNet.Subnets | Where-Object Name -eq $Subnet | Select-Object -ExpandProperty Id
if (!(get-AzNetworkInterface -Name $vNicName)) {
    $vNic = New-AzNetworkInterface -Name $vNicName -ResourceGroupName $resourceGroupName -Location $azRegion -SubnetId $subnetId -PrivateIpAddress $privateIP
}
else{
    $vNic = get-AzNetworkInterface -Name $vNicName
}

$vm = New-AzVMConfig -VMName $vmName -VMSize $vmSize
$vm = Set-AzVMOperatingSystem -VM $vm -Windows -ComputerName $vmName -Credential $Credential -ProvisionVMAgent
$vm = Add-AzVMNetworkInterface -VM $vm -Id $vNic.Id
$vm = Set-AzVMSourceImage -VM $vm -PublisherName $publisherName -Offer $offer -Skus $sku -Version $version

$res = New-AzVM -ResourceGroupName $resourceGroupName -Location $azRegion -VM $vm -LicenseType "Windows_Server" -Verbose


if ($res.StatusCode -eq "OK") {Write-Host "Done" -ForegroundColor Green} 
else {
    Write-host "Error" -ForegroundColor Red
    $res
} #

$azDataDiskName = "$vmName-data1"

$diskConfig = New-AzDiskConfig `
    -Location $azRegion `
    -CreateOption Empty `
    -DiskSizeGB 64 `
    -SkuName "Standard_LRS"

$dataDisk = New-AzDisk `
    -ResourceGroupName $resourceGroupName `
    -DiskName $azDataDiskName `
    -Disk $diskConfig

Get-AzDisk `
    -ResourceGroupName $resourceGroupName `
    -DiskName $azDataDiskName


$vm = Get-AzVM `
    -ResourceGroupName $resourceGroupName `
    -Name $vmName

$vm = Add-AzVMDataDisk `
    -VM $vm `
    -Name $azDataDiskName `
    -CreateOption Attach `
    -ManagedDiskId $dataDisk.Id `
    -Lun 1

$res = Update-AzVM `
    -ResourceGroupName $resourceGroupName `
    -VM $vm

if ($res.StatusCode -eq "OK") {Write-Host "Done" -ForegroundColor Green} 
else {
        Write-host "Error" -ForegroundColor Red
        $res
} #