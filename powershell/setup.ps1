
# Install other chocolatey packages
Set-Location $HOME/Documents/go-nuclear/choco

Write-Host('Installing chocolatey packages...')
Invoke-Command -ScriptBlock {
    choco install packages.config --yes
}

# Start python script
Set-Location $HOME/Documents/go-nuclear/python
pip install -r requirements.txt
python setup.py
Write-Host('')

if($LastExitCode -ne 0) {
    throw 'Setup failed, aborting.'
}
