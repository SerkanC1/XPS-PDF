import os
import glob
import subprocess
import shutil
from pathlib import Path
from pypdf import PdfWriter, PdfReader

def ensure_temp_dir(base_dir):
    """Proje dizininde temp klasörünü oluşturur."""
    temp_dir = os.path.join(base_dir, "temp")
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    return temp_dir

def convert_xps_to_pdf_with_pymupdf(xps_path, pdf_path):
    """PyMuPDF (fitz) kullanarak XPS dosyasını PDF'e dönüştürür."""
    try:
        import fitz  # PyMuPDF

        # XPS dosyasını aç
        doc = fitz.open(xps_path)
        
        # PDF olarak kaydet
        doc.save(pdf_path)
        doc.close()
        
        if os.path.exists(pdf_path):
            return True
        return False
    except Exception as e:
        print(f"PyMuPDF dönüştürme hatası: {e}")
        return False

def convert_with_gxps(xps_path, pdf_path):
    """GhostXPS ile dönüştürmeyi dener."""
    try:
        # Belirtilen GhostXPS yolu
        gs_path = r"C:\Program Files\gs\ghostxps-10.04.0-win64"
        gxps_cmd = os.path.join(gs_path, "gxpswin64.exe")
        
        if not os.path.exists(gxps_cmd):
            print(f"GhostXPS bulunamadı: {gxps_cmd}")
            return False
            
        # GhostXPS ile dönüştür
        subprocess.run([
            gxps_cmd, 
            "-sDEVICE=pdfwrite", 
            "-dNOPAUSE", 
            "-dBATCH", 
            "-dQUIET",
            f"-sOutputFile={pdf_path}", 
            xps_path
        ], check=True)
        
        return os.path.exists(pdf_path)
    except Exception as e:
        print(f"GhostXPS dönüştürme hatası: {e}")
        return False

def compress_pdf(input_pdf, output_pdf, compression_level="medium"):
    """PDF dosyasını sıkıştırır."""
    try:
        print(f"PDF sıkıştırılıyor: {os.path.basename(input_pdf)}")
        
        # PyPDF ile sıkıştırma
        reader = PdfReader(input_pdf)
        writer = PdfWriter()
        
        # Sıkıştırma seviyesi ayarları
        if compression_level == "low":
            image_quality = 90
        elif compression_level == "high":
            image_quality = 60
        else:  # medium
            image_quality = 75
        
        # Her sayfayı ekle
        for page in reader.pages:
            writer.add_page(page)
        
        # Metadata'yı kopyala
        metadata = reader.metadata
        if metadata:
            writer.add_metadata(metadata)
        
        # Sıkıştırma uygula
        writer.compress = True
        
        # Dosyayı kaydet
        with open(output_pdf, "wb") as f:
            writer.write(f)
        
        # Boyut bilgilerini göster
        input_size = os.path.getsize(input_pdf) / (1024 * 1024)  # MB
        output_size = os.path.getsize(output_pdf) / (1024 * 1024)  # MB
        compression_ratio = (1 - (output_size / input_size)) * 100 if input_size > 0 else 0
        
        print(f"Sıkıştırma oranı: %{compression_ratio:.2f} "
              f"({input_size:.2f} MB -> {output_size:.2f} MB)")
        
        return True
    except Exception as e:
        print(f"PDF sıkıştırma hatası: {e}")
        # Hata durumunda orijinal dosyayı kopyala
        shutil.copy(input_pdf, output_pdf)
        return False

def merge_pdfs(pdf_files, output_path):
    """PdfWriter kullanarak PDF dosyalarını birleştirir."""
    try:
        writer = PdfWriter()
        
        # Her dosyayı birleştir
        for pdf_file in pdf_files:
            print(f"Ekleniyor: {os.path.basename(pdf_file)}")
            reader = PdfReader(pdf_file)
            for page in reader.pages:
                writer.add_page(page)
        
        # Birleştirilmiş PDF'i kaydet
        with open(output_path, "wb") as f:
            writer.write(f)
            
        return True
    except Exception as e:
        print(f"PDF birleştirme hatası: {e}")
        return False

