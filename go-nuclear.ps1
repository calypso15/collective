Invoke-Command -ScriptBlock {
    winget install python --accept-package-agreements --accept-source-agreements
    winget install git.git --accept-package-agreements --accept-source-agreements
}

$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
Set-Location $HOME

Invoke-Command -ScriptBlock {
    git clone https://github.com/calypso15/go-nuclear.git
}

Set-Location $HOME/go-nuclear

Invoke-Command -ScriptBlock {
    pip install -r requirements.txt
    python check-requirements.py
}

Write-Output "TEST"