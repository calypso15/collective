[CmdletBinding()]
param (
    [Parameter()]
    [string]
    $Step,

    [Parameter()]
    [string]
    $EnableAutologon,

    [Parameter()]
    [string]
    $Username,

    [Parameter()]
    [string]
    $Password,

    [Parameter()]
    [string]
    $ConfigPath
)

if ($ConfigPath -in  $PSBoundParameters.Keys)
{

    $config = Get-Content $ConfigPath | ConvertFrom-Json

    if ('Step' -notin  $PSBoundParameters.Keys)
    {
        $Step = $null
    }

    if ('EnableAutologon' -notin  $PSBoundParameters.Keys) {
        $EnableAutologon = $null
    }

    if ('Username' -notin  $PSBoundParameters.Keys) {
        $EnableAutologon = $null
        $Username = $null
        $Password = $null
    }

    if ('Password' -notin  $PSBoundParameters.Keys) {
        $EnableAutologon = $null
        $Username = $null
        $Password = $null
    }
}

$Running = $false

function Should-Run([string] $TargetStep)
{
    if ($global:Step -eq $TargetStep -or $global:Step -eq $null) {
        $global:Running = $true
    }

    return $global:Running
}

if(Should-Run "Enable-Autologon")
{
    $RegistryPath = 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon'
    if((Get-ItemProperty $RegistryPath -ErrorAction SilentlyContinue | Select-Object -ExpandProperty AutoAdminLogon) -ne "1")
    {
        if($EnableAutologon -eq $null)
        {
            $EnableAutologon = ((Read-Host 'Enable Windows Autologon [y/n]? ').ToLower() -eq "y")
        }

        if($EnableAutologon)
        {
            Write-Host('Enabling autologon...')
            $Username = Read-Host "NUC Windows Username: "
            $Password = Read-Host "NUC Windows Password: "
            Set-ItemProperty $RegistryPath 'AutoAdminLogon' -Value "1" -Type String
            Set-ItemProperty $RegistryPath 'DefaultUsername' -Value "$Username" -type String
            Set-ItemProperty $RegistryPath 'DefaultPassword' -Value "$Password" -type String
        }
    }
}

if(Should-Run "Install-Packages")
{
    # Install other chocolatey packages
    Set-Location $HOME/Documents/go-nuclear/choco

    Write-Host('Installing chocolatey packages...')
    Invoke-Command -ScriptBlock {
        choco install packages.config --yes
    }

    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

    if($LastExitCode -eq 3010) {
        Write-Host('Restarting system...')
        Register-ScheduledTask -TaskName "Resume-Setup" -Principal (New-ScheduledTaskPrincipal -UserID $env:USERNAME -RunLevel Highest -LogonType Interactive) -Trigger (New-ScheduledTaskTrigger -AtLogon) -Action (New-ScheduledTaskAction -Execute "${Env:WinDir}\System32\WindowsPowerShell\v1.0\powershell.exe" -Argument ("-NoExit -ExecutionPolicy Bypass -File `"" + $PSCommandPath + "`" "+@$PSBoundParameters+" -Step: Run-Python-Setup")) -Force;
        Restart-Computer
    }
}

if(Should-Run "Run-Python-Setup")
{
    Unregister-ScheduledTask -TaskName "Resume-Setup" -Confirm:$false -ErrorAction SilentlyContinue

    # Start python script
    Set-Location $HOME/Documents/go-nuclear/python

    Write-Host('Starting Python setup...')
    pip install -r requirements.txt
    python setup.py
    Write-Host('')
}

if($LastExitCode -ne 0) {
    throw 'Setup failed, aborting.'
}
