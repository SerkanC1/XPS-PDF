#!/bin/bash

# Kullanıcıdan silinecek karakter uzunluğunu al
read -p "Dosya adından kaç karakter silinecek? (örn. 4): " char_count

# Tüm dosyaları döngü ile işle
for file in *; do
    # Eğer dosya adı belirtilen karakter sayısından uzunsa
    if [[ ${#file} -gt $char_count ]]; then
        # Yeni dosya adını oluştur (ilk n karakteri silerek)
        new_filename="${file:$char_count}"
        
        # Dosyayı yeniden adlandır
        mv "$file" "$new_filename"
        echo "Dosya yeniden adlandırıldı: $file -> $new_filename"
    fi
done

echo "İşlem tamamlandı."
