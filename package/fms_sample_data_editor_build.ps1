$Version = (Get-Content $PSScriptRoot/../version.txt)
$Version = $Version.Trim()
$WorkPath = "$PSScriptRoot/../build"
$DistPath = "$PSScriptRoot/../dist"
Write-Output $Version
(Get-Content $PSScriptRoot/versionfile.yml.in).Replace('#VERSION#', $Version) | Set-Content $WorkPath/versionfile.yml
$Name = "geomech-fms-sample-data-editor." + $Version
create-version-file $WorkPath/versionfile.yml --outfile $WorkPath/win32_versionfile.txt

pyinstaller --onefile `
            --windowed `
            --noconfirm `
            --clean `
            --splash=$PSScriptRoot/../icons/logo.png `
            --specpath=$WorkPath `
            --distpath=$DistPath `
            --workpath=$WorkPath `
            --name=$Name `
            --splash=../icons/logo.png `
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
            $PSScriptRoot/../fms_sample_data_editor_main.py