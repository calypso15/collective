[CmdletBinding()]
param (
    [Parameter()]
    [string]
    $ConfigFile
)

Write-Host("Attempting to create file '$ConfigFile'.")

Add-Type -AssemblyName System.Windows.Forms
[System.Windows.Forms.Application]::EnableVisualStyles()

$ConfigUI                        = New-Object system.Windows.Forms.Form
$ConfigUI.ClientSize             = New-Object System.Drawing.Point(330,424)
$ConfigUI.text                   = "Config Creator"
$ConfigUI.TopMost                = $false

$NucGroup                        = New-Object system.Windows.Forms.Groupbox
$NucGroup.height                 = 107
$NucGroup.width                  = 306
$NucGroup.text                   = "NUC"
$NucGroup.location               = New-Object System.Drawing.Point(13,18)

$Nuc_UsernameLabel               = New-Object system.Windows.Forms.Label
$Nuc_UsernameLabel.text          = "Username"
$Nuc_UsernameLabel.AutoSize      = $true
$Nuc_UsernameLabel.width         = 25
$Nuc_UsernameLabel.height        = 10
$Nuc_UsernameLabel.location      = New-Object System.Drawing.Point(15,22)
$Nuc_UsernameLabel.Font          = New-Object System.Drawing.Font('Microsoft Sans Serif',10)

$Nuc_Username                    = New-Object system.Windows.Forms.TextBox
$Nuc_Username.multiline          = $false
$Nuc_Username.width              = 162
$Nuc_Username.height             = 20
$Nuc_Username.location           = New-Object System.Drawing.Point(123,19)
$Nuc_Username.Font               = New-Object System.Drawing.Font('Microsoft Sans Serif',10)

$Nuc_PasswordLabel               = New-Object system.Windows.Forms.Label
$Nuc_PasswordLabel.text          = "Password"
$Nuc_PasswordLabel.AutoSize      = $true
$Nuc_PasswordLabel.width         = 25
$Nuc_PasswordLabel.height        = 10
$Nuc_PasswordLabel.location      = New-Object System.Drawing.Point(15,51)
$Nuc_PasswordLabel.Font          = New-Object System.Drawing.Font('Microsoft Sans Serif',10)

$MaskedTextBox1                  = New-Object system.Windows.Forms.MaskedTextBox
$MaskedTextBox1.multiline        = $false
$MaskedTextBox1.width            = 162
$MaskedTextBox1.height           = 20
$MaskedTextBox1.location         = New-Object System.Drawing.Point(123,48)
$MaskedTextBox1.Font             = New-Object System.Drawing.Font('Microsoft Sans Serif',10)

$Nuc_Autologon                   = New-Object system.Windows.Forms.CheckBox
$Nuc_Autologon.text              = "Autologon?"
$Nuc_Autologon.AutoSize          = $false
$Nuc_Autologon.width             = 95
$Nuc_Autologon.height            = 20
$Nuc_Autologon.location          = New-Object System.Drawing.Point(15,79)
$Nuc_Autologon.Font              = New-Object System.Drawing.Font('Microsoft Sans Serif',10)

$VcloudGroup                     = New-Object system.Windows.Forms.Groupbox
$VcloudGroup.height              = 113
$VcloudGroup.width               = 306
$VcloudGroup.text                = "VCloud"
$VcloudGroup.location            = New-Object System.Drawing.Point(13,146)

$Vcloud_UrlLabel                 = New-Object system.Windows.Forms.Label
$Vcloud_UrlLabel.text            = "Url"
$Vcloud_UrlLabel.AutoSize        = $true
$Vcloud_UrlLabel.width           = 25
$Vcloud_UrlLabel.height          = 10
$Vcloud_UrlLabel.location        = New-Object System.Drawing.Point(17,23)
$Vcloud_UrlLabel.Font            = New-Object System.Drawing.Font('Microsoft Sans Serif',10)

$Vcloud_Url                      = New-Object system.Windows.Forms.TextBox
$Vcloud_Url.multiline            = $false
$Vcloud_Url.width                = 162
$Vcloud_Url.height               = 20
$Vcloud_Url.location             = New-Object System.Drawing.Point(123,19)
$Vcloud_Url.Font                 = New-Object System.Drawing.Font('Microsoft Sans Serif',10)

