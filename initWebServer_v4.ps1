configuration initWebServer_v4              # IIS, ASP.net4.5, SMTP server, URL Rewrite, ASP
{
    param
    (
        [Parameter(Mandatory=$false)]
        [String]$Driveletter
    )

    Import-DscResource –ModuleName PSDesiredStateConfiguration
    Import-DscResource -module xAzureTempDrive
    Import-DSCResource -ModuleName StorageDsc
    Import-DscResource -Module WebAdministrationDsc

    Node  localhost
    {
        xAzureTempDrive AzureTempDrive
        {
            Driveletter = $Driveletter
        }

        Disk DVolume
        {
            DiskId = 2
            DriveLetter = 'D'
            FSLabel = 'Data1'
            FSFormat = 'NTFS'
            DependsOn = '[xAzureTempDrive]AzureTempDrive'
        }
        # WaitForDisk Disk2
        # {
        #     DiskId = 2
        #     RetryIntervalSec = 60
        #     RetryCount = 60
        # }


        # Create D:\inetpub folders
        File CreateInetpub {
            Ensure          = "present"
            DestinationPath = "D:\inetpub"
            Type            = "Directory"
            #DependsOn       = '[Disk]DVolume'
        }

        File CreateMailDir {
            Ensure          = "present"
            DestinationPath = "D:\inetpub\mailroot"
            Type            = "Directory"
            #DependsOn       = '[Disk]DVolume'
        }

        File CreateLogDir {
            Ensure          = "present"
            DestinationPath = "D:\Logfiles"
            Type            = "Directory"
            #DependsOn       = '[Disk]DVolume'
        }

        File CreateMailDirBadmail {
            Ensure          = "present"
            DestinationPath = "D:\inetpub\mailroot\badmail"
            Type            = "Directory"
            #DependsOn       = '[Disk]DVolume'
        }

        File CreateMailDirDrop {
            Ensure          = "present"
            DestinationPath = "D:\inetpub\mailroot\drop"
            Type            = "Directory"
            #DependsOn       = '[Disk]DVolume'
        }

        File CreateMailDirPickup {
            Ensure          = "present"
            DestinationPath = "D:\inetpub\mailroot\pickup"
            Type            = "Directory"
            #DependsOn       = '[Disk]DVolume'
        }

        File CreateMailDirQueue {
            Ensure          = "present"
            DestinationPath = "D:\inetpub\mailroot\queue"
            Type            = "Directory"
            #DependsOn       = '[Disk]DVolume'
        }

        WindowsFeature IIS # название Role-провайдера и произвольное уникальное имя
        {
            # Ensure показывает, что роль будет добавлена (по умолчанию), чтобы удалить, необходимо установить в Absent        
            Ensure ="Present" 
            Name ="Web-Server" # имя устанавливаемой роли полученного Get-WindowsFeature
        }

        WindowsFeature ASP45
        {
            Ensure ="Present"
            Name ="Web-Asp-Net45"
        }
        
        WindowsFeature ASP             
        {
            Ensure ="Present"
            Name ="Web-Asp"
        }

        WindowsFeature NETFramework47
        {
            Ensure ="Present"
            Name ="Net-Framework-45-core"
        }

        WindowsFeature ASPNETFramework47
        {
            Ensure ="Present"
            Name ="Net-Framework-45-Aspnet"
        }

        WindowsFeature WebServerManagementConsole
        {
            Ensure = "Present"
            Name = "Web-Mgmt-Console"
        }

        WindowsFeature SMTP-Server
        {
            Ensure = "Present"
            Name = "SMTP-server"

        }

        Website DefaultSite
        {
            Ensure          = "Present"
            Name            = "Default Web Site"
            State           = "Stopped"
            PhysicalPath    = "D:\inetpub\"
            DependsOn       = "[WindowsFeature]IIS"
        }

        IisLogging DefaultIisLogging
        {
            LogPath         = "D:\Logfiles\"
            LogFormat       = "IIS"
            DependsOn       = "[WindowsFeature]IIS"
        }

        Package UrlRewrite
        {
            Ensure = "Present"
            Name = "IIS URL Rewrite Module 2"
            Path = "https://download.microsoft.com/download/1/2/8/128E2E22-C1B9-44A4-BE2A-5859ED1D4592/rewrite_amd64_en-US.msi"
            Arguments = "/quiet"
            ProductId = "9BCA2118-F753-4A1E-BCF3-5A820729965C"
            DependsOn = "[WindowsFeature]IIS"
        }
    }

}