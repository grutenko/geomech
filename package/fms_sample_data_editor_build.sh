#!/bin/bash

# Получаем версию из файла
Version=$(cat "$(dirname "$0")/../version.txt")
Version=$(echo "$Version" | xargs)  # Убираем пробелы в начале и конце
WorkPath="$(dirname "$0")/../build"
DistPath="$(dirname "$0")/../dist"
echo "$Version"

# Заменяем #VERSION# в файле versionfile.yml.in на актуальную версию
sed "s/#VERSION#/$Version/g" "$(dirname "$0")/versionfile.yml.in" > "$WorkPath/versionfile.yml"

Name="geomech-fms-sample-data-editor.$Version"

# Создаем версионный файл
create-version-file "$WorkPath/versionfile.yml" --outfile "$WorkPath/win32_versionfile.txt"

# Запускаем PyInstaller с указанными параметрами
pyinstaller --onefile \
            --windowed \
            --noconfirm \
            --clean \
            --specpath="$WorkPath" \
            --distpath="$DistPath" \
            --workpath="$WorkPath" \
            --name="$Name" \
            --strip \
            --add-data="$(dirname "$0")/../icons:icons" \
            --icon="$(dirname "$0")/../icons/logo.png" \
            --version-file="$WorkPath/win32_versionfile.txt" \
            --runtime-hook="$(dirname "$0")/hooks/env.py" \
            --hidden-import=wx._xml \
            --hidden-import=pony.orm.dbproviders \
            --hidden-import=pony.orm.dbproviders.postgres \
            --hidden-import=psycopg2 \
            --hidden-import=transliterate \
            --optimize=2 \
            "$(dirname "$0")/../fms_sample_data_editor_main.py"
