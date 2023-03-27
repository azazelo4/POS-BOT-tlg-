Configuration SMTPRelayConfig
{
    Node localhost
    {
        #надо доустановить эти модули. иначе скрипт не будет работать
        WindowsFeature WebWMI
        {
            Ensure ="Present"
            Name ="Web-WMI"
        }
    
        WindowsFeature Web-Scripting-Tools
        {
            Ensure = "Present"
            Name = "Web-Scripting-Tools"
        }
        # Устанавливаем путь к папкам
        Script mailPath
        {
            SetScript = {
                $smtpServer = Get-WmiObject -Namespace "root/MicrosoftIISv2" -Class "IIsSMTPServerSetting" -Filter "Name='SMTPSVC/1'"
                $badmailPath = "D:\inetpub\mailroot\Badmail"
                $queuePath = "D:\inetpub\mailroot\Queue"
                $dropPath = "D:\inetpub\mailroot\Drop"
                $pickupPath = "D:\inetpub\mailroot\Pickup"
                $smtpServer.PickupDirectory = $pickupPath
                $smtpServer.DropDirectory = $dropPath
                $smtpServer.PickupDirectory = $queuePath
                $smtpServer.BadMailDirectory = $badmailPath
                $smtpServer.Put()
            }
            TestScript = {
                $smtpServer = Get-WmiObject -Namespace "root/MicrosoftIISv2" -Class "IIsSMTPServerSetting" -Filter "Name='SMTPSVC/1'"
                return $smtpServer.BadMailDirectory -eq "D:\inetpub\mailroot\Badmail"
            }
            GetScript = { return @{ Name = "mailPath" } }
        }
    }
}