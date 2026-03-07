import os
import json

from tapsilat_py.client import TapsilatAPI
from tapsilat_py.models import CallbackURLDTO


def load_env(env_path):
    try:
        from dotenv import load_dotenv

        load_dotenv(dotenv_path=env_path)
    except ImportError:
        try:
            with open(env_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        os.environ[k.strip()] = v.strip().strip("'").strip('"')
        except FileNotFoundError:
            pass


def print_step(title, desc=""):
    print("\n" + "=" * 60)
    print(f"👉 SONRAKİ ADIM: {title}")
    if desc:
        print(f"Açıklama: {desc}")
    print("=" * 60)
    input("=> Onaylamak ve işleme devam etmek için ENTER'a basın...\n")


def pretty_print(data):
    try:
        if isinstance(data, dict):
            print(json.dumps(data, indent=4, ensure_ascii=False))
        elif hasattr(data, "__dict__"):
            print(json.dumps(data.__dict__, indent=4, ensure_ascii=False))
        else:
            print(data)
    except TypeError:
        print(data)


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(base_dir, ".env")

    load_env(env_path)
    api_key = os.environ.get("TAPSILAT_API_KEY")
    if not api_key:
        print(f"HATA: API_KEY bulunamadı! '{env_path}' dosyasını kontrol edin.")
        return

    client = TapsilatAPI(api_key=api_key)

    # --- ADIM 1: MEVCUT WEBHOOK (CALLBACK) URL'LERİNİ ALMA ---
    print_step(
        "Mevcut Webhook Ayarlarını Getir (get_organization_callback)",
        "Organizasyonunuza ait mevcut callback URL'leri API'den alınacak.",
    )
    try:
        callback_res = client.get_organization_callback()
        print("\n✅ Mevcut Webhook (Callback) Ayarları:")
        pretty_print(callback_res)
    except Exception as e:
        print(f"❌ Webhook ayarları alınırken hata: {e}")

    # --- ADIM 2: WEBHOOK (CALLBACK) URL'LERİNİ GÜNCELLEME ---
    print_step(
        "Webhook Ayarlarını Güncelle (update_organization_callback)",
        "Organizasyonunuz için yeni callback URL'leri (success, fail, cancel, refund) belirlenecek.",
    )
    try:
        update_req = CallbackURLDTO(
            callback_url="https://api.example.com/webhook/success",
            fail_callback_url="https://api.example.com/webhook/fail",
            cancel_callback_url="https://api.example.com/webhook/cancel",
            refund_callback_url="https://api.example.com/webhook/refund",
        )
        update_res = client.update_organization_callback(update_req)
        print("\n✅ Webhook (Callback) Güncelleme Yanıtı:")
        pretty_print(update_res)
    except Exception as e:
        print(f"❌ Webhook ayarları güncellenirken hata: {e}")

    print("\n🎉 Tüm örnek Webhook/Callback akışı başarıyla tamamlandı!")


if __name__ == "__main__":
    main()
