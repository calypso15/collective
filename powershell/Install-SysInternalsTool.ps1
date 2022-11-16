#Install SysInternals BGInfo/AutoLogon tools
function Install-SysInternalsTool
{
    #Target directory is %WinDir%C:\Windows\System32\SysInternals
    $targetDir = Join-Path $env:WinDir "System32\SysInternals"

    #Tools to be downloaded
    $tools = @{
        Bginfo    = "http://live.sysinternals.com/Bginfo.exe"
        Autologon = "http://live.sysinternals.com/Autologon.exe"
    }

    #Create Directory
    Write-Verbose "Create Directory: $targetDir"
    New-Item -ItemType Directory -Path $targetDir -Force | Out-Null

    #Download tools to target directory
    try{
        $wc = New-Object System.Net.WebClient
        foreach($tool in $tools.Values){
            $filePath = Join-Path $targetDir ([IO.Path]::GetFileName($tool))
            Write-Verbose "Downloading $tool"
            $wc.DownloadFile($tool,$filePath)
        }
    }
    finally{
        $wc.Dispose()
    }
}

#Enable auto logon using SysInternals AutoLogon.exe
function Enable-AutoLogon
{
param(
[string] $UserName,
[string] $Password
)
    $exePath = Join-Path $env:WinDir "System32\SysInternals\AutoLogon.exe"
    if(!(Test-Path $exePath)){
        Write-Error "AutoLogon.exe is not found at $exePath"
    }

    $paths = $UserName.Split("\")
    $domain = $paths[0]
    $user   = $paths[1]

    Start-Process -FilePath  $exePath -ArgumentList "/accepteula", $user, $domain, $password -Wait
}

#Register BGInfo.exe to startup comand
function Register-BGInfoStartup
{
    $exePath = Join-Path $env:WinDir "System32\SysInternals\BGInfo.exe"
    if(!(Test-Path $exePath)){
        Write-Error "BGInfo.exe is not found at $exePath"
    }

    #Register Startup command for All User
    $startupPath =  Join-Path $env:ProgramData "Microsoft\Windows\Start Menu\Programs\Startup\BGInfo.lnk"
    $shell = New-Object -COM WScript.Shell
    $shortcut = $shell.CreateShortcut($startupPath)
    $shortcut.TargetPath = $exePath
    $shortcut.Arguments = "/accepteula /timer:0 /silent"
    $shortcut.Save()
}