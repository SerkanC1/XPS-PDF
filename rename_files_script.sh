#!/bin/bash

# Kullanıcıdan dosya adının başlangıç karakterlerini al
read -p "Dosya adının başlangıç karakterlerini girin (örn. OB): " prefix

# Dosya adının başına eklenecek karakterleri al
read -p "Dosya adının başına eklenecek karakterleri girin (örn. A_): " prepend_chars

# Belirtilen ön eke sahip dosyaları bul ve yeniden adlandır
for file in *; do
    # Dosyanın başlangıç karakterlerini kontrol et
    if [[ "$file" == "$prefix"* ]]; then
        # Yeni dosya adını oluştur
        new_filename="${prepend_chars}${file}"
        
        # Dosyayı yeniden adlandır
        mv "$file" "$new_filename"
        echo "Dosya yeniden adlandırıldı: $file -> $new_filename"
    fi
done

echo "İşlem tamamlandı."
