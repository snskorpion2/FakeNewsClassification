# download-data-parallel.ps1
# Requires PowerShell 7+

# Basis-Ordner
$baseDir = Join-Path $PSScriptRoot 'src\data'

# Liste der Quellen
$sources = @(
    @{ Name = 'Saurabh Shahane - Fake_News_Classification'; Url = 'https://zenodo.org/records/4561253/files/WELFake_Dataset.csv'; FileName = 'WELFake_Dataset.csv' },
    @{ Name = 'GonzaloA - fake_news'; Url = 'https://huggingface.co/datasets/GonzaloA/fake_news/resolve/main/evaluation.csv'; FileName = 'evaluation.csv' },
    @{ Name = 'GonzaloA - fake_news'; Url = 'https://huggingface.co/datasets/GonzaloA/fake_news/resolve/main/test.csv'; FileName = 'test.csv' },
    @{ Name = 'GonzaloA - fake_news'; Url = 'https://huggingface.co/datasets/GonzaloA/fake_news/resolve/main/train.csv'; FileName = 'train.csv' },
    @{ Name = 'ErfanMoosaviMonazzah - fake-news-detection-dataset-English'; Url = 'https://huggingface.co/datasets/ErfanMoosaviMonazzah/fake-news-detection-dataset-English/resolve/main/validation.tsv'; FileName = 'validation.tsv' },
    @{ Name = 'ErfanMoosaviMonazzah - fake-news-detection-dataset-English'; Url = 'https://huggingface.co/datasets/ErfanMoosaviMonazzah/fake-news-detection-dataset-English/resolve/main/test.tsv'; FileName = 'test.tsv' },
    @{ Name = 'ErfanMoosaviMonazzah - fake-news-detection-dataset-English'; Url = 'https://huggingface.co/datasets/ErfanMoosaviMonazzah/fake-news-detection-dataset-English/resolve/main/train.tsv'; FileName = 'train.tsv' }
    @{ Name = 'Bhavik Jikadara - Fake News Detection'; Url = 'https://drive.google.com/uc?export=download&id=1MU4BSdFGdb8tyJHUUB_t1pQ3GaHUumnR'; FileName = 'fake.csv' },
    @{ Name = 'Bhavik Jikadara - Fake News Detection'; Url = 'https://drive.google.com/uc?export=download&id=10Lo7cLLo5Icd4jdfRtfe_uS9qajZKNHh'; FileName = 'true.csv' },
    @{ Name = 'Aleksei Golovin - Fake_News'; Url = 'https://drive.google.com/uc?export=download&id=1dGbmtcPBr3x3oaHHoHsDUqxgPRscY7SG'; FileName = 'FakeNewsNet.csv' }
)

# Basis-Verzeichnis anlegen, falls es nicht existiert
if (-not (Test-Path $baseDir)) {
    New-Item -Path $baseDir -ItemType Directory -Force | Out-Null
}

# Parallel-Download aller Quellen (ThrottleLimit steuert max. gleichzeitige Downloads)
$sources | ForEach-Object -Parallel {
    $src = $_
    $targetDir = Join-Path $using:baseDir $src.Name

    # Ziel-Unterordner anlegen
    if (-not (Test-Path $targetDir)) {
        New-Item -Path $targetDir -ItemType Directory -Force | Out-Null
    }

    $outFile = Join-Path $targetDir $src.FileName
    Write-Host "[$($PID)] Lade herunter: $($src.Url)"
    Invoke-WebRequest -Uri $src.Url -OutFile $outFile -UseBasicParsing

    # Keine ZIP-Extraktion mehr
} -ThrottleLimit 4

Write-Host "Alle Downloads abgeschlossen."
