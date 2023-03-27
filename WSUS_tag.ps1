# UpdateServer                                           Id                                   Name
# ------------                                           --                                   ----
# Microsoft.UpdateServices.Internal.BaseApi.UpdateServer a0a08746-4dbe-4a37-9adf-9e7652c0b421 All Computers
# Microsoft.UpdateServices.Internal.BaseApi.UpdateServer ffdfbab8-6707-4885-bb32-ae6b52675cc1 DevTest and Qa
# Microsoft.UpdateServices.Internal.BaseApi.UpdateServer 30c8ee03-d3c0-4e40-8bab-1e229b685907 PROD week1
# Microsoft.UpdateServices.Internal.BaseApi.UpdateServer 748ecf47-10ec-4c97-9a20-bbd6d01d9b5c PROD week2
# Microsoft.UpdateServices.Internal.BaseApi.UpdateServer 1a1df0b5-4aa6-404a-a3ff-3fe960b75858 PROD week3
# Microsoft.UpdateServices.Internal.BaseApi.UpdateServer bfc7498f-5ade-41da-8c48-c00baaf7654b PROD week4
# Microsoft.UpdateServices.Internal.BaseApi.UpdateServer 204e82fa-4dec-4e29-926e-f0ad6299786f Release
# Microsoft.UpdateServices.Internal.BaseApi.UpdateServer b73ca6ed-5727-47f3-84de-015e03f6a88a Unassigned Computers


#Var's
$Login = 'ServiceAccountName'
$Pass = 'S0me9oodP@s5'
$Subs = @("Microsoft Azure Enterprise";"Microsoft Azure Enterprise Travelzoo-Inc";"Microsoft Azure Enterprise Travelzoo-Pub";"Microsoft Azure Enterprise Travelzoo-Pub-Legacy")
$AzureVM = @()

#Connect to Azure via Az CLI
az login -u $Login -p $Pass

Foreach ($Sub in $Subs) {
    az account set --subscription "$Sub"
    
    #Make array with all VM's in Sub
    $VM = az vm list | ConvertFrom-Json
    foreach ($VMName in $VM) {
        $weekNum = $null
        write-host "working with" $vmname.name
        $VMhost = az vm get-instance-view -n $vmname.name -g $VMname.ResourceGroup |ConvertFrom-Json #All about VM
        $VMhostname = $VMhost.instanceview.computername # //get hostname of VM
        write-host "$VMhostname"
        $GroupIDs = get-wsuscomputer -NameIncludes $VMhostname | select ComputerTargetGroupIds  # // get groupID for compare and assign $weekNum
        if ($null -ne $GroupIDs) {  #check that groupID not null
            Foreach ($GroupID in $GroupIDs.ComputerTargetGroupIds) { #assign $weekNum
                Write-Host $GroupID
                if ($GroupID -eq '30c8ee03-d3c0-4e40-8bab-1e229b685907') {
                    $weekNum = '1' 
                    } elseif ($GroupID -eq '748ecf47-10ec-4c97-9a20-bbd6d01d9b5c') {
                    $weekNum = '2'
                    } elseif ($GroupID -eq '1a1df0b5-4aa6-404a-a3ff-3fe960b75858') {
                    $weekNum = '3'
                    } elseif ($GroupID -eq 'bfc7498f-5ade-41da-8c48-c00baaf7654b') {
                    $weekNum = '4'
                    } elseif ($GroupID -eq 'ffdfbab8-6707-4885-bb32-ae6b52675cc1') {
                    $weekNum = '0'
                    } elseif (($GroupID -eq 'a0a08746-4dbe-4a37-9adf-9e7652c0b421') -or ($GroupID -eq 'b73ca6ed-5727-47f3-84de-015e03f6a88a')) {   
                    Write-host "GROUP: ALL PC or Unassigned"
                    } else {
                        Write-Host $weekNum   
                }
            }  
        }
        $AzureVM += new-object PSObject -property (@{AZVMNAME = $vmname.name ; OSNAME = $VMhostname ; WEEK = $weekNum ; RG = $VMName.ResourceGroup})   #   //add to array VM hostname and week of update   
    }
    $AzureVM


    # Assign TAG to Azure VM
    foreach ($AVM in $AzureVM) {
        if ($($AVM.WEEK) -ne $null) {
            write-host $AVM
            az vm update -g $($AVM.RG) -n $($AVM.AZVMNAME) --set tags.Updates=$($AVM.WEEK)
        }
    }
}