function ShowDialog($FilePath)
{
    Add-Type -AssemblyName System.Windows.Forms
    [System.Windows.Forms.Application]::EnableVisualStyles()

    $ConfigUI                        = New-Object system.Windows.Forms.Form
    $ConfigUI.ClientSize             = New-Object System.Drawing.Point(330,454)
    $ConfigUI.text                   = "Config Creator"
    $ConfigUI.FormBorderStyle        = 'FixedDialog'
    $ConfigUI.TopMost                = $true

    $Vcloud_LinkLabel                = New-Object system.Windows.Forms.LinkLabel
    $Vcloud_LinkLabel.text           = "Click here to copy the URL for a Google Doc containing setup information. Open in an S1-linked browser."
    $Vcloud_LinkLabel.AutoSize       = $true
    $Vcloud_LinkLabel.MaximumSize    = New-Object System.Drawing.Size(280,0)
    $Vcloud_LinkLabel.location       = New-Object System.Drawing.Point(15,20)
    $Vcloud_LinkLabel.Font           = New-Object System.Drawing.Font('Microsoft Sans Serif',8)
    $Vcloud_LinkLabel.LinkArea       = New-Object System.Windows.Forms.LinkArea(0, 10);

    $CopyTooltip                     = New-Object System.Windows.Forms.ToolTip
    $CopyTooltip.SetToolTip($Vcloud_LinkLabel, "")

    $Vcloud_UrlLabel                 = New-Object system.Windows.Forms.Label
    $Vcloud_UrlLabel.text            = "Url"
    $Vcloud_UrlLabel.AutoSize        = $true
    $Vcloud_UrlLabel.width           = 25
    $Vcloud_UrlLabel.height          = 10
    $Vcloud_UrlLabel.location        = New-Object System.Drawing.Point(15,50)
    $Vcloud_UrlLabel.Font            = New-Object System.Drawing.Font('Microsoft Sans Serif',10)

    $Vcloud_Url                      = New-Object system.Windows.Forms.TextBox
    $Vcloud_Url.multiline            = $false
    $Vcloud_Url.width                = 162
    $Vcloud_Url.height               = 20
    $Vcloud_Url.location             = New-Object System.Drawing.Point(123,50)
    $Vcloud_Url.Font                 = New-Object System.Drawing.Font('Microsoft Sans Serif',10)

    $Vcloud_UsernameLabel            = New-Object system.Windows.Forms.Label
    $Vcloud_UsernameLabel.text       = "Username"
    $Vcloud_UsernameLabel.AutoSize   = $true
    $Vcloud_UsernameLabel.width      = 25
    $Vcloud_UsernameLabel.height     = 10
    $Vcloud_UsernameLabel.location   = New-Object System.Drawing.Point(15,80)
    $Vcloud_UsernameLabel.Font       = New-Object System.Drawing.Font('Microsoft Sans Serif',10)

    $Vcloud_Username                 = New-Object system.Windows.Forms.TextBox
    $Vcloud_Username.multiline       = $false
    $Vcloud_Username.width           = 162
    $Vcloud_Username.height          = 20
    $Vcloud_Username.location        = New-Object System.Drawing.Point(123,80)
    $Vcloud_Username.Font            = New-Object System.Drawing.Font('Microsoft Sans Serif',10)

    $Vcloud_PasswordLabel            = New-Object system.Windows.Forms.Label
    $Vcloud_PasswordLabel.text       = "Password"
    $Vcloud_PasswordLabel.AutoSize   = $true
    $Vcloud_PasswordLabel.width      = 25
    $Vcloud_PasswordLabel.height     = 10
    $Vcloud_PasswordLabel.location   = New-Object System.Drawing.Point(15,110)
    $Vcloud_PasswordLabel.Font       = New-Object System.Drawing.Font('Microsoft Sans Serif',10)

    $Vcloud_Password                  = New-Object system.Windows.Forms.TextBox
    $Vcloud_Password.multiline        = $false
    $Vcloud_Password.width            = 162
    $Vcloud_Password.height           = 20
    $Vcloud_Password.passwordchar     = "*"
    $Vcloud_Password.location         = New-Object System.Drawing.Point(123,110)
    $Vcloud_Password.Font             = New-Object System.Drawing.Font('Microsoft Sans Serif',10)

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

    $VcloudGroup                     = New-Object system.Windows.Forms.Groupbox
    $VcloudGroup.height              = 143
    $VcloudGroup.width               = 306
    $VcloudGroup.text                = "VCloud"
    $VcloudGroup.location            = New-Object System.Drawing.Point(13,18)

    $NucGroup                        = New-Object system.Windows.Forms.Groupbox
    $NucGroup.height                 = 107
    $NucGroup.width                  = 306
    $NucGroup.text                   = "NUC"
    $NucGroup.location               = New-Object System.Drawing.Point(13,176)

    $SiteTokenLabel                  = New-Object system.Windows.Forms.Label
    $SiteTokenLabel.text             = "Site Token"
    $SiteTokenLabel.AutoSize         = $true
    $SiteTokenLabel.width            = 25
    $SiteTokenLabel.height           = 10
    $SiteTokenLabel.location         = New-Object System.Drawing.Point(16,302)
    $SiteTokenLabel.Font             = New-Object System.Drawing.Font('Microsoft Sans Serif',10)

    $SiteToken                       = New-Object system.Windows.Forms.TextBox
    $SiteToken.multiline             = $false
    $SiteToken.width                 = 298
    $SiteToken.height                = 20
    $SiteToken.location              = New-Object System.Drawing.Point(16,320)
    $SiteToken.Font                  = New-Object System.Drawing.Font('Microsoft Sans Serif',10)

    $IgnoreWarnings                  = New-Object system.Windows.Forms.CheckBox
    $IgnoreWarnings.text             = "Ignore Warnings?"
    $IgnoreWarnings.AutoSize         = $true
    $IgnoreWarnings.height           = 20
    $IgnoreWarnings.location         = New-Object System.Drawing.Point(28,351)
    $IgnoreWarnings.Font             = New-Object System.Drawing.Font('Microsoft Sans Serif',10)

    $IgnoreErrors                    = New-Object system.Windows.Forms.CheckBox
    $IgnoreErrors.text               = "Ignore Errors?"
    $IgnoreErrors.AutoSize           = $true
    $IgnoreErrors.height             = 20
    $IgnoreErrors.location           = New-Object System.Drawing.Point(28,376)
    $IgnoreErrors.Font               = New-Object System.Drawing.Font('Microsoft Sans Serif',10)

    $NonInteractive                  = New-Object system.Windows.Forms.CheckBox
    $NonInteractive.text             = "Non-Interactive?"
    $NonInteractive.AutoSize         = $true
    $NonInteractive.height           = 20
    $NonInteractive.location         = New-Object System.Drawing.Point(180,351)
    $NonInteractive.Font             = New-Object System.Drawing.Font('Microsoft Sans Serif',10)

    $CreateButton                    = New-Object system.Windows.Forms.Button
    $CreateButton.text               = "Create"
    $CreateButton.width              = 60
    $CreateButton.height             = 30
    $CreateButton.location           = New-Object System.Drawing.Point(104,409)
    $CreateButton.Font               = New-Object System.Drawing.Font('Microsoft Sans Serif',10)

    $CancelButton                    = New-Object system.Windows.Forms.Button
    $CancelButton.text               = "Cancel"
    $CancelButton.width              = 60
    $CancelButton.height             = 30
    $CancelButton.location           = New-Object System.Drawing.Point(173,409)
    $CancelButton.Font               = New-Object System.Drawing.Font('Microsoft Sans Serif',10)

    $VcloudGroup.controls.AddRange(@($Vcloud_UrlLabel,$Vcloud_Url,$Vcloud_UsernameLabel,$Vcloud_Username,$Vcloud_PasswordLabel,$Vcloud_Password,$Vcloud_LinkLabel))
    $NucGroup.controls.AddRange(@($Nuc_UsernameLabel,$Nuc_Username,$Nuc_PasswordLabel,$Nuc_Password,$Nuc_Autologon))
    $ConfigUI.controls.AddRange(@($VcloudGroup,$NucGroup,$SiteTokenLabel,$SiteToken,$IgnoreWarnings,$IgnoreErrors,$NonInteractive,$CreateButton,$CancelButton))

    $SiteToken.BringToFront()

    $ConfigUI.AcceptButton = $CreateButton
    $ConfigUI.CancelButton = $CancelButton

    $Vcloud_Url.Text = "https://vcloud.sentinelone.skytapdns.com/"
    $Vcloud_Username.Text = "sentinel"
    $IgnoreWarnings.Checked = $true

    $Vcloud_LinkLabel.Add_Click(
    {
        $CopyTooltip.SetToolTip($Vcloud_LinkLabel, "")
        Set-Clipboard -Value "https://docs.google.com/document/d/1uY1_32poau6uA7Xnki9bB3DxGm5j5C26_FAKG0HbOV4/"
    })

    $CreateButton.Add_Click(
    {
        $result = [ordered]@{}

        $valid = $true
        
        if ($Vcloud_Url.Text -eq "") {
            $Vcloud_Url.BackColor = [System.Drawing.Color]::LightPink
            $valid = $false
        } else {
            $Vcloud_Url.BackColor = [System.Drawing.SystemColors]::Window
        }

        if ($Vcloud_Username.Text -eq "") {
            $Vcloud_Username.BackColor = [System.Drawing.Color]::LightPink
            $valid = $false
        } else {
            $Vcloud_Username.BackColor = [System.Drawing.SystemColors]::Window
        }

        if ($Vcloud_Password.Text -eq "") {
            $Vcloud_Password.BackColor = [System.Drawing.Color]::LightPink
            $valid = $false
        } else {
            $Vcloud_Password.BackColor = [System.Drawing.SystemColors]::Window
        }

        if ($Nuc_Autologon.Checked -eq $true) {
            if ($Nuc_Username.Text -eq "") {
                $Nuc_Username.BackColor = [System.Drawing.Color]::LightPink
                $valid = $false
            } else {
                $Nuc_Username.BackColor = [System.Drawing.SystemColors]::Window
            }

            if ($Nuc_Password.Text -eq "") {
                $Nuc_Password.BackColor = [System.Drawing.Color]::LightPink
                $valid = $false
            } else {
                $Nuc_Password.BackColor = [System.Drawing.SystemColors]::Window
            }
        }

        if (!($valid)) {
            return
        }

        Write-Host("Attempting to create '$FilePath'.")

        $result["Vcloud"] = [ordered]@{}
        $result["Vcloud"]["Url"] = $Vcloud_Url.Text
        $result["Vcloud"]["Username"] = $Vcloud_Username.Text
        $result["Vcloud"]["Password"] = $Vcloud_Password.Text

        $result["Windows"] = [ordered]@{}
        $result["Windows"]["EnableAutologon"] = $Nuc_Autologon.Checked
        $result["Windows"]["Username"] = $Nuc_Username.Text
        $result["Windows"]["Password"] = $Nuc_Password.Text

        if ($SiteToken.Text.Trim() -eq "") {
            $result["SiteToken"] = $null
        }
        else {
            $result["SiteToken"] = $SiteToken.Text
        }

        $result["IgnoreWarnings"] = $IgnoreWarnings.Checked
        $result["IgnoreErrors"] = $IgnoreErrors.Checked
        $result["NonInteractive"] = $NonInteractive.Checked

        ConvertTo-Json -Depth 5 -InputObject $result | Set-Content $FilePath
        $ConfigUI.DialogResult = [System.Windows.Forms.DialogResult]::OK
    })

    $CancelButton.Add_Click({ $ConfigUI.DialogResult = [System.Windows.Forms.DialogResult]::Cancel })

    return $ConfigUI.ShowDialog()
}
