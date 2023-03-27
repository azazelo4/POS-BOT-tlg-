Configuration WebsiteDefault
{
    param
    (
        # Target nodes to apply the configuration
        [String[]] $NodeName = 'localhost'
    )
    # Import the module that defines custom resources
    Import-DscResource -Module WebAdministrationDsc
    
    Node $NodeName
    {
        
        # Stop the default website
        Website DefaultSite
        {
            Ensure          = "Present"
            Name            = "Default Web Site"
            State           = "Stopped"
            PhysicalPath    = "D:\inetpub\"
            # DependsOn       = "[WindowsFeature]IIS"
        }

        IisLogging DefaultIisLogging
        {
            LogPath         = "D:\Logfiles\"
            LogFormat       = "IIS"
            # DependsOn       = "[WindowsFeature]IIS"
        }
    }

}