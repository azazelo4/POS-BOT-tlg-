configuration initWebServer_v1              # IIS, ASP.net4.5, SMTP server, URL Rewrite, ASP
{
    param
    (
        [Parameter(Mandatory)]
        [String]$Driveletter
    )

    Import-DscResource –ModuleName PSDesiredStateConfiguration
    Import-DscResource -module xAzureTempDrive
    Import-DSCResource -ModuleName StorageDsc
    Import-DscResource -Module WebAdministrationDsc

    Node local
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
            DependsOn       = '[Disk]DVolume'
        }

        File CreateLogDir {
            Ensure          = "present"
            DestinationPath = "D:\Logfiles"
            Type            = "Directory"
            DependsOn       = '[Disk]DVolume'
        }

        File CreateMailDir {
            Ensure          = "present"
            DestinationPath = "D:\mailroot"
            Type            = "Directory"
            DependsOn       = '[Disk]DVolume'
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