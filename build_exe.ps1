# build_exe.ps1
# Script untuk build WordToPDF.exe menggunakan PyInstaller
# Jalankan: .\build_exe.ps1

Write-Host "=== Word to PDF - Build EXE ===" -ForegroundColor Cyan

# 1. Install dependencies
Write-Host "`n[1/3] Install dependencies..." -ForegroundColor Yellow
pip install pyinstaller tkinterdnd2 docx2pdf -q

# 2. Build
Write-Host "[2/3] Building .exe (mungkin 1-2 menit)..." -ForegroundColor Yellow
python -m PyInstaller word_to_pdf.spec --clean --noconfirm

# 3. Hasil
$exe = "dist\WordToPDF.exe"
if (Test-Path $exe) {
    $size = [math]::Round((Get-Item $exe).Length / 1MB, 1)
    Write-Host "`n[3/3] BERHASIL!" -ForegroundColor Green
    Write-Host "File EXE: $((Get-Item $exe).FullName)" -ForegroundColor Green
    Write-Host "Ukuran  : $size MB" -ForegroundColor Green
    Write-Host "`nBagikan file 'dist\WordToPDF.exe' ke pengguna lain." -ForegroundColor Cyan
} else {
    Write-Host "`n[3/3] BUILD GAGAL. Cek output di atas." -ForegroundColor Red
}
