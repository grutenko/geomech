$Version = python $PSScriptRoot/../scripts/make_version.py | Out-String
$Version = $Version.Trim()
Write-Output $Version
(Get-Content $PSScriptRoot/versionfile.yml.in).Replace('#VERSION#', $Version) | Set-Content $PSScriptRoot/versionfile.yml
$VersionMaj = $Version -replace '\.[^\.]+$'
$Name = "geomech-" + $VersionMaj
create-version-file $PSScriptRoot/versionfile.yml --outfile $PSScriptRoot/win32_versionfile.txt
pyinstaller --onefile --windowed --noconfirm --clean --distpath=$PSScriptRoot/../dist --workpath=$PSScriptRoot/../build --name=$Name --add-data=$PSScriptRoot/../html:html --add-data=$PSScriptRoot/../icons:icons --icon=$PSScriptRoot/../icons/logo.ico --version-file=$PSScriptRoot/win32_versionfile.txt --runtime-hook=$PSScriptRoot/hooks/env.py --hidden-import=pony.orm.dbproviders --hidden-import=pony.orm.dbproviders.postgres --hidden-import=psycopg2 $PSScriptRoot/../main.py