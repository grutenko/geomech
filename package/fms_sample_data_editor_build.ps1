$Version = (Get-Content $PSScriptRoot/../version.txt)
$Version = $Version.Trim()
$WorkPath = "$PSScriptRoot/../build"
$DistPath = "$PSScriptRoot/../dist"
Write-Output $Version
(Get-Content $PSScriptRoot/versionfile.yml.in).Replace('#VERSION#', $Version) | Set-Content $WorkPath/versionfile.yml
$Name = "geomech." + $Version
create-version-file $WorkPath/versionfile.yml --outfile $WorkPath/win32_versionfile.txt

pyinstaller --onefile `
            --windowed `
            --noconfirm `
            --clean `
            --strip `
            --specpath=$WorkPath `
            --distpath=$DistPath `
            --workpath=$WorkPath `
            --name=$Name `
            --add-data=$PSScriptRoot/../icons:icons `
            --icon=$PSScriptRoot/../icons/logo.ico `
            --version-file=$WorkPath/win32_versionfile.txt `
            --runtime-hook=$PSScriptRoot/hooks/env.py `
            --hidden-import=wx._xml `
            --hidden-import=pony.orm.dbproviders `
            --hidden-import=pony.orm.dbproviders.postgres `
            --hidden-import=psycopg2 `
            --hidden-import=transliterate `
            --optimize=2 `
            $PSScriptRoot/../main.py