def main():
    print("XPS-PDF Dönüştürücü ve Birleştirici")
    print("===================================")
    
    # Proje dizinini al
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Proje dizini: {script_dir}")
    
    # Geçici klasörü oluştur
    temp_dir = ensure_temp_dir(script_dir)
    print(f"Geçici klasör: {temp_dir}")
    
    # XPS dosyalarının bulunduğu klasör
    input_folder = input("XPS dosyalarının bulunduğu klasörü girin: ")
    if not os.path.exists(input_folder):
        print("Belirtilen klasör bulunamadı!")
        return
    
    # Çıktı PDF dosyasının adı
    output_pdf = input("Çıktı PDF dosyasının adını girin (örn: birlestirilmis.pdf): ")
    
    # Sıkıştırma seviyesi
    print("\nSıkıştırma seviyesi seçin:")
    print("1. Düşük (yüksek kalite, büyük dosya)")
    print("2. Orta (dengeli) - Önerilen")
    print("3. Yüksek (düşük kalite, küçük dosya)")
    compression_choice = input("Seçiminiz (1/2/3): ")
    
    if compression_choice == "1":
        compression_level = "low"
    elif compression_choice == "3":
        compression_level = "high"
    else:
        compression_level = "medium"
    
    # Tüm XPS dosyalarını bul ve alfabetik sırala
    xps_files = sorted(glob.glob(os.path.join(input_folder, "*.xps")))
    
    if not xps_files:
        print(f"Belirtilen klasörde XPS dosyası bulunamadı: {input_folder}")
        return
    
    total_files = len(xps_files)
    print(f"Toplam {total_files} XPS dosyası bulundu.")
    
    # İşlenen PDF dosyalarının listesi
    pdf_files = []
    
    # Her bir XPS dosyasını işle
    for i, xps_file in enumerate(xps_files, 1):
        file_name = os.path.basename(xps_file)
        base_name = Path(file_name).stem
        pdf_name = f"{i:03d}_{base_name}.pdf"
        pdf_path = os.path.join(temp_dir, pdf_name)
        
        print(f"\n[{i}/{total_files}] {file_name} dönüştürülüyor...")
        
        # PyMuPDF ile dönüştürmeyi dene
        converted = convert_xps_to_pdf_with_pymupdf(xps_file, pdf_path)
        
        # PyMuPDF başarısız olursa, GhostXPS ile dene
        if not converted:
            converted = convert_with_gxps(xps_file, pdf_path)
        
        # Dosya dönüştürüldü mü kontrol et
        if converted and os.path.exists(pdf_path):
            pdf_files.append(pdf_path)
            print(f"Dönüştürme başarılı: {pdf_path}")
        else:
            print(f"Dönüştürme başarısız: {file_name}")
            
            # Manuel dönüştürme seçeneği sun
            print("\nBu dosyayı manuel olarak dönüştürmek ister misiniz? (E/H): ", end="")
            manual_convert = input().lower()
            
            if manual_convert == 'e':
                print(f"XPS dosyası açılıyor: {xps_file}")
                print("Lütfen şu adımları izleyin:")
                print("1. Dosya açıldığında, Yazdır (Ctrl+P) seçeneğini kullanın")
                print('2. "Microsoft Print to PDF" yazıcısını seçin')
                print(f"3. Dosyayı şu isimle kaydedin: {pdf_path}")
                
                # Dosyayı aç
                os.startfile(xps_file)
                
                # Kullanıcının işlemi tamamlaması için bekle
                input("\nDönüştürme işlemini tamamladıktan sonra ENTER tuşuna basın...")
                
                if os.path.exists(pdf_path):
                    pdf_files.append(pdf_path)
                    print(f"Manuel dönüştürme başarılı: {pdf_path}")
                else:
                    alt_path = input("Eğer dosyayı farklı bir konuma kaydettiyseniz, tam yolunu girin (atlamak için ENTER): ")
                    if alt_path and os.path.exists(alt_path):
                        shutil.copy(alt_path, pdf_path)
                        pdf_files.append(pdf_path)
                        print(f"Dosya kopyalandı: {alt_path} -> {pdf_path}")
    
    if not pdf_files:
        print("Hiçbir dosya dönüştürülemedi.")
        return
    
    # PDF dosyalarını birleştir
    print(f"\nPDF dosyaları birleştiriliyor... ({len(pdf_files)} dosya)")
    temp_merged_pdf = os.path.join(temp_dir, "merged_temp.pdf")
    
    # PdfWriter kullanarak birleştir
    if merge_pdfs(pdf_files, temp_merged_pdf):
        print(f"Birleştirme tamamlandı.")
        
        # PDF'i sıkıştır
        output_path = os.path.join(script_dir, output_pdf)
        compress_pdf(temp_merged_pdf, output_path, compression_level)
        
        print(f"\nİşlem tamamlandı! Birleştirilmiş PDF: {output_path}")
    else:
        print("Birleştirme işlemi başarısız oldu.")
        return
    
    # Geçici dosyaları temizle
    cleanup = input("\nGeçici PDF dosyaları silinsin mi? (E/H): ").lower()
    if cleanup == 'e':
        try:
            for pdf_file in pdf_files:
                os.remove(pdf_file)
            if os.path.exists(temp_merged_pdf):
                os.remove(temp_merged_pdf)
            print(f"Geçici dosyalar temizlendi.")
        except Exception as e:
            print(f"Dosya temizleme hatası: {e}")

if __name__ == "__main__":
    main()
