configuration initializeDisk
{
    param
    (
        [Parameter(Mandatory)]
        [String]$Driveletter
    )

    Import-DscResource –ModuleName PSDesiredStateConfiguration
    Import-DscResource -module xAzureTempDrive
    Import-DSCResource -ModuleName StorageDsc

    # LocalConfigurationManager
    #   {
    #       AllowModuleOverwrite = $true
    #       RefreshMode = 'Push'
    #       ConfigurationMode = 'ApplyAndAutoCorrect'
    #       RebootNodeIfNeeded = $true
    #       DebugMode = "All"
    #   }

    Node localhost
    {

        xAzureTempDrive AzureTempDrive
        {
            Driveletter = $Driveletter
        }
    
        # WaitForDisk Disk2
        # {
        #     DiskId = 2
        #     RetryIntervalSec = 60
        #     RetryCount = 60
        # }

        Disk DVolume
        {
            DiskId = 2
            DriveLetter = 'D'
            FSLabel = 'Data1'
            FSFormat = 'NTFS'
            DependsOn = '[xAzureTempDrive]AzureTempDrive'
        }

        # Create D:\inetpub folder
        File CreateInetpub {
            Ensure          = "present"
            DestinationPath = "D:\inetpub"
            Type            = "Directory"
            #DependsOn       = '[Disk]DVolume'
        }

        File CreateLogDir {
            Ensure          = "present"
            DestinationPath = "D:\Logfiles"
            Type            = "Directory"
            #DependsOn       = '[Disk]DVolume'
        }
    }
}