Configuration installFeatures
{
    Node local # указываем узлы
    {
    	WindowsFeature IIS # название Role-провайдера и произвольное уникальное имя
        {
            # Ensure показывает, что роль будет добавлена (по умолчанию), чтобы удалить, необходимо установить в Absent        
            Ensure ="Present" 
            Name ="Web-Server" # имя устанавливаемой роли полученного Get-WindowsFeature
        }

        WindowsFeature ASP
        {
            Ensure ="Present"
            Name ="Web-Asp-Net45"
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
    }
    
}