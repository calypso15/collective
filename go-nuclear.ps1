# Install Chocolatey
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install important tools with Chocolatey
Invoke-Command -ScriptBlock {
    choco install git --yes
    choco install python --yes
}

# Clone the go-nuclear repo if it doesn't already exist
if (!Test-Path -Path $HOME/go-nuclear) {
    Invoke-Command -ScriptBlock {
        git clone https://github.com/calypso15/go-nuclear.git
    }
}

Set-Location $HOME/go-nuclear

Invoke-Command -ScriptBlock {
    git pull
}

Invoke-Command -ScriptBlock {
    pip install -r requirements.txt
    python check-requirements.py
}

Write-Output "TEST"