$Vcloud_UsernameLabel            = New-Object system.Windows.Forms.Label
$Vcloud_UsernameLabel.text       = "Username"
$Vcloud_UsernameLabel.AutoSize   = $true
$Vcloud_UsernameLabel.width      = 25
$Vcloud_UsernameLabel.height     = 10
$Vcloud_UsernameLabel.location   = New-Object System.Drawing.Point(17,52)
$Vcloud_UsernameLabel.Font       = New-Object System.Drawing.Font('Microsoft Sans Serif',10)

$Vcloud_Username                 = New-Object system.Windows.Forms.TextBox
$Vcloud_Username.multiline       = $false
$Vcloud_Username.width           = 162
$Vcloud_Username.height          = 20
$Vcloud_Username.location        = New-Object System.Drawing.Point(123,49)
$Vcloud_Username.Font            = New-Object System.Drawing.Font('Microsoft Sans Serif',10)

$Vcloud_PasswordLabel            = New-Object system.Windows.Forms.Label
$Vcloud_PasswordLabel.text       = "Password"
$Vcloud_PasswordLabel.AutoSize   = $true
$Vcloud_PasswordLabel.width      = 25
$Vcloud_PasswordLabel.height     = 10
$Vcloud_PasswordLabel.location   = New-Object System.Drawing.Point(17,82)
$Vcloud_PasswordLabel.Font       = New-Object System.Drawing.Font('Microsoft Sans Serif',10)

$MaskedTextBox2                  = New-Object system.Windows.Forms.MaskedTextBox
$MaskedTextBox2.multiline        = $false
$MaskedTextBox2.width            = 162
$MaskedTextBox2.height           = 20
$MaskedTextBox2.location         = New-Object System.Drawing.Point(123,79)
$MaskedTextBox2.Font             = New-Object System.Drawing.Font('Microsoft Sans Serif',10)

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
$SiteToken.width                 = 301
$SiteToken.height                = 20
$SiteToken.location              = New-Object System.Drawing.Point(16,290)
$SiteToken.Font                  = New-Object System.Drawing.Font('Microsoft Sans Serif',10)

$NonInteractive                  = New-Object system.Windows.Forms.CheckBox
$NonInteractive.text             = "Non-Interactive?"
$NonInteractive.AutoSize         = $false
$NonInteractive.width            = 95
$NonInteractive.height           = 20
$NonInteractive.location         = New-Object System.Drawing.Point(198,321)
$NonInteractive.Font             = New-Object System.Drawing.Font('Microsoft Sans Serif',10)

$IgnoreWarnings                  = New-Object system.Windows.Forms.CheckBox
$IgnoreWarnings.text             = "Ignore Warnings?"
$IgnoreWarnings.AutoSize         = $false
$IgnoreWarnings.width            = 95
$IgnoreWarnings.height           = 20
$IgnoreWarnings.location         = New-Object System.Drawing.Point(28,321)
$IgnoreWarnings.Font             = New-Object System.Drawing.Font('Microsoft Sans Serif',10)

$IgnoreErrors                    = New-Object system.Windows.Forms.CheckBox
$IgnoreErrors.text               = "Ignore Errors?"
$IgnoreErrors.AutoSize           = $false
$IgnoreErrors.width              = 95
$IgnoreErrors.height             = 20
$IgnoreErrors.location           = New-Object System.Drawing.Point(28,346)
$IgnoreErrors.Font               = New-Object System.Drawing.Font('Microsoft Sans Serif',10)

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

$ConfigUI.controls.AddRange(@($NucGroup,$VcloudGroup,$SiteTokenLabel,$SiteToken,$NonInteractive,$IgnoreWarnings,$IgnoreErrors,$CreateButton,$CancelButton))
$NucGroup.controls.AddRange(@($Nuc_UsernameLabel,$Nuc_Username,$Nuc_PasswordLabel,$MaskedTextBox1,$Nuc_Autologon))
$VcloudGroup.controls.AddRange(@($Vcloud_UrlLabel,$Vcloud_Url,$Vcloud_UsernameLabel,$Vcloud_Username,$Vcloud_PasswordLabel,$MaskedTextBox2))


#region Logic 

#endregion

[void]$ConfigUI.ShowDialog()