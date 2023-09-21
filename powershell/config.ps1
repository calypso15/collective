$ConfigFile = $null

function CreateConfig
{
    Write-Host("Attempting to create '$ConfigFile'.")
    $ConfigUI.DialogResult = [System.Windows.Forms.DialogResult]::OK
}

function ShowDialog($FilePath)
{
    $ConfigFile = $FilePath

    Add-Type -AssemblyName System.Windows.Forms
    [System.Windows.Forms.Application]::EnableVisualStyles()

    $ConfigUI                        = New-Object system.Windows.Forms.Form
    $ConfigUI.ClientSize             = New-Object System.Drawing.Point(330,424)
    $ConfigUI.text                   = "Config Creator"
    $ConfigUI.FormBorderStyle        = 'FixedDialog'
    $ConfigUI.TopMost                = $true

    $Nuc_UsernameLabel               = New-Object system.Windows.Forms.Label
    $Nuc_UsernameLabel.text          = "Username"
    $Nuc_UsernameLabel.AutoSize      = $true
    $Nuc_UsernameLabel.width         = 25
    $Nuc_UsernameLabel.height        = 10
    $Nuc_UsernameLabel.location      = New-Object System.Drawing.Point(15,20)
    $Nuc_UsernameLabel.Font          = New-Object System.Drawing.Font('Microsoft Sans Serif',10)

    $Nuc_Username                    = New-Object system.Windows.Forms.TextBox
    $Nuc_Username.multiline          = $false
    $Nuc_Username.width              = 162
    $Nuc_Username.height             = 20
    $Nuc_Username.location           = New-Object System.Drawing.Point(123,20)
    $Nuc_Username.Font               = New-Object System.Drawing.Font('Microsoft Sans Serif',10)

    $Nuc_PasswordLabel               = New-Object system.Windows.Forms.Label
    $Nuc_PasswordLabel.text          = "Password"
    $Nuc_PasswordLabel.AutoSize      = $true
    $Nuc_PasswordLabel.width         = 25
    $Nuc_PasswordLabel.height        = 10
    $Nuc_PasswordLabel.location      = New-Object System.Drawing.Point(15,50)
    $Nuc_PasswordLabel.Font          = New-Object System.Drawing.Font('Microsoft Sans Serif',10)

    $Nuc_Password                  = New-Object system.Windows.Forms.TextBox
    $Nuc_Password.multiline        = $false
    $Nuc_Password.width            = 162
    $Nuc_Password.height           = 20
    $Nuc_Password.passwordchar     = "*"
    $Nuc_Password.location         = New-Object System.Drawing.Point(123,50)
    $Nuc_Password.Font             = New-Object System.Drawing.Font('Microsoft Sans Serif',10)

    $Nuc_Autologon                   = New-Object system.Windows.Forms.CheckBox
    $Nuc_Autologon.text              = "Autologon?"
    $Nuc_Autologon.AutoSize          = $true
    $Nuc_Autologon.width             = 95
    $Nuc_Autologon.height            = 20
    $Nuc_Autologon.location          = New-Object System.Drawing.Point(15,80)
    $Nuc_Autologon.Font              = New-Object System.Drawing.Font('Microsoft Sans Serif',10)

    $Vcloud_UrlLabel                 = New-Object system.Windows.Forms.Label
    $Vcloud_UrlLabel.text            = "Url"
    $Vcloud_UrlLabel.AutoSize        = $true
    $Vcloud_UrlLabel.width           = 25
    $Vcloud_UrlLabel.height          = 10
    $Vcloud_UrlLabel.location        = New-Object System.Drawing.Point(15,20)
    $Vcloud_UrlLabel.Font            = New-Object System.Drawing.Font('Microsoft Sans Serif',10)

    $Vcloud_Url                      = New-Object system.Windows.Forms.TextBox
    $Vcloud_Url.multiline            = $false
    $Vcloud_Url.width                = 162
    $Vcloud_Url.height               = 20
    $Vcloud_Url.location             = New-Object System.Drawing.Point(123,20)
    $Vcloud_Url.Font                 = New-Object System.Drawing.Font('Microsoft Sans Serif',10)

    $Vcloud_UsernameLabel            = New-Object system.Windows.Forms.Label
    $Vcloud_UsernameLabel.text       = "Username"
    $Vcloud_UsernameLabel.AutoSize   = $true
    $Vcloud_UsernameLabel.width      = 25
    $Vcloud_UsernameLabel.height     = 10
    $Vcloud_UsernameLabel.location   = New-Object System.Drawing.Point(15,50)
    $Vcloud_UsernameLabel.Font       = New-Object System.Drawing.Font('Microsoft Sans Serif',10)

    $Vcloud_Username                 = New-Object system.Windows.Forms.TextBox
    $Vcloud_Username.multiline       = $false
    $Vcloud_Username.width           = 162
    $Vcloud_Username.height          = 20
    $Vcloud_Username.location        = New-Object System.Drawing.Point(123,50)
    $Vcloud_Username.Font            = New-Object System.Drawing.Font('Microsoft Sans Serif',10)

    $Vcloud_PasswordLabel            = New-Object system.Windows.Forms.Label
    $Vcloud_PasswordLabel.text       = "Password"
    $Vcloud_PasswordLabel.AutoSize   = $true
    $Vcloud_PasswordLabel.width      = 25
    $Vcloud_PasswordLabel.height     = 10
    $Vcloud_PasswordLabel.location   = New-Object System.Drawing.Point(15,80)
    $Vcloud_PasswordLabel.Font       = New-Object System.Drawing.Font('Microsoft Sans Serif',10)

    $Vcloud_Password                  = New-Object system.Windows.Forms.TextBox
    $Vcloud_Password.multiline        = $false
    $Vcloud_Password.width            = 162
    $Vcloud_Password.height           = 20
    $Vcloud_Password.passwordchar     = "*"
    $Vcloud_Password.location         = New-Object System.Drawing.Point(123,80)
    $Vcloud_Password.Font             = New-Object System.Drawing.Font('Microsoft Sans Serif',10)

    $CreateButton                    = New-Object system.Windows.Forms.Button
    $CreateButton.text               = "Create"
    $CreateButton.width              = 60
    $CreateButton.height             = 30
    $CreateButton.location           = New-Object System.Drawing.Point(104,379)
    $CreateButton.Font               = New-Object System.Drawing.Font('Microsoft Sans Serif',10)

    $CancelButton                    = New-Object system.Windows.Forms.Button
    $CancelButton.text               = "Cancel"
    $CancelButton.width              = 60
    $CancelButton.height             = 30
    $CancelButton.location           = New-Object System.Drawing.Point(173,379)
    $CancelButton.Font               = New-Object System.Drawing.Font('Microsoft Sans Serif',10)

    $NucGroup                        = New-Object system.Windows.Forms.Groupbox
    $NucGroup.height                 = 107
    $NucGroup.width                  = 306
    $NucGroup.text                   = "NUC"
    $NucGroup.location               = New-Object System.Drawing.Point(13,18)

    $VcloudGroup                     = New-Object system.Windows.Forms.Groupbox
    $VcloudGroup.height              = 113
    $VcloudGroup.width               = 306
    $VcloudGroup.text                = "VCloud"
    $VcloudGroup.location            = New-Object System.Drawing.Point(13,146)

    $SiteTokenLabel                  = New-Object system.Windows.Forms.Label
    $SiteTokenLabel.text             = "Site Token"
    $SiteTokenLabel.AutoSize         = $true
    $SiteTokenLabel.width            = 25
    $SiteTokenLabel.height           = 10
    $SiteTokenLabel.location         = New-Object System.Drawing.Point(16,272)
    $SiteTokenLabel.Font             = New-Object System.Drawing.Font('Microsoft Sans Serif',10)
    $SiteTokenLabel.BackColor        = [System.Drawing.ColorTranslator]::FromHtml("transparent")

    $SiteToken                       = New-Object system.Windows.Forms.TextBox
    $SiteToken.multiline             = $false
    $SiteToken.width                 = 298
    $SiteToken.height                = 20
    $SiteToken.location              = New-Object System.Drawing.Point(16,290)
    $SiteToken.Font                  = New-Object System.Drawing.Font('Microsoft Sans Serif',10)

    $IgnoreWarnings                  = New-Object system.Windows.Forms.CheckBox
    $IgnoreWarnings.text             = "Ignore Warnings?"
    $IgnoreWarnings.AutoSize         = $true
    $IgnoreWarnings.height           = 20
    $IgnoreWarnings.location         = New-Object System.Drawing.Point(28,321)
    $IgnoreWarnings.Font             = New-Object System.Drawing.Font('Microsoft Sans Serif',10)

    $IgnoreErrors                    = New-Object system.Windows.Forms.CheckBox
    $IgnoreErrors.text               = "Ignore Errors?"
    $IgnoreErrors.AutoSize           = $true
    $IgnoreErrors.height             = 20
    $IgnoreErrors.location           = New-Object System.Drawing.Point(28,346)
    $IgnoreErrors.Font               = New-Object System.Drawing.Font('Microsoft Sans Serif',10)

    $NonInteractive                  = New-Object system.Windows.Forms.CheckBox
    $NonInteractive.text             = "Non-Interactive?"
    $NonInteractive.AutoSize         = $true
    $NonInteractive.height           = 20
    $NonInteractive.location         = New-Object System.Drawing.Point(180,321)
    $NonInteractive.Font             = New-Object System.Drawing.Font('Microsoft Sans Serif',10)

    $NucGroup.controls.AddRange(@($Nuc_UsernameLabel,$Nuc_Username,$Nuc_PasswordLabel,$Nuc_Password,$Nuc_Autologon))
    $VcloudGroup.controls.AddRange(@($Vcloud_UrlLabel,$Vcloud_Url,$Vcloud_UsernameLabel,$Vcloud_Username,$Vcloud_PasswordLabel,$Vcloud_Password))
    $ConfigUI.controls.AddRange(@($CreateButton,$CancelButton,$NucGroup,$VcloudGroup,$SiteTokenLabel,$SiteToken,$IgnoreWarnings,$IgnoreErrors,$NonInteractive))

    $SiteToken.BringToFront()

    $ConfigUI.AcceptButton = $CreateButton
    $ConfigUI.CancelButton = $CancelButton

    $CreateButton.Add_Click({ CreateConfig })
    $CancelButton.Add_Click({ $ConfigUI.DialogResult = [System.Windows.Forms.DialogResult]::Cancel })

    return $ConfigUI.ShowDialog()
